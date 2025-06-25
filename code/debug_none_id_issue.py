# -*- coding: utf-8 -*-
"""
调试None ID问题的完整测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search_interface import SearchInterface
from context_manager import ContextManager
from multi_stage_query import MultiStageQuerySystem
from dimension_analyzer import DimensionAnalyzer

def debug_none_id_issue():
    """
    调试None ID问题的完整流程
    """
    print("=== 调试None ID问题 ===")
    
    try:
        # 1. 初始化搜索接口
        print("\n1. 初始化搜索接口...")
        search_interface = SearchInterface()
        if not search_interface.initialize():
            print("❌ 搜索接口初始化失败")
            return
        
        # 2. 执行搜索
        print("\n2. 执行搜索...")
        test_query = "测试"
        search_result = search_interface.search(test_query, top_k=5)
        
        print(f"搜索结果类型: {type(search_result)}")
        print(f"搜索结果键: {search_result.keys() if isinstance(search_result, dict) else 'N/A'}")
        
        if 'results' in search_result:
            results = search_result['results']
            print(f"\n找到 {len(results)} 个结果")
            
            # 检查每个结果的ID
            for i, result in enumerate(results):
                print(f"\n--- 结果 {i+1} ---")
                print(f"结果类型: {type(result)}")
                print(f"结果键: {result.keys() if isinstance(result, dict) else 'N/A'}")
                
                # 检查document_id字段
                document_id = result.get('document_id')
                print(f"document_id: {document_id} (类型: {type(document_id)})")
                
                # 检查原始id字段
                if 'id' in result:
                    print(f"原始id: {result['id']} (类型: {type(result['id'])})")
                
                # 检查metadata
                metadata = result.get('metadata', {})
                print(f"metadata键: {metadata.keys() if isinstance(metadata, dict) else 'N/A'}")
                
                if document_id is None or str(document_id).lower() == 'none':
                    print(f"⚠️  发现None ID在结果 {i+1}")
                    print(f"完整结果: {result}")
        
        # 3. 测试多阶段查询系统
        print("\n\n3. 测试多阶段查询系统...")
        dimension_analyzer = DimensionAnalyzer()
        multi_stage_query = MultiStageQuerySystem(search_interface)
        
        dimension_result = dimension_analyzer.analyze_query_dimensions(test_query)
        multi_stage_result = multi_stage_query.multi_stage_search(
            query=test_query,
            max_results=5,
            dimension_analysis=dimension_result
        )
        
        print(f"多阶段搜索结果类型: {type(multi_stage_result)}")
        
        if isinstance(multi_stage_result, dict) and 'results' in multi_stage_result:
            ms_results = multi_stage_result['results']
            print(f"多阶段搜索找到 {len(ms_results)} 个结果")
            
            for i, result in enumerate(ms_results):
                print(f"\n--- 多阶段结果 {i+1} ---")
                result_id = result.get('id')
                document_id = result.get('document_id')
                print(f"id: {result_id} (类型: {type(result_id)})")
                print(f"document_id: {document_id} (类型: {type(document_id)})")
                
                if result_id is None or document_id is None:
                    print(f"⚠️  发现None ID在多阶段结果 {i+1}")
                    print(f"完整结果: {result}")
        
        # 4. 测试上下文管理器
        print("\n\n4. 测试上下文管理器...")
        # 获取搜索系统和collection
        search_system = search_interface.search_system
        collection = search_interface.vectorizer.collection
        context_manager = ContextManager(search_system, collection)
        
        # 使用多阶段搜索的结果
        if isinstance(multi_stage_result, dict) and 'results' in multi_stage_result:
            context_result = context_manager.process_search_results(
                query=test_query,
                search_results=multi_stage_result['results'],
                max_results=5
            )
            
            print(f"上下文处理结果类型: {type(context_result)}")
            
            if isinstance(context_result, dict):
                processed_results = context_result.get('processed_results', [])
                print(f"处理后结果数量: {len(processed_results)}")
                
                for i, result in enumerate(processed_results):
                    print(f"\n--- 处理后结果 {i+1} ---")
                    result_id = result.get('id')
                    document_id = result.get('document_id')
                    print(f"id: {result_id} (类型: {type(result_id)})")
                    print(f"document_id: {document_id} (类型: {type(document_id)})")
                    
                    if result_id is None or document_id is None:
                        print(f"⚠️  发现None ID在处理后结果 {i+1}")
                        print(f"完整结果: {result}")
                
                # 检查上下文字符串中的None引用
                context_str = context_result.get('context', '')
                if 'None' in context_str:
                    print(f"\n⚠️  上下文字符串中包含'None'")
                    # 找到包含None的行
                    lines = context_str.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if 'None' in line:
                            print(f"第{line_num}行: {line}")
        
        print("\n=== 调试完成 ===")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_none_id_issue()