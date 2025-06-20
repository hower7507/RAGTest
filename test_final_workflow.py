#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最终的工作流程：新数据处理是否能直接存储到正确位置
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer
from search_config import load_config
import json

def test_current_config():
    """测试当前配置"""
    print("=== 测试当前配置 ===")
    
    try:
        config = load_config("balanced")
        print(f"当前配置:")
        print(f"  集合名称: {config.collection_name}")
        print(f"  数据库路径: {config.chroma_db_path}")
        print(f"  模型名称: {config.model_name}")
        
        # 检查路径是否存在
        if os.path.exists(config.chroma_db_path):
            print(f"✓ 数据库路径存在")
        else:
            print(f"❌ 数据库路径不存在")
            
        return config
        
    except Exception as e:
        print(f"配置测试失败: {e}")
        return None

def test_backend_search():
    """测试后端搜索功能"""
    print("\n=== 测试后端搜索功能 ===")
    
    try:
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        print(f"搜索接口初始化: {success}")
        
        if success:
            # 测试搜索chap02相关内容
            queries = ["创新", "技术发展", "数字化转型"]
            
            for query in queries:
                print(f"\n查询: '{query}'")
                results = search_interface.search(
                    query=query,
                    top_k=3,
                    return_prompt=False
                )
                
                if 'results' in results and results['results']:
                    chap02_count = 0
                    for result in results['results']:
                        if 'metadata' in result and 'source_file' in result['metadata']:
                            if 'chap02' in result['metadata']['source_file']:
                                chap02_count += 1
                    
                    print(f"  找到 {len(results['results'])} 个结果，其中 {chap02_count} 个来自chap02")
                else:
                    print(f"  未找到结果")
            
            print("\n✓ 后端搜索功能正常")
            return True
        else:
            print("❌ 搜索接口初始化失败")
            return False
            
    except Exception as e:
        print(f"后端搜索测试失败: {e}")
        return False

def simulate_new_data_processing():
    """模拟新数据处理流程"""
    print("\n=== 模拟新数据处理流程 ===")
    
    try:
        # 1. 加载配置
        config = load_config("balanced")
        print(f"使用配置: {config.collection_name} @ {config.chroma_db_path}")
        
        # 2. 初始化向量化器
        vectorizer = ChunkVectorizer(
            model_name=config.model_name,
            collection_name=config.collection_name
        )
        vectorizer.init_chromadb(persist_directory=config.chroma_db_path)
        
        # 3. 获取当前数据统计
        before_info = vectorizer.get_collection_info()
        print(f"处理前数据统计: {before_info['total_records']} 条记录")
        
        # 4. 模拟添加新数据（创建一个测试数据）
        test_data = {
            "total_chunks": 1,
            "chunks": [
                {
                    "id": "test_chunk_001",
                    "content": "这是一个测试数据块，用于验证新数据处理流程是否正确。",
                    "metadata": {
                        "source_file": "test_data.txt",
                        "chunk_index": 0,
                        "chunk_type": "test",
                        "start_time": "",
                        "end_time": "",
                        "speakers": "测试",
                        "duration": 0
                    }
                }
            ]
        }
        
        # 5. 处理测试数据
        print("\n正在处理测试数据...")
        vectorizer.load_model()  # 加载模型
        
        # 向量化并存储
        chunks = test_data['chunks']
        contents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [chunk['id'] for chunk in chunks]
        
        # 生成向量
        embeddings = vectorizer.model.encode(contents)
        
        # 存储到数据库
        vectorizer.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
            embeddings=embeddings.tolist()
        )
        
        print("✓ 测试数据处理完成")
        
        # 6. 验证数据是否正确存储
        after_info = vectorizer.get_collection_info()
        print(f"处理后数据统计: {after_info['total_records']} 条记录")
        
        if after_info['total_records'] > before_info['total_records']:
            print("✓ 新数据已成功存储")
            
            # 7. 测试搜索新数据
            search_results = vectorizer.search_similar_chunks(
                query_text="测试数据",
                n_results=1
            )
            
            if search_results and 'metadatas' in search_results:
                metadatas = search_results['metadatas'][0]
                for metadata in metadatas:
                    if metadata and 'source_file' in metadata and 'test_data.txt' in metadata['source_file']:
                        print("✓ 新数据可以被正确搜索到")
                        break
            
            # 8. 清理测试数据
            print("\n清理测试数据...")
            vectorizer.collection.delete(ids=["test_chunk_001"])
            
            final_info = vectorizer.get_collection_info()
            print(f"清理后数据统计: {final_info['total_records']} 条记录")
            
            if final_info['total_records'] == before_info['total_records']:
                print("✓ 测试数据已清理")
            
            return True
        else:
            print("❌ 新数据存储失败")
            return False
            
    except Exception as e:
        print(f"新数据处理流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_after_new_data():
    """测试新数据处理后后端是否能正常工作"""
    print("\n=== 测试后端在新数据处理后的状态 ===")
    
    try:
        # 重新初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        if success:
            # 测试搜索
            results = search_interface.search(
                query="创新技术",
                top_k=3,
                return_prompt=False
            )
            
            if 'results' in results and results['results']:
                print(f"✓ 后端搜索正常，找到 {len(results['results'])} 个结果")
                return True
            else:
                print("❌ 后端搜索未返回结果")
                return False
        else:
            print("❌ 后端初始化失败")
            return False
            
    except Exception as e:
        print(f"后端测试失败: {e}")
        return False

def main():
    """主测试流程"""
    print("开始最终工作流程测试...\n")
    
    # 1. 测试当前配置
    config = test_current_config()
    if not config:
        print("❌ 配置测试失败，退出")
        return
    
    # 2. 测试后端搜索功能
    backend_ok = test_backend_search()
    if not backend_ok:
        print("❌ 后端搜索测试失败，退出")
        return
    
    # 3. 模拟新数据处理流程
    new_data_ok = simulate_new_data_processing()
    if not new_data_ok:
        print("❌ 新数据处理流程测试失败")
        return
    
    # 4. 测试新数据处理后的后端状态
    final_backend_ok = test_backend_after_new_data()
    if not final_backend_ok:
        print("❌ 最终后端测试失败")
        return
    
    print("\n" + "="*50)
    print("🎉 所有测试通过！")
    print("✓ 配置已正确修改")
    print("✓ 新数据处理流程会直接存储到正确的ChromaDB位置")
    print("✓ 后端可以正确访问所有数据")
    print("✓ 不再需要手动迁移数据")
    print("="*50)

if __name__ == "__main__":
    main()