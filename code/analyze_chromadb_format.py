# -*- coding: utf-8 -*-
"""
分析ChromaDB中的数据格式和集合分布
"""

import chromadb
import os
from collections import Counter

def analyze_chromadb_format():
    """
    分析ChromaDB中的数据格式
    """
    print("=== ChromaDB数据格式分析 ===")
    
    # ChromaDB配置
    db_path = "./chroma_db"
    
    try:
        # 连接ChromaDB
        print(f"连接ChromaDB: {os.path.abspath(db_path)}")
        client = chromadb.PersistentClient(path=db_path)
        
        # 列出所有集合
        collections = client.list_collections()
        print(f"\n总集合数: {len(collections)}")
        
        for collection in collections:
            print(f"\n{'='*60}")
            print(f"集合名称: {collection.name}")
            
            count = collection.count()
            print(f"文档总数: {count}")
            
            if count == 0:
                print("集合为空")
                continue
            
            # 获取样本数据进行分析
            sample_size = min(50, count)
            sample = collection.get(
                limit=sample_size,
                include=["documents", "metadatas"]
            )
            
            # 分析数据来源
            source_files = []
            chunk_types = []
            
            for metadata in sample['metadatas']:
                source_file = metadata.get('source_file', 'unknown')
                chunk_type = metadata.get('chunk_type', 'unknown')
                source_files.append(source_file)
                chunk_types.append(chunk_type)
            
            # 统计来源文件
            source_counter = Counter(source_files)
            print("\n📁 数据来源分布:")
            for source, count in source_counter.most_common():
                print(f"  {source}: {count} 个文档")
            
            # 统计块类型
            type_counter = Counter(chunk_types)
            print("\n📊 数据类型分布:")
            for chunk_type, count in type_counter.most_common():
                print(f"  {chunk_type}: {count} 个文档")
            
            # 显示示例文档
            print("\n📄 示例文档:")
            for i in range(min(3, len(sample['ids']))):
                doc_id = sample['ids'][i]
                content = sample['documents'][i]
                metadata = sample['metadatas'][i]
                
                print(f"\n  文档 {i+1}:")
                print(f"    ID: {doc_id}")
                print(f"    来源: {metadata.get('source_file', 'N/A')}")
                print(f"    类型: {metadata.get('chunk_type', 'N/A')}")
                print(f"    内容: {content[:100]}...")
                
                # 显示特定类型的元数据
                chunk_type = metadata.get('chunk_type', '')
                if chunk_type == 'qa_pair':
                    print(f"    问题: {metadata.get('question', 'N/A')[:50]}...")
                    print(f"    答案: {metadata.get('answer', 'N/A')[:50]}...")
                elif chunk_type == 'traditional':
                    print(f"    时间: {metadata.get('start_time', 'N/A')} - {metadata.get('end_time', 'N/A')}")
                    print(f"    说话人: {metadata.get('speakers', 'N/A')}")
                elif chunk_type == 'general_text':
                    print(f"    字数: {metadata.get('word_count', 'N/A')}")
            
            # 检查chap01和chap02的分布
            print("\n🔍 章节数据分析:")
            chap01_count = sum(1 for sf in source_files if 'chap01' in sf.lower())
            chap02_count = sum(1 for sf in source_files if 'chap02' in sf.lower())
            
            print(f"  chap01相关文档: {chap01_count} 个")
            print(f"  chap02相关文档: {chap02_count} 个")
            
            if chap01_count > 0 and chap02_count > 0:
                print("  ✅ chap01和chap02存储在同一个集合中")
            elif chap01_count > 0:
                print("  📝 只有chap01数据")
            elif chap02_count > 0:
                print("  📝 只有chap02数据")
            else:
                print("  ❌ 没有找到chap01或chap02数据")
        
        # 总结
        print(f"\n{'='*60}")
        print("📋 总结:")
        print(f"  - 总集合数: {len(collections)}")
        if collections:
            main_collection = collections[0]
            total_docs = main_collection.count()
            print(f"  - 主集合: {main_collection.name}")
            print(f"  - 总文档数: {total_docs}")
            
            # 获取所有文档的来源统计
            if total_docs > 0:
                all_sample = main_collection.get(
                    limit=min(1000, total_docs),
                    include=["metadatas"]
                )
                all_sources = [m.get('source_file', 'unknown') for m in all_sample['metadatas']]
                all_source_counter = Counter(all_sources)
                
                chap01_total = sum(count for source, count in all_source_counter.items() if 'chap01' in source.lower())
                chap02_total = sum(count for source, count in all_source_counter.items() if 'chap02' in source.lower())
                
                print(f"  - chap01总文档数: {chap01_total}")
                print(f"  - chap02总文档数: {chap02_total}")
                
                if chap01_total > 0 and chap02_total > 0:
                    print("  ✅ chap01和chap02确实存储在同一个集合中")
                    
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数
    """
    analyze_chromadb_format()

if __name__ == "__main__":
    main()