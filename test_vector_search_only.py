# -*- coding: utf-8 -*-
"""
测试纯向量搜索功能
排除BM25影响，专门测试向量搜索
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from vectorize_chunks import ChunkVectorizer
from search_config import load_config

def test_vector_search_only():
    """
    测试纯向量搜索
    """
    print("=" * 60)
    print("测试纯向量搜索功能")
    print("=" * 60)
    
    # 加载配置
    config = load_config("balanced")
    
    # 初始化向量化器
    vectorizer = ChunkVectorizer(
        model_name=config.model_name,
        collection_name=config.collection_name
    )
    
    # 初始化ChromaDB
    try:
        vectorizer.init_chromadb(config.chroma_db_path)
        print(f"✅ ChromaDB连接成功: {config.chroma_db_path}")
    except Exception as e:
        print(f"❌ ChromaDB连接失败: {e}")
        return
    
    # 加载模型
    try:
        vectorizer.load_model()
        print(f"✅ 模型加载成功: {config.model_name}")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 获取数据库信息
    info = vectorizer.get_collection_info()
    print(f"\n数据库信息:")
    print(f"  集合名称: {info.get('collection_name')}")
    print(f"  总记录数: {info.get('total_records')}")
    
    print("\n" + "=" * 40)
    print("测试查询1: 乔老师的手机")
    print("=" * 40)
    
    query1 = "乔老师的手机"
    try:
        results1 = vectorizer.search_similar_chunks(query1, n_results=10)
        
        print(f"查询: {query1}")
        print(f"返回结果数: {len(results1.get('documents', [[]])[0])}")
        
        if results1.get('documents') and results1['documents'][0]:
            print("\n向量搜索结果:")
            for i, (doc, metadata, doc_id, distance) in enumerate(zip(
                results1['documents'][0],
                results1['metadatas'][0],
                results1['ids'][0],
                results1.get('distances', [[]])[0] if results1.get('distances') else [0]*len(results1['documents'][0])
            )):
                print(f"\n结果{i+1}:")
                print(f"  文档ID: {doc_id}")
                print(f"  向量距离: {distance:.4f}")
                print(f"  来源文件: {metadata.get('source_file', '未知')}")
                print(f"  内容: {doc[:100]}...")
                
                # 检查是否包含关键词
                if '乔' in doc or '手机' in doc:
                    print(f"  ✅ 包含关键词")
                else:
                    print(f"  ❌ 不包含关键词")
        else:
            print("❌ 向量搜索没有返回结果")
            
    except Exception as e:
        print(f"查询1失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("测试查询2: 技术真的可以拉开差距吗")
    print("=" * 40)
    
    query2 = "技术真的可以拉开差距吗"
    try:
        results2 = vectorizer.search_similar_chunks(query2, n_results=10)
        
        print(f"查询: {query2}")
        print(f"返回结果数: {len(results2.get('documents', [[]])[0])}")
        
        if results2.get('documents') and results2['documents'][0]:
            print("\n向量搜索结果:")
            for i, (doc, metadata, doc_id, distance) in enumerate(zip(
                results2['documents'][0],
                results2['metadatas'][0],
                results2['ids'][0],
                results2.get('distances', [[]])[0] if results2.get('distances') else [0]*len(results2['documents'][0])
            )):
                print(f"\n结果{i+1}:")
                print(f"  文档ID: {doc_id}")
                print(f"  向量距离: {distance:.4f}")
                print(f"  来源文件: {metadata.get('source_file', '未知')}")
                print(f"  内容: {doc[:100]}...")
                
                # 检查是否包含关键词
                if '技术' in doc or '差距' in doc:
                    print(f"  ✅ 包含关键词")
                else:
                    print(f"  ❌ 不包含关键词")
        else:
            print("❌ 向量搜索没有返回结果")
            
    except Exception as e:
        print(f"查询2失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("测试简单查询: 机器学习")
    print("=" * 40)
    
    query3 = "机器学习"
    try:
        results3 = vectorizer.search_similar_chunks(query3, n_results=5)
        
        print(f"查询: {query3}")
        print(f"返回结果数: {len(results3.get('documents', [[]])[0])}")
        
        if results3.get('documents') and results3['documents'][0]:
            print("\n向量搜索结果:")
            for i, (doc, metadata, doc_id, distance) in enumerate(zip(
                results3['documents'][0],
                results3['metadatas'][0],
                results3['ids'][0],
                results3.get('distances', [[]])[0] if results3.get('distances') else [0]*len(results3['documents'][0])
            )):
                print(f"\n结果{i+1}:")
                print(f"  文档ID: {doc_id}")
                print(f"  向量距离: {distance:.4f}")
                print(f"  来源文件: {metadata.get('source_file', '未知')}")
                print(f"  内容: {doc[:100]}...")
        else:
            print("❌ 向量搜索没有返回结果")
            
    except Exception as e:
        print(f"查询3失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("检查数据库中的具体内容")
    print("=" * 40)
    
    try:
        # 获取所有数据
        all_results = vectorizer.collection.get()
        
        print(f"数据库总记录数: {len(all_results.get('ids', []))}")
        
        # 查找包含关键词的文档
        keywords_to_check = ['乔', '手机', '技术', '差距']
        
        for keyword in keywords_to_check:
            print(f"\n查找包含'{keyword}'的文档:")
            found_count = 0
            
            for i, (doc_id, content, metadata) in enumerate(zip(
                all_results['ids'],
                all_results['documents'],
                all_results['metadatas']
            )):
                if keyword in content:
                    found_count += 1
                    if found_count <= 3:  # 只显示前3个
                        print(f"  文档{found_count}: {doc_id}")
                        print(f"    来源: {metadata.get('source_file', '未知')}")
                        print(f"    内容片段: ...{content[max(0, content.find(keyword)-20):content.find(keyword)+50]}...")
            
            print(f"  总共找到 {found_count} 个包含'{keyword}'的文档")
    
    except Exception as e:
        print(f"检查数据库内容失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_vector_search_only()