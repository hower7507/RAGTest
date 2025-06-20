#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查ChromaDB数据库状态
"""

import chromadb
import os

def check_chromadb():
    print("=== 检查ChromaDB状态 ===")
    
    # 检查当前目录下的chroma_db
    db_path = "./chroma_db"
    print(f"数据库路径: {os.path.abspath(db_path)}")
    print(f"路径是否存在: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print(f"数据库目录内容: {os.listdir(db_path)}")
    
    try:
        # 连接ChromaDB
        client = chromadb.PersistentClient(path=db_path)
        
        # 列出所有集合
        collections = client.list_collections()
        print(f"\n可用集合数量: {len(collections)}")
        
        for i, collection in enumerate(collections):
            print(f"\n集合 {i+1}: {collection.name}")
            try:
                count = collection.count()
                print(f"  文档数量: {count}")
                
                if count > 0:
                    # 获取前几个文档的示例
                    sample = collection.get(limit=3, include=["documents", "metadatas"])
                    print(f"  示例文档ID: {sample['ids'][:3]}")
                    if sample['documents']:
                        print(f"  示例内容: {sample['documents'][0][:100]}...")
                    if sample['metadatas']:
                        print(f"  示例元数据: {sample['metadatas'][0]}")
            except Exception as e:
                print(f"  ❌ 获取集合信息失败: {e}")
        
        # 尝试常见的集合名称
        common_names = ['qa_chunks', 'qa_system_chunks', 'chunks', 'documents']
        print(f"\n=== 尝试常见集合名称 ===")
        for name in common_names:
            try:
                collection = client.get_collection(name)
                count = collection.count()
                print(f"集合 '{name}': {count} 个文档")
            except Exception as e:
                print(f"集合 '{name}': 不存在")
                
    except Exception as e:
        print(f"❌ ChromaDB连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_chromadb()