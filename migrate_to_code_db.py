#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将数据从root目录的ChromaDB迁移到code目录的ChromaDB
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from vectorize_chunks import ChunkVectorizer
import json

def migrate_data():
    """迁移数据从root目录到code目录"""
    print("=== 数据迁移：从root目录到code目录 ===")
    
    root_chroma_path = "e:\\PyProjects\\QASystem\\chroma_db"
    code_chroma_path = "e:\\PyProjects\\QASystem\\code\\chroma_db"
    
    try:
        # 1. 初始化源数据库（root目录）
        print("\n1. 连接源数据库（root目录）")
        source_vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        source_vectorizer.init_chromadb(persist_directory=root_chroma_path)
        
        source_info = source_vectorizer.get_collection_info()
        print(f"源数据库信息: {source_info}")
        
        if source_info['total_records'] == 0:
            print("❌ 源数据库中没有数据，无需迁移")
            return
        
        # 2. 获取所有数据
        print("\n2. 获取源数据")
        all_data = source_vectorizer.collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        print(f"获取到 {len(all_data['ids'])} 条记录")
        
        # 3. 初始化目标数据库（code目录）
        print("\n3. 连接目标数据库（code目录）")
        target_vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        target_vectorizer.init_chromadb(persist_directory=code_chroma_path)
        
        target_info = target_vectorizer.get_collection_info()
        print(f"目标数据库信息: {target_info}")
        
        # 4. 清空目标数据库（如果有数据）
        if target_info['total_records'] > 0:
            print("\n4. 清空目标数据库")
            # 获取所有ID并删除
            existing_data = target_vectorizer.collection.get()
            if existing_data['ids']:
                target_vectorizer.collection.delete(ids=existing_data['ids'])
                print(f"删除了 {len(existing_data['ids'])} 条现有记录")
        
        # 5. 迁移数据
        print("\n5. 迁移数据")
        target_vectorizer.collection.add(
            ids=all_data['ids'],
            documents=all_data['documents'],
            metadatas=all_data['metadatas'],
            embeddings=all_data['embeddings']
        )
        
        # 6. 验证迁移结果
        print("\n6. 验证迁移结果")
        final_info = target_vectorizer.get_collection_info()
        print(f"迁移后目标数据库信息: {final_info}")
        
        # 检查chap02数据
        chap02_count = 0
        for metadata in all_data['metadatas']:
            if metadata and 'source_file' in metadata and 'chap02' in metadata['source_file']:
                chap02_count += 1
        
        print(f"✓ 迁移完成！总共迁移 {len(all_data['ids'])} 条记录")
        print(f"✓ 其中包含 {chap02_count} 条chap02相关记录")
        
        # 7. 测试搜索功能
        print("\n7. 测试搜索功能")
        test_search_results = target_vectorizer.search_similar_chunks(
            query_text="创新",
            n_results=3
        )
        
        if test_search_results and 'metadatas' in test_search_results:
            metadatas = test_search_results['metadatas'][0]
            chap02_search_count = 0
            for metadata in metadatas:
                if metadata and 'source_file' in metadata and 'chap02' in metadata['source_file']:
                    chap02_search_count += 1
            
            print(f"✓ 搜索测试成功，找到 {len(metadatas)} 个结果")
            print(f"✓ 其中包含 {chap02_search_count} 个chap02相关结果")
        else:
            print("❌ 搜索测试失败")
        
    except Exception as e:
        print(f"迁移过程中出错: {e}")
        import traceback
        traceback.print_exc()

def test_backend_after_migration():
    """测试迁移后的后端搜索功能"""
    print("\n=== 测试迁移后的后端搜索功能 ===")
    
    try:
        from search_interface import SearchInterface
        
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        print(f"搜索接口初始化结果: {success}")
        
        if success:
            # 测试搜索
            results = search_interface.search(
                query="创新",
                top_k=3,
                return_prompt=False
            )
            
            if 'results' in results and results['results']:
                print(f"✓ 后端搜索成功，找到 {len(results['results'])} 个结果")
                
                chap02_count = 0
                for result in results['results']:
                    if 'metadata' in result and 'source_file' in result['metadata']:
                        if 'chap02' in result['metadata']['source_file']:
                            chap02_count += 1
                
                print(f"✓ 其中包含 {chap02_count} 个chap02相关结果")
                print("✓ 迁移成功！后端现在可以正确访问所有数据")
            else:
                print("❌ 后端搜索未返回结果")
        else:
            print("❌ 后端搜索接口初始化失败")
            
    except Exception as e:
        print(f"测试后端时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 执行数据迁移
    migrate_data()
    
    # 测试迁移后的后端功能
    test_backend_after_migration()