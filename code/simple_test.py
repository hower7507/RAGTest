# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search_interface import SearchInterface

def simple_test():
    print("=== 简单测试 ===")
    
    # 初始化搜索接口
    search_interface = SearchInterface()
    if not search_interface.initialize():
        print("❌ 搜索接口初始化失败")
        return
    
    # 执行搜索
    query = "测试"
    search_result = search_interface.search(query, top_k=3)
    
    print(f"\n搜索结果类型: {type(search_result)}")
    
    if 'results' in search_result:
        results = search_result['results']
        print(f"找到 {len(results)} 个结果")
        
        for i, result in enumerate(results):
            print(f"\n--- 结果 {i+1} ---")
            document_id = result.get('document_id')
            print(f"document_id: {document_id}")
            print(f"document_id类型: {type(document_id)}")
            
            if document_id is None:
                print(f"❌ 发现None ID!")
            elif str(document_id).lower() == 'none':
                print(f"❌ 发现字符串'None' ID!")
            else:
                print(f"✅ ID正常")

if __name__ == "__main__":
    simple_test()