# -*- coding: utf-8 -*-
"""
上下文管理器
处理搜索结果的去重、重排序和上下文拼接
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import os
from advanced_search_system import AdvancedSearchSystem
from vectorize_chunks import ChunkVectorizer

class ContextManager:
    """
    上下文管理器：处理搜索结果的整合和优化
    """
    
    def __init__(self, 
                 search_system: AdvancedSearchSystem,
                 collection: Any, # chromadb.Collection
                 use_bre_reranking: bool = True):
        """
        初始化上下文管理器
        
        Args:
            vectorizer: 向量化器实例
            use_bre_reranking: 是否使用BRE重排序
        """
        self.search_system = search_system
        self.collection = collection
        self.use_bre_reranking = use_bre_reranking
        
        # BRE重排序系统现在直接使用传入的search_system
        self.bre_system = self.search_system if use_bre_reranking else None
        
        print(f"上下文管理器初始化完成，BRE重排序: {use_bre_reranking}")
    
    def deduplicate_by_chunk_id(self, 
                               search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于chunk_id进行去重
        
        Args:
            search_results: 搜索结果列表
            
        Returns:
            去重后的结果列表
        """
        print(f"开始去重，原始结果数: {len(search_results)}")
        
        # 按chunk_id分组，保留优先级最高的结果
        chunk_groups = defaultdict(list)
        
        for result in search_results:
            # 获取chunk_id
            chunk_id = self._extract_chunk_id(result)
            if chunk_id is not None:
                chunk_groups[chunk_id].append(result)
            else:
                # 如果无法提取chunk_id，使用result的id
                result_id = result.get('id', f"unknown_{len(chunk_groups)}")
                chunk_groups[result_id].append(result)
        
        # 为每个chunk_id选择最佳结果
        deduplicated_results = []
        
        for chunk_id, results in chunk_groups.items():
            if len(results) == 1:
                deduplicated_results.append(results[0])
            else:
                # 多个结果时，选择优先级最高的
                best_result = self._select_best_result(results)
                deduplicated_results.append(best_result)
        
        print(f"去重完成，结果数: {len(deduplicated_results)}")
        return deduplicated_results
    
    def _extract_chunk_id(self, result: Dict[str, Any]) -> Optional[int]:
        """
        从搜索结果中提取chunk_id
        
        Args:
            result: 搜索结果
            
        Returns:
            chunk_id或None
        """
        # 尝试从metadata中获取
        metadata = result.get('metadata', {})
        if 'chunk_id' in metadata:
            return metadata['chunk_id']
        
        # 尝试从id中解析
        result_id = result.get('id', '')
        if isinstance(result_id, str):
            # 处理 chapXX-N 格式
            if '-' in result_id:
                try:
                    chunk_part = result_id.split('-')[-1]  # 取最后一部分
                    return int(chunk_part)
                except (ValueError, IndexError):
                    pass
            # 处理 chunk_N 格式
            elif result_id.startswith('chunk_'):
                try:
                    return int(result_id.split('_')[1])
                except (IndexError, ValueError):
                    pass
        
        # 尝试从document_id中获取
        doc_id = result.get('document_id', '')
        if isinstance(doc_id, str):
            # 处理 chapXX-N 格式
            if '-' in doc_id:
                try:
                    chunk_part = doc_id.split('-')[-1]  # 取最后一部分
                    return int(chunk_part)
                except (ValueError, IndexError):
                    pass
            # 处理 chunk_N 格式
            elif doc_id.startswith('chunk_'):
                try:
                    return int(doc_id.split('_')[1])
                except (IndexError, ValueError):
                    pass
        
        return None
    
    def _select_best_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从多个相同chunk_id的结果中选择最佳的
        
        Args:
            results: 相同chunk_id的结果列表
            
        Returns:
            最佳结果
        """
        # 按搜索优先级排序（向量搜索 > 关键词搜索 > 时间搜索）
        priority_order = {
            'vector_search': 1,
            'keyword_search': 2,
            'time_search': 3
        }
        
        # 按优先级和得分排序
        sorted_results = sorted(
            results,
            key=lambda x: (
                priority_order.get(x.get('search_source', 'unknown'), 999),
                -x.get('score', 0)  # 得分降序
            )
        )
        
        best_result = sorted_results[0]
        
        # 融合得分（如果有多个来源）
        if len(results) > 1:
            total_score = sum(r.get('score', 0) for r in results)
            best_result['fused_score'] = total_score
            best_result['source_count'] = len(results)
            best_result['all_sources'] = [r.get('search_source', 'unknown') for r in results]
        
        return best_result
    
    def apply_bre_reranking(self,
                          query: str,
                          search_results: List[Dict[str, Any]],
                          top_k: int = 10) -> List[Dict[str, Any]]:
        """
        应用BRE重排序（已禁用 - 仅去重和截取）
        
        Args:
            query: 查询文本
            search_results: 搜索结果
            top_k: 返回结果数量
            
        Returns:
            去重并截取后的结果（跳过BRE重排序）
        """
        print("🚫 BRE重排序已被强制禁用，仅进行去重和截取操作")
        
        if not search_results:
            print("⚠️ 搜索结果为空，返回空列表")
            return []
        
        print(f"📥 输入结果数: {len(search_results)}")
        
        # 先进行去重（基于chunk_id或document_id）
        deduplicated_results = self.deduplicate_by_chunk_id(search_results)
        print(f"🔄 去重后结果数: {len(deduplicated_results)}")
        
        # 截取到指定数量
        final_results = deduplicated_results[:top_k]
        print(f"✂️ 截取后最终结果数: {len(final_results)}")
        
        # 确保每个结果都有必要的字段
        for i, result in enumerate(final_results):
            if 'final_rank' not in result:
                result['final_rank'] = i + 1
            if 'final_score' not in result:
                result['final_score'] = result.get('score', 0.0)
        
        print(f"✅ 处理完成：从 {len(search_results)} 个结果 → 去重到 {len(deduplicated_results)} 个 → 最终返回 {len(final_results)} 个结果")
        
        return final_results
    
    def build_context(self, 
                     search_results: List[Dict[str, Any]],
                     max_context_length: int = 2000) -> str:
        """
        构建上下文字符串
        
        Args:
            search_results: 搜索结果
            max_context_length: 最大上下文长度
            
        Returns:
            构建的上下文字符串
        """
        if not search_results:
            return "没有找到相关内容。"
        
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            
            # 根据数据格式动态格式化结果
            if 'question' in metadata and 'answer' in metadata:
                # QA格式数据
                source_file = metadata.get('source_file', '')
                # 提取文件名（去掉路径和扩展名）
                if source_file:
                    file_name = os.path.basename(source_file).replace('.txt', '').replace('_processed.json', '')
                else:
                    file_name = '未知来源'
                chunk_id = self._extract_chunk_id(result)
                # 如果chunk_id为None，使用空字符串
                chunk_id_str = str(chunk_id) if chunk_id is not None else ""
                result_text = f"""[参考片段{file_name}-{chunk_id_str} - 来源: {file_name}]
问题: {metadata.get('question', '')}
答案: {metadata.get('answer', '')}
相关度: {result.get('bre_score', result.get('score', 0)):.3f}
"""
            else:
                # 传统时间戳格式数据
                source_file = metadata.get('source_file', '')
                # 提取文件名（去掉路径和扩展名）
                if source_file:
                    file_name = os.path.basename(source_file).replace('.txt', '').replace('_processed.json', '')
                else:
                    file_name = '未知来源'
                
                chunk_id = self._extract_chunk_id(result)
                # 如果chunk_id为None，使用空字符串
                chunk_id_str = str(chunk_id) if chunk_id is not None else ""
                result_text = f"""[{file_name}-{chunk_id_str} - 来源: {file_name}]
时间: {metadata.get('start_time', '')} - {metadata.get('end_time', '')}
说话人: {metadata.get('speakers', '未知')}
内容: {content}
相关度: {result.get('bre_score', result.get('score', 0)):.3f}
"""
            
            # 检查长度限制
            if current_length + len(result_text) > max_context_length:
                break
            
            context_parts.append(result_text)
            current_length += len(result_text)
        
        return "\n".join(context_parts)
    
    def process_search_results(self, 
                             query: str,
                             search_results: List[Dict[str, Any]],
                             max_results: int = 10,
                             max_context_length: int = 2000) -> Dict[str, Any]:
        """
        完整的搜索结果处理流程
        
        Args:
            query: 查询文本
            search_results: 原始搜索结果
            max_results: 最大结果数量
            max_context_length: 最大上下文长度
            
        Returns:
            处理后的结果和上下文
        """
        print(f"\n=== 开始处理搜索结果 ===")
        print(f"原始结果数: {len(search_results)}")
        
        # 1. 去重
        deduplicated_results = self.deduplicate_by_chunk_id(search_results)
        
        # 2. BRE重排序
        reranked_results = self.apply_bre_reranking(
            query=query,
            search_results=deduplicated_results,
            top_k=max_results
        )
        
        # 3. 构建上下文
        context = self.build_context(
            search_results=reranked_results,
            max_context_length=max_context_length
        )
        
        print(f"=== 搜索结果处理完成 ===")
        print(f"最终结果数: {len(reranked_results)}")
        print(f"上下文长度: {len(context)}字符")
        
        return {
            'processed_results': reranked_results,
            'context': context,
            'stats': {
                'original_count': len(search_results),
                'deduplicated_count': len(deduplicated_results),
                'final_count': len(reranked_results),
                'context_length': len(context)
            }
        }

# 使用示例
if __name__ == "__main__":
    # 创建上下文管理器
    context_manager = ContextManager(use_bre_reranking=False)  # 暂时不使用BRE
    
    # 模拟搜索结果
    mock_results = [
        {
            'id': 'chunk_1',
            'content': '这是第一个文档内容',
            'metadata': {'chunk_id': 1, 'start_time': '00:01', 'speakers': '说话人1'},
            'score': 0.8,
            'search_source': 'vector_search'
        },
        {
            'id': 'chunk_1',  # 重复的chunk_id
            'content': '这是第一个文档内容（重复）',
            'metadata': {'chunk_id': 1, 'start_time': '00:01', 'speakers': '说话人1'},
            'score': 0.6,
            'search_source': 'keyword_search'
        },
        {
            'id': 'chunk_2',
            'content': '这是第二个文档内容',
            'metadata': {'chunk_id': 2, 'start_time': '00:05', 'speakers': '说话人2'},
            'score': 0.7,
            'search_source': 'vector_search'
        }
    ]
    
    # 处理搜索结果
    result = context_manager.process_search_results(
        query="测试查询",
        search_results=mock_results,
        max_results=5
    )
    
    print("\n处理结果:")
    print(f"统计信息: {result['stats']}")
    print(f"\n上下文:\n{result['context']}")