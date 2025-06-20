#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新处理chap02数据，直接存储到后端使用的ChromaDB位置
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from qa_document_processor import QADocumentProcessor
from vectorize_chunks import ChunkVectorizer
import chromadb

def clean_existing_chap02_data():
    """清理现有的chap02数据"""
    print("正在清理现有的chap02数据...")
    
    try:
        # 连接到后端使用的ChromaDB
        client = chromadb.PersistentClient(path='e:\\PyProjects\\QASystem\\chroma_db')
        
        # 获取qa_system_chunks集合
        try:
            collection = client.get_collection('qa_system_chunks')
            
            # 获取所有数据
            results = collection.get(include=['metadatas'])
            
            # 找到chap02相关的ID
            chap02_ids = []
            for i, metadata in enumerate(results['metadatas']):
                if metadata and (
                    ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                    ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                ):
                    chap02_ids.append(results['ids'][i])
            
            if chap02_ids:
                print(f"找到 {len(chap02_ids)} 条chap02数据，正在删除...")
                collection.delete(ids=chap02_ids)
                print("✓ 清理完成")
            else:
                print("未找到chap02数据")
                
        except Exception as e:
            print(f"获取集合时出错: {e}")
            
    except Exception as e:
        print(f"清理数据时出错: {e}")

def reprocess_chap02():
    """重新处理chap02数据"""
    print("\n=== 重新处理chap02数据 ===")
    
    # 步骤1: 清理现有数据
    clean_existing_chap02_data()
    
    # 步骤2: 重新处理文档
    print("\n步骤1: 重新处理问答对文档")
    print("-" * 40)
    
    qa_file = "e:\\PyProjects\\QASystem\\data\\chap02.txt"
    processor = QADocumentProcessor(qa_file)
    
    # 处理文档并生成chunks
    chunks = processor.process_document(save_output=True)
    
    if not chunks:
        print("❌ 文档处理失败")
        return False
    
    print(f"✓ 成功处理 {len(chunks)} 个问答对")
    
    # 步骤3: 向量化和存储到正确位置
    print("\n步骤2: 向量化和存储到后端ChromaDB")
    print("-" * 40)
    
    # 创建向量化器 - 使用后端相同的配置
    vectorizer = ChunkVectorizer(
        model_name="BAAI/bge-small-zh-v1.5",
        collection_name="qa_system_chunks"  # 后端使用的集合名称
    )
    
    # 向量化并存储到后端数据库
    processed_file = qa_file.replace('.txt', '_qa_processed.json')
    success = vectorizer.process_and_store(
        json_file_path=processed_file,
        persist_directory="e:\\PyProjects\\QASystem\\chroma_db"  # 后端使用的数据库路径
    )
    
    if not success:
        print("❌ 向量化失败")
        return False
    
    print("✓ 向量化和存储完成")
    
    # 步骤4: 验证存储结果
    print("\n步骤3: 验证存储结果")
    print("-" * 40)
    
    try:
        # 检查集合信息
        info = vectorizer.get_collection_info()
        print(f"集合名称: {info.get('collection_name', 'unknown')}")
        print(f"总记录数: {info.get('total_records', 0)}")
        
        # 测试搜索功能
        test_queries = ["创新商业化", "人才标准"]
        
        for query in test_queries:
            print(f"\n测试查询: '{query}'")
            results = vectorizer.search_similar_chunks(
                query_text=query,
                n_results=2
            )
            
            if results and 'metadatas' in results:
                chap02_count = 0
                for metadata in results['metadatas'][0]:
                    if metadata and (
                        ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                        ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                    ):
                        chap02_count += 1
                        print(f"  ✓ 找到chap02数据: {metadata.get('question', 'N/A')[:40]}...")
                
                if chap02_count == 0:
                    print(f"  ⚠️  未找到chap02数据")
            else:
                print(f"  ❌ 查询失败")
    
    except Exception as e:
        print(f"验证时出错: {e}")
        return False
    
    print("\n=== 重新处理完成 ===")
    print("✅ chap02数据已成功存储到后端ChromaDB")
    print("✅ 后续新增数据将直接存储到正确位置")
    
    return True

def verify_backend_access():
    """验证后端能否访问chap02数据"""
    print("\n=== 验证后端访问 ===")
    
    try:
        from search_interface import SearchInterface
        
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        if not success:
            print("❌ 后端搜索接口初始化失败")
            return False
        
        # 测试搜索
        results = search_interface.search(
            query="创新商业化",
            top_k=3,
            return_prompt=False
        )
        
        if results and 'search_results' in results:
            chap02_found = False
            for result in results['search_results']:
                metadata = result.get('metadata', {})
                if metadata and (
                    ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                    ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                ):
                    chap02_found = True
                    break
            
            if chap02_found:
                print("✅ 后端搜索接口能够访问chap02数据")
                return True
            else:
                print("❌ 后端搜索接口无法找到chap02数据")
                return False
        else:
            print("❌ 后端搜索接口查询失败")
            return False
            
    except Exception as e:
        print(f"验证后端访问时出错: {e}")
        return False

if __name__ == "__main__":
    print("开始重新处理chap02数据...")
    
    # 重新处理数据
    success = reprocess_chap02()
    
    if success:
        # 验证后端访问
        verify_backend_access()
    
    print("\n处理完成！")