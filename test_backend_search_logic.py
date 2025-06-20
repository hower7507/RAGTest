# -*- coding: utf-8 -*-
"""
测试后端搜索逻辑
验证chap01和chap02的查询功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from search_interface import SearchInterface
import json

def test_search_logic():
    """
    测试搜索逻辑
    """
    print("=" * 60)
    print("测试后端搜索逻辑")
    print("=" * 60)
    
    # 初始化搜索接口
    search_interface = SearchInterface("balanced")
    
    if not search_interface.initialize():
        print("❌ 搜索系统初始化失败")
        return
    
    print("\n" + "=" * 40)
    print("数据库状态检查")
    print("=" * 40)
    
    # 检查数据库状态
    try:
        collection_info = search_interface.vectorizer.get_collection_info()
        print(f"总记录数: {collection_info.get('total_records', 0)}")
        
        # 获取所有数据进行分析
        all_results = search_interface.vectorizer.collection.get()
        
        chap01_count = 0
        chap02_count = 0
        qa_count = 0
        other_count = 0
        
        print("\n数据分布分析:")
        for i, metadata in enumerate(all_results.get('metadatas', [])):
            if metadata:
                source_file = metadata.get('source_file', '')
                question = metadata.get('question', '')
                
                if 'chap01' in source_file:
                    chap01_count += 1
                elif 'chap02' in source_file:
                    chap02_count += 1
                elif question and question.strip():
                    qa_count += 1
                else:
                    other_count += 1
                    
                # 显示前几条记录的详细信息
                if i < 5:
                    print(f"  记录{i+1}: source_file='{source_file}', question='{question[:30]}...'")
        
        print(f"\nchap01数据: {chap01_count}条")
        print(f"chap02数据: {chap02_count}条")
        print(f"QA数据: {qa_count}条")
        print(f"其他数据: {other_count}条")
        
    except Exception as e:
        print(f"数据库状态检查失败: {e}")
    
    print("\n" + "=" * 40)
    print("测试查询1: chap01 - 乔老师的手机")
    print("=" * 40)
    
    query1 = "乔老师的手机"
    try:
        result1 = search_interface.search(query1, top_k=5)
        
        print(f"查询: {query1}")
        print(f"结果数量: {result1.get('total_results', 0)}")
        print(f"搜索时间: {result1.get('search_time', 0):.3f}秒")
        print(f"候选文档数: {result1.get('total_candidates', 0)}")
        print(f"提取关键词: {result1.get('keywords_extracted', [])}")
        
        if result1.get('results'):
            print("\n搜索结果:")
            for i, res in enumerate(result1['results'][:3]):
                print(f"\n结果{i+1}:")
                print(f"  文档ID: {res['document_id']}")
                print(f"  得分: {res['score']:.4f}")
                print(f"  来源文件: {res['metadata'].get('source_file', '未知')}")
                print(f"  内容: {res['content'][:100]}...")
                print(f"  得分详情: vector={res['scores']['vector_score']:.4f}, bm25={res['scores']['bm25_score']:.4f}, exact={res['scores']['exact_score']:.4f}")
        else:
            print("❌ 没有找到相关结果")
            
    except Exception as e:
        print(f"查询1失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("测试查询2: chap02 - 技术真的可以拉开差距吗")
    print("=" * 40)
    
    query2 = "技术真的可以拉开差距吗"
    try:
        result2 = search_interface.search(query2, top_k=5)
        
        print(f"查询: {query2}")
        print(f"结果数量: {result2.get('total_results', 0)}")
        print(f"搜索时间: {result2.get('search_time', 0):.3f}秒")
        print(f"候选文档数: {result2.get('total_candidates', 0)}")
        print(f"提取关键词: {result2.get('keywords_extracted', [])}")
        
        if result2.get('results'):
            print("\n搜索结果:")
            for i, res in enumerate(result2['results'][:3]):
                print(f"\n结果{i+1}:")
                print(f"  文档ID: {res['document_id']}")
                print(f"  得分: {res['score']:.4f}")
                print(f"  来源文件: {res['metadata'].get('source_file', '未知')}")
                print(f"  内容: {res['content'][:100]}...")
                print(f"  得分详情: vector={res['scores']['vector_score']:.4f}, bm25={res['scores']['bm25_score']:.4f}, exact={res['scores']['exact_score']:.4f}")
        else:
            print("❌ 没有找到相关结果")
            
    except Exception as e:
        print(f"查询2失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("BM25索引状态检查")
    print("=" * 40)
    
    try:
        search_system = search_interface.search_system
        if hasattr(search_system, 'bm25_index'):
            print(f"BM25索引文档数: {len(search_system.bm25_index)}")
            print(f"平均文档长度: {search_system.avg_doc_length:.1f}")
            print(f"词项文档频率统计: {len(search_system.term_doc_freq)}个词项")
            
            # 检查一些关键词的文档频率
            test_terms = ['乔老师', '手机', '技术', '差距']
            print("\n关键词文档频率:")
            for term in test_terms:
                freq = search_system.term_doc_freq.get(term, 0)
                print(f"  '{term}': {freq}个文档")
                
            # 显示前几个BM25索引的ID
            print("\nBM25索引ID示例:")
            for i, doc_id in enumerate(list(search_system.bm25_index.keys())[:5]):
                print(f"  {i+1}: {doc_id}")
        else:
            print("❌ BM25索引未构建")
            
    except Exception as e:
        print(f"BM25索引检查失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_search_logic()