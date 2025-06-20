#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_system_chunks集合备份脚本
备份主数据库中的qa_system_chunks集合，包括文档、元数据和向量嵌入
"""

import chromadb
import json
import pickle
from datetime import datetime
import os

def backup_qa_system_chunks():
    """备份qa_system_chunks集合"""
    # 主数据库路径
    main_db_path = r"e:\PyProjects\QASystem\chroma_db"
    
    print(f"连接到主数据库: {main_db_path}")
    
    try:
        # 连接到主数据库
        client = chromadb.PersistentClient(path=main_db_path)
        
        # 检查qa_system_chunks集合是否存在
        collections = client.list_collections()
        qa_chunks_exists = False
        
        for collection in collections:
            if collection.name == "qa_system_chunks":
                qa_chunks_exists = True
                break
        
        if not qa_chunks_exists:
            print("错误: 主数据库中未找到qa_system_chunks集合")
            return False
        
        # 获取集合
        collection = client.get_collection("qa_system_chunks")
        doc_count = collection.count()
        
        print(f"\n=== 备份qa_system_chunks集合 ===")
        print(f"文档数量: {doc_count}")
        
        # 获取所有数据（包括向量嵌入）
        print("正在获取所有数据...")
        results = collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存为JSON格式（不包含嵌入向量，便于查看）
        json_backup_file = f"qa_system_chunks_backup_{timestamp}.json"
        json_data = {
            "backup_time": datetime.now().isoformat(),
            "source_db": main_db_path,
            "collection_name": "qa_system_chunks",
            "document_count": len(results['documents']),
            "documents": results['documents'],
            "metadatas": results['metadatas']
        }
        
        with open(json_backup_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON备份已保存: {json_backup_file}")
        
        # 2. 保存为Pickle格式（包含完整数据，包括嵌入向量）
        pickle_backup_file = f"qa_system_chunks_full_backup_{timestamp}.pkl"
        full_data = {
            "backup_time": datetime.now().isoformat(),
            "source_db": main_db_path,
            "collection_name": "qa_system_chunks",
            "document_count": len(results['documents']),
            "documents": results['documents'],
            "metadatas": results['metadatas'],
            "embeddings": results['embeddings']
        }
        
        with open(pickle_backup_file, 'wb') as f:
            pickle.dump(full_data, f)
        
        print(f"✓ 完整备份已保存: {pickle_backup_file}")
        
        # 3. 创建恢复脚本
        restore_script = f"restore_qa_system_chunks_{timestamp}.py"
        restore_code = f'''#!/usr/bin/env python3
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
    main_db_path = r"e:\\PyProjects\\QASystem\\chroma_db"
    backup_file = "{pickle_backup_file}"
    
    print(f"从备份文件恢复: {{backup_file}}")
    print(f"目标数据库: {{main_db_path}}")
    
    try:
        # 加载备份数据
        with open(backup_file, 'rb') as f:
            backup_data = pickle.load(f)
        
        print(f"\\n备份信息:")
        print(f"- 备份时间: {{backup_data['backup_time']}}")
        print(f"- 文档数量: {{backup_data['document_count']}}")
        
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
        print("\\n正在恢复数据...")
        
        documents = backup_data['documents']
        metadatas = backup_data['metadatas']
        embeddings = backup_data['embeddings']
        
        # 生成ID
        ids = [f"doc_{{i}}" for i in range(len(documents))]
        
        # 添加数据到集合
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        
        print(f"✓ 已恢复 {{len(documents)}} 个文档")
        
        # 验证恢复结果
        final_count = collection.count()
        print(f"✓ 集合文档数量: {{final_count}}")
        
        if final_count == backup_data['document_count']:
            print("✅ 恢复成功！")
        else:
            print(f"⚠️ 警告: 恢复的文档数量不匹配 (期望: {{backup_data['document_count']}}, 实际: {{final_count}})")
        
        return True
        
    except Exception as e:
        print(f"恢复失败: {{e}}")
        return False

if __name__ == "__main__":
    restore_qa_system_chunks()
'''
        
        with open(restore_script, 'w', encoding='utf-8') as f:
            f.write(restore_code)
        
        print(f"✓ 恢复脚本已创建: {restore_script}")
        
        # 显示备份摘要
        print(f"\n=== 备份完成 ===")
        print(f"备份时间: {datetime.now().isoformat()}")
        print(f"文档数量: {doc_count}")
        print(f"\n备份文件:")
        print(f"1. JSON格式 (可读): {json_backup_file}")
        print(f"2. 完整备份 (含向量): {pickle_backup_file}")
        print(f"3. 恢复脚本: {restore_script}")
        
        # 获取文件大小
        json_size = os.path.getsize(json_backup_file) / 1024 / 1024
        pickle_size = os.path.getsize(pickle_backup_file) / 1024 / 1024
        
        print(f"\n文件大小:")
        print(f"- JSON备份: {json_size:.2f} MB")
        print(f"- 完整备份: {pickle_size:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"备份失败: {e}")
        return False

if __name__ == "__main__":
    backup_qa_system_chunks()