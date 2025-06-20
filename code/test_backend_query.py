# -*- coding: utf-8 -*-
"""
测试后台查询功能
模拟实际查询过程，诊断查询问题
"""

import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer

def test_direct_chromadb_query():
    """
    直接测试ChromaDB查询
    """
    print("=" * 80)
    print("🔍 直接测试ChromaDB查询")
    print("=" * 80)
    
    try:
        # 初始化向量化器
        vectorizer = ChunkVectorizer(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            collection_name="qa_system_chunks"
        )
        
        # 连接到主数据库
        main_db_path = "e:\\PyProjects\\QASystem\\chroma_db"
        vectorizer.init_chromadb(main_db_path)
        
        print(f"✅ 成功连接到数据库: {main_db_path}")
        
        # 获取集合信息
        info = vectorizer.get_collection_info()
        print(f"📊 集合信息: {info}")
        
        # 测试简单查询
        print("\n🔍 测试简单查询...")
        test_queries = [
            "自然语言处理",
            "机器学习",
            "深度学习",
            "人工智能",
            "数据挖掘"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            try:
                # 直接使用ChromaDB查询
                results = vectorizer.collection.query(
                    query_texts=[query],
                    n_results=5,
                    include=["documents", "metadatas", "distances"]
                )
                
                if results and 'documents' in results and results['documents'][0]:
                    print(f"  ✅ 找到 {len(results['documents'][0])} 个结果")
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0][:3],  # 只显示前3个
                        results['metadatas'][0][:3],
                        results['distances'][0][:3]
                    )):
                        print(f"    结果 {i+1}:")
                        print(f"      距离: {distance:.4f}")
                        print(f"      内容: {doc[:50]}...")
                        print(f"      来源: {metadata.get('source', 'unknown')}")
                        print(f"      类型: {metadata.get('chunk_type', 'unknown')}")
                else:
                    print(f"  ❌ 没有找到结果")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 直接ChromaDB测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_interface():
    """
    测试搜索接口
    """
    print("\n" + "=" * 80)
    print("🔍 测试搜索接口")
    print("=" * 80)
    
    try:
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        
        # 初始化
        if not search_interface.initialize():
            print("❌ 搜索接口初始化失败")
            return False
        
        print("✅ 搜索接口初始化成功")
        
        # 测试查询
        test_queries = [
            "自然语言处理是什么",
            "机器学习算法",
            "深度学习模型",
            "人工智能应用"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            try:
                result = search_interface.search(
                    query=query,
                    top_k=5,
                    return_prompt=False
                )
                
                if 'error' in result:
                    print(f"  ❌ 查询错误: {result['error']}")
                elif result.get('total_results', 0) > 0:
                    print(f"  ✅ 找到 {result['total_results']} 个结果")
                    print(f"  🕐 搜索时间: {result.get('search_time', 0):.3f}秒")
                    print(f"  📊 候选文档: {result.get('total_candidates', 0)}")
                    
                    # 显示前3个结果
                    for i, res in enumerate(result['results'][:3]):
                        print(f"    结果 {i+1}:")
                        print(f"      得分: {res.get('score', 0):.4f}")
                        print(f"      内容: {res['content'][:50]}...")
                        metadata = res.get('metadata', {})
                        print(f"      来源: {metadata.get('source', metadata.get('source_file', 'unknown'))}")
                        print(f"      类型: {metadata.get('chunk_type', 'unknown')}")
                else:
                    print(f"  ❌ 没有找到结果")
                    print(f"  详细信息: {result}")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_metadata_query():
    """
    测试特定元数据查询
    """
    print("\n" + "=" * 80)
    print("🔍 测试特定元数据查询")
    print("=" * 80)
    
    try:
        # 初始化向量化器
        vectorizer = ChunkVectorizer(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            collection_name="qa_system_chunks"
        )
        
        # 连接到主数据库
        main_db_path = "e:\\PyProjects\\QASystem\\chroma_db"
        vectorizer.init_chromadb(main_db_path)
        
        # 测试按来源过滤
        print("\n🔍 测试按来源过滤...")
        sources_to_test = ['chap01.txt', 'chap02.txt']
        
        for source in sources_to_test:
            print(f"\n查找来源为 '{source}' 的文档:")
            try:
                # 使用where条件查询
                results = vectorizer.collection.get(
                    where={"source": source},
                    limit=10,
                    include=["documents", "metadatas"]
                )
                
                if results and 'documents' in results and results['documents']:
                    print(f"  ✅ 找到 {len(results['documents'])} 个结果")
                    for i, (doc, metadata) in enumerate(zip(
                        results['documents'][:3],
                        results['metadatas'][:3]
                    )):
                        print(f"    文档 {i+1}:")
                        print(f"      内容: {doc[:50]}...")
                        print(f"      来源: {metadata.get('source', 'unknown')}")
                        print(f"      类型: {metadata.get('chunk_type', 'unknown')}")
                        print(f"      字数: {metadata.get('word_count', 'unknown')}")
                else:
                    print(f"  ❌ 没有找到来源为 '{source}' 的文档")
                    
                # 尝试使用source_file字段
                print(f"  尝试使用source_file字段查找 '{source}':")
                results2 = vectorizer.collection.get(
                    where={"source_file": source},
                    limit=10,
                    include=["documents", "metadatas"]
                )
                
                if results2 and 'documents' in results2 and results2['documents']:
                    print(f"    ✅ 通过source_file找到 {len(results2['documents'])} 个结果")
                else:
                    print(f"    ❌ 通过source_file也没有找到结果")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {e}")
        
        # 测试按类型过滤
        print("\n🔍 测试按类型过滤...")
        chunk_types = ['general_text', 'qa_pair', 'traditional']
        
        for chunk_type in chunk_types:
            print(f"\n查找类型为 '{chunk_type}' 的文档:")
            try:
                results = vectorizer.collection.get(
                    where={"chunk_type": chunk_type},
                    limit=5,
                    include=["documents", "metadatas"]
                )
                
                if results and 'documents' in results and results['documents']:
                    print(f"  ✅ 找到 {len(results['documents'])} 个结果")
                else:
                    print(f"  ❌ 没有找到类型为 '{chunk_type}' 的文档")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 元数据查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    主测试函数
    """
    print(f"🚀 开始后台查询测试")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试1: 直接ChromaDB查询
    success1 = test_direct_chromadb_query()
    
    # 测试2: 搜索接口
    success2 = test_search_interface()
    
    # 测试3: 特定元数据查询
    success3 = test_specific_metadata_query()
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    print(f"直接ChromaDB查询: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"搜索接口测试: {'✅ 成功' if success2 else '❌ 失败'}")
    print(f"元数据查询测试: {'✅ 成功' if success3 else '❌ 失败'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息")

if __name__ == "__main__":
    main()