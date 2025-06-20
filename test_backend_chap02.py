#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端是否能正确访问chap02数据
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer

def test_backend_chap02_access():
    """测试后端搜索系统是否能访问chap02数据"""
    
    print("=== 测试后端chap02数据访问 ===")
    
    try:
        # 1. 测试搜索接口初始化
        print("\n1. 初始化搜索接口...")
        search_interface = SearchInterface(config_name="balanced")
        
        # 2. 初始化搜索系统
        print("\n2. 初始化搜索系统...")
        success = search_interface.initialize()
        
        if not success:
            print("❌ 搜索系统初始化失败")
            return False
        
        print("✅ 搜索系统初始化成功")
        
        # 3. 检查数据统计
        print("\n3. 检查数据统计...")
        vectorizer = search_interface.vectorizer
        info = vectorizer.get_collection_info()
        
        print(f"集合名称: {info.get('collection_name', 'unknown')}")
        print(f"总记录数: {info.get('total_records', 0)}")
        print(f"示例ID: {info.get('sample_ids', [])[:5]}")
        
        # 4. 测试chap02相关查询
        print("\n4. 测试chap02相关查询...")
        
        test_queries = [
            "中国AI发展",
            "创新和商业化", 
            "人才标准",
            "技术探索",
            "快速商业化"
        ]
        
        chap02_found = False
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            
            try:
                results = search_interface.search(
                    query=query,
                    top_k=3,
                    return_prompt=False
                )
                
                if results and 'search_results' in results:
                    search_results = results['search_results']
                    print(f"找到 {len(search_results)} 个结果")
                    
                    for i, result in enumerate(search_results[:2]):
                        metadata = result.get('metadata', {})
                        
                        # 检查是否是chap02数据
                        is_chap02 = (
                            ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                            ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                        )
                        
                        if is_chap02:
                            chap02_found = True
                            print(f"  ✅ 结果{i+1}: chap02数据")
                            if 'question' in metadata:
                                print(f"     问题: {metadata['question'][:50]}...")
                            if 'keywords' in metadata:
                                print(f"     关键词: {metadata['keywords']}")
                        else:
                            print(f"  ⚪ 结果{i+1}: 其他数据 (来源: {metadata.get('source_file', 'unknown')})")
                        
                        print(f"     相似度: {result.get('similarity', 'N/A')}")
                else:
                    print("  未找到结果")
                    
            except Exception as e:
                print(f"  查询出错: {e}")
        
        # 5. 总结
        print("\n=== 测试总结 ===")
        if chap02_found:
            print("✅ 成功：后端能够访问chap02数据")
            print("✅ chap02问答对数据已正确集成到搜索系统中")
        else:
            print("❌ 问题：后端无法找到chap02数据")
            print("❌ 可能需要检查数据迁移或搜索配置")
        
        return chap02_found
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_vectorizer():
    """直接测试向量化器访问chap02数据"""
    
    print("\n=== 直接测试向量化器 ===")
    
    try:
        # 创建向量化器
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        # 初始化
        vectorizer.load_model()
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 搜索chap02数据
        results = vectorizer.search_similar_chunks(
            query_text="创新商业化",
            n_results=5
        )
        
        if results and 'metadatas' in results:
            chap02_count = 0
            for metadata in results['metadatas'][0]:
                if metadata and (
                    ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                    ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                ):
                    chap02_count += 1
            
            print(f"在前5个搜索结果中找到 {chap02_count} 条chap02数据")
            return chap02_count > 0
        else:
            print("搜索未返回结果")
            return False
            
    except Exception as e:
        print(f"直接测试向量化器时出错: {e}")
        return False

if __name__ == "__main__":
    # 测试后端访问
    backend_success = test_backend_chap02_access()
    
    # 测试直接访问
    direct_success = test_direct_vectorizer()
    
    print("\n=== 最终结论 ===")
    if backend_success and direct_success:
        print("✅ chap02数据已成功集成，前端应该能够获取相关知识")
    elif direct_success:
        print("⚠️  数据存在但后端搜索接口可能有问题")
    else:
        print("❌ chap02数据访问存在问题")