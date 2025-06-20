# -*- coding: utf-8 -*-
"""
导出ChromaDB中所有chap01.txt相关的文段到txt文件
用于核对向量数据库中的数据完整性
"""

import chromadb
import os
from datetime import datetime

def export_chap01_chunks():
    """
    导出ChromaDB中所有来源为chap01.txt的文段
    """
    print("=== 开始导出chap01.txt文段 ===")
    
    # ChromaDB配置
    db_path = "./chroma_db"
    collection_name = "qa_system_chunks"
    
    # 输出文件配置
    output_file = f"chap01_chunks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        # 连接ChromaDB
        print(f"连接ChromaDB: {os.path.abspath(db_path)}")
        client = chromadb.PersistentClient(path=db_path)
        
        # 获取集合
        try:
            collection = client.get_collection(name=collection_name)
            print(f"找到集合: {collection_name}")
        except Exception as e:
            print(f"❌ 集合 '{collection_name}' 不存在: {e}")
            
            # 尝试列出所有可用集合
            collections = client.list_collections()
            if collections:
                print("\n可用的集合:")
                for i, coll in enumerate(collections):
                    print(f"  {i+1}. {coll.name}")
                    
                # 使用第一个集合
                collection = collections[0]
                collection_name = collection.name
                print(f"\n使用集合: {collection_name}")
            else:
                print("❌ 没有找到任何集合")
                return
        
        # 获取集合中的总文档数
        total_count = collection.count()
        print(f"集合中总文档数: {total_count}")
        
        if total_count == 0:
            print("❌ 集合为空")
            return
        
        # 分批获取所有文档（避免内存问题）
        batch_size = 100
        all_chap01_chunks = []
        
        print("\n正在搜索chap01.txt相关文档...")
        
        # 获取所有文档
        offset = 0
        while offset < total_count:
            try:
                # 获取一批文档
                batch = collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=["documents", "metadatas"]
                )
                
                # 筛选chap01.txt相关的文档
                for i, metadata in enumerate(batch['metadatas']):
                    source_file = metadata.get('source_file', '')
                    
                    # 检查是否来源于chap01.txt
                    if 'chap01' in source_file.lower():
                        chunk_data = {
                            'id': batch['ids'][i],
                            'content': batch['documents'][i],
                            'metadata': metadata
                        }
                        all_chap01_chunks.append(chunk_data)
                
                offset += batch_size
                print(f"已处理: {min(offset, total_count)}/{total_count}")
                
            except Exception as e:
                print(f"❌ 获取批次数据失败 (offset={offset}): {e}")
                break
        
        print(f"\n找到 {len(all_chap01_chunks)} 个chap01.txt相关文段")
        
        if not all_chap01_chunks:
            print("❌ 没有找到chap01.txt相关的文段")
            return
        
        # 按chunk_id排序（如果有的话）
        try:
            all_chap01_chunks.sort(key=lambda x: x['id'])
        except:
            print("注意: 无法按ID排序")
        
        # 写入文件
        print(f"\n正在写入文件: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"chap01.txt文段导出报告\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总文段数: {len(all_chap01_chunks)}\n")
            f.write(f"数据库路径: {os.path.abspath(db_path)}\n")
            f.write(f"集合名称: {collection_name}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, chunk in enumerate(all_chap01_chunks, 1):
                f.write(f"【文段 {i}】\n")
                f.write(f"ID: {chunk['id']}\n")
                
                # 写入元数据
                metadata = chunk['metadata']
                f.write(f"来源文件: {metadata.get('source_file', 'N/A')}\n")
                f.write(f"块类型: {metadata.get('chunk_type', 'N/A')}\n")
                
                # 根据不同类型显示不同信息
                chunk_type = metadata.get('chunk_type', '')
                if chunk_type == 'qa_pair':
                    f.write(f"问题: {metadata.get('question', 'N/A')}\n")
                    f.write(f"答案: {metadata.get('answer', 'N/A')}\n")
                    f.write(f"关键词: {metadata.get('keywords', 'N/A')}\n")
                elif chunk_type == 'traditional':
                    f.write(f"开始时间: {metadata.get('start_time', 'N/A')}\n")
                    f.write(f"结束时间: {metadata.get('end_time', 'N/A')}\n")
                    f.write(f"说话人: {metadata.get('speakers', 'N/A')}\n")
                
                f.write(f"字数: {metadata.get('word_count', metadata.get('total_words', 'N/A'))}\n")
                f.write(f"创建时间: {metadata.get('created_at', 'N/A')}\n")
                
                f.write("\n内容:\n")
                f.write(chunk['content'])
                f.write("\n" + "-" * 60 + "\n\n")
        
        print(f"✅ 导出完成!")
        print(f"文件保存为: {os.path.abspath(output_file)}")
        print(f"共导出 {len(all_chap01_chunks)} 个文段")
        
        # 统计信息
        chunk_types = {}
        for chunk in all_chap01_chunks:
            chunk_type = chunk['metadata'].get('chunk_type', 'unknown')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        print("\n文段类型统计:")
        for chunk_type, count in chunk_types.items():
            print(f"  {chunk_type}: {count} 个")
            
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数
    """
    print("ChromaDB chap01.txt文段导出工具")
    print("用于检查向量数据库中chap01.txt的数据完整性")
    print()
    
    export_chap01_chunks()

if __name__ == "__main__":
    main()