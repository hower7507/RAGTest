#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理主数据库脚本
1. 删除主数据库中的chat_conversations集合
2. 导出qa_system_chunks集合到txt文件
"""

import chromadb
import json
from datetime import datetime
import os

def main():
    # 主数据库路径
    main_db_path = r"e:\PyProjects\QASystem\chroma_db"
    
    print(f"连接到主数据库: {main_db_path}")
    
    try:
        # 连接到主数据库
        client = chromadb.PersistentClient(path=main_db_path)
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"\n当前集合数量: {len(collections)}")
        
        for collection in collections:
            print(f"- {collection.name}: {collection.count()} 文档")
        
        # 1. 删除chat_conversations集合
        chat_conversations_exists = False
        for collection in collections:
            if collection.name == "chat_conversations":
                chat_conversations_exists = True
                break
        
        if chat_conversations_exists:
            print("\n=== 删除chat_conversations集合 ===")
            confirm = input("确认删除主数据库中的chat_conversations集合? (y/N): ")
            if confirm.lower() == 'y':
                client.delete_collection("chat_conversations")
                print("✓ chat_conversations集合已删除")
            else:
                print("取消删除操作")
        else:
            print("\n主数据库中未找到chat_conversations集合")
        
        # 2. 导出qa_system_chunks集合
        qa_chunks_exists = False
        for collection in collections:
            if collection.name == "qa_system_chunks":
                qa_chunks_exists = True
                break
        
        if qa_chunks_exists:
            print("\n=== 导出qa_system_chunks集合 ===")
            collection = client.get_collection("qa_system_chunks")
            
            # 获取所有文档
            results = collection.get(
                include=["documents", "metadatas", "embeddings"]
            )
            
            # 生成导出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"main_qa_system_chunks_export_{timestamp}.txt"
            
            print(f"导出到文件: {export_file}")
            print(f"文档数量: {len(results['documents'])}")
            
            # 写入文件
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write(f"qa_system_chunks集合导出\n")
                f.write(f"导出时间: {datetime.now().isoformat()}\n")
                f.write(f"数据库路径: {main_db_path}\n")
                f.write(f"文档总数: {len(results['documents'])}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    f.write(f"文档 {i+1}:\n")
                    f.write(f"内容: {doc}\n")
                    f.write(f"元数据: {json.dumps(metadata, ensure_ascii=False, indent=2)}\n")
                    f.write("-" * 60 + "\n\n")
            
            print(f"✓ qa_system_chunks集合已导出到 {export_file}")
        else:
            print("\n主数据库中未找到qa_system_chunks集合")
        
        # 显示最终状态
        print("\n=== 操作完成后的集合状态 ===")
        final_collections = client.list_collections()
        print(f"集合数量: {len(final_collections)}")
        
        for collection in final_collections:
            print(f"- {collection.name}: {collection.count()} 文档")
            
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()