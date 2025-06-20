# -*- coding: utf-8 -*-
"""
系统健康检查模块
用于监控各个组件的状态
"""

import os
import json
from typing import Dict, Any
from datetime import datetime

def check_chromadb_health(chroma_db_path: str, collection_name: str) -> Dict[str, Any]:
    """
    检查ChromaDB健康状态
    
    Args:
        chroma_db_path: ChromaDB路径
        collection_name: 集合名称
        
    Returns:
        健康检查结果
    """
    result = {
        'status': 'unknown',
        'path_exists': False,
        'collection_exists': False,
        'total_records': 0,
        'chap02_records': 0,
        'error': None
    }
    
    try:
        # 检查路径是否存在
        result['path_exists'] = os.path.exists(chroma_db_path)
        if not result['path_exists']:
            result['status'] = 'error'
            result['error'] = f'ChromaDB路径不存在: {chroma_db_path}'
            return result
        
        # 尝试连接ChromaDB
        import chromadb
        client = chromadb.PersistentClient(path=chroma_db_path)
        
        # 检查集合是否存在
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        result['collection_exists'] = collection_name in collection_names
        
        if not result['collection_exists']:
            result['status'] = 'error'
            result['error'] = f'集合不存在: {collection_name}，可用集合: {collection_names}'
            return result
        
        # 获取集合信息
        collection = client.get_collection(collection_name)
        count_result = collection.count()
        result['total_records'] = count_result
        
        # 检查chap02数据
        if count_result > 0:
            sample_results = collection.get(limit=min(100, count_result))
            chap02_count = 0
            for metadata in sample_results.get('metadatas', []):
                if metadata and (
                    ('source_file' in metadata and 'chap02' in metadata['source_file']) or
                    ('question' in metadata and metadata.get('question'))
                ):
                    chap02_count += 1
            result['chap02_records'] = chap02_count
        
        result['status'] = 'healthy'
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def check_search_interface_health(search_interface) -> Dict[str, Any]:
    """
    检查搜索接口健康状态
    
    Args:
        search_interface: 搜索接口实例
        
    Returns:
        健康检查结果
    """
    result = {
        'status': 'unknown',
        'initialized': False,
        'vectorizer_available': False,
        'search_system_available': False,
        'error': None
    }
    
    try:
        result['initialized'] = getattr(search_interface, 'initialized', False)
        result['vectorizer_available'] = search_interface.vectorizer is not None
        result['search_system_available'] = search_interface.search_system is not None
        
        if result['initialized'] and result['vectorizer_available'] and result['search_system_available']:
            result['status'] = 'healthy'
        else:
            result['status'] = 'degraded'
            issues = []
            if not result['initialized']:
                issues.append('未初始化')
            if not result['vectorizer_available']:
                issues.append('向量化器不可用')
            if not result['search_system_available']:
                issues.append('搜索系统不可用')
            result['error'] = '问题: ' + ', '.join(issues)
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def check_deepseek_client_health(deepseek_client) -> Dict[str, Any]:
    """
    检查DeepSeek客户端健康状态
    
    Args:
        deepseek_client: DeepSeek客户端实例
        
    Returns:
        健康检查结果
    """
    result = {
        'status': 'unknown',
        'api_key_available': False,
        'config_valid': False,
        'error': None
    }
    
    try:
        # 检查API密钥
        result['api_key_available'] = bool(getattr(deepseek_client, 'api_key', None))
        
        # 检查配置
        if hasattr(deepseek_client, 'validate'):
            try:
                deepseek_client.validate()
                result['config_valid'] = True
            except Exception as e:
                result['config_valid'] = False
                result['error'] = f'配置验证失败: {e}'
        
        if result['api_key_available'] and result['config_valid']:
            result['status'] = 'healthy'
        else:
            result['status'] = 'degraded'
            issues = []
            if not result['api_key_available']:
                issues.append('API密钥不可用')
            if not result['config_valid']:
                issues.append('配置无效')
            if not result['error']:
                result['error'] = '问题: ' + ', '.join(issues)
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def generate_health_report(search_interface, deepseek_client, config) -> Dict[str, Any]:
    """
    生成完整的健康检查报告
    
    Args:
        search_interface: 搜索接口实例
        deepseek_client: DeepSeek客户端实例
        config: 配置对象
        
    Returns:
        完整的健康检查报告
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'unknown',
        'components': {}
    }
    
    # 检查ChromaDB
    report['components']['chromadb'] = check_chromadb_health(
        config.chroma_db_path, 
        config.collection_name
    )
    
    # 检查搜索接口
    report['components']['search_interface'] = check_search_interface_health(search_interface)
    
    # 检查DeepSeek客户端
    report['components']['deepseek_client'] = check_deepseek_client_health(deepseek_client)
    
    # 计算总体状态
    statuses = [comp['status'] for comp in report['components'].values()]
    if all(status == 'healthy' for status in statuses):
        report['overall_status'] = 'healthy'
    elif any(status == 'error' for status in statuses):
        report['overall_status'] = 'error'
    else:
        report['overall_status'] = 'degraded'
    
    return report