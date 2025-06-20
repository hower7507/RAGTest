#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查code目录下ChromaDB中的集合信息
"""

import chromadb

def check_code_collections():
    """检查code目录下ChromaDB中的所有集合"""
    try:
        # 连接到code目录下的ChromaDB
        client = chromadb.PersistentClient(path='e:\\PyProjects\\QASystem\\code\\chroma_db')
        
        # 获取所有集合
        collections = client.list_collections()
        
        print("Code目录ChromaDB集合信息:")
        print("=" * 50)
        
        if not collections:
            print("没有找到任何集合")
            return
        
        for col in collections:
            print(f"集合名称: {col.name}")
            print(f"文档数量: {col.count()}")
            
            # 获取一些示例数据
            if col.count() > 0:
                try:
                    results = col.peek(limit=2)
                    print(f"示例ID: {results['ids'][:2] if results['ids'] else '无'}")
                    if results.get('metadatas'):
                        metadata = results['metadatas'][0] if results['metadatas'] else {}
                        print(f"示例元数据: {metadata}")
                        
                        # 检查是否是chap02数据
                        if 'source_file' in metadata and 'chap02' in metadata['source_file']:
                            print("*** 发现chap02数据! ***")
                        elif 'chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair':
                            print("*** 发现问答对数据! ***")
                            
                except Exception as e:
                    print(f"获取示例数据失败: {e}")
            
            print("-" * 30)
        
        # 检查特定集合
        target_collections = ['qa_system_chunks', 'qa_collection', 'qa_demo_collection']
        print("\n检查目标集合:")
        for target in target_collections:
            try:
                collection = client.get_collection(target)
                count = collection.count()
                print(f"✓ {target}: {count} 文档")
                
                # 如果有数据，检查是否包含chap02
                if count > 0:
                    try:
                        results = collection.get(limit=5, include=['metadatas'])
                        chap02_count = 0
                        for metadata in results.get('metadatas', []):
                            if metadata and 'source_file' in metadata and 'chap02' in metadata['source_file']:
                                chap02_count += 1
                            elif metadata and 'chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair':
                                chap02_count += 1
                        
                        if chap02_count > 0:
                            print(f"  -> 包含 {chap02_count} 条chap02/问答对数据")
                    except Exception as e:
                        print(f"  -> 检查chap02数据时出错: {e}")
                        
            except Exception:
                print(f"✗ {target}: 不存在")
                
    except Exception as e:
        print(f"检查集合时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_code_collections()