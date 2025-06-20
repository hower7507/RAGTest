#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将chap02问答对数据迁移到正确的ChromaDB位置和集合
"""

import chromadb
import json
from typing import List, Dict, Any

def migrate_chap02_data():
    """将chap02数据从code目录迁移到根目录的qa_system_chunks集合"""
    
    print("开始迁移chap02问答对数据...")
    
    try:
        # 连接源数据库（code目录）
        source_client = chromadb.PersistentClient(path='e:\\PyProjects\\QASystem\\code\\chroma_db')
        
        # 连接目标数据库（根目录）
        target_client = chromadb.PersistentClient(path='e:\\PyProjects\\QASystem\\chroma_db')
        
        # 获取源集合中的chap02数据
        source_collections = ['qa_collection', 'qa_demo_collection']
        
        # 获取或创建目标集合
        try:
            target_collection = target_client.get_collection('qa_system_chunks')
            print(f"目标集合qa_system_chunks已存在，当前有{target_collection.count()}条记录")
        except:
            target_collection = target_client.create_collection('qa_system_chunks')
            print("创建了新的目标集合qa_system_chunks")
        
        migrated_count = 0
        
        for collection_name in source_collections:
            try:
                source_collection = source_client.get_collection(collection_name)
                count = source_collection.count()
                
                if count == 0:
                    print(f"集合{collection_name}为空，跳过")
                    continue
                
                print(f"\n处理源集合: {collection_name} ({count}条记录)")
                
                # 获取所有数据
                results = source_collection.get(
                    include=['documents', 'metadatas', 'embeddings']
                )
                
                # 筛选chap02相关数据
                chap02_ids = []
                chap02_documents = []
                chap02_metadatas = []
                chap02_embeddings = []
                
                for i, metadata in enumerate(results['metadatas']):
                    if metadata and (
                        ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                        ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                    ):
                        # 修改ID以避免冲突
                        new_id = f"chap02_{results['ids'][i]}"
                        chap02_ids.append(new_id)
                        chap02_documents.append(results['documents'][i])
                        chap02_metadatas.append(metadata)
                        chap02_embeddings.append(results['embeddings'][i])
                
                if chap02_ids:
                    print(f"找到{len(chap02_ids)}条chap02数据")
                    
                    # 检查目标集合中是否已存在这些ID
                    existing_ids = set()
                    try:
                        existing_results = target_collection.get(ids=chap02_ids)
                        existing_ids = set(existing_results['ids'])
                    except:
                        pass  # 如果获取失败，说明没有重复ID
                    
                    # 过滤掉已存在的ID
                    new_ids = []
                    new_documents = []
                    new_metadatas = []
                    new_embeddings = []
                    
                    for i, id in enumerate(chap02_ids):
                        if id not in existing_ids:
                            new_ids.append(id)
                            new_documents.append(chap02_documents[i])
                            new_metadatas.append(chap02_metadatas[i])
                            new_embeddings.append(chap02_embeddings[i])
                    
                    if new_ids:
                        # 添加到目标集合
                        target_collection.add(
                            ids=new_ids,
                            documents=new_documents,
                            metadatas=new_metadatas,
                            embeddings=new_embeddings
                        )
                        
                        migrated_count += len(new_ids)
                        print(f"成功迁移{len(new_ids)}条新数据")
                    else:
                        print("所有数据已存在，跳过")
                else:
                    print("未找到chap02数据")
                    
            except Exception as e:
                print(f"处理集合{collection_name}时出错: {e}")
        
        print(f"\n迁移完成！总共迁移了{migrated_count}条chap02数据")
        
        # 验证迁移结果
        final_count = target_collection.count()
        print(f"目标集合qa_system_chunks现在有{final_count}条记录")
        
        # 检查chap02数据
        try:
            sample_results = target_collection.get(limit=10, include=['metadatas'])
            chap02_count = 0
            for metadata in sample_results.get('metadatas', []):
                if metadata and (
                    ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                    ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                ):
                    chap02_count += 1
            
            print(f"验证：在前10条记录中发现{chap02_count}条chap02数据")
        except Exception as e:
            print(f"验证时出错: {e}")
            
    except Exception as e:
        print(f"迁移过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_chap02_data()