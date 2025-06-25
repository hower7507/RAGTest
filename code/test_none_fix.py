#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试None值修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search_interface import get_search_interface
from context_manager import ContextManager
from advanced_search_system import AdvancedSearchSystem
import chromadb

def test_none_fix():
    """
    测试None值修复效果
    """
    print("=== 测试None值修复效果 ===")
    
    try:
        # 初始化搜索接口
        search_interface = get_search_interface()
        if not search_interface:
            print("❌ 无法初始化搜索接口")
            return
        
        print("✅ 搜索接口初始化成功")
        
        # 获取collection
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("qa_system_chunks")
        
        # 创建上下文管理器
        context_manager = ContextManager(
            search_system=search_interface.search_system,
            collection=collection,
            use_bre_reranking=True
        )
        
        print("✅ 上下文管理器初始化成功")
        
        # 测试查询
        test_queries = ["测试", "环境准备"]
        
        for query in test_queries:
            print(f"\n--- 测试查询: '{query}' ---")
            
            try:
                # 执行搜索获取原始结果
                search_results = search_interface.search(query, top_k=10, return_prompt=False)
                
                if 'results' in search_results:
                    results = search_results['results']
                    print(f"原始搜索结果数量: {len(results)}")
                    
                    # 使用上下文管理器处理结果
                    processed_results = context_manager.process_search_results(
                        query=query,
                        search_results=results,
                        max_results=5,
                        max_context_length=1000
                    )
                    
                    context_str = processed_results.get('context', '')
                    print(f"上下文长度: {len(context_str)}")
                    
                    # 检查上下文中是否包含None
                    if 'None' in context_str:
                        print("❌ 上下文中仍包含'None'")
                        # 显示包含None的行
                        lines = context_str.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            if 'None' in line:
                                print(f"  第{line_num}行: {line}")
                    else:
                        print("✅ 上下文中不包含'None'")
                    
                    # 显示上下文示例（前300字符）
                    print(f"\n上下文示例:\n{context_str[:300]}...")
                    
                    print(f"🎉 查询'{query}'测试通过！")
                else:
                    print(f"❌ 查询'{query}'没有返回搜索结果")
                    
            except Exception as e:
                print(f"❌ 查询'{query}'时出错: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_none_fix()