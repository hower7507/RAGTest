# -*- coding: utf-8 -*-
"""
调试chap02数据检测逻辑
分析为什么显示未连接chap02
"""

import os
import sys
sys.path.append('code')

from vectorize_chunks import ChunkVectorizer
from search_config import load_config

def debug_chap02_detection():
    """
    调试chap02数据检测逻辑
    """
    print("=== 调试chap02数据检测逻辑 ===")
    
    try:
        # 1. 加载配置
        config = load_config("balanced")
        print(f"配置加载成功: {config.collection_name}")
        print(f"数据库路径: {config.chroma_db_path}")
        
        # 2. 初始化向量化器
        vectorizer = ChunkVectorizer(
            model_name=config.model_name,
            collection_name=config.collection_name
        )
        
        # 3. 连接数据库
        vectorizer.init_chromadb(config.chroma_db_path)
        print(f"数据库连接成功")
        
        # 4. 获取集合信息
        info = vectorizer.get_collection_info()
        total_records = info.get('total_records', 0)
        print(f"总记录数: {total_records}")
        
        if total_records == 0:
            print("❌ 没有数据")
            return
        
        # 5. 详细分析前100条记录
        print("\n=== 分析前100条记录的元数据 ===")
        test_results = vectorizer.collection.get(limit=min(100, total_records))
        
        chap01_count = 0
        chap02_count = 0
        qa_count = 0
        other_count = 0
        
        metadatas = test_results.get('metadatas', [])
        print(f"获取到 {len(metadatas)} 条元数据")
        
        for i, metadata in enumerate(metadatas):
            if not metadata:
                print(f"记录 {i}: 元数据为空")
                other_count += 1
                continue
                
            source_file = metadata.get('source_file', '')
            question = metadata.get('question', '')
            chunk_type = metadata.get('chunk_type', '')
            
            # 打印前5条记录的详细信息
            if i < 5:
                print(f"\n记录 {i}:")
                print(f"  source_file: {source_file}")
                print(f"  question: {question}")
                print(f"  chunk_type: {chunk_type}")
                print(f"  所有字段: {list(metadata.keys())}")
            
            # 统计分类
            if 'chap01' in source_file:
                chap01_count += 1
            elif 'chap02' in source_file:
                chap02_count += 1
            elif question and question.strip():
                qa_count += 1
                print(f"记录 {i}: 发现QA数据 - question: {question[:50]}...")
            else:
                other_count += 1
                if i < 10:  # 只打印前10条其他类型的记录
                    print(f"记录 {i}: 其他类型 - source_file: {source_file}, chunk_type: {chunk_type}")
        
        print(f"\n=== 统计结果 ===")
        print(f"chap01数据: {chap01_count} 条")
        print(f"chap02数据: {chap02_count} 条")
        print(f"QA数据: {qa_count} 条")
        print(f"其他数据: {other_count} 条")
        
        # 6. 使用原始检测逻辑
        print(f"\n=== 原始检测逻辑测试 ===")
        original_chap02_count = 0
        for metadata in metadatas:
            if metadata and (
                ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                ('question' in metadata and metadata.get('question'))
            ):
                original_chap02_count += 1
        
        print(f"原始检测逻辑结果: {original_chap02_count} 条chap02相关数据")
        
        # 7. 改进的检测逻辑
        print(f"\n=== 改进检测逻辑测试 ===")
        improved_chap02_count = 0
        for metadata in metadatas:
            if metadata:
                source_file = metadata.get('source_file', '')
                question = metadata.get('question', '')
                
                # 检测chap02文件
                if 'chap02' in source_file:
                    improved_chap02_count += 1
                # 检测QA数据（通常来自chap02）
                elif question and question.strip():
                    improved_chap02_count += 1
        
        print(f"改进检测逻辑结果: {improved_chap02_count} 条chap02相关数据")
        
        # 8. 检查更多记录
        if total_records > 100:
            print(f"\n=== 检查所有 {total_records} 条记录 ===")
            all_results = vectorizer.collection.get()
            all_metadatas = all_results.get('metadatas', [])
            
            all_chap01 = 0
            all_chap02 = 0
            all_qa = 0
            all_other = 0
            
            for metadata in all_metadatas:
                if not metadata:
                    all_other += 1
                    continue
                    
                source_file = metadata.get('source_file', '')
                question = metadata.get('question', '')
                
                if 'chap01' in source_file:
                    all_chap01 += 1
                elif 'chap02' in source_file:
                    all_chap02 += 1
                elif question and question.strip():
                    all_qa += 1
                else:
                    all_other += 1
            
            print(f"全部数据统计:")
            print(f"  chap01数据: {all_chap01} 条")
            print(f"  chap02数据: {all_chap02} 条")
            print(f"  QA数据: {all_qa} 条")
            print(f"  其他数据: {all_other} 条")
            
            total_chap02_related = all_chap02 + all_qa
            print(f"  chap02相关总数: {total_chap02_related} 条")
        
    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chap02_detection()