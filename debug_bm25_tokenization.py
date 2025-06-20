# -*- coding: utf-8 -*-
"""
调试BM25索引和分词问题
分析为什么"乔老师"无法被正确索引
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from search_interface import SearchInterface
from advanced_search_system import AdvancedSearchSystem
import jieba
import jieba.analyse
from collections import Counter

def debug_tokenization():
    """
    调试分词和索引问题
    """
    print("=" * 60)
    print("调试BM25索引和分词问题")
    print("=" * 60)
    
    # 初始化搜索接口
    search_interface = SearchInterface("balanced")
    
    if not search_interface.initialize():
        print("❌ 搜索系统初始化失败")
        return
    
    search_system = search_interface.search_system
    
    print("\n" + "=" * 40)
    print("测试分词效果")
    print("=" * 40)
    
    test_texts = [
        "乔老师的手机号13926026874",
        "我的名字你在屏幕上可以看到叫乔梁，然后我的邮箱就是 Bridge@139.com，就是乔梁的英文，然后我的手机号13926026874",
        "技术真的可以拉开差距吗",
        "在颠覆性的技术面前，闭源形成的护城河是短暂的"
    ]
    
    for text in test_texts:
        print(f"\n原文: {text}")
        
        # 使用jieba分词
        jieba_words = jieba.lcut(text)
        print(f"jieba分词: {jieba_words}")
        
        # 使用搜索系统的预处理
        processed_words = search_system.preprocess_text(text)
        print(f"系统预处理: {processed_words}")
        
        # 使用jieba关键词抽取
        keywords = jieba.analyse.extract_tags(text, topK=5, withWeight=True)
        print(f"关键词抽取: {keywords}")
    
    print("\n" + "=" * 40)
    print("检查BM25索引中的具体内容")
    print("=" * 40)
    
    # 查找包含"乔"或"手机"的文档
    target_terms = ['乔', '老师', '手机', '乔老师', '乔梁']
    
    for term in target_terms:
        print(f"\n检查词项: '{term}'")
        
        # 检查词项文档频率
        doc_freq = search_system.term_doc_freq.get(term, 0)
        print(f"  文档频率: {doc_freq}")
        
        # 查找包含该词项的文档
        matching_docs = []
        for doc_id, word_freq in search_system.bm25_index.items():
            if term in word_freq:
                matching_docs.append((doc_id, word_freq[term]))
        
        if matching_docs:
            print(f"  包含该词项的文档数: {len(matching_docs)}")
            # 显示前几个匹配的文档
            for i, (doc_id, freq) in enumerate(matching_docs[:3]):
                print(f"    文档{i+1}: {doc_id}, 频率: {freq}")
        else:
            print(f"  ❌ 没有文档包含词项'{term}'")
    
    print("\n" + "=" * 40)
    print("检查原始文档内容")
    print("=" * 40)
    
    # 获取包含"乔"或"手机"的原始文档
    try:
        all_results = search_interface.vectorizer.collection.get()
        
        print("查找包含'乔'或'手机'的文档:")
        found_docs = []
        
        for i, (doc_id, content, metadata) in enumerate(zip(
            all_results['ids'],
            all_results['documents'],
            all_results['metadatas']
        )):
            if '乔' in content or '手机' in content:
                found_docs.append((doc_id, content, metadata))
                
                if len(found_docs) <= 5:  # 只显示前5个
                    print(f"\n文档{len(found_docs)}:")
                    print(f"  ID: {doc_id}")
                    print(f"  来源: {metadata.get('source_file', '未知')}")
                    print(f"  内容: {content[:100]}...")
                    
                    # 检查这个文档在BM25索引中的状态
                    if doc_id in search_system.bm25_index:
                        word_freq = search_system.bm25_index[doc_id]
                        relevant_words = {k: v for k, v in word_freq.items() if '乔' in k or '手机' in k or k in ['乔', '老师', '手机']}
                        print(f"  BM25索引中的相关词项: {relevant_words}")
                    else:
                        print(f"  ❌ 该文档不在BM25索引中")
        
        print(f"\n总共找到 {len(found_docs)} 个包含'乔'或'手机'的文档")
        
    except Exception as e:
        print(f"检查原始文档失败: {e}")
    
    print("\n" + "=" * 40)
    print("测试手动BM25计算")
    print("=" * 40)
    
    # 手动测试BM25计算
    query = "乔老师的手机"
    query_terms = search_system.preprocess_text(query)
    print(f"查询: {query}")
    print(f"查询词项: {query_terms}")
    
    # 找几个测试文档
    test_doc_ids = list(search_system.bm25_index.keys())[:5]
    
    for doc_id in test_doc_ids:
        score = search_system.calculate_bm25_score(query_terms, doc_id)
        print(f"文档 {doc_id}: BM25得分 = {score:.4f}")
        
        # 显示文档的词项频率
        word_freq = search_system.bm25_index[doc_id]
        relevant_terms = {term: freq for term, freq in word_freq.items() if term in query_terms}
        if relevant_terms:
            print(f"  匹配的词项: {relevant_terms}")
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == "__main__":
    debug_tokenization()