# -*- coding: utf-8 -*-
"""
分析主数据库中qa_system_chunks集合的详细结构
诊断查询问题的根本原因
"""

import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
import json

def analyze_qa_system_chunks():
    """
    详细分析qa_system_chunks集合的结构
    """
    # 主数据库路径
    main_db_path = "e:\\PyProjects\\QASystem\\chroma_db"
    
    print(f"🔍 分析主数据库: {main_db_path}")
    print(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if not os.path.exists(main_db_path):
        print(f"❌ 主数据库路径不存在: {main_db_path}")
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
        count = collection.count()
        print(f"📊 集合文档总数: {count}")
        print()
        
        if count == 0:
            print("⚠️  集合为空，没有文档")
            return True
        
        # 获取前5个文档进行详细分析
        print("📋 获取前5个文档进行结构分析...")
        print("-" * 60)
        
        results = collection.get(
            limit=5,
            include=["documents", "metadatas"]
        )
        
        print(f"🔍 实际获取到的文档数量: {len(results['documents'])}")
        print()
        
        # 分析每个文档的结构
        for i, (document, metadata) in enumerate(zip(
            results['documents'], 
            results['metadatas']
        )):
            print(f"📄 文档 {i+1}:")
            print(f"   🆔 ID: [文档索引 {i}]")
            print(f"   📝 文档内容长度: {len(document) if document else 0} 字符")
            
            # 显示文档内容的前100个字符
            if document:
                preview = document[:100] + "..." if len(document) > 100 else document
                print(f"   📖 内容预览: {preview}")
            else:
                print(f"   📖 内容预览: [空文档]")
            
            # 详细分析元数据
            print(f"   🏷️  元数据字段数量: {len(metadata) if metadata else 0}")
            if metadata:
                print(f"   🏷️  元数据详情:")
                for key, value in metadata.items():
                    print(f"      - {key}: {value}")
            else:
                print(f"   🏷️  元数据详情: [无元数据]")
            
            print()
        
        # 分析所有文档的元数据字段统计
        print("📊 元数据字段统计分析...")
        print("-" * 60)
        
        # 获取更多文档来分析元数据模式
        all_results = collection.get(
            limit=min(100, count),  # 最多分析100个文档
            include=["metadatas"]
        )
        
        # 统计元数据字段
        field_counts = {}
        field_values = {}
        
        for metadata in all_results['metadatas']:
            if metadata:
                for key, value in metadata.items():
                    # 统计字段出现次数
                    field_counts[key] = field_counts.get(key, 0) + 1
                    
                    # 收集字段值的样本
                    if key not in field_values:
                        field_values[key] = set()
                    field_values[key].add(str(value))
        
        print(f"📈 分析了 {len(all_results['metadatas'])} 个文档的元数据")
        print(f"🔑 发现的元数据字段:")
        
        for field, count in sorted(field_counts.items()):
            coverage = (count / len(all_results['metadatas'])) * 100
            sample_values = list(field_values[field])[:5]  # 显示前5个不同的值
            
            print(f"   - {field}:")
            print(f"     📊 出现次数: {count}/{len(all_results['metadatas'])} ({coverage:.1f}%)")
            print(f"     📝 样本值: {sample_values}")
            if len(field_values[field]) > 5:
                print(f"     📝 (还有 {len(field_values[field]) - 5} 个不同值...)")
            print()
        
        # 检查是否存在常见的查询字段
        print("🔍 查询相关字段检查...")
        print("-" * 60)
        
        important_fields = ['source', 'chunk_type', 'chapter', 'section', 'document_type']
        
        for field in important_fields:
            if field in field_counts:
                print(f"✅ 发现重要字段 '{field}': {field_counts[field]} 个文档包含此字段")
                # 显示该字段的所有不同值
                unique_values = list(field_values[field])
                print(f"   📋 所有值: {unique_values}")
            else:
                print(f"❌ 缺少重要字段 '{field}'")
            print()
        
        # 检查文档内容是否为空
        print("📄 文档内容检查...")
        print("-" * 60)
        
        content_results = collection.get(
            limit=min(50, count),
            include=["documents"]
        )
        
        empty_docs = 0
        short_docs = 0
        normal_docs = 0
        
        for document in content_results['documents']:
            if not document or len(document.strip()) == 0:
                empty_docs += 1
            elif len(document.strip()) < 50:
                short_docs += 1
            else:
                normal_docs += 1
        
        total_checked = len(content_results['documents'])
        print(f"📊 文档内容统计 (检查了 {total_checked} 个文档):")
        print(f"   📄 正常文档 (≥50字符): {normal_docs} ({(normal_docs/total_checked)*100:.1f}%)")
        print(f"   📄 短文档 (<50字符): {short_docs} ({(short_docs/total_checked)*100:.1f}%)")
        print(f"   📄 空文档: {empty_docs} ({(empty_docs/total_checked)*100:.1f}%)")
        
        print()
        print("✅ 分析完成")
        
        # 提供诊断建议
        print()
        print("🔧 诊断建议:")
        print("-" * 60)
        
        if empty_docs > 0:
            print(f"⚠️  发现 {empty_docs} 个空文档，这可能影响查询结果")
        
        if 'source' not in field_counts:
            print("⚠️  缺少 'source' 字段，这可能影响按来源过滤")
        
        if 'chunk_type' not in field_counts:
            print("⚠️  缺少 'chunk_type' 字段，这可能影响按类型过滤")
        
        if field_counts:
            print("✅ 元数据结构看起来正常")
        else:
            print("❌ 所有文档都缺少元数据，这会严重影响查询功能")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_qa_system_chunks()