#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的配置是否正确工作
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer
from search_config import load_config

def test_config_change():
    """测试配置修改后的效果"""
    print("=== 测试配置修改后的效果 ===")
    
    try:
        # 测试配置加载
        print("\n1. 测试配置加载")
        config = load_config("balanced")
        print(f"配置详情:")
        print(f"  模型名称: {config.model_name}")
        print(f"  集合名称: {config.collection_name}")
        print(f"  数据库路径: {config.chroma_db_path}")
        
        # 检查数据库路径是否存在
        if os.path.exists(config.chroma_db_path):
            print(f"✓ 数据库路径存在")
        else:
            print(f"❌ 数据库路径不存在: {config.chroma_db_path}")
            return
        
        # 测试向量化器初始化
        print("\n2. 测试向量化器初始化")
        vectorizer = ChunkVectorizer(
            model_name=config.model_name,
            collection_name=config.collection_name
        )
        vectorizer.init_chromadb(persist_directory=config.chroma_db_path)
        
        # 获取集合信息
        info = vectorizer.get_collection_info()
        print(f"集合信息: {info}")
        
        # 测试搜索接口初始化
        print("\n3. 测试搜索接口初始化")
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        print(f"搜索接口初始化结果: {success}")
        
        if success:
            # 测试搜索功能
            print("\n4. 测试搜索功能")
            query = "创新"
            results = search_interface.search(
                query=query,
                top_k=3,
                return_prompt=False
            )
            
            if 'results' in results and results['results']:
                print(f"✓ 搜索成功，找到 {len(results['results'])} 个结果")
                
                # 检查是否有chap02数据
                chap02_count = 0
                for result in results['results']:
                    if 'metadata' in result:
                        metadata = result['metadata']
                        if 'source_file' in metadata and 'chap02' in metadata['source_file']:
                            chap02_count += 1
                
                print(f"✓ 其中包含 {chap02_count} 个chap02相关结果")
                
                if chap02_count > 0:
                    print("✓ 配置修改成功！后端可以正确访问chap02数据")
                else:
                    print("⚠️ 未找到chap02数据，可能需要重新处理数据")
            else:
                print("❌ 搜索未返回结果")
        else:
            print("❌ 搜索接口初始化失败")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

def test_data_migration_status():
    """检查数据迁移状态"""
    print("\n=== 检查数据迁移状态 ===")
    
    try:
        # 检查code目录下的ChromaDB
        code_chroma_path = "e:\\PyProjects\\QASystem\\code\\chroma_db"
        root_chroma_path = "e:\\PyProjects\\QASystem\\chroma_db"
        
        print(f"\ncode目录ChromaDB路径: {code_chroma_path}")
        print(f"存在: {os.path.exists(code_chroma_path)}")
        
        print(f"\nroot目录ChromaDB路径: {root_chroma_path}")
        print(f"存在: {os.path.exists(root_chroma_path)}")
        
        # 检查code目录下的集合
        if os.path.exists(code_chroma_path):
            print("\n检查code目录下的集合:")
            vectorizer_code = ChunkVectorizer(
                model_name="BAAI/bge-small-zh-v1.5",
                collection_name="qa_system_chunks"
            )
            vectorizer_code.init_chromadb(persist_directory=code_chroma_path)
            
            info_code = vectorizer_code.get_collection_info()
            print(f"code目录集合信息: {info_code}")
        
        # 检查root目录下的集合
        if os.path.exists(root_chroma_path):
            print("\n检查root目录下的集合:")
            vectorizer_root = ChunkVectorizer(
                model_name="BAAI/bge-small-zh-v1.5",
                collection_name="qa_system_chunks"
            )
            vectorizer_root.init_chromadb(persist_directory=root_chroma_path)
            
            info_root = vectorizer_root.get_collection_info()
            print(f"root目录集合信息: {info_root}")
            
    except Exception as e:
        print(f"检查数据迁移状态时出错: {e}")

if __name__ == "__main__":
    # 检查数据迁移状态
    test_data_migration_status()
    
    # 测试配置修改后的效果
    test_config_change()