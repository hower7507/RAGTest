#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查两个ChromaDB目录的集合内容
"""

import chromadb
import os
from datetime import datetime

def check_chromadb_directory(db_path, description):
    """
    检查指定ChromaDB目录的集合内容
    
    Args:
        db_path: ChromaDB目录路径
        description: 目录描述
    """
    print(f"\n{'='*60}")
    print(f"检查 {description}")
    print(f"路径: {db_path}")
    print(f"{'='*60}")
    
    # 检查目录是否存在
    if not os.path.exists(db_path):
        print(f"❌ 目录不存在: {db_path}")
        return
    
    try:
        # 连接ChromaDB
        client = chromadb.PersistentClient(path=db_path)
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"\n📊 总集合数: {len(collections)}")
        
        if not collections:
            print("❌ 没有找到任何集合")
            return
        
        # 遍历每个集合
        for i, collection in enumerate(collections, 1):
            print(f"\n--- 集合 {i}: {collection.name} ---")
            
            try:
                # 获取集合信息
                count = collection.count()
                print(f"文档数量: {count}")
                
                if count > 0:
                    # 获取前5个文档作为示例
                    sample_size = min(5, count)
                    results = collection.get(limit=sample_size)
                    
                    print(f"\n📝 示例文档 (前{sample_size}个):")
                    
                    for j, (doc_id, metadata, document) in enumerate(zip(
                        results.get('ids', []),
                        results.get('metadatas', []),
                        results.get('documents', [])
                    ), 1):
                        print(f"\n  文档 {j}:")
                        print(f"    ID: {doc_id}")
                        
                        # 显示元数据
                        if metadata:
                            print(f"    元数据:")
                            for key, value in metadata.items():
                                # 限制显示长度
                                if isinstance(value, str) and len(value) > 50:
                                    value = value[:50] + "..."
                                print(f"      {key}: {value}")
                        
                        # 显示文档内容（前100字符）
                        if document:
                            content_preview = document[:100] + "..." if len(document) > 100 else document
                            print(f"    内容: {content_preview}")
                    
                    # 分析元数据统计
                    print(f"\n📈 元数据统计:")
                    metadata_stats = {}
                    all_results = collection.get()
                    
                    for metadata in all_results.get('metadatas', []):
                        if metadata:
                            for key, value in metadata.items():
                                if key not in metadata_stats:
                                    metadata_stats[key] = set()
                                metadata_stats[key].add(str(value))
                    
                    for key, values in metadata_stats.items():
                        unique_count = len(values)
                        print(f"    {key}: {unique_count} 个不同值")
                        
                        # 如果是source_file，显示具体文件
                        if key == 'source_file' and unique_count <= 10:
                            print(f"      文件列表: {', '.join(sorted(values))}")
                        
                        # 如果是chunk_type，显示类型分布
                        if key == 'chunk_type' and unique_count <= 10:
                            print(f"      类型列表: {', '.join(sorted(values))}")
                
                else:
                    print("❌ 集合为空")
                    
            except Exception as e:
                print(f"❌ 检查集合 {collection.name} 时出错: {e}")
                
    except Exception as e:
        print(f"❌ 连接ChromaDB失败: {e}")

def main():
    """
    主函数：检查两个ChromaDB目录
    """
    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"chromadb_dirs_report_{timestamp}.txt"
    
    # 重定向输出到文件
    import sys
    original_stdout = sys.stdout
    
    with open(output_file, 'w', encoding='utf-8') as f:
        sys.stdout = f
        
        print(f"ChromaDB目录内容检查报告")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 定义两个目录
        directories = [
            {
                'path': 'e:\\PyProjects\\QASystem\\chroma_db',
                'description': '主数据库目录 (QA系统文档数据)'
            },
            {
                'path': 'e:\\PyProjects\\QASystem\\code\\chroma_db',
                'description': '会话数据库目录 (聊天会话数据)'
            }
        ]
        
        # 检查每个目录
        for dir_info in directories:
            check_chromadb_directory(dir_info['path'], dir_info['description'])
        
        print(f"\n{'='*60}")
        print("检查完成")
        print(f"{'='*60}")
    
    # 恢复标准输出
    sys.stdout = original_stdout
    print(f"报告已保存到: {output_file}")

if __name__ == "__main__":
    main()