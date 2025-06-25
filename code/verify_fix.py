# -*- coding: utf-8 -*-
"""
验证None ID问题修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search_interface import SearchInterface
from context_manager import ContextManager
from multi_stage_query import MultiStageQuerySystem
from dimension_analyzer import DimensionAnalyzer

def verify_fix():
    """
    验证None ID问题是否已修复
    """
    print("=== 验证None ID问题修复效果 ===")
    
    try:
        # 初始化搜索接口
        search_interface = SearchInterface()
        if not search_interface.initialize():
            print("❌ 搜索接口初始化失败")
            return False
        
        # 测试单个查询
        test_queries = [
            "测试"
        ]
        
        all_passed = True
        
        for query in test_queries:
            print(f"\n--- 测试查询: {query} ---")
            
            # 1. 测试搜索接口
            search_result = search_interface.search(query, top_k=3)
            
            if 'results' in search_result:
                results = search_result['results']
                print(f"搜索接口返回 {len(results)} 个结果")
                
                for i, result in enumerate(results):
                    document_id = result.get('document_id')
                    print(f"  结果 {i+1}: document_id={document_id}")
                    if document_id is None or str(document_id).lower() == 'none':
                        print(f"❌ 搜索接口结果 {i+1} 仍有None ID: {document_id}")
                        all_passed = False
                    else:
                        print(f"✅ 搜索接口结果 {i+1} ID正常: {document_id}")
            
            # 2. 测试多阶段查询
            dimension_analyzer = DimensionAnalyzer()
            multi_stage_query = MultiStageQuerySystem(search_interface)
            
            dimension_result = dimension_analyzer.analyze_query_dimensions(query)
            multi_stage_result = multi_stage_query.multi_stage_search(
                query=query,
                max_results=3,
                dimension_analysis=dimension_result
            )
            
            if isinstance(multi_stage_result, dict) and 'results' in multi_stage_result:
                ms_results = multi_stage_result['results']
                print(f"多阶段查询返回 {len(ms_results)} 个结果")
                
                for i, result in enumerate(ms_results):
                    result_id = result.get('id')
                    document_id = result.get('document_id')
                    print(f"  多阶段结果 {i+1}: id={result_id}, document_id={document_id}")
                    if result_id is None or document_id is None:
                        print(f"❌ 多阶段结果 {i+1} 仍有None ID: id={result_id}, document_id={document_id}")
                        all_passed = False
                    else:
                        print(f"✅ 多阶段结果 {i+1} ID正常: id={result_id}, document_id={document_id}")
            
            # 3. 测试上下文管理器
            search_system = search_interface.search_system
            collection = search_interface.vectorizer.collection
            context_manager = ContextManager(search_system, collection)
            
            if isinstance(multi_stage_result, dict) and 'results' in multi_stage_result:
                context_result = context_manager.process_search_results(
                    query=query,
                    search_results=multi_stage_result['results'],
                    max_results=3
                )
                
                if isinstance(context_result, dict):
                    context_str = context_result.get('context', '')
                    
                    # 检查上下文字符串中是否还有None
                    if 'None' in context_str:
                        print(f"❌ 上下文字符串仍包含'None'")
                        # 显示包含None的行
                        lines = context_str.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            if 'None' in line:
                                print(f"  第{line_num}行: {line}")
                        all_passed = False
                    else:
                        print(f"✅ 上下文字符串不包含'None'")
                        
                    # 显示前几行上下文作为示例
                    lines = context_str.split('\n')[:3]
                    print(f"上下文示例:")
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
        
        print(f"\n=== 验证结果 ===")
        if all_passed:
            print("🎉 所有测试通过！None ID问题已完全修复！")
            return True
        else:
            print("❌ 仍存在None ID问题")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_fix()
    if success:
        print("\n✅ 修复验证成功！")
    else:
        print("\n❌ 修复验证失败！")