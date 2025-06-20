#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查ChromaDB中的集合信息
"""

import chromadb

def check_collections():
    """检查ChromaDB中的所有集合"""
    try:
        # 连接到ChromaDB
        client = chromadb.PersistentClient(path='e:\\PyProjects\\QASystem\\chroma_db')
        
        # 获取所有集合
        collections = client.list_collections()
        
        print("ChromaDB集合信息:")
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
                    results = col.peek(limit=3)
                    print(f"示例ID: {results['ids'][:3] if results['ids'] else '无'}")
                    if results.get('metadatas'):
                        print(f"示例元数据: {results['metadatas'][0] if results['metadatas'] else '无'}")
                except Exception as e:
                    print(f"获取示例数据失败: {e}")
            
            print("-" * 30)
        
        # 检查特定集合
        target_collections = ['qa_system_chunks', 'qa_collection', 'qa_demo_collection']
        print("\n检查目标集合:")
        for target in target_collections:
            try:
                collection = client.get_collection(target)
                print(f"✓ {target}: {collection.count()} 文档")
            except Exception:
                print(f"✗ {target}: 不存在")
                
    except Exception as e:
        print(f"检查集合时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_collections()