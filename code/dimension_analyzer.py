# -*- coding: utf-8 -*-
"""
维度分析器
使用DeepSeek判断查询是否需要额外搜索以及缺失的维度
"""

import json
import re
from typing import Dict, List, Any, Optional
from deepseek_client import DeepSeekClient
from deepseek_config_presets import DeepSeekPresets

class DimensionAnalyzer:
    """
    维度分析器：使用DeepSeek判断查询的缺失维度
    """
    
    def __init__(self, deepseek_client: DeepSeekClient = None):
        """
        初始化维度分析器
        
        Args:
            deepseek_client: DeepSeek客户端实例
        """
        self.deepseek_client = deepseek_client or DeepSeekClient(DeepSeekPresets.get_precise())
        
        # 维度判断的提示词模板
        self.dimension_prompt_template = """
你是一个专业的查询分析助手。请分析用户的查询是否需要额外的搜索来获取完整信息。

用户查询：{query}

当前可用的上下文信息：
{current_context}

请判断：
1. 当前上下文是否足够回答用户的查询？
2. 如果不足够，需要哪些额外的搜索维度？

可用的搜索维度包括：
- vector_search: 向量语义搜索（适用于概念性、主题性查询）
- keyword_search: 关键词搜索（适用于精确词汇匹配）
- time_search: 时间范围搜索（适用于特定时间段的内容）

请以JSON格式回复，格式如下：
{{
    "needs_additional_search": true/false,
    "missing_dimensions": ["dimension1", "dimension2"],
    "confidence": 0.0-1.0,
    "reasoning": "判断理由"
}}

注意：
- 如果当前上下文已经包含足够信息回答查询，设置needs_additional_search为false
- missing_dimensions只能包含上述三种维度
- confidence表示判断的置信度
- reasoning简要说明判断理由
"""
    
    def analyze_query_dimensions(self, query: str, current_context: str = None) -> Dict[str, Any]:
        """
        分析查询的维度需求
        
        Args:
            query: 用户查询
            current_context: 当前上下文（可选）
            
        Returns:
            维度分析结果
        """
        # 首先尝试使用DeepSeek进行分析
        try:
            print(f"使用DeepSeek分析查询维度: {query}")
            
            # 准备提示词
            context_info = current_context or "当前没有上下文信息"
            prompt = self.dimension_prompt_template.format(
                query=query,
                current_context=context_info
            )
            
            # 调用DeepSeek
            response = self.deepseek_client.simple_chat(prompt)
            print(f"DeepSeek原始响应长度: {len(response)}")
            print(f"DeepSeek原始响应: {repr(response)}")
            print(f"DeepSeek响应前100字符: {response[:100]}")
            print(f"DeepSeek响应后100字符: {response[-100:]}")
            
            # 清理和解析JSON响应
            cleaned_response = response.strip()
            
            # 移除可能的markdown代码块标记
            if '```json' in cleaned_response:
                start_idx = cleaned_response.find('```json') + 7
                end_idx = cleaned_response.find('```', start_idx)
                if end_idx != -1:
                    cleaned_response = cleaned_response[start_idx:end_idx].strip()
            elif '```' in cleaned_response:
                start_idx = cleaned_response.find('```') + 3
                end_idx = cleaned_response.find('```', start_idx)
                if end_idx != -1:
                    cleaned_response = cleaned_response[start_idx:end_idx].strip()
            
            # 如果响应不是以{开头或}结尾，尝试提取JSON部分
            if not (cleaned_response.startswith('{') and cleaned_response.endswith('}')):
                # 查找JSON部分
                start_idx = cleaned_response.find('{')
                end_idx = cleaned_response.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    cleaned_response = cleaned_response[start_idx:end_idx]
                    print(f"提取的JSON部分: {repr(cleaned_response)}")
            
            # 解析JSON - 增强容错性
            try:
                # 尝试修复常见的JSON格式问题
                fixed_response = self._fix_json_format(cleaned_response)
                result = json.loads(fixed_response)
                print(f"解析后的结果: {result}")
                
                # 验证结果格式
                if self._validate_analysis_result(result):
                    # 添加兼容性字段
                    result["dimensions"] = result["missing_dimensions"]
                    print("DeepSeek分析成功")
                    return result
                else:
                    print("DeepSeek结果格式验证失败，使用规则分析")
                    return self._rule_based_analysis(query)
                    
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"原始响应: {repr(response)}")
                print(f"清理后响应: {repr(cleaned_response)}")
                print(f"修复后响应: {repr(fixed_response)}")
                print("尝试使用规则分析作为备选方案")
                return self._rule_based_analysis(query)
            except Exception as e:
                print(f"DeepSeek分析出现未知错误: {e}，使用规则分析")
                return self._rule_based_analysis(query)
                
        except Exception as e:
            print(f"DeepSeek分析失败: {e}，回退到规则分析")
            return self._rule_based_analysis(query)
    
    def _rule_based_analysis(self, query: str) -> Dict[str, Any]:
        """
        基于规则的维度分析（作为DeepSeek的回退方案）
        
        Args:
            query: 用户查询
            
        Returns:
            分析结果
        """
        print("使用规则分析作为回退方案")
        
        missing_dimensions = []
        
        # 检查是否包含时间信息
        time_keywords = ['时间', '分钟', '秒', '小时', '开始', '结束', '期间', '之间']
        if any(keyword in query for keyword in time_keywords):
            missing_dimensions.append('time_search')
        
        # 检查是否包含特定关键词
        if len(query) > 2:  # 简单判断
            missing_dimensions.append('keyword_search')
        
        # 默认都需要向量搜索
        missing_dimensions.append('vector_search')
        
        # 去重
        missing_dimensions = list(set(missing_dimensions))
        
        return {
            "needs_additional_search": True,
            "missing_dimensions": missing_dimensions,
            "confidence": 0.8,
            "reasoning": "基于规则的回退分析",
            "dimensions": missing_dimensions  # 添加这个字段以保持兼容性
        }
    
    def _fix_json_format(self, json_str: str) -> str:
        """
        修复常见的JSON格式问题
        
        Args:
            json_str: 原始JSON字符串
            
        Returns:
            修复后的JSON字符串
        """
        try:
            # 移除多余的空白字符
            json_str = json_str.strip()
            
            # 移除markdown代码块标记
            if '```json' in json_str:
                start_idx = json_str.find('```json') + 7
                end_idx = json_str.find('```', start_idx)
                if end_idx != -1:
                    json_str = json_str[start_idx:end_idx].strip()
            elif '```' in json_str:
                start_idx = json_str.find('```') + 3
                end_idx = json_str.find('```', start_idx)
                if end_idx != -1:
                    json_str = json_str[start_idx:end_idx].strip()
            
            # 如果不是以{开头或}结尾，尝试提取JSON部分
            if not (json_str.startswith('{') and json_str.endswith('}')):
                start_idx = json_str.find('{')
                end_idx = json_str.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = json_str[start_idx:end_idx]
            
            # 智能修复单引号为双引号（避免破坏字符串内容中的单引号）
            # 只替换作为JSON语法的单引号，不替换字符串内容中的单引号
            import re
            
            # JSON字符串中的单引号是合法的，不需要转义
            # 只需要替换作为JSON语法的单引号（键名和简单值）
            
            # 替换键名周围的单引号
            json_str = re.sub(r"'([^']+)'\s*:", r'"\1":', json_str)
            # 替换简单值周围的单引号（不包含转义字符的）
            json_str = re.sub(r":\s*'([^'\\]*)'([,}\]])", r': "\1"\2', json_str)
            
            # 修复尾随逗号
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            # 修复缺失的引号（但要小心不要破坏已有的引号）
            # 只修复明显缺少引号的键名
            json_str = re.sub(r'([^"\s])([a-zA-Z_][a-zA-Z0-9_]*):', r'\1"\2":', json_str)
            json_str = re.sub(r'^([a-zA-Z_][a-zA-Z0-9_]*):', r'"\1":', json_str, flags=re.MULTILINE)
            
            # 修复布尔值
            json_str = json_str.replace('True', 'true').replace('False', 'false')
            
            return json_str
        except Exception as e:
            print(f"JSON修复失败: {e}")
            return json_str
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> bool:
        """
        验证分析结果的格式
        
        Args:
            result: 分析结果
            
        Returns:
            是否有效
        """
        required_fields = ["needs_additional_search", "missing_dimensions", "confidence", "reasoning"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in result:
                print(f"缺少必需字段: {field}")
                return False
        
        # 检查字段类型
        if not isinstance(result["needs_additional_search"], bool):
            print("needs_additional_search必须是布尔值")
            return False
            
        if not isinstance(result["missing_dimensions"], list):
            print("missing_dimensions必须是列表")
            return False
            
        if not isinstance(result["confidence"], (int, float)) or not (0 <= result["confidence"] <= 1):
            print("confidence必须是0-1之间的数值")
            return False
            
        # 检查维度有效性
        valid_dimensions = {"vector_search", "keyword_search", "time_search"}
        for dim in result["missing_dimensions"]:
            if dim not in valid_dimensions:
                print(f"无效的搜索维度: {dim}")
                return False
        
        return True
    
    def _get_fallback_result(self, reason: str) -> Dict[str, Any]:
        """
        获取回退结果（当DeepSeek分析失败时）
        
        Args:
            reason: 失败原因
            
        Returns:
            回退的分析结果
        """
        print(f"使用回退策略: {reason}")
        return {
            "needs_additional_search": True,  # 保守策略：默认需要额外搜索
            "missing_dimensions": ["vector_search"],  # 默认使用向量搜索
            "confidence": 0.5,
            "reasoning": f"DeepSeek分析失败，使用回退策略: {reason}"
        }
    
    def should_use_additional_search(self, 
                                   query: str, 
                                   current_context: str = "",
                                   confidence_threshold: float = 0.7) -> bool:
        """
        简化的判断接口：是否需要额外搜索
        
        Args:
            query: 用户查询
            current_context: 当前上下文
            confidence_threshold: 置信度阈值
            
        Returns:
            是否需要额外搜索
        """
        result = self.analyze_query_dimensions(query, current_context)
        
        # 如果置信度低于阈值，使用保守策略
        if result["confidence"] < confidence_threshold:
            print(f"置信度{result['confidence']:.2f}低于阈值{confidence_threshold}，使用保守策略")
            return True
            
        return result["needs_additional_search"]
    
    def get_missing_dimensions(self, 
                             query: str, 
                             current_context: str = "") -> List[str]:
        """
        获取缺失的搜索维度
        
        Args:
            query: 用户查询
            current_context: 当前上下文
            
        Returns:
            缺失的维度列表
        """
        result = self.analyze_query_dimensions(query, current_context)
        return result["missing_dimensions"]

# 使用示例
if __name__ == "__main__":
    # 创建分析器实例
    analyzer = DimensionAnalyzer()
    
    # 测试查询
    test_query = "老师在课程中提到了什么关于自然语言处理的定义？"
    test_context = "当前没有相关上下文信息"
    
    # 进行维度分析
    result = analyzer.analyze_query_dimensions(test_query, test_context)
    print("维度分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 简化判断
    needs_search = analyzer.should_use_additional_search(test_query, test_context)
    print(f"\n是否需要额外搜索: {needs_search}")
    
    # 获取缺失维度
    missing_dims = analyzer.get_missing_dimensions(test_query, test_context)
    print(f"缺失的维度: {missing_dims}")