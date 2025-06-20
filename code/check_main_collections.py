#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查主数据库中的集合状态
查询主数据库（e:\PyProjects\QASystem\chroma_db）中的所有集合
"""

import chromadb
from chromadb.config import Settings
import os
from datetime import datetime

def check_main_collections():
    """
    检查主数据库中的集合状态
    """
    # 主数据库路径
    main_db_path = "e:\\PyProjects\\QASystem\\chroma_db"
    
    print(f"🔍 检查主数据库: {main_db_path}")
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if not os.path.exists(main_db_path):
        print(f"❌ 主数据库路径不存在: {main_db_path}")
        return False
    
    try:
        # 连接到主数据库
        client = chromadb.PersistentClient(
            path=main_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"📋 主数据库集合总数: {len(collections)}")
        print()
        
        if len(collections) == 0:
            print("⚠️  主数据库中没有任何集合")
            return True
        
        # 检查每个集合的详细信息
        total_documents = 0
        
        for i, collection in enumerate(collections, 1):
            collection_name = collection.name
            
            # 获取集合中的文档数量
            try:
                doc_count = collection.count()
                total_documents += doc_count
            except Exception as e:
                doc_count = f"获取失败: {e}"
            
            print(f"📁 集合 {i}: {collection_name}")
            print(f"   📊 文档数量: {doc_count}")
            
            # 获取集合元数据
            try:
                metadata = collection.metadata
                if metadata:
                    print(f"   📝 元数据: {metadata}")
                else:
                    print(f"   📝 元数据: 无")
            except:
                print(f"   📝 元数据: 获取失败")
            
            # 如果文档数量不多，可以查看一些样本
            if isinstance(doc_count, int) and 0 < doc_count <= 5:
                try:
                    # 获取前几个文档的ID和元数据
                    results = collection.get(limit=min(3, doc_count))
                    if results['ids']:
                        print(f"   📄 样本文档ID: {results['ids'][:3]}")
                        if results['metadatas'] and results['metadatas'][0]:
                            sample_metadata = results['metadatas'][0]
                            # 只显示关键字段
                            key_fields = ['source_file', 'chunk_type', 'created_at', 'word_count']
                            sample_info = {k: v for k, v in sample_metadata.items() if k in key_fields}
                            if sample_info:
                                print(f"   📋 样本元数据: {sample_info}")
                except Exception as e:
                    print(f"   ⚠️  获取样本失败: {e}")
            
            print()
        
        # 生成总结报告
        print("=" * 60)
        print("📊 主数据库总结:")
        print(f"   📁 集合总数: {len(collections)}")
        print(f"   📄 文档总数: {total_documents if isinstance(total_documents, int) else '部分统计失败'}")
        print()
        
        # 列出所有集合名称
        print("📋 所有集合列表:")
        for i, collection in enumerate(collections, 1):
            print(f"   {i}. {collection.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始检查主数据库集合状态...")
    print()
    
    success = check_main_collections()
    
    print()
    if success:
        print("✅ 检查完成")
    else:
        print("❌ 检查失败")