# -*- coding: utf-8 -*-
"""
专门测试时间参数传递问题
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from advanced_search_system import AdvancedSearchSystem
from vectorize_chunks import ChunkVectorizer

def test_time_parameter_issue():
    """测试时间参数传递问题"""
    
    print("=== 测试时间参数传递问题 ===")
    
    try:
        # 1. 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        if not success:
            print("❌ SearchInterface初始化失败")
            return
        
        # 2. 测试不同的时间参数组合
        test_cases = [
            {
                "name": "无时间参数",
                "query": "技术",
                "start_time": None,
                "end_time": None
            },
            {
                "name": "只有开始时间",
                "query": "技术",
                "start_time": "10:00",
                "end_time": None
            },
            {
                "name": "只有结束时间",
                "query": "技术",
                "start_time": None,
                "end_time": "20:00"
            },
            {
                "name": "完整时间范围",
                "query": "技术",
                "start_time": "10:00",
                "end_time": "20:00"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- 测试案例 {i}: {test_case['name']} ---")
            print(f"查询: {test_case['query']}")
            print(f"开始时间: {test_case['start_time']}")
            print(f"结束时间: {test_case['end_time']}")
            
            try:
                # 调用SearchInterface.search
                print("\n调用SearchInterface.search...")
                result = search_interface.search(
                    query=test_case['query'],
                    top_k=3,
                    start_time=test_case['start_time'],
                    end_time=test_case['end_time'],
                    return_prompt=False
                )
                
                print(f"SearchInterface.search返回结果:")
                if isinstance(result, dict):
                    print(f"  结果类型: dict")
                    print(f"  键: {list(result.keys())}")
                    
                    if 'search_results' in result:
                        search_results = result['search_results']
                        print(f"  搜索结果数量: {len(search_results)}")
                        
                        # 检查结果中的时间信息
                        for j, res in enumerate(search_results[:2]):
                            metadata = res.get('metadata', {})
                            print(f"    结果{j+1}元数据: {metadata}")
                    
                    if 'results' in result:
                        results = result['results']
                        print(f"  结果数量: {len(results)}")
                        
                        # 检查结果中的时间信息
                        for j, res in enumerate(results[:2]):
                            metadata = res.get('metadata', {})
                            print(f"    结果{j+1}元数据: {metadata}")
                else:
                    print(f"  结果类型: {type(result)}")
                    print(f"  结果内容: {result}")
                
                # 直接调用AdvancedSearchSystem.search来对比
                print("\n直接调用AdvancedSearchSystem.search...")
                direct_result = search_interface.search_system.search(
                    query=test_case['query'],
                    top_k=3,
                    start_time=test_case['start_time'],
                    end_time=test_case['end_time'],
                    max_context_length=2000
                )
                
                print(f"AdvancedSearchSystem.search返回结果:")
                if isinstance(direct_result, dict):
                    print(f"  结果类型: dict")
                    print(f"  键: {list(direct_result.keys())}")
                    
                    if 'results' in direct_result:
                        results = direct_result['results']
                        print(f"  结果数量: {len(results)}")
                        
                        # 检查结果中的时间信息
                        for j, res in enumerate(results[:2]):
                            metadata = res.get('metadata', {})
                            print(f"    结果{j+1}元数据: {metadata}")
                else:
                    print(f"  结果类型: {type(direct_result)}")
                    print(f"  结果内容: {direct_result}")
                
            except Exception as e:
                print(f"❌ 测试案例 {i} 失败: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ 时间参数测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_vectorizer_time_filtering():
    """测试向量化器的时间过滤功能"""
    
    print("\n=== 测试向量化器时间过滤功能 ===")
    
    try:
        # 直接测试ChunkVectorizer的时间过滤
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        vectorizer.load_model()
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 测试时间过滤
        test_cases = [
            {
                "name": "无时间过滤",
                "start_time": None,
                "end_time": None
            },
            {
                "name": "时间范围过滤",
                "start_time": "10:00",
                "end_time": "20:00"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n--- {test_case['name']} ---")
            print(f"开始时间: {test_case['start_time']}")
            print(f"结束时间: {test_case['end_time']}")
            
            try:
                results = vectorizer.search_similar_chunks(
                    query_text="技术",
                    n_results=5,
                    start_time=test_case['start_time'],
                    end_time=test_case['end_time']
                )
                
                print(f"向量搜索结果:")
                if isinstance(results, dict):
                    for key, value in results.items():
                        if isinstance(value, list) and len(value) > 0:
                            if isinstance(value[0], list):
                                print(f"  {key}: {len(value[0])} 项")
                            else:
                                print(f"  {key}: {len(value)} 项")
                        else:
                            print(f"  {key}: {value}")
                    
                    # 检查元数据中的时间信息
                    if 'metadatas' in results and results['metadatas']:
                        metadatas = results['metadatas'][0] if isinstance(results['metadatas'][0], list) else results['metadatas']
                        print(f"  前3个结果的时间信息:")
                        for i, metadata in enumerate(metadatas[:3]):
                            if metadata:
                                start_time_meta = metadata.get('start_time', metadata.get('start_timestamp', 'N/A'))
                                end_time_meta = metadata.get('end_time', metadata.get('end_timestamp', 'N/A'))
                                print(f"    结果{i+1}: start={start_time_meta}, end={end_time_meta}")
                
            except Exception as e:
                print(f"❌ 向量化器时间过滤测试失败: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ 向量化器时间过滤测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    
    print("🔍 开始测试时间参数传递问题")
    print("=" * 60)
    
    # 1. 测试时间参数传递
    test_time_parameter_issue()
    
    # 2. 测试向量化器时间过滤
    test_vectorizer_time_filtering()
    
    print("\n" + "=" * 60)
    print("📋 时间参数传递测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()