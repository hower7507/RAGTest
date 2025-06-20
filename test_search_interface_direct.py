# -*- coding: utf-8 -*-
"""
直接测试搜索接口功能
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface

def test_search_interface():
    """测试搜索接口"""
    
    print("=== 测试搜索接口功能 ===")
    
    try:
        # 创建搜索接口
        print("正在初始化搜索接口...")
        search_interface = SearchInterface()
        
        print("搜索接口初始化完成")
        
        # 测试查询
        test_queries = [
            "自然语言处理",
            "机器学习", 
            "中国AI发展",
            "人工智能创新"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            
            try:
                # 使用搜索接口搜索
                result = search_interface.search(
                    query=query,
                    top_k=3,
                    return_prompt=False
                )
                
                if 'error' in result:
                    print(f"  ❌ 搜索出错: {result['error']}")
                    continue
                
                print(f"  ✅ 找到 {result.get('total_results', 0)} 个结果")
                print(f"  搜索时间: {result.get('search_time', 0):.2f}秒")
                print(f"  候选文档数: {result.get('total_candidates', 0)}")
                
                # 显示结果详情
                for i, res in enumerate(result.get('results', [])):
                    print(f"    结果{i+1}:")
                    print(f"      ID: {res.get('document_id', 'unknown')}")
                    print(f"      得分: {res.get('score', 0):.3f}")
                    print(f"      内容: {res.get('content', '')[:80]}...")
                    
                    metadata = res.get('metadata', {})
                    if metadata:
                        # 检查数据来源
                        source = metadata.get('source_file', metadata.get('source', 'unknown'))
                        chunk_type = metadata.get('chunk_type', 'unknown')
                        print(f"      来源: {source}")
                        print(f"      类型: {chunk_type}")
                        
                        if 'question' in metadata:
                            print(f"      问题: {metadata['question'][:50]}...")
                        if 'start_time' in metadata:
                            print(f"      时间: {metadata.get('start_time', '')} - {metadata.get('end_time', '')}")
                        if 'word_count' in metadata:
                            print(f"      字数: {metadata['word_count']}")
                    print()
                    
            except Exception as e:
                print(f"  ❌ 搜索出错: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"测试搜索接口时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_interface_initialization():
    """测试搜索接口初始化过程"""
    
    print("\n=== 测试搜索接口初始化 ===")
    
    try:
        # 创建搜索接口并观察初始化过程
        print("正在创建搜索接口实例...")
        search_interface = SearchInterface()
        
        # 检查各个组件是否正确初始化
        print(f"配置加载: {'✅' if hasattr(search_interface, 'config') else '❌'}")
        print(f"向量化器: {'✅' if hasattr(search_interface, 'vectorizer') and search_interface.vectorizer else '❌'}")
        print(f"搜索系统: {'✅' if hasattr(search_interface, 'search_system') and search_interface.search_system else '❌'}")
        
        # 检查数据库连接
        if hasattr(search_interface, 'vectorizer') and search_interface.vectorizer:
            if hasattr(search_interface.vectorizer, 'collection') and search_interface.vectorizer.collection:
                info = search_interface.vectorizer.get_collection_info()
                print(f"数据库连接: ✅ (共{info.get('total_records', 0)}条记录)")
            else:
                print(f"数据库连接: ❌")
        
        return True
        
    except Exception as e:
        print(f"测试初始化时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_search():
    """测试快速搜索功能"""
    
    print("\n=== 测试快速搜索功能 ===")
    
    try:
        # 创建搜索接口
        search_interface = SearchInterface()
        
        # 测试快速搜索
        test_queries = ["自然语言处理", "机器学习"]
        
        for query in test_queries:
            print(f"\n🔍 快速搜索: '{query}'")
            
            try:
                result = search_interface.quick_search(query, top_k=2)
                print(f"结果: {result[:200]}..." if len(result) > 200 else f"结果: {result}")
                
            except Exception as e:
                print(f"  ❌ 快速搜索出错: {e}")
        
        return True
        
    except Exception as e:
        print(f"测试快速搜索时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 测试初始化
    init_success = test_search_interface_initialization()
    
    if init_success:
        # 测试搜索功能
        search_success = test_search_interface()
        
        # 测试快速搜索
        quick_search_success = test_quick_search()
        
        print(f"\n=== 测试总结 ===")
        print(f"初始化测试: {'✅ 成功' if init_success else '❌ 失败'}")
        print(f"搜索功能测试: {'✅ 成功' if search_success else '❌ 失败'}")
        print(f"快速搜索测试: {'✅ 成功' if quick_search_success else '❌ 失败'}")
    else:
        print("\n❌ 初始化失败，跳过其他测试")