#!/usr/bin/env python3
"""
导出会话数据库中所有集合的内容到单独的文本文件
"""

import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
import json

def export_collection_to_file(collection, collection_name, output_dir):
    """
    导出单个集合的内容到文本文件
    
    Args:
        collection: ChromaDB集合对象
        collection_name: 集合名称
        output_dir: 输出目录
    """
    try:
        # 获取集合中的所有数据
        results = collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
        
        # 创建输出文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_collection_{collection_name}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== 会话数据库集合: {collection_name} ===\n")
            f.write(f"导出时间: {datetime.now().isoformat()}\n")
            f.write(f"总文档数: {len(results['ids'])}\n")
            f.write("=" * 80 + "\n\n")
            
            if len(results['ids']) == 0:
                f.write("该集合为空\n")
                return filepath
            
            # 导出每个文档
            for i, doc_id in enumerate(results['ids']):
                f.write(f"--- 文档 {i+1}: {doc_id} ---\n")
                
                # 文档内容
                if results['documents'] and i < len(results['documents']):
                    content = results['documents'][i]
                    f.write(f"内容: {content}\n")
                
                # 元数据
                if results['metadatas'] and i < len(results['metadatas']):
                    metadata = results['metadatas'][i]
                    f.write(f"元数据: {json.dumps(metadata, ensure_ascii=False, indent=2)}\n")
                
                # 向量维度信息（不输出具体向量值，太长）
                if results['embeddings'] and i < len(results['embeddings']):
                    embedding = results['embeddings'][i]
                    if embedding:
                        f.write(f"向量维度: {len(embedding)}\n")
                
                f.write("\n" + "-" * 60 + "\n\n")
            
            # 统计信息
            f.write("\n=== 统计信息 ===\n")
            
            # 元数据统计
            if results['metadatas']:
                metadata_keys = set()
                for metadata in results['metadatas']:
                    if metadata:
                        metadata_keys.update(metadata.keys())
                
                f.write(f"元数据字段: {sorted(list(metadata_keys))}\n")
                
                # 统计每个字段的唯一值
                for key in sorted(metadata_keys):
                    values = set()
                    for metadata in results['metadatas']:
                        if metadata and key in metadata:
                            values.add(str(metadata[key]))
                    f.write(f"  {key}: {len(values)} 个唯一值\n")
                    if len(values) <= 10:  # 如果唯一值不多，列出来
                        f.write(f"    值: {sorted(list(values))}\n")
        
        print(f"✅ 集合 {collection_name} 已导出到: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ 导出集合 {collection_name} 失败: {e}")
        return None

def main():
    """
    主函数：导出会话数据库中所有集合
    """
    # 会话数据库路径
    session_db_path = "./chroma_db"
    
    if not os.path.exists(session_db_path):
        print(f"❌ 会话数据库路径不存在: {session_db_path}")
        return
    
    try:
        # 连接到会话数据库
        client = chromadb.PersistentClient(
            path=session_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取所有集合
        collections = client.list_collections()
        print(f"找到 {len(collections)} 个集合")
        
        if len(collections) == 0:
            print("会话数据库中没有集合")
            return
        
        # 创建输出目录
        output_dir = "./session_collections_export"
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = []
        
        # 导出每个集合
        for collection_info in collections:
            collection_name = collection_info.name
            print(f"正在导出集合: {collection_name}")
            
            try:
                collection = client.get_collection(collection_name)
                filepath = export_collection_to_file(collection, collection_name, output_dir)
                if filepath:
                    exported_files.append(filepath)
            except Exception as e:
                print(f"❌ 处理集合 {collection_name} 时出错: {e}")
        
        # 创建总结报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(output_dir, f"export_summary_{timestamp}.txt")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=== 会话数据库集合导出总结 ===\n")
            f.write(f"导出时间: {datetime.now().isoformat()}\n")
            f.write(f"数据库路径: {os.path.abspath(session_db_path)}\n")
            f.write(f"总集合数: {len(collections)}\n")
            f.write(f"成功导出: {len(exported_files)} 个文件\n")
            f.write("\n导出的文件列表:\n")
            for filepath in exported_files:
                f.write(f"  - {os.path.basename(filepath)}\n")
        
        print(f"\n✅ 导出完成！")
        print(f"导出目录: {os.path.abspath(output_dir)}")
        print(f"总结报告: {summary_file}")
        print(f"导出文件数: {len(exported_files)}")
        
    except Exception as e:
        print(f"❌ 导出过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()