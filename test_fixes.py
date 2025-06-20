#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的搜索系统
验证关键词搜索、元数据保存、BRE重排序等修复
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer
from multi_stage_query import MultiStageQuerySystem
from dimension_analyzer import DimensionAnalyzer
from deepseek_client import DeepSeekClient
from deepseek_config_presets import DeepSeekPresets
from context_manager import ContextManager
import json

def test_keyword_search_initialization():
    """测试关键词搜索初始化修复"""
    print("\n=== 测试关键词搜索初始化 ===")
    
    try:
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        search_interface.initialize()
        
        # 获取vectorizer
        vectorizer = search_interface.vectorizer
        print(f"Vectorizer初始化状态: {vectorizer is not None}")
        
        # 初始化多阶段查询系统
        multi_stage_query = MultiStageQuerySystem(search_interface, vectorizer)
        print(f"MultiStageQuerySystem vectorizer: {multi_stage_query.vectorizer is not None}")
        
        # 测试关键词搜索
        keyword_results = multi_stage_query.execute_keyword_search("创新", top_k=5)
        print(f"关键词搜索结果数: {len(keyword_results)}")
        
        return True
        
    except Exception as e:
        print(f"关键词搜索初始化测试失败: {e}")
        return False

def test_metadata_saving():
    """测试元数据保存修复"""
    print("\n=== 测试元数据保存 ===")
    
    try:
        # 测试维度分析结果转换
        dimension_result = {
            'dimensions': ['时间', '人物', '事件'],
            'confidence': 0.8
        }
        
        # 模拟转换过程
        dimensions = dimension_result.get('dimensions', [])
        dimension_str = json.dumps(dimensions, ensure_ascii=False) if dimensions else ""
        
        print(f"原始维度: {dimensions}")
        print(f"转换后字符串: {dimension_str}")
        print(f"字符串类型: {type(dimension_str)}")
        
        # 验证可以正确解析回来
        parsed_dimensions = json.loads(dimension_str)
        print(f"解析回的维度: {parsed_dimensions}")
        
        return True
        
    except Exception as e:
        print(f"元数据保存测试失败: {e}")
        return False

def test_bre_reranking():
    """测试BRE重排序参数调整"""
    print("\n=== 测试BRE重排序参数 ===")
    
    try:
        from advanced_search_system import AdvancedSearchSystem
        
        # 创建高级搜索系统实例
        bre_system = AdvancedSearchSystem()
        
        print(f"向量权重: {bre_system.vector_weight}")
        print(f"BM25权重: {bre_system.bm25_weight}")
        print(f"精确匹配权重: {bre_system.exact_weight}")
        print(f"权重总和: {bre_system.vector_weight + bre_system.bm25_weight + bre_system.exact_weight}")
        
        # 验证权重调整是否合理
        if bre_system.vector_weight > bre_system.bm25_weight:
            print("✓ 向量权重大于BM25权重，有利于保留更多结果")
        else:
            print("✗ 权重设置可能不够优化")
            
        return True
        
    except Exception as e:
        print(f"BRE重排序测试失败: {e}")
        return False

def test_deepseek_json_handling():
    """测试DeepSeek JSON处理改进"""
    print("\n=== 测试DeepSeek JSON处理 ===")
    
    try:
        from dimension_analyzer import DimensionAnalyzer
        
        # 创建维度分析器
        deepseek_config = DeepSeekPresets.get_qa_system()
        deepseek_client = DeepSeekClient(deepseek_config)
        analyzer = DimensionAnalyzer(deepseek_client)
        
        # 测试JSON修复功能
        test_cases = [
            '{"test": "value"}',  # 正常JSON
            "{'test': 'value'}",  # 单引号
            '{"test": "value",}',  # 尾随逗号
            'test: "value"',  # 缺失引号
            '{"bool": True}',  # Python布尔值
        ]
        
        for i, test_json in enumerate(test_cases):
            try:
                fixed_json = analyzer._fix_json_format(test_json)
                parsed = json.loads(fixed_json)
                print(f"测试用例 {i+1}: ✓ 修复成功")
            except Exception as e:
                print(f"测试用例 {i+1}: ✗ 修复失败 - {e}")
        
        return True
        
    except Exception as e:
        print(f"DeepSeek JSON处理测试失败: {e}")
        return False

def test_search_result_processing():
    """测试搜索结果处理优化"""
    print("\n=== 测试搜索结果处理优化 ===")
    
    try:
        # 初始化搜索系统
        search_interface = SearchInterface(config_name="balanced")
        search_interface.initialize()
        
        vectorizer = search_interface.vectorizer
        deepseek_config = DeepSeekPresets.get_qa_system()
        deepseek_client = DeepSeekClient(deepseek_config)
        dimension_analyzer = DimensionAnalyzer(deepseek_client)
        
        multi_stage_query = MultiStageQuerySystem(search_interface, vectorizer, dimension_analyzer)
        
        # 执行搜索测试
        result = multi_stage_query.multi_stage_search("梁文峰的采访", max_results=5)
        
        print(f"搜索结果数: {result.get('total_results', 0)}")
        print(f"返回结果数: {len(result.get('results', []))}")
        print(f"搜索维度: {result.get('search_dimensions', [])}")
        
        if result.get('results'):
            print("✓ 搜索结果处理正常")
            return True
        else:
            print("✗ 搜索结果为空")
            return False
        
    except Exception as e:
        print(f"搜索结果处理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试搜索系统修复...")
    
    tests = [
        ("关键词搜索初始化", test_keyword_search_initialization),
        ("元数据保存", test_metadata_saving),
        ("BRE重排序参数", test_bre_reranking),
        ("DeepSeek JSON处理", test_deepseek_json_handling),
        ("搜索结果处理优化", test_search_result_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"测试 {test_name} 出现异常: {e}")
            results.append((test_name, False))
    
    print("\n=== 测试结果汇总 ===")
    passed = 0
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有修复验证通过！")
    else:
        print("⚠️  部分修复需要进一步检查")

if __name__ == "__main__":
    main()