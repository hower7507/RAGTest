#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除会话数据库中的非必要集合
保留chat_conversations集合，删除qa_chunks、qa_collection、qa_demo_collection
"""

import chromadb
from chromadb.config import Settings
import os

def delete_unnecessary_collections():
    """
    删除会话数据库中不需要的集合
    """
    # 会话数据库路径
    session_db_path = "./chroma_db"
    
    if not os.path.exists(session_db_path):
        print(f"❌ 会话数据库路径不存在: {session_db_path}")
        return False
    
    try:
        # 连接到会话数据库
        client = chromadb.PersistentClient(
            path=session_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"📋 当前集合数量: {len(collections)}")
        
        for collection in collections:
            print(f"  - {collection.name}")
        
        # 要删除的集合列表
        collections_to_delete = ["qa_chunks", "qa_collection", "qa_demo_collection"]
        
        # 删除指定集合
        deleted_count = 0
        for collection_name in collections_to_delete:
            try:
                # 检查集合是否存在
                existing_collections = [c.name for c in client.list_collections()]
                if collection_name in existing_collections:
                    client.delete_collection(collection_name)
                    print(f"✅ 已删除集合: {collection_name}")
                    deleted_count += 1
                else:
                    print(f"⚠️  集合不存在，跳过: {collection_name}")
            except Exception as e:
                print(f"❌ 删除集合 {collection_name} 失败: {e}")
        
        # 显示删除后的集合状态
        print(f"\n🔄 删除操作完成，共删除 {deleted_count} 个集合")
        
        remaining_collections = client.list_collections()
        print(f"📋 剩余集合数量: {len(remaining_collections)}")
        for collection in remaining_collections:
            print(f"  - {collection.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

if __name__ == "__main__":
    print("🗑️  开始删除会话数据库中的非必要集合...")
    print("📌 将保留: chat_conversations")
    print("🗑️  将删除: qa_chunks, qa_collection, qa_demo_collection")
    print()
    
    # 确认操作
    confirm = input("确认执行删除操作吗？(y/N): ")
    if confirm.lower() in ['y', 'yes', '是']:
        success = delete_unnecessary_collections()
        if success:
            print("\n✅ 删除操作成功完成！")
        else:
            print("\n❌ 删除操作失败！")
    else:
        print("❌ 操作已取消")