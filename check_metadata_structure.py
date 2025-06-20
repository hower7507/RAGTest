# -*- coding: utf-8 -*-
"""
检查数据库中的元数据结构
"""

import sys
import os
sys.path.append('e:\\PyProjects\\QASystem\\code')

from vectorize_chunks import ChunkVectorizer

def check_metadata_structure():
    """检查数据库中的元数据结构"""
    
    print("=== 检查数据库元数据结构 ===")
    
    try:
        # 初始化向量化器
        vectorizer = ChunkVectorizer(
            model_name="BAAI/bge-small-zh-v1.5",
            collection_name="qa_system_chunks"
        )
        
        vectorizer.load_model()
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 获取集合信息
        info = vectorizer.get_collection_info()
        print(f"集合名称: {info.get('collection_name', 'unknown')}")
        print(f"总记录数: {info.get('total_records', 0)}")
        
        # 获取前10个文档的元数据
        print("\n=== 前10个文档的元数据结构 ===")
        
        sample_data = vectorizer.collection.get(
            limit=10,
            include=["metadatas", "documents"]
        )
        
        if sample_data and 'metadatas' in sample_data:
            metadatas = sample_data['metadatas']
            documents = sample_data.get('documents', [])
            
            for i, (metadata, doc) in enumerate(zip(metadatas, documents)):
                print(f"\n--- 文档 {i+1} ---")
                print(f"内容长度: {len(doc) if doc else 0}")
                print(f"内容预览: {doc[:100] if doc else 'N/A'}...")
                
                if metadata:
                    print(f"元数据键: {list(metadata.keys())}")
                    
                    # 检查时间相关字段
                    time_fields = ['start_time', 'end_time', 'start_timestamp', 'end_timestamp']
                    print(f"时间字段:")
                    for field in time_fields:
                        if field in metadata:
                            print(f"  {field}: {metadata[field]} (类型: {type(metadata[field])})")
                        else:
                            print(f"  {field}: 不存在")
                    
                    # 检查其他重要字段
                    other_fields = ['source', 'source_file', 'chunk_type', 'question', 'answer']
                    print(f"其他字段:")
                    for field in other_fields:
                        if field in metadata:
                            value = metadata[field]
                            if isinstance(value, str) and len(value) > 50:
                                value = value[:50] + "..."
                            print(f"  {field}: {value} (类型: {type(metadata[field])})")
                        else:
                            print(f"  {field}: 不存在")
                else:
                    print(f"元数据: None")
        
        # 统计不同类型的元数据
        print("\n=== 元数据类型统计 ===")
        
        all_data = vectorizer.collection.get(
            limit=info.get('total_records', 1000),
            include=["metadatas"]
        )
        
        if all_data and 'metadatas' in all_data:
            metadatas = all_data['metadatas']
            
            # 统计字段出现频率
            field_counts = {}
            time_field_counts = {}
            
            for metadata in metadatas:
                if metadata:
                    for key in metadata.keys():
                        field_counts[key] = field_counts.get(key, 0) + 1
                        
                        # 特别统计时间字段
                        if key in ['start_time', 'end_time', 'start_timestamp', 'end_timestamp']:
                            time_field_counts[key] = time_field_counts.get(key, 0) + 1
            
            print(f"\n所有字段出现频率:")
            for field, count in sorted(field_counts.items()):
                percentage = (count / len(metadatas)) * 100
                print(f"  {field}: {count}/{len(metadatas)} ({percentage:.1f}%)")
            
            print(f"\n时间字段详细统计:")
            for field, count in sorted(time_field_counts.items()):
                percentage = (count / len(metadatas)) * 100
                print(f"  {field}: {count}/{len(metadatas)} ({percentage:.1f}%)")
            
            # 检查时间字段的实际值
            print(f"\n时间字段值示例:")
            for field in ['start_time', 'end_time', 'start_timestamp', 'end_timestamp']:
                values = []
                for metadata in metadatas[:20]:  # 只检查前20个
                    if metadata and field in metadata:
                        values.append(metadata[field])
                
                if values:
                    print(f"  {field} 示例值: {values[:5]}")
                    print(f"  {field} 值类型: {[type(v) for v in values[:3]]}")
        
    except Exception as e:
        print(f"❌ 检查元数据结构失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    
    print("🔍 开始检查数据库元数据结构")
    print("=" * 60)
    
    check_metadata_structure()
    
    print("\n" + "=" * 60)
    print("📋 元数据结构检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()