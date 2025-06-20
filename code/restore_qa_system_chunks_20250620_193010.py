#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_system_chunks集合恢复脚本
从备份文件恢复qa_system_chunks集合到主数据库
"""

import chromadb
import pickle
import json
from datetime import datetime

def restore_qa_system_chunks():
    """从备份恢复qa_system_chunks集合"""
    # 主数据库路径
    main_db_path = r"e:\PyProjects\QASystem\chroma_db"
    backup_file = "qa_system_chunks_full_backup_20250620_193010.pkl"
    
    print(f"从备份文件恢复: {backup_file}")
    print(f"目标数据库: {main_db_path}")
    
    try:
        # 加载备份数据
        with open(backup_file, 'rb') as f:
            backup_data = pickle.load(f)
        
        print(f"\n备份信息:")
        print(f"- 备份时间: {backup_data['backup_time']}")
        print(f"- 文档数量: {backup_data['document_count']}")
        
        # 连接到主数据库
        client = chromadb.PersistentClient(path=main_db_path)
        
        # 检查是否已存在qa_system_chunks集合
        collections = client.list_collections()
        collection_exists = any(col.name == "qa_system_chunks" for col in collections)
        
        if collection_exists:
            confirm = input("qa_system_chunks集合已存在，是否删除并重新创建? (y/N): ")
            if confirm.lower() == 'y':
                client.delete_collection("qa_system_chunks")
                print("✓ 已删除现有集合")
            else:
                print("取消恢复操作")
                return False
        
        # 创建新集合
        collection = client.create_collection("qa_system_chunks")
        
        # 恢复数据
        print("\n正在恢复数据...")
        
        documents = backup_data['documents']
        metadatas = backup_data['metadatas']
        embeddings = backup_data['embeddings']
        
        # 生成ID
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # 添加数据到集合
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        
        print(f"✓ 已恢复 {len(documents)} 个文档")
        
        # 验证恢复结果
        final_count = collection.count()
        print(f"✓ 集合文档数量: {final_count}")
        
        if final_count == backup_data['document_count']:
            print("✅ 恢复成功！")
        else:
            print(f"⚠️ 警告: 恢复的文档数量不匹配 (期望: {backup_data['document_count']}, 实际: {final_count})")
        
        return True
        
    except Exception as e:
        print(f"恢复失败: {e}")
        return False

if __name__ == "__main__":
    restore_qa_system_chunks()
