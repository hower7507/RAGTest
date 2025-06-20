#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试搜索接口的具体问题
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer

def test_search_interface_step_by_step():
    """逐步测试搜索接口"""
    print("=== 逐步测试搜索接口 ===")
    
    try:
        # 步骤1: 初始化搜索接口
        print("\n步骤1: 初始化搜索接口")
        search_interface = SearchInterface(config_name="balanced")
        print(f"配置: {search_interface.config}")
        
        # 步骤2: 初始化搜索系统
        print("\n步骤2: 初始化搜索系统")
        success = search_interface.initialize()
        print(f"初始化结果: {success}")
        
        if not success:
            print("❌ 初始化失败，退出测试")
            return
        
        # 步骤3: 检查向量化器状态
        print("\n步骤3: 检查向量化器状态")
        vectorizer = search_interface.vectorizer
        if vectorizer:
            info = vectorizer.get_collection_info()
            print(f"集合信息: {info}")
        else:
            print("❌ 向量化器未初始化")
            return
        
        # 步骤4: 检查搜索系统状态
        print("\n步骤4: 检查搜索系统状态")
        search_system = search_interface.search_system
        if search_system:
            print(f"搜索系统已初始化: {type(search_system)}")
        else:
            print("❌ 搜索系统未初始化")
            return
        
        # 步骤5: 测试简单搜索
        print("\n步骤5: 测试简单搜索")
        query = "创新"
        print(f"查询: '{query}'")
        
        try:
            results = search_interface.search(
                query=query,
                top_k=3,
                return_prompt=False
            )
            
            print(f"搜索结果类型: {type(results)}")
            if results:
                print(f"结果键: {list(results.keys())}")
                
                if 'results' in results:
                    search_results = results['results']
                    print(f"搜索结果数量: {len(search_results)}")
                    
                    chap02_count = 0
                    for i, result in enumerate(search_results[:3]):
                        print(f"\n结果 {i+1}:")
                        print(f"  类型: {type(result)}")
                        print(f"  键: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                        
                        if 'metadata' in result:
                            metadata = result['metadata']
                            print(f"  元数据: {metadata}")
                            
                            # 检查是否是chap02数据
                            is_chap02 = (
                                ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                                ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                            )
                            print(f"  是否chap02数据: {is_chap02}")
                            
                            if is_chap02:
                                chap02_count += 1
                    
                    print(f"\n✓ 找到 {chap02_count} 个chap02相关结果")
                else:
                    print("❌ 结果中没有results键")
            else:
                print("❌ 搜索返回空结果")
                
        except Exception as e:
            print(f"❌ 搜索时出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 步骤6: 直接测试向量化器搜索
        print("\n步骤6: 直接测试向量化器搜索")
        try:
            direct_results = vectorizer.search_similar_chunks(
                query_text=query,
                n_results=3
            )
            
            print(f"直接搜索结果类型: {type(direct_results)}")
            if direct_results:
                print(f"直接搜索结果键: {list(direct_results.keys())}")
                
                if 'metadatas' in direct_results and direct_results['metadatas']:
                    metadatas = direct_results['metadatas'][0]
                    print(f"元数据数量: {len(metadatas)}")
                    
                    chap02_count = 0
                    for metadata in metadatas:
                        if metadata and (
                            ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                            ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                        ):
                            chap02_count += 1
                    
                    print(f"chap02数据数量: {chap02_count}")
            else:
                print("❌ 直接搜索返回空结果")
                
        except Exception as e:
            print(f"❌ 直接搜索时出错: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

def test_search_config():
    """测试搜索配置"""
    print("\n=== 测试搜索配置 ===")
    
    try:
        from search_config import load_config
        
        config = load_config("balanced")
        print(f"配置详情:")
        print(f"  模型名称: {config.model_name}")
        print(f"  集合名称: {config.collection_name}")
        print(f"  数据库路径: {config.chroma_db_path}")
        print(f"  向量权重: {config.vector_weight}")
        print(f"  BM25权重: {config.bm25_weight}")
        print(f"  精确匹配权重: {config.exact_weight}")
        
        # 检查数据库路径是否存在
        if os.path.exists(config.chroma_db_path):
            print(f"✓ 数据库路径存在")
        else:
            print(f"❌ 数据库路径不存在: {config.chroma_db_path}")
            
    except Exception as e:
        print(f"测试配置时出错: {e}")

if __name__ == "__main__":
    # 测试配置
    test_search_config()
    
    # 逐步测试搜索接口
    test_search_interface_step_by_step()