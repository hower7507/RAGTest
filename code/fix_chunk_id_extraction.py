# -*- coding: utf-8 -*-
"""
修复chunk_id提取问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chunk_id_extraction():
    """
    测试当前的chunk_id提取逻辑
    """
    print("=== 测试chunk_id提取逻辑 ===")
    
    # 模拟实际的搜索结果
    test_results = [
        {
            'id': 'chap01-1',
            'document_id': 'chap01-1',
            'metadata': {}
        },
        {
            'id': 'chap02-14', 
            'document_id': 'chap02-14',
            'metadata': {}
        },
        {
            'id': 'chunk_1',
            'document_id': 'chunk_1', 
            'metadata': {'chunk_id': 1}
        }
    ]
    
    # 当前的提取逻辑
    def current_extract_chunk_id(result):
        """当前的_extract_chunk_id逻辑"""
        # 尝试从metadata中获取
        metadata = result.get('metadata', {})
        if 'chunk_id' in metadata:
            return metadata['chunk_id']
        
        # 尝试从id中解析（格式：chunk_N）
        result_id = result.get('id', '')
        if isinstance(result_id, str) and result_id.startswith('chunk_'):
            try:
                return int(result_id.split('_')[1])
            except (IndexError, ValueError):
                pass
        
        # 尝试从document_id中获取
        doc_id = result.get('document_id', '')
        if isinstance(doc_id, str) and doc_id.startswith('chunk_'):
            try:
                return int(doc_id.split('_')[1])
            except (IndexError, ValueError):
                pass
        
        return None
    
    # 改进的提取逻辑
    def improved_extract_chunk_id(result):
        """改进的_extract_chunk_id逻辑"""
        # 尝试从metadata中获取
        metadata = result.get('metadata', {})
        if 'chunk_id' in metadata:
            return metadata['chunk_id']
        
        # 尝试从id中解析
        result_id = result.get('id', '')
        if isinstance(result_id, str):
            # 处理 chapXX-N 格式
            if '-' in result_id:
                try:
                    chunk_part = result_id.split('-')[-1]  # 取最后一部分
                    return int(chunk_part)
                except (ValueError, IndexError):
                    pass
            # 处理 chunk_N 格式
            elif result_id.startswith('chunk_'):
                try:
                    return int(result_id.split('_')[1])
                except (IndexError, ValueError):
                    pass
        
        # 尝试从document_id中获取
        doc_id = result.get('document_id', '')
        if isinstance(doc_id, str):
            # 处理 chapXX-N 格式
            if '-' in doc_id:
                try:
                    chunk_part = doc_id.split('-')[-1]  # 取最后一部分
                    return int(chunk_part)
                except (ValueError, IndexError):
                    pass
            # 处理 chunk_N 格式
            elif doc_id.startswith('chunk_'):
                try:
                    return int(doc_id.split('_')[1])
                except (IndexError, ValueError):
                    pass
        
        return None
    
    print("\n测试结果对比:")
    for i, result in enumerate(test_results, 1):
        print(f"\n--- 测试用例 {i} ---")
        print(f"ID: {result.get('id')}")
        print(f"Document ID: {result.get('document_id')}")
        print(f"Metadata: {result.get('metadata')}")
        
        current_result = current_extract_chunk_id(result)
        improved_result = improved_extract_chunk_id(result)
        
        print(f"当前逻辑结果: {current_result}")
        print(f"改进逻辑结果: {improved_result}")
        
        if current_result != improved_result:
            print(f"⚠️  结果不同！当前: {current_result}, 改进: {improved_result}")
        else:
            print("✅ 结果一致")

if __name__ == "__main__":
    test_chunk_id_extraction()