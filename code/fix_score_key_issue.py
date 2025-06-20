# -*- coding: utf-8 -*-
"""
修复分数键值问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vectorize_chunks import ChunkVectorizer
from advanced_search_system import AdvancedSearchSystem

def fix_score_key_issue():
    """
    修复分数键值问题
    """
    print("=== 修复分数键值问题 ===")
    
    # 初始化系统
    print("\n1. 初始化系统...")
    vectorizer = ChunkVectorizer()
    vectorizer.init_chromadb()
    vectorizer.load_model()
    search_system = AdvancedSearchSystem(vectorizer)
    
    query = "技术真的可以拉开差距吗？"
    print(f"\n2. 测试查询: {query}")
    
    # 测试rerank_with_bre方法的返回结果
    print("\n3. 测试rerank_with_bre方法...")
    
    # 先获取候选文档
    candidates = search_system.search_candidates(
        query=query,
        n_candidates=10
    )
    
    print(f"获得 {len(candidates)} 个候选文档")
    
    if candidates:
        # 调用rerank_with_bre方法
        reranked_results = search_system.rerank_with_bre(query, candidates, top_k=3)
        
        print(f"\n4. rerank_with_bre返回 {len(reranked_results)} 个结果")
        
        for i, result in enumerate(reranked_results):
            print(f"\n结果 {i+1}:")
            print(f"  所有键: {list(result.keys())}")
            print(f"  ID: {result.get('id', 'N/A')}")
            print(f"  final_score: {result.get('final_score', 'N/A')}")
            print(f"  score: {result.get('score', 'N/A')}")
            print(f"  vector_score: {result.get('vector_score', 'N/A')}")
            print(f"  bm25_score: {result.get('bm25_score', 'N/A')}")
            print(f"  exact_score: {result.get('exact_score', 'N/A')}")
            
            # 检查score_breakdown
            if 'score_breakdown' in result:
                breakdown = result['score_breakdown']
                print(f"  score_breakdown: {breakdown}")
    
    # 测试完整的search方法
    print("\n5. 测试完整search方法...")
    search_results = search_system.search(query=query, top_k=3)
    
    if isinstance(search_results, dict) and 'results' in search_results:
        results = search_results['results']
        print(f"search方法返回 {len(results)} 个结果")
        
        for i, result in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"  所有键: {list(result.keys())}")
            print(f"  ID: {result.get('id', 'N/A')}")
            print(f"  final_score: {result.get('final_score', 'N/A')}")
            print(f"  score: {result.get('score', 'N/A')}")
            print(f"  vector_score: {result.get('vector_score', 'N/A')}")
            print(f"  bm25_score: {result.get('bm25_score', 'N/A')}")
            print(f"  exact_score: {result.get('exact_score', 'N/A')}")
    
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    try:
        fix_score_key_issue()
    except Exception as e:
        print(f"[ERROR] 修复失败: {e}")
        import traceback
        traceback.print_exc()