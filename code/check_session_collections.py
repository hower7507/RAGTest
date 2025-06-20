#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查会话数据库中的集合状态
验证删除操作是否成功执行
"""

import chromadb
from chromadb.config import Settings
import os
from datetime import datetime

def check_session_collections():
    """
    检查会话数据库中的集合状态
    """
    # 会话数据库路径
    session_db_path = "./chroma_db"
    
    print(f"🔍 检查会话数据库: {os.path.abspath(session_db_path)}")
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
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
        print(f"📋 当前集合总数: {len(collections)}")
        print()
        
        if len(collections) == 0:
            print("⚠️  数据库中没有任何集合")
            return True
        
        # 检查每个集合的详细信息
        expected_collections = ["chat_conversations"]
        unexpected_collections = ["qa_chunks", "qa_collection", "qa_demo_collection"]
        
        found_expected = []
        found_unexpected = []
        other_collections = []
        
        for collection in collections:
            collection_name = collection.name
            
            # 获取集合中的文档数量
            try:
                doc_count = collection.count()
            except:
                doc_count = "未知"
            
            print(f"📁 集合: {collection_name}")
            print(f"   📊 文档数量: {doc_count}")
            
            if collection_name in expected_collections:
                found_expected.append(collection_name)
                print(f"   ✅ 状态: 正常保留")
            elif collection_name in unexpected_collections:
                found_unexpected.append(collection_name)
                print(f"   ❌ 状态: 应该被删除但仍存在")
            else:
                other_collections.append(collection_name)
                print(f"   ⚠️  状态: 未知集合")
            
            print()
        
        # 生成检查报告
        print("=" * 60)
        print("📊 检查报告:")
        print()
        
        print(f"✅ 应保留的集合 ({len(found_expected)}/{len(expected_collections)}):")
        for name in expected_collections:
            if name in found_expected:
                print(f"   ✓ {name} - 已找到")
            else:
                print(f"   ✗ {name} - 缺失")
        print()
        
        print(f"🗑️  应删除的集合检查:")
        if found_unexpected:
            print(f"   ❌ 发现 {len(found_unexpected)} 个未删除的集合:")
            for name in found_unexpected:
                print(f"      - {name}")
        else:
            print(f"   ✅ 所有目标集合已成功删除")
        print()
        
        if other_collections:
            print(f"⚠️  其他集合 ({len(other_collections)}):")
            for name in other_collections:
                print(f"   - {name}")
            print()
        
        # 总结
        if not found_unexpected and "chat_conversations" in found_expected:
            print("🎉 删除操作验证成功！")
            print("   - 会话集合正常保留")
            print("   - 无用集合已被删除")
            return True
        else:
            print("⚠️  删除操作可能未完全成功")
            if found_unexpected:
                print(f"   - 仍有 {len(found_unexpected)} 个集合需要删除")
            if "chat_conversations" not in found_expected:
                print("   - 会话集合缺失")
            return False
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始检查会话数据库集合状态...")
    print()
    
    success = check_session_collections()
    
    print()
    if success:
        print("✅ 检查完成")
    else:
        print("❌ 检查发现问题")