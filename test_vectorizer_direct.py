# -*- coding: utf-8 -*-
"""
直接测试向量化器的搜索功能
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from vectorize_chunks import ChunkVectorizer

def test_vectorizer_search():
    """直接测试向量化器搜索功能"""
    
    print("=== 直接测试向量化器搜索功能 ===")
    
    try:
        # 创建向量化器
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        # 加载模型
        print("正在加载模型...")
        vectorizer.load_model()
        
        # 初始化ChromaDB
        print("正在初始化ChromaDB...")
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 获取集合信息
        info = vectorizer.get_collection_info()
        print(f"\n数据库信息:")
        print(f"  集合名称: {info.get('collection_name', 'unknown')}")
        print(f"  总记录数: {info.get('total_records', 0)}")
        print(f"  示例ID: {info.get('sample_ids', [])[:5]}")
        
        if info.get('total_records', 0) == 0:
            print("❌ 数据库中没有数据")
            return False
        
        # 测试搜索功能
        test_queries = [
            "自然语言处理",
            "机器学习",
            "中国AI发展",
            "人工智能"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            
            try:
                # 使用向量化器搜索
                results = vectorizer.search_similar_chunks(
                    query_text=query,
                    n_results=3
                )
                
                if results and 'documents' in results:
                    documents = results['documents'][0]
                    metadatas = results.get('metadatas', [[]])[0]
                    ids = results.get('ids', [[]])[0]
                    
                    print(f"  找到 {len(documents)} 个结果:")
                    
                    for i, (doc, metadata, doc_id) in enumerate(zip(documents, metadatas, ids)):
                        print(f"    结果{i+1}:")
                        print(f"      ID: {doc_id}")
                        print(f"      内容: {doc[:100]}...")
                        
                        if metadata:
                            # 检查数据来源
                            source = metadata.get('source', metadata.get('source_file', 'unknown'))
                            chunk_type = metadata.get('chunk_type', 'unknown')
                            print(f"      来源: {source}")
                            print(f"      类型: {chunk_type}")
                            
                            if 'question' in metadata:
                                print(f"      问题: {metadata['question'][:50]}...")
                            if 'word_count' in metadata:
                                print(f"      字数: {metadata['word_count']}")
                        else:
                            print(f"      元数据: 无")
                        print()
                else:
                    print("  未找到结果")
                    
            except Exception as e:
                print(f"  搜索出错: {e}")
        
        return True
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_collection_data():
    """测试集合中的数据分布"""
    
    print("\n=== 测试集合数据分布 ===")
    
    try:
        # 创建向量化器
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        # 初始化ChromaDB（不需要加载模型）
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 获取所有数据
        all_data = vectorizer.collection.get(
            limit=1000,  # 限制获取数量
            include=["metadatas", "documents"]
        )
        
        total_count = len(all_data.get('metadatas', []))
        print(f"总数据量: {total_count}")
        
        if total_count == 0:
            print("❌ 集合中没有数据")
            return
        
        # 统计数据分布
        chap01_count = 0
        chap02_count = 0
        other_count = 0
        qa_pair_count = 0
        
        for i, metadata in enumerate(all_data.get('metadatas', [])):
            if metadata:
                source = metadata.get('source', metadata.get('source_file', ''))
                chunk_type = metadata.get('chunk_type', '')
                
                if 'chap01' in str(source).lower():
                    chap01_count += 1
                elif 'chap02' in str(source).lower() or chunk_type == 'qa_pair':
                    chap02_count += 1
                    if chunk_type == 'qa_pair':
                        qa_pair_count += 1
                else:
                    other_count += 1
                    
                # 显示前几个数据的详细信息
                if i < 5:
                    print(f"\n示例数据 {i+1}:")
                    print(f"  来源: {source}")
                    print(f"  类型: {chunk_type}")
                    if 'question' in metadata:
                        print(f"  问题: {metadata['question'][:50]}...")
                    if 'word_count' in metadata:
                        print(f"  字数: {metadata['word_count']}")
                    
                    # 显示内容片段
                    documents = all_data.get('documents', [])
                    if i < len(documents):
                        content = documents[i]
                        print(f"  内容: {content[:80]}...")
        
        print(f"\n📊 数据分布统计:")
        print(f"  chap01数据: {chap01_count} ({(chap01_count/total_count)*100:.1f}%)")
        print(f"  chap02数据: {chap02_count} ({(chap02_count/total_count)*100:.1f}%)")
        print(f"    其中QA对: {qa_pair_count}")
        print(f"  其他数据: {other_count} ({(other_count/total_count)*100:.1f}%)")
        
    except Exception as e:
        print(f"测试集合数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 测试集合数据分布
    test_collection_data()
    
    # 测试搜索功能
    test_vectorizer_search()