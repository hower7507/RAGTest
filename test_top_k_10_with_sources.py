#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试top_k=10和文档来源标注功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from search_interface import SearchInterface

def test_top_k_10_with_sources():
    """
    测试返回10个文档并验证来源标注
    """
    print("=== 测试top_k=10和文档来源标注功能 ===")
    
    # 初始化搜索接口
    search_interface = SearchInterface("balanced")
    
    # 测试查询
    test_queries = [
        "自然语言处理的应用有哪些？",
        "机器学习算法"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"{'='*60}")
        
        # 执行搜索（不指定top_k，使用默认值10）
        result = search_interface.search(query)
        
        if 'error' in result:
            print(f"搜索失败: {result['error']}")
            continue
        
        print(f"\n搜索结果统计:")
        print(f"  总结果数: {result['total_results']}")
        print(f"  搜索时间: {result['search_time']:.2f}秒")
        print(f"  候选文档数: {result['total_candidates']}")
        
        print(f"\n前5个结果的来源文件:")
        for i, res in enumerate(result['results'][:5]):
            source_file = res['metadata'].get('source_file', '未知')
            file_name = os.path.basename(source_file).replace('.txt', '').replace('_processed.json', '') if source_file else '未知来源'
            print(f"  结果{i+1}: 来源={file_name}, 得分={res['score']:.3f}")
        
        # 检查提示词中的来源标注
        if 'prompt' in result:
            prompt = result['prompt']
            print(f"\n提示词长度: {len(prompt)} 字符")
            
            # 检查是否包含来源标注
            source_count = prompt.count('来源文件:')
            print(f"提示词中包含 {source_count} 个文档来源标注")
            
            # 显示提示词的前500字符
            print(f"\n提示词预览:")
            print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
        
        print(f"\n验证: 返回了 {result['total_results']} 个文档（期望10个）")
        if result['total_results'] == 10:
            print("✅ top_k=10 设置正确")
        else:
            print(f"⚠️  实际返回 {result['total_results']} 个文档，可能是数据库中文档不足10个")

def test_explicit_top_k():
    """
    测试显式指定top_k参数
    """
    print(f"\n\n=== 测试显式指定top_k参数 ===")
    
    search_interface = SearchInterface("balanced")
    
    # 测试不同的top_k值
    test_values = [3, 5, 8, 15]
    query = "自然语言处理"
    
    for top_k in test_values:
        print(f"\n测试 top_k={top_k}:")
        result = search_interface.search(query, top_k=top_k)
        
        if 'error' not in result:
            actual_count = result['total_results']
            print(f"  期望: {top_k}, 实际: {actual_count}")
            if actual_count == top_k:
                print(f"  ✅ top_k={top_k} 正确")
            else:
                print(f"  ⚠️  可能是数据库中文档不足{top_k}个")
        else:
            print(f"  ❌ 搜索失败: {result['error']}")

if __name__ == "__main__":
    test_top_k_10_with_sources()
    test_explicit_top_k()
    print("\n=== 测试完成 ===")