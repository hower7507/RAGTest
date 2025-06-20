# -*- coding: utf-8 -*-
"""
多阶段查询系统
根据维度分析结果执行不同的搜索策略并整合结果
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer
from dimension_analyzer import DimensionAnalyzer

class MultiStageQuerySystem:
    """
    多阶段查询系统：根据缺失维度执行不同搜索策略
    """
    
    def __init__(self, 
                 search_interface: SearchInterface = None,
                 vectorizer: ChunkVectorizer = None,
                 dimension_analyzer: DimensionAnalyzer = None):
        """
        初始化多阶段查询系统
        
        Args:
            search_interface: 搜索接口实例
            vectorizer: 向量化器实例
            dimension_analyzer: 维度分析器实例
        """
        self.search_interface = search_interface or SearchInterface(config_name="balanced")
        self.vectorizer = vectorizer
        self.dimension_analyzer = dimension_analyzer or DimensionAnalyzer()
        
        # 搜索策略优先级（向量搜索 > 关键词搜索 > 时间搜索）
        self.search_priority = {
            "vector_search": 1,
            "keyword_search": 2, 
            "time_search": 3
        }
        
        print("多阶段查询系统初始化完成")
    
    def execute_vector_search(self, 
                            query: str, 
                            top_k: int = 5,
                            **kwargs) -> List[Dict[str, Any]]:
        """
        执行向量搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            搜索结果列表
        """
        try:
            print(f"执行向量搜索: {query}")
            
            # 使用search_interface进行向量搜索
            search_result = self.search_interface.search(
                query=query,
                top_k=top_k,
                return_prompt=False
            )
            
            if search_result.get('error'):
                print(f"向量搜索失败: {search_result['error']}")
                return []
            
            results = search_result.get('results', [])
            
            # 标记搜索来源
            for result in results:
                result['search_source'] = 'vector_search'
                result['search_priority'] = self.search_priority['vector_search']
            
            print(f"向量搜索完成，获得{len(results)}个结果")
            return results
            
        except Exception as e:
            print(f"向量搜索异常: {e}")
            return []
    
    def execute_keyword_search(self, 
                             query: str, 
                             top_k: int = 5,
                             **kwargs) -> List[Dict[str, Any]]:
        """
        执行关键词搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            搜索结果列表
        """
        try:
            print(f"执行关键词搜索: {query}")
            
            # 使用vectorizer的关键词搜索功能
            if not self.vectorizer:
                print("vectorizer未初始化，跳过关键词搜索")
                return []
            
            # 这里可以实现基于关键词的搜索逻辑
            # 暂时使用向量搜索作为替代（实际项目中可以实现专门的关键词搜索）
            search_result = self.search_interface.search(
                query=query,
                top_k=top_k,
                return_prompt=False
            )
            
            if search_result.get('error'):
                print(f"关键词搜索失败: {search_result['error']}")
                return []
            
            results = search_result.get('results', [])
            
            # 标记搜索来源
            for result in results:
                result['search_source'] = 'keyword_search'
                result['search_priority'] = self.search_priority['keyword_search']
            
            print(f"关键词搜索完成，获得{len(results)}个结果")
            return results
            
        except Exception as e:
            print(f"关键词搜索异常: {e}")
            return []
    
    def execute_time_search(self, 
                          query: str, 
                          start_time: str = None,
                          end_time: str = None,
                          top_k: int = 5,
                          **kwargs) -> List[Dict[str, Any]]:
        """
        执行时间范围搜索
        
        Args:
            query: 查询文本
            start_time: 开始时间
            end_time: 结束时间
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            搜索结果列表
        """
        try:
            print(f"执行时间搜索: {query}, 时间范围: {start_time} - {end_time}")
            
            if not self.vectorizer:
                print("vectorizer未初始化，跳过时间搜索")
                return []
            
            # 使用vectorizer的时间范围搜索
            time_results = self.vectorizer.search_by_time_range(
                start_time=start_time or "00:00",
                end_time=end_time or "99:99",
                n_results=top_k
            )
            
            if not time_results or 'ids' not in time_results:
                print("时间搜索无结果")
                return []
            
            # 转换为统一格式
            results = []
            for doc_id, metadata, document in zip(
                time_results['ids'],
                time_results['metadatas'],
                time_results.get('documents', [])
            ):
                result = {
                    'id': doc_id,
                    'content': document or '',
                    'metadata': metadata,
                    'search_source': 'time_search',
                    'search_priority': self.search_priority['time_search'],
                    'score': 0.5  # 时间搜索的默认得分
                }
                results.append(result)
            
            print(f"时间搜索完成，获得{len(results)}个结果")
            return results
            
        except Exception as e:
            print(f"时间搜索异常: {e}")
            return []
    
    def execute_serial_search(self, 
                            query: str,
                            missing_dimensions: List[str],
                            top_k_per_dimension: int = 5,
                            **kwargs) -> List[Dict[str, Any]]:
        """
        串行执行多个搜索维度
        
        Args:
            query: 查询文本
            missing_dimensions: 需要搜索的维度列表
            top_k_per_dimension: 每个维度返回的结果数量
            **kwargs: 其他参数
            
        Returns:
            合并后的搜索结果
        """
        print(f"开始串行搜索，维度: {missing_dimensions}")
        
        all_results = []
        
        # 按优先级排序维度
        sorted_dimensions = sorted(
            missing_dimensions, 
            key=lambda x: self.search_priority.get(x, 999)
        )
        
        for dimension in sorted_dimensions:
            print(f"\n执行搜索维度: {dimension}")
            
            # 过滤kwargs，避免top_k参数冲突
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'top_k'}
            
            if dimension == "vector_search":
                results = self.execute_vector_search(
                    query=query, 
                    top_k=top_k_per_dimension,
                    **filtered_kwargs
                )
            elif dimension == "keyword_search":
                results = self.execute_keyword_search(
                    query=query,
                    top_k=top_k_per_dimension,
                    **filtered_kwargs
                )
            elif dimension == "time_search":
                results = self.execute_time_search(
                    query=query,
                    top_k=top_k_per_dimension,
                    **filtered_kwargs
                )
            else:
                print(f"未知的搜索维度: {dimension}")
                continue
            
            all_results.extend(results)
            print(f"维度 {dimension} 完成，累计结果数: {len(all_results)}")
        
        return all_results
    
    def multi_stage_search(self, 
                         query: str,
                         current_context: str = "",
                         max_results: int = 10,
                         **kwargs) -> Dict[str, Any]:
        """
        执行完整的多阶段搜索
        
        Args:
            query: 用户查询
            current_context: 当前上下文
            max_results: 最大结果数量
            **kwargs: 其他参数
            
        Returns:
            搜索结果和元信息
        """
        start_time = datetime.now()
        print(f"\n=== 开始多阶段搜索 ===")
        print(f"查询: {query}")
        
        try:
            # 1. 维度分析
            print("\n步骤1: 维度分析")
            dimension_result = self.dimension_analyzer.analyze_query_dimensions(
                query=query,
                current_context=current_context
            )
            
            print(f"分析结果: {dimension_result}")
            
            # 2. 判断是否需要额外搜索
            if not dimension_result["needs_additional_search"]:
                print("当前上下文足够，无需额外搜索")
                return {
                    'query': query,
                    'needs_search': False,
                    'dimension_analysis': dimension_result,
                    'results': [],
                    'search_time': 0,
                    'message': '当前上下文已足够回答查询'
                }
            
            # 3. 执行串行搜索
            print("\n步骤2: 执行搜索")
            missing_dimensions = dimension_result["missing_dimensions"]
            
            if not missing_dimensions:
                print("没有指定搜索维度，使用默认向量搜索")
                missing_dimensions = ["vector_search"]
            
            # 确保每个维度获取足够的结果，避免过度过滤
            per_dimension_results = max(max_results // len(missing_dimensions) + 5, 10)
            search_results = self.execute_serial_search(
                query=query,
                missing_dimensions=missing_dimensions,
                top_k_per_dimension=per_dimension_results,
                **kwargs
            )
            
            # 4. 计算搜索时间
            search_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n=== 多阶段搜索完成 ===")
            print(f"总结果数: {len(search_results)}")
            print(f"搜索耗时: {search_time:.2f}秒")
            
            return {
                'query': query,
                'needs_search': True,
                'dimension_analysis': dimension_result,
                'results': search_results[:max_results],
                'total_results': len(search_results),
                'search_time': search_time,
                'search_dimensions': missing_dimensions
            }
            
        except Exception as e:
            print(f"多阶段搜索失败: {e}")
            
            # 回退到原始搜索逻辑
            print("回退到原始搜索逻辑")
            fallback_result = self.search_interface.search(
                query=query,
                top_k=max_results,
                return_prompt=False
            )
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'query': query,
                'needs_search': True,
                'dimension_analysis': {'error': str(e)},
                'results': fallback_result.get('results', []),
                'search_time': search_time,
                'fallback': True,
                'error': str(e)
            }

# 使用示例
if __name__ == "__main__":
    # 创建多阶段查询系统
    multi_stage_system = MultiStageQuerySystem()
    
    # 测试查询
    test_query = "老师在课程开始时说了什么？"
    
    # 执行多阶段搜索
    result = multi_stage_system.multi_stage_search(
        query=test_query,
        current_context="",
        max_results=5
    )
    
    print("\n最终结果:")
    print(f"查询: {result['query']}")
    print(f"需要搜索: {result['needs_search']}")
    print(f"结果数量: {len(result['results'])}")
    print(f"搜索时间: {result['search_time']:.2f}秒")