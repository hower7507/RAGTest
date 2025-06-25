#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vectorize_chunks import ChunkVectorizer

def debug_none_ids():
    """调试None ID问题"""
    print("=== 调试None ID问题 ===")
    
    try:
        # 初始化向量化器
        vectorizer = ChunkVectorizer(
            model_name="e:\\PyProjects\\QASystem\\code\\model",
            collection_name="qa_system_chunks"
        )
        
        # 连接到数据库
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        print(f"✅ 成功连接到数据库")
        
        # 获取集合信息
        info = vectorizer.get_collection_info()
        print(f"📊 集合信息: {info}")
        
        # 跳过查询，直接获取数据检查ID结构
        print("\n🔍 跳过查询（避免维度问题），直接检查数据...")
        
        # 尝试直接获取所有数据来检查
        print("\n🔍 获取所有数据进行检查...")
        all_results = vectorizer.collection.get(
            include=["documents", "metadatas"]
        )
        
        if 'ids' in all_results:
            all_ids = all_results['ids']
            none_count = sum(1 for id_val in all_ids if id_val is None or str(id_val).lower() == 'none')
            print(f"📊 总数据量: {len(all_ids)}")
            print(f"⚠️  None ID数量: {none_count}")
            
            if none_count > 0:
                print("\n🔍 None ID的详细信息:")
                for i, id_val in enumerate(all_ids):
                    if id_val is None or str(id_val).lower() == 'none':
                        print(f"  索引 {i}: ID='{id_val}', metadata={all_results['metadatas'][i]}")
                        if i >= 5:  # 只显示前5个
                            print(f"  ... 还有 {none_count - 5} 个None ID")
                            break
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_none_ids()