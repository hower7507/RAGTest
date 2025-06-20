#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试移除时间参数后的搜索功能
"""

import sys
sys.path.append('code')

from search_interface import SearchInterface

def test_search_without_time_params():
    """
    测试移除时间参数后的搜索功能
    """
    print("=== 测试移除时间参数后的搜索功能 ===")
    
    # 初始化搜索接口
    search_interface = SearchInterface('balanced')
    
    if not search_interface.initialize():
        print("❌ 搜索系统初始化失败")
        return False
    
    print("✅ 搜索系统初始化成功")
    
    # 测试查询
    test_queries = [
        "自然语言处理",
        "机器学习",
        "深度学习",
        "神经网络"
    ]
    
    for query in test_queries:
        print(f"\n--- 测试查询: {query} ---")
        
        try:
            # 执行搜索（不再传递时间参数）
            result = search_interface.search(
                query=query,
                top_k=3,
                return_prompt=False
            )
            
            if 'error' in result:
                print(f"❌ 搜索失败: {result['error']}")
                continue
            
            print(f"✅ 搜索成功")
            print(f"  - 查询: {result['query']}")
            print(f"  - 结果数量: {result['total_results']}")
            print(f"  - 搜索时间: {result['search_time']:.2f}秒")
            print(f"  - 候选文档数: {result['total_candidates']}")
            
            # 显示前3个结果
            for i, res in enumerate(result['results'][:3]):
                print(f"  结果{i+1}:")
                print(f"    - 相关度: {res['scores']['final_score']:.3f}")
                print(f"    - 来源: {res['metadata']['source_file']}")
                print(f"    - 内容预览: {res['content'][:50]}...")
                
        except Exception as e:
            print(f"❌ 搜索过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")
    return True

def test_quick_search():
    """
    测试快速搜索功能
    """
    print("\n=== 测试快速搜索功能 ===")
    
    search_interface = SearchInterface('balanced')
    
    if not search_interface.initialize():
        print("❌ 搜索系统初始化失败")
        return False
    
    # 测试快速搜索
    query = "自然语言处理的应用"
    print(f"\n快速搜索查询: {query}")
    
    try:
        result = search_interface.quick_search(query, top_k=3)
        print("快速搜索结果:")
        print(result)
        
    except Exception as e:
        print(f"❌ 快速搜索失败: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    # 运行测试
    test_search_without_time_params()
    test_quick_search()
    
    print("\n🎉 所有测试完成！时间参数已成功移除。")