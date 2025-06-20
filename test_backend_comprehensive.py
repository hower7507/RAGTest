# -*- coding: utf-8 -*-
"""
综合测试后端查询系统对chap01和chap02内容的访问能力
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from search_interface import SearchInterface
from vectorize_chunks import ChunkVectorizer

def test_chap01_queries():
    """测试chap01相关查询"""
    
    print("\n=== 测试chap01内容查询 ===")
    
    # chap01相关的测试查询
    chap01_queries = [
        "自然语言处理",
        "机器学习",
        "数据库查询",
        "文本挖掘",
        "深度学习",
        "NLP课程"
    ]
    
    try:
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        if not success:
            print("❌ 搜索系统初始化失败")
            return False
        
        chap01_results_found = 0
        total_queries = len(chap01_queries)
        
        for i, query in enumerate(chap01_queries, 1):
            print(f"\n[{i}/{total_queries}] 查询: '{query}'")
            
            try:
                results = search_interface.search(
                    query=query,
                    top_k=5,
                    return_prompt=False
                )
                
                if results and 'search_results' in results:
                    search_results = results['search_results']
                    print(f"  找到 {len(search_results)} 个结果")
                    
                    chap01_found_in_query = False
                    
                    for j, result in enumerate(search_results[:3]):
                        metadata = result.get('metadata', {})
                        content = result.get('content', '')[:100] + "..."
                        
                        # 检查是否是chap01数据
                        is_chap01 = (
                            ('source' in metadata and 'chap01' in str(metadata['source'])) or
                            ('source_file' in metadata and 'chap01' in str(metadata['source_file']))
                        )
                        
                        if is_chap01:
                            chap01_found_in_query = True
                            print(f"    ✅ 结果{j+1}: chap01数据")
                            print(f"       来源: {metadata.get('source', metadata.get('source_file', 'unknown'))}")
                            print(f"       内容: {content}")
                            print(f"       相似度: {result.get('similarity', result.get('final_score', 'N/A'))}")
                        else:
                            print(f"    ⚪ 结果{j+1}: 其他数据")
                    
                    if chap01_found_in_query:
                        chap01_results_found += 1
                        
                else:
                    print("  未找到结果")
                    
            except Exception as e:
                print(f"  查询出错: {e}")
        
        success_rate = (chap01_results_found / total_queries) * 100
        print(f"\n📊 chap01查询成功率: {chap01_results_found}/{total_queries} ({success_rate:.1f}%)")
        
        return chap01_results_found > 0
        
    except Exception as e:
        print(f"chap01测试过程中出错: {e}")
        return False

def test_chap02_queries():
    """测试chap02相关查询"""
    
    print("\n=== 测试chap02内容查询 ===")
    
    # chap02相关的测试查询
    chap02_queries = [
        "中国AI发展",
        "人工智能创新",
        "商业化",
        "技术探索",
        "人才标准",
        "AI产业"
    ]
    
    try:
        # 初始化搜索接口
        search_interface = SearchInterface(config_name="balanced")
        success = search_interface.initialize()
        
        if not success:
            print("❌ 搜索系统初始化失败")
            return False
        
        chap02_results_found = 0
        total_queries = len(chap02_queries)
        
        for i, query in enumerate(chap02_queries, 1):
            print(f"\n[{i}/{total_queries}] 查询: '{query}'")
            
            try:
                results = search_interface.search(
                    query=query,
                    top_k=5,
                    return_prompt=False
                )
                
                if results and 'search_results' in results:
                    search_results = results['search_results']
                    print(f"  找到 {len(search_results)} 个结果")
                    
                    chap02_found_in_query = False
                    
                    for j, result in enumerate(search_results[:3]):
                        metadata = result.get('metadata', {})
                        content = result.get('content', '')[:100] + "..."
                        
                        # 检查是否是chap02数据
                        is_chap02 = (
                            ('source' in metadata and 'chap02' in str(metadata['source'])) or
                            ('source_file' in metadata and 'chap02' in str(metadata['source_file'])) or
                            ('chunk_type' in metadata and metadata['chunk_type'] == 'qa_pair')
                        )
                        
                        if is_chap02:
                            chap02_found_in_query = True
                            print(f"    ✅ 结果{j+1}: chap02数据")
                            print(f"       来源: {metadata.get('source', metadata.get('source_file', 'unknown'))}")
                            if 'question' in metadata:
                                print(f"       问题: {metadata['question'][:80]}...")
                            if 'keywords' in metadata:
                                print(f"       关键词: {metadata['keywords']}")
                            print(f"       内容: {content}")
                            print(f"       相似度: {result.get('similarity', result.get('final_score', 'N/A'))}")
                        else:
                            print(f"    ⚪ 结果{j+1}: 其他数据")
                    
                    if chap02_found_in_query:
                        chap02_results_found += 1
                        
                else:
                    print("  未找到结果")
                    
            except Exception as e:
                print(f"  查询出错: {e}")
        
        success_rate = (chap02_results_found / total_queries) * 100
        print(f"\n📊 chap02查询成功率: {chap02_results_found}/{total_queries} ({success_rate:.1f}%)")
        
        return chap02_results_found > 0
        
    except Exception as e:
        print(f"chap02测试过程中出错: {e}")
        return False

def test_database_statistics():
    """测试数据库统计信息"""
    
    print("\n=== 数据库统计信息 ===")
    
    try:
        # 创建向量化器
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        # 初始化
        vectorizer.load_model()
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 获取集合信息
        info = vectorizer.get_collection_info()
        
        print(f"集合名称: {info.get('collection_name', 'unknown')}")
        print(f"总记录数: {info.get('total_records', 0)}")
        print(f"示例ID: {info.get('sample_ids', [])[:10]}")
        
        # 统计不同来源的数据
        if info.get('total_records', 0) > 0:
            # 获取所有元数据进行统计
            all_data = vectorizer.collection.get(
                limit=info.get('total_records', 1000),
                include=["metadatas"]
            )
            
            chap01_count = 0
            chap02_count = 0
            other_count = 0
            
            for metadata in all_data.get('metadatas', []):
                if metadata:
                    source = metadata.get('source', metadata.get('source_file', ''))
                    if 'chap01' in str(source):
                        chap01_count += 1
                    elif 'chap02' in str(source) or metadata.get('chunk_type') == 'qa_pair':
                        chap02_count += 1
                    else:
                        other_count += 1
            
            total = chap01_count + chap02_count + other_count
            print(f"\n📊 数据分布:")
            print(f"  chap01数据: {chap01_count} ({(chap01_count/total)*100:.1f}%)")
            print(f"  chap02数据: {chap02_count} ({(chap02_count/total)*100:.1f}%)")
            print(f"  其他数据: {other_count} ({(other_count/total)*100:.1f}%)")
            
            return chap01_count > 0, chap02_count > 0
        
        return False, False
        
    except Exception as e:
        print(f"获取数据库统计信息时出错: {e}")
        return False, False

def main():
    """主测试函数"""
    
    print("🔍 开始综合测试后端查询系统")
    print("=" * 60)
    
    # 1. 测试数据库统计
    has_chap01_data, has_chap02_data = test_database_statistics()
    
    # 2. 测试chap01查询
    chap01_success = False
    if has_chap01_data:
        chap01_success = test_chap01_queries()
    else:
        print("\n⚠️  数据库中未发现chap01数据，跳过chap01查询测试")
    
    # 3. 测试chap02查询
    chap02_success = False
    if has_chap02_data:
        chap02_success = test_chap02_queries()
    else:
        print("\n⚠️  数据库中未发现chap02数据，跳过chap02查询测试")
    
    # 4. 总结报告
    print("\n" + "=" * 60)
    print("📋 综合测试报告")
    print("=" * 60)
    
    print(f"数据库状态:")
    print(f"  ✅ chap01数据存在: {'是' if has_chap01_data else '否'}")
    print(f"  ✅ chap02数据存在: {'是' if has_chap02_data else '否'}")
    
    print(f"\n查询功能测试:")
    if has_chap01_data:
        print(f"  ✅ chap01查询功能: {'正常' if chap01_success else '异常'}")
    if has_chap02_data:
        print(f"  ✅ chap02查询功能: {'正常' if chap02_success else '异常'}")
    
    # 最终结论
    if (has_chap01_data and chap01_success) and (has_chap02_data and chap02_success):
        print("\n🎉 结论: 后端查询系统运行正常，能够正确访问chap01和chap02内容")
    elif (has_chap01_data and chap01_success) or (has_chap02_data and chap02_success):
        print("\n⚠️  结论: 后端查询系统部分正常，部分内容可以正确访问")
    else:
        print("\n❌ 结论: 后端查询系统存在问题，无法正确访问内容")

if __name__ == "__main__":
    main()