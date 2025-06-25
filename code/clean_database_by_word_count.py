#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库清理脚本
删除word_count字段小于15的数据，并对chunk_id进行重新编号
"""

import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
import json
import re

def clean_database_by_word_count():
    """
    清理数据库：删除word_count < 15的数据，重新编号chunk_id
    """
    # 主数据库路径
    main_db_path = "e:\\PyProjects\\QASystem\\chroma_db"
    
    print(f"🧹 开始清理数据库: {main_db_path}")
    print(f"📅 清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if not os.path.exists(main_db_path):
        print(f"❌ 数据库路径不存在: {main_db_path}")
        return False
    
    try:
        # 连接到主数据库
        client = chromadb.PersistentClient(
            path=main_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取qa_system_chunks集合
        try:
            collection = client.get_collection("qa_system_chunks")
            print(f"✅ 成功连接到集合: qa_system_chunks")
        except Exception as e:
            print(f"❌ 无法获取集合qa_system_chunks: {e}")
            return False
        
        # 获取集合基本信息
        original_count = collection.count()
        print(f"📊 原始文档总数: {original_count}")
        
        if original_count == 0:
            print("⚠️  集合为空，没有文档需要清理")
            return True
        
        # 获取所有文档数据
        print("📥 获取所有文档数据...")
        all_results = collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
        
        print(f"📋 获取到 {len(all_results['documents'])} 个文档")
        
        # 分析需要删除的文档
        documents_to_keep = []
        metadatas_to_keep = []
        embeddings_to_keep = []
        ids_to_keep = []
        
        deleted_count = 0
        kept_count = 0
        
        print("🔍 分析文档，筛选word_count >= 15的数据...")
        
        for i, (doc_id, document, metadata, embedding) in enumerate(zip(
            all_results['ids'],
            all_results['documents'], 
            all_results['metadatas'],
            all_results['embeddings']
        )):
            # 检查word_count字段
            word_count = metadata.get('word_count', 0) if metadata else 0
            
            # 如果word_count是字符串，转换为整数
            if isinstance(word_count, str):
                try:
                    word_count = int(word_count)
                except ValueError:
                    word_count = 0
            
            # 保留word_count >= 15的文档
            if word_count >= 15:
                documents_to_keep.append(document)
                metadatas_to_keep.append(metadata)
                embeddings_to_keep.append(embedding)
                ids_to_keep.append(doc_id)
                kept_count += 1
            else:
                deleted_count += 1
                if deleted_count <= 5:  # 只显示前5个被删除的文档信息
                    print(f"   🗑️  删除文档 {i+1}: word_count={word_count}, chunk_id={metadata.get('chunk_id', 'N/A') if metadata else 'N/A'}")
        
        print(f"\n📊 清理统计:")
        print(f"   ✅ 保留文档: {kept_count}")
        print(f"   🗑️  删除文档: {deleted_count}")
        
        if deleted_count == 0:
            print("✅ 没有需要删除的文档，数据库已经是干净的")
            return True
        
        # 重新编号chunk_id
        print("\n🔢 重新编号chunk_id...")
        
        # 按source分组重新编号
        source_counters = {}
        
        for i, metadata in enumerate(metadatas_to_keep):
            if metadata:
                source = metadata.get('source', 'unknown')
                
                # 初始化计数器
                if source not in source_counters:
                    source_counters[source] = 0
                
                source_counters[source] += 1
                
                # 生成新的chunk_id
                if source.endswith('.txt'):
                    base_name = source[:-4]  # 去掉.txt后缀
                else:
                    base_name = source
                
                new_chunk_id = f"{base_name}-{source_counters[source]}"
                metadata['chunk_id'] = new_chunk_id
                
                # 更新created_at时间戳
                metadata['updated_at'] = datetime.now().isoformat()
        
        print(f"📋 重新编号完成，各源文件统计:")
        for source, count in source_counters.items():
            print(f"   📄 {source}: {count} 个chunk")
        
        # 备份操作确认
        print(f"\n⚠️  即将执行以下操作:")
        print(f"   🗑️  删除 {deleted_count} 个word_count < 15的文档")
        print(f"   🔢 重新编号 {kept_count} 个文档的chunk_id")
        print(f"   💾 更新数据库")
        
        confirm = input("\n❓ 确认执行清理操作？(输入 'yes' 确认): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return False
        
        # 删除原集合
        print("\n🗑️  删除原集合...")
        client.delete_collection("qa_system_chunks")
        
        # 重新创建集合
        print("🆕 重新创建集合...")
        new_collection = client.create_collection(
            name="qa_system_chunks",
            metadata={"description": "QA System document chunks with embeddings - cleaned"}
        )
        
        # 生成新的ID
        new_ids = [f"doc_{i+1}" for i in range(len(documents_to_keep))]
        
        # 添加清理后的数据
        print("💾 添加清理后的数据...")
        if documents_to_keep:
            new_collection.add(
                ids=new_ids,
                documents=documents_to_keep,
                metadatas=metadatas_to_keep,
                embeddings=embeddings_to_keep
            )
        
        # 验证结果
        final_count = new_collection.count()
        print(f"\n✅ 清理完成!")
        print(f"📊 最终统计:")
        print(f"   📄 原始文档数: {original_count}")
        print(f"   🗑️  删除文档数: {deleted_count}")
        print(f"   📄 最终文档数: {final_count}")
        print(f"   📈 数据减少: {((original_count - final_count) / original_count * 100):.1f}%")
        
        # 保存清理报告
        report_file = f"database_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"数据库清理报告\n")
            f.write(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"原始文档数: {original_count}\n")
            f.write(f"删除文档数: {deleted_count}\n")
            f.write(f"最终文档数: {final_count}\n")
            f.write(f"数据减少: {((original_count - final_count) / original_count * 100):.1f}%\n\n")
            f.write("各源文件统计:\n")
            for source, count in source_counters.items():
                f.write(f"  {source}: {count} 个chunk\n")
        
        print(f"📄 清理报告已保存到: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def preview_cleanup():
    """
    预览清理操作，不实际执行删除
    """
    # 主数据库路径
    main_db_path = "e:\\PyProjects\\QASystem\\chroma_db"
    
    print(f"👀 预览清理操作: {main_db_path}")
    print(f"📅 预览时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if not os.path.exists(main_db_path):
        print(f"❌ 数据库路径不存在: {main_db_path}")
        return False
    
    try:
        # 连接到主数据库
        client = chromadb.PersistentClient(
            path=main_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取qa_system_chunks集合
        collection = client.get_collection("qa_system_chunks")
        
        # 获取所有文档的元数据
        all_results = collection.get(
            include=["metadatas"]
        )
        
        # 统计word_count分布
        word_count_stats = {}
        to_delete = []
        to_keep = []
        
        for i, metadata in enumerate(all_results['metadatas']):
            word_count = metadata.get('word_count', 0) if metadata else 0
            
            if isinstance(word_count, str):
                try:
                    word_count = int(word_count)
                except ValueError:
                    word_count = 0
            
            # 统计分布
            if word_count in word_count_stats:
                word_count_stats[word_count] += 1
            else:
                word_count_stats[word_count] = 1
            
            # 分类
            if word_count < 15:
                to_delete.append((i, word_count, metadata.get('chunk_id', 'N/A') if metadata else 'N/A'))
            else:
                to_keep.append((i, word_count, metadata.get('chunk_id', 'N/A') if metadata else 'N/A'))
        
        print(f"📊 Word Count 分布统计:")
        for wc in sorted(word_count_stats.keys()):
            count = word_count_stats[wc]
            status = "🗑️ 将删除" if wc < 15 else "✅ 保留"
            print(f"   word_count={wc}: {count} 个文档 {status}")
        
        print(f"\n📋 清理预览:")
        print(f"   🗑️  将删除: {len(to_delete)} 个文档 (word_count < 15)")
        print(f"   ✅ 将保留: {len(to_keep)} 个文档 (word_count >= 15)")
        
        if len(to_delete) > 0:
            print(f"\n🗑️  前10个将被删除的文档:")
            for i, (doc_idx, wc, chunk_id) in enumerate(to_delete[:10]):
                print(f"   {i+1}. chunk_{doc_idx+1}: word_count={wc}, chunk_id={chunk_id}")
            
            if len(to_delete) > 10:
                print(f"   ... 还有 {len(to_delete) - 10} 个文档将被删除")
        
        return True
        
    except Exception as e:
        print(f"❌ 预览过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    print("数据库清理脚本")
    print("1. 预览清理操作")
    print("2. 执行清理操作")
    
    choice = input("请选择操作 (1/2): ")
    
    if choice == "1":
        preview_cleanup()
    elif choice == "2":
        clean_database_by_word_count()
    else:
        print("❌ 无效选择")