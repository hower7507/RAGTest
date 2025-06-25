#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问答对系统演示脚本
展示从文档处理到向量化存储再到查询的完整流程
"""

from qa_document_processor import QADocumentProcessor
from vectorize_chunks import ChunkVectorizer
import os

def demo_complete_qa_workflow():
    """
    演示完整的问答对处理工作流程
    """
    print("=== 问答对系统完整演示 ===")
    
    # 步骤1: 处理问答对文档
    print("\n步骤1: 处理问答对文档")
    print("-" * 40)
    
    qa_file = "e:\\PyProjects\\QASystem\\data\\chap02.txt"
    processor = QADocumentProcessor(qa_file)
    
    # 处理文档并生成chunks
    chunks = processor.process_document(save_output=True)
    
    if not chunks:
        print("文档处理失败，退出演示")
        return
    
    print(f"✓ 成功处理 {len(chunks)} 个问答对")
    
    # 步骤2: 向量化和存储
    print("\n步骤2: 向量化和存储到ChromaDB")
    print("-" * 40)
    
    # 创建向量化器 - 使用后端相同的配置
    vectorizer = ChunkVectorizer(
        model_name="e:\\PyProjects\\QASystem\\code\\model",
        collection_name="qa_system_chunks"  # 使用后端相同的集合名称
    )
    
    # 向量化并存储 - 直接存储到后端使用的ChromaDB
    processed_file = qa_file.replace('.txt', '_qa_processed.json')
    success = vectorizer.process_and_store(
        json_file_path=processed_file,
        persist_directory="e:\\PyProjects\\QASystem\\chroma_db"  # 使用后端相同的数据库路径
    )
    
    if not success:
        print("向量化失败，退出演示")
        return
    
    print("✓ 向量化和存储完成")
    
    # 步骤3: 演示查询功能
    print("\n步骤3: 演示查询功能")
    print("-" * 40)
    
    # 定义测试查询
    test_queries = [
        {
            "query": "中国AI发展",
            "description": "查询中国AI发展相关内容"
        },
        {
            "query": "创新和商业化",
            "description": "查询创新与商业化的关系"
        },
        {
            "query": "人才标准",
            "description": "查询人才招聘和选择标准"
        },
        {
            "query": "技术探索",
            "description": "查询技术探索和研究方向"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n查询 {i}: {test_case['description']}")
        print(f"查询词: '{test_case['query']}'")
        
        results = vectorizer.search_similar_chunks(
            query_text=test_case['query'],
            n_results=2
        )
        
        if results and 'documents' in results and results['documents'][0]:
            for j, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"\n  结果 {j+1}:")
                print(f"    问题: {metadata.get('question', 'N/A')[:60]}...")
                print(f"    答案预览: {metadata.get('answer', 'N/A')[:80]}...")
                print(f"    关键词: {metadata.get('keywords', 'N/A')}")
                print(f"    相似度: {results['distances'][0][j]:.4f}")
        else:
            print("    未找到相关结果")
    
    # 步骤4: 展示系统特点
    print("\n步骤4: 系统特点总结")
    print("-" * 40)
    
    print("✓ 特点1: 一个问答对一个chunk，保持语义完整性")
    print("✓ 特点2: 自动提取关键词标签，增强检索效果")
    print("✓ 特点3: 无需修改现有查询逻辑，兼容性好")
    print("✓ 特点4: 支持语义搜索，能理解查询意图")
    print("✓ 特点5: 元数据丰富，支持多维度检索")
    
    # 步骤5: 数据统计
    print("\n步骤5: 数据统计")
    print("-" * 40)
    
    collection_info = vectorizer.get_collection_info()
    print(f"集合名称: {collection_info.get('collection_name', 'unknown')}")
    print(f"总记录数: {collection_info.get('total_records', 0)}")
    print(f"示例ID: {collection_info.get('sample_ids', [])[:3]}")
    
    # 关键词统计
    print("\n关键词分布:")
    all_keywords = []
    for chunk in chunks:
        all_keywords.extend(chunk.get('keywords', []))
    
    from collections import Counter
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(10)
    
    for keyword, count in top_keywords:
        print(f"  {keyword}: {count}次")
    
    print("\n=== 演示完成 ===")
    print("\n系统已准备就绪，可以开始使用问答对检索功能！")

def demo_simple_search():
    """
    简单的搜索演示
    """
    print("\n=== 简单搜索演示 ===")
    
    # 创建向量化器（假设数据已经存在）- 使用后端相同配置
    vectorizer = ChunkVectorizer(
        model_name="e:\\PyProjects\\QASystem\\code\\model",
        collection_name="qa_system_chunks"  # 使用后端相同的集合名称
    )
    
    # 初始化 - 使用后端相同的数据库路径
    vectorizer.load_model()
    vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
    
    # 交互式搜索
    print("\n输入查询词进行搜索（输入'quit'退出）:")
    
    while True:
        query = input("\n请输入查询: ").strip()
        
        if query.lower() in ['quit', 'exit', '退出', 'q']:
            break
        
        if not query:
            continue
        
        print(f"\n搜索: '{query}'")
        results = vectorizer.search_similar_chunks(
            query_text=query,
            n_results=3
        )
        
        if results and 'documents' in results and results['documents'][0]:
            print(f"找到 {len(results['documents'][0])} 个相关结果:")
            
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"\n结果 {i+1}:")
                print(f"问题: {metadata.get('question', 'N/A')}")
                print(f"答案: {metadata.get('answer', 'N/A')[:100]}...")
                print(f"关键词: {metadata.get('keywords', 'N/A')}")
                print(f"相似度: {results['distances'][0][i]:.4f}")
        else:
            print("未找到相关结果")
    
    print("搜索演示结束")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        # 只运行搜索演示
        demo_simple_search()
    else:
        # 运行完整演示
        demo_complete_qa_workflow()