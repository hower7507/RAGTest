#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理会话数据库中的qa_system_chunks集合
该集合应该只存在于主数据库中，不应该在会话数据库中
"""

import chromadb
import os
from datetime import datetime

def clean_session_qa_chunks():
    """
    从会话数据库中删除qa_system_chunks集合
    """
    # 会话数据库路径（code目录下的chroma_db）
    session_db_path = os.path.join(os.path.dirname(__file__), 'chroma_db')
    
    print(f"会话数据库路径: {session_db_path}")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 连接到会话数据库
        client = chromadb.PersistentClient(path=session_db_path)
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"会话数据库当前集合数量: {len(collections)}")
        
        # 查找qa_system_chunks集合
        qa_chunks_found = False
        for collection in collections:
            print(f"📁 集合: {collection.name}")
            if collection.name == "qa_system_chunks":
                qa_chunks_found = True
                doc_count = collection.count()
                print(f"   📊 文档数量: {doc_count}")
                print(f"   ⚠️  这个集合不应该在会话数据库中！")
        
        if qa_chunks_found:
            print("\n🗑️  准备删除qa_system_chunks集合...")
            
            # 确认删除
            confirm = input("确认删除会话数据库中的qa_system_chunks集合？(y/N): ")
            if confirm.lower() == 'y':
                try:
                    client.delete_collection("qa_system_chunks")
                    print("✅ 成功删除qa_system_chunks集合")
                    
                    # 再次检查
                    remaining_collections = client.list_collections()
                    print(f"\n📊 删除后剩余集合数量: {len(remaining_collections)}")
                    for collection in remaining_collections:
                        print(f"   📁 {collection.name}")
                        
                except Exception as e:
                    print(f"❌ 删除失败: {e}")
            else:
                print("❌ 取消删除操作")
        else:
            print("✅ 会话数据库中没有找到qa_system_chunks集合")
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
    
    print("\n✅ 检查完成")

if __name__ == "__main__":
    clean_session_qa_chunks()