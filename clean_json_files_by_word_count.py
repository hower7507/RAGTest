#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理JSON文件中word_count小于等于15的数据块
删除低质量数据并重新编号chunk_id
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的JSON数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件 {file_path} 失败: {e}")
        return None

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    保存JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 保存路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件 {file_path} 失败: {e}")
        return False

def clean_chunks_by_word_count(data: Dict[str, Any], min_word_count: int = 16) -> Dict[str, Any]:
    """
    清理chunks中word_count小于指定值的数据块
    
    Args:
        data: JSON数据
        min_word_count: 最小词数阈值（默认16，即删除<=15的）
        
    Returns:
        清理后的数据
    """
    if not data or 'chunks' not in data:
        print("数据格式错误，缺少chunks字段")
        return data
    
    original_chunks = data['chunks']
    original_count = len(original_chunks)
    
    # 过滤掉word_count小于阈值的chunks
    filtered_chunks = []
    for chunk in original_chunks:
        if chunk.get('word_count', 0) >= min_word_count:
            filtered_chunks.append(chunk)
    
    # 重新编号chunk_id
    source_file = data.get('source_file', 'unknown')
    base_name = source_file.replace('.txt', '') if source_file.endswith('.txt') else source_file
    
    for i, chunk in enumerate(filtered_chunks, 1):
        chunk['chunk_id'] = f"{base_name}-{i}"
    
    # 更新数据
    cleaned_data = data.copy()
    cleaned_data['chunks'] = filtered_chunks
    cleaned_data['total_chunks'] = len(filtered_chunks)
    cleaned_data['processing_time'] = datetime.now().isoformat()
    
    # 添加清理信息
    cleaned_data['cleaning_info'] = {
        'original_chunks': original_count,
        'filtered_chunks': len(filtered_chunks),
        'removed_chunks': original_count - len(filtered_chunks),
        'min_word_count_threshold': min_word_count,
        'cleaning_time': datetime.now().isoformat()
    }
    
    return cleaned_data

def analyze_word_count_distribution(chunks: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    分析word_count分布
    
    Args:
        chunks: 数据块列表
        
    Returns:
        统计信息
    """
    stats = {
        'total': len(chunks),
        'word_count_1_5': 0,
        'word_count_6_10': 0,
        'word_count_11_15': 0,
        'word_count_16_50': 0,
        'word_count_51_100': 0,
        'word_count_100_plus': 0
    }
    
    for chunk in chunks:
        word_count = chunk.get('word_count', 0)
        if 1 <= word_count <= 5:
            stats['word_count_1_5'] += 1
        elif 6 <= word_count <= 10:
            stats['word_count_6_10'] += 1
        elif 11 <= word_count <= 15:
            stats['word_count_11_15'] += 1
        elif 16 <= word_count <= 50:
            stats['word_count_16_50'] += 1
        elif 51 <= word_count <= 100:
            stats['word_count_51_100'] += 1
        elif word_count > 100:
            stats['word_count_100_plus'] += 1
    
    return stats

def process_file(file_path: str, output_path: str = None, preview_only: bool = False) -> bool:
    """
    处理单个JSON文件
    
    Args:
        file_path: 输入文件路径
        output_path: 输出文件路径（如果为None，则覆盖原文件）
        preview_only: 是否只预览不实际处理
        
    Returns:
        是否处理成功
    """
    print(f"\n{'='*60}")
    print(f"处理文件: {file_path}")
    print(f"{'='*60}")
    
    # 加载数据
    data = load_json_file(file_path)
    if not data:
        return False
    
    # 分析原始数据
    original_chunks = data.get('chunks', [])
    original_stats = analyze_word_count_distribution(original_chunks)
    
    print(f"\n原始数据统计:")
    print(f"  总数据块: {original_stats['total']}")
    print(f"  词数1-5: {original_stats['word_count_1_5']}")
    print(f"  词数6-10: {original_stats['word_count_6_10']}")
    print(f"  词数11-15: {original_stats['word_count_11_15']}")
    print(f"  词数16-50: {original_stats['word_count_16_50']}")
    print(f"  词数51-100: {original_stats['word_count_51_100']}")
    print(f"  词数100+: {original_stats['word_count_100_plus']}")
    
    # 计算将要删除的数据
    to_remove = original_stats['word_count_1_5'] + original_stats['word_count_6_10'] + original_stats['word_count_11_15']
    to_keep = original_stats['total'] - to_remove
    
    print(f"\n清理预览:")
    print(f"  将删除数据块: {to_remove} (word_count <= 15)")
    print(f"  将保留数据块: {to_keep} (word_count >= 16)")
    print(f"  删除比例: {to_remove/original_stats['total']*100:.1f}%")
    
    if preview_only:
        print(f"\n[预览模式] 不执行实际清理操作")
        return True
    
    # 执行清理
    cleaned_data = clean_chunks_by_word_count(data, min_word_count=16)
    
    # 验证清理结果
    cleaned_chunks = cleaned_data.get('chunks', [])
    cleaned_stats = analyze_word_count_distribution(cleaned_chunks)
    
    print(f"\n清理后统计:")
    print(f"  总数据块: {cleaned_stats['total']}")
    print(f"  词数16-50: {cleaned_stats['word_count_16_50']}")
    print(f"  词数51-100: {cleaned_stats['word_count_51_100']}")
    print(f"  词数100+: {cleaned_stats['word_count_100_plus']}")
    
    # 保存文件
    if output_path is None:
        # 创建备份
        backup_path = file_path.replace('.json', '_backup.json')
        if os.path.exists(file_path):
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"\n已创建备份: {backup_path}")
        output_path = file_path
    
    if save_json_file(cleaned_data, output_path):
        print(f"\n清理完成，已保存到: {output_path}")
        return True
    else:
        return False

def main():
    """
    主函数
    """
    # 定义要处理的文件
    files_to_process = [
        r"e:\PyProjects\QASystem\data\chap01_processed.json",
        r"e:\PyProjects\QASystem\data\chap02_processed.json"
    ]
    
    print("JSON文件清理工具")
    print("功能: 删除word_count <= 15的数据块并重新编号")
    print("="*60)
    
    # 询问用户操作模式
    while True:
        mode = input("\n请选择操作模式:\n1. 预览模式（只查看统计，不执行清理）\n2. 执行清理\n请输入选择 (1/2): ").strip()
        if mode in ['1', '2']:
            break
        print("无效选择，请输入1或2")
    
    preview_only = (mode == '1')
    
    if not preview_only:
        confirm = input("\n确认要执行清理操作吗？这将修改原文件（会自动创建备份）(y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("操作已取消")
            return
    
    # 处理每个文件
    success_count = 0
    for file_path in files_to_process:
        if os.path.exists(file_path):
            if process_file(file_path, preview_only=preview_only):
                success_count += 1
        else:
            print(f"\n文件不存在: {file_path}")
    
    print(f"\n{'='*60}")
    print(f"处理完成: {success_count}/{len(files_to_process)} 个文件成功处理")
    if not preview_only and success_count > 0:
        print("注意: 原文件已备份为 *_backup.json")

if __name__ == "__main__":
    main()