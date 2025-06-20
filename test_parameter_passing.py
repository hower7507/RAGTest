# -*- coding: utf-8 -*-
"""
测试参数传递问题
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from advanced_search_system import AdvancedSearchSystem
from vectorize_chunks import ChunkVectorizer

def test_parameter_passing():
    """测试参数传递链条"""
    
    print("=== 测试参数传递链条 ===")
    
    # 1. 测试SearchInterface.search方法的参数
    print("\n1. 测试SearchInterface.search方法参数:")
    try:
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        if not success:
            print("❌ SearchInterface初始化失败")
            return
        
        # 测试参数传递
        query = "测试查询"
        top_k = 5
        start_time = None
        end_time = None
        
        print(f"传入参数: query='{query}', top_k={top_k}, start_time={start_time}, end_time={end_time}")
        
        # 检查SearchInterface.search方法的参数传递
        print("\n调用SearchInterface.search...")
        
        # 手动调用search_system.search来检查参数
        print("\n2. 测试AdvancedSearchSystem.search方法参数:")
        result = search_interface.search_system.search(
            query=query,
            top_k=top_k,
            start_time=start_time,
            end_time=end_time,
            max_context_length=search_interface.config.max_context_length
        )
        
        print(f"AdvancedSearchSystem.search接收到的参数:")
        print(f"  query: {query}")
        print(f"  top_k: {top_k}")
        print(f"  start_time: {start_time}")
        print(f"  end_time: {end_time}")
        print(f"  max_context_length: {search_interface.config.max_context_length}")
        
        print(f"\n返回结果类型: {type(result)}")
        print(f"返回结果键: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and 'results' in result:
            print(f"结果数量: {len(result['results'])}")
        
    except Exception as e:
        print(f"❌ 参数传递测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_vectorizer_parameters():
    """测试向量化器参数传递"""
    
    print("\n=== 测试向量化器参数传递 ===")
    
    try:
        # 直接测试ChunkVectorizer
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        vectorizer.load_model()
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 测试search_similar_chunks参数
        query_text = "测试查询"
        n_results = 5
        start_time = None
        end_time = None
        
        print(f"\n调用ChunkVectorizer.search_similar_chunks:")
        print(f"  query_text: {query_text}")
        print(f"  n_results: {n_results}")
        print(f"  start_time: {start_time}")
        print(f"  end_time: {end_time}")
        
        results = vectorizer.search_similar_chunks(
            query_text=query_text,
            n_results=n_results,
            start_time=start_time,
            end_time=end_time
        )
        
        print(f"\n向量搜索结果类型: {type(results)}")
        print(f"向量搜索结果键: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"  {key}: {len(value[0]) if isinstance(value[0], list) else len(value)} 项")
                else:
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ 向量化器参数测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_search_candidates_parameters():
    """测试search_candidates参数传递"""
    
    print("\n=== 测试search_candidates参数传递 ===")
    
    try:
        # 创建AdvancedSearchSystem实例
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        vectorizer.load_model()
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        search_system = AdvancedSearchSystem(
            vectorizer=vectorizer,
            bm25_weight=0.4,
            vector_weight=0.4,
            exact_weight=0.2
        )
        
        # 测试search_candidates参数
        query = "测试查询"
        n_candidates = 10
        start_time = None
        end_time = None
        
        print(f"\n调用AdvancedSearchSystem.search_candidates:")
        print(f"  query: {query}")
        print(f"  n_candidates: {n_candidates}")
        print(f"  start_time: {start_time}")
        print(f"  end_time: {end_time}")
        
        candidates = search_system.search_candidates(
            query=query,
            n_candidates=n_candidates,
            start_time=start_time,
            end_time=end_time
        )
        
        print(f"\nsearch_candidates返回结果类型: {type(candidates)}")
        print(f"候选文档数量: {len(candidates) if isinstance(candidates, list) else 'Not a list'}")
        
        if isinstance(candidates, list) and len(candidates) > 0:
            print(f"第一个候选文档键: {list(candidates[0].keys())}")
        
    except Exception as e:
        print(f"❌ search_candidates参数测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    
    print("🔍 开始测试参数传递问题")
    print("=" * 60)
    
    # 1. 测试基本参数传递
    test_parameter_passing()
    
    # 2. 测试向量化器参数
    test_vectorizer_parameters()
    
    # 3. 测试search_candidates参数
    test_search_candidates_parameters()
    
    print("\n" + "=" * 60)
    print("📋 参数传递测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()