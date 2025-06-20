#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索系统接口
提供简化的搜索接口，方便用户快速使用
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from advanced_search_system import AdvancedSearchSystem
from vectorize_chunks import ChunkVectorizer
from search_config import SearchConfig, load_config

class SearchInterface:
    """
    搜索系统接口
    提供简化的搜索功能
    """
    
    def __init__(self, config_name: str = "balanced"):
        """
        初始化搜索接口
        
        Args:
            config_name: 配置名称
        """
        self.config = load_config(config_name)
        self.vectorizer = None
        self.search_system = None
        self.initialized = False
        
        print(f"搜索接口初始化完成，使用配置: {config_name}")
    
    def initialize(self) -> bool:
        """
        初始化搜索系统
        
        Returns:
            是否初始化成功
        """
        try:
            print("正在初始化搜索系统...")
            
            # 1. 初始化向量化器
            self.vectorizer = ChunkVectorizer(
                model_name=self.config.model_name,
                collection_name=self.config.collection_name
            )
            
            # 2. 初始化ChromaDB
            if not os.path.exists(self.config.chroma_db_path):
                print(f"错误: ChromaDB路径不存在: {self.config.chroma_db_path}")
                return False
            
            try:
                self.vectorizer.init_chromadb(self.config.chroma_db_path)
                print(f"✅ ChromaDB连接成功: {self.config.chroma_db_path}")
            except Exception as e:
                print(f"❌ ChromaDB连接失败: {e}")
                print(f"数据库路径: {self.config.chroma_db_path}")
                print(f"集合名称: {self.config.collection_name}")
                return False
            
            # 3. 检查数据
            info = self.vectorizer.get_collection_info()
            total_records = info.get('total_records', 0)
            if total_records == 0:
                print("警告: 没有找到向量数据，请先运行向量化程序")
                return False
            
            print(f"加载了{total_records}条向量数据")
            
            # 4. 检查chap02数据是否存在
            try:
                # 检查所有记录而不是只检查前100条
                all_results = self.vectorizer.collection.get()
                chap02_count = 0
                qa_count = 0
                
                for metadata in all_results.get('metadatas', []):
                    if metadata:
                        source_file = metadata.get('source_file', '')
                        question = metadata.get('question', '')
                        
                        # 检测chap02文件
                        if 'chap02' in source_file:
                            chap02_count += 1
                        # 检测QA数据
                        elif question and question.strip():
                            qa_count += 1
                
                total_chap02_related = chap02_count + qa_count
                if total_chap02_related > 0:
                    print(f"✅ 检测到chap02相关数据: {chap02_count}条文本 + {qa_count}条QA = {total_chap02_related}条")
                else:
                    print("⚠️ 未检测到chap02数据，可能影响问答效果")
            except Exception as e:
                print(f"⚠️ 检查chap02数据时出错: {e}")
            
            # 4. 加载模型
            self.vectorizer.load_model()
            
            # 5. 初始化搜索系统
            self.search_system = AdvancedSearchSystem(
                vectorizer=self.vectorizer,
                bm25_k1=self.config.bm25_k1,
                bm25_b=self.config.bm25_b,
                vector_weight=self.config.vector_weight,
                bm25_weight=self.config.bm25_weight,
                exact_weight=self.config.exact_weight
            )
            
            self.initialized = True
            print("搜索系统初始化成功！")
            return True
            
        except Exception as e:
            print(f"搜索系统初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search(self, 
               query: str, 
               top_k: Optional[int] = None,
               return_prompt: bool = True) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            return_prompt: 是否返回提示词
            
        Returns:
            搜索结果
        """
        if not self.initialized:
            if not self.initialize():
                return {
                    'error': '搜索系统初始化失败',
                    'query': query,
                    'results': []
                }
        
        if not query.strip():
            return {
                'error': '查询不能为空',
                'query': query,
                'results': []
            }
        
        try:
            # 使用配置中的默认值
            if top_k is None:
                top_k = self.config.default_top_k
            
            # 执行搜索
            result = self.search_system.search(
                query=query,
                top_k=top_k,
                max_context_length=self.config.max_context_length
            )
            
            # 格式化结果
            formatted_result = {
                'query': result['query'],
                'total_results': len(result['results']),
                'search_time': result['search_time'],
                'total_candidates': result['total_candidates'],
                'keywords_extracted': result['keywords_extracted'],
                'results': []
            }
            
            # 格式化每个结果
            for i, res in enumerate(result['results']):
                # 基础格式化结果
                formatted_res = {
                    'rank': i + 1,
                    'document_id': res['id'],
                    'content': res['content'],
                    'metadata': {},
                    'score': res.get('score', res['final_score']),  # 添加score键以保持兼容性
                    'scores': {
                        'final_score': res['final_score'],
                        'vector_score': res['score_breakdown']['vector'],
                        'bm25_score': res['score_breakdown']['bm25'],
                        'exact_score': res['score_breakdown']['exact']
                    }
                }
                
                # 处理元数据
                metadata = res['metadata']
                
                # 统一的元数据格式
                formatted_res['metadata'] = {
                    'source_file': metadata.get('source_file', ''),
                    'chunk_type': metadata.get('chunk_type', 'text'),
                    'word_count': metadata.get('word_count', 0)
                }
                
                # 如果是QA格式数据，添加问答信息
                if 'question' in metadata and 'answer' in metadata:
                    formatted_res['metadata'].update({
                        'question': metadata.get('question', ''),
                        'answer': metadata.get('answer', '')
                    })
                
                formatted_result['results'].append(formatted_res)
            
            # 添加提示词
            if return_prompt:
                formatted_result['prompt'] = result['prompt']
            
            return formatted_result
            
        except Exception as e:
            print(f"搜索过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'error': f'搜索失败: {str(e)}',
                'query': query,
                'results': []
            }
    
    def quick_search(self, query: str, top_k: int = 3) -> str:
        """
        快速搜索，返回简化的文本结果
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            简化的搜索结果文本
        """
        result = self.search(query, top_k=top_k, return_prompt=False)
        
        if 'error' in result:
            return f"搜索失败: {result['error']}"
        
        if not result['results']:
            return f"没有找到与'{query}'相关的内容"
        
        # 格式化输出
        output_lines = [
            f"查询: {query}",
            f"找到{result['total_results']}个相关结果（搜索时间: {result['search_time']:.2f}秒）",
            ""
        ]
        
        for res in result['results']:
            # 统一的输出格式
            output_lines.extend([
                f"结果{res['rank']}:",
                f"  相关度: {res['scores']['final_score']:.3f}",
                f"  来源: {res['metadata']['source_file']}"
            ])
            
            # 如果是QA格式数据，显示问答信息
            if 'question' in res['metadata']:
                output_lines.extend([
                    f"  问题: {res['metadata']['question'][:80]}{'...' if len(res['metadata']['question']) > 80 else ''}",
                    f"  答案: {res['metadata']['answer'][:100]}{'...' if len(res['metadata']['answer']) > 100 else ''}"
                ])
            else:
                # 显示内容
                output_lines.append(f"  内容: {res['content'][:150]}{'...' if len(res['content']) > 150 else ''}")
            
            output_lines.append("")  # 空行分隔
        
        return "\n".join(output_lines)
    
    def batch_search(self, queries: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        批量搜索
        
        Args:
            queries: 查询列表
            top_k: 每个查询返回的结果数量
            
        Returns:
            批量搜索结果
        """
        results = []
        
        for i, query in enumerate(queries):
            print(f"处理查询 {i+1}/{len(queries)}: {query}")
            result = self.search(query, top_k=top_k)
            results.append(result)
        
        return results
    
    def search_with_time_filter(self, 
                                query: str, 
                                start_time: str, 
                                end_time: str, 
                                top_k: int = 5) -> Dict[str, Any]:
        """
        带时间过滤的搜索
        
        Args:
            query: 查询文本
            start_time: 开始时间 (格式: "HH:MM" 或 "HH:MM:SS")
            end_time: 结束时间 (格式: "HH:MM" 或 "HH:MM:SS")
            top_k: 返回结果数量
            
        Returns:
            搜索结果
        """
        return self.search(
            query=query,
            top_k=top_k,
            start_time=start_time,
            end_time=end_time
        )
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            系统信息
        """
        info = {
            'initialized': self.initialized,
            'config': self.config.to_dict()
        }
        
        if self.initialized and self.vectorizer:
            try:
                collection_info = self.vectorizer.get_collection_info()
                info['database'] = collection_info
            except Exception as e:
                info['database_error'] = str(e)
        
        return info
    
    def save_search_results(self, results: Dict[str, Any], filename: str):
        """
        保存搜索结果到文件
        
        Args:
            results: 搜索结果
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"搜索结果已保存到: {filename}")
        except Exception as e:
            print(f"保存搜索结果失败: {e}")


# === 便捷函数 ===

# 全局搜索接口实例
_global_search_interface = None

def get_search_interface(config_name: str = "balanced") -> SearchInterface:
    """
    获取全局搜索接口实例
    
    Args:
        config_name: 配置名称
        
    Returns:
        搜索接口实例
    """
    global _global_search_interface
    
    if _global_search_interface is None:
        _global_search_interface = SearchInterface(config_name)
    
    return _global_search_interface

def quick_search(query: str, top_k: int = 3) -> str:
    """
    快速搜索便捷函数
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
        
    Returns:
        搜索结果文本
    """
    interface = get_search_interface()
    return interface.quick_search(query, top_k)

def search(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    搜索便捷函数
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
        
    Returns:
        搜索结果
    """
    interface = get_search_interface()
    return interface.search(query, top_k)

def search_with_time(query: str, start_time: str, end_time: str, top_k: int = 5) -> Dict[str, Any]:
    """
    带时间过滤的搜索便捷函数
    
    Args:
        query: 查询文本
        start_time: 开始时间
        end_time: 结束时间
        top_k: 返回结果数量
        
    Returns:
        搜索结果
    """
    interface = get_search_interface()
    return interface.search_with_time_filter(query, start_time, end_time, top_k)


def demo_search_interface():
    """
    演示搜索接口
    """
    print("=== 搜索接口演示 ===")
    
    # 1. 创建搜索接口
    search_interface = SearchInterface("balanced")
    
    # 2. 显示系统信息
    print("\n=== 系统信息 ===")
    info = search_interface.get_system_info()
    print(f"初始化状态: {info['initialized']}")
    print(f"配置: {info['config']['model_name']}")
    
    # 3. 测试搜索
    test_queries = [
        "乔老师的邮箱"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"测试查询: {query}")
        
        # 快速搜索
        print("\n--- 快速搜索结果 ---")
        quick_result = search_interface.quick_search(query, top_k=2)
        print(quick_result)
        
        # 详细搜索
        print("\n--- 详细搜索结果 ---")
        detailed_result = search_interface.search(query, top_k=2, return_prompt=False)
        
        if 'error' not in detailed_result:
            print(f"查询: {detailed_result['query']}")
            print(f"结果数: {detailed_result['total_results']}")
            print(f"搜索时间: {detailed_result['search_time']:.2f}秒")
            print(f"关键词: {detailed_result['keywords_extracted']}")
            
            for res in detailed_result['results']:
                print(f"\n  结果{res['rank']}:")
                print(f"    综合得分: {res['scores']['final_score']:.3f}")
                print(f"    时间: {res['metadata']['start_time']} - {res['metadata']['end_time']}")
                print(f"    内容: {res['content'][:100]}...")
        else:
            print(f"搜索失败: {detailed_result['error']}")
    
    # 4. 测试时间过滤搜索
    print(f"\n{'='*50}")
    print("测试时间过滤搜索")
    
    time_result = search_interface.search_with_time_filter(
        query="技术发展",
        start_time="00:00",
        end_time="10:00",
        top_k=3
    )
    
    if 'error' not in time_result:
        print(f"时间过滤搜索结果数: {time_result['total_results']}")
    else:
        print(f"时间过滤搜索失败: {time_result['error']}")
    
    # 5. 测试便捷函数
    print(f"\n{'='*50}")
    print("测试便捷函数")
    
    convenience_result = quick_search("人工智能", top_k=2)
    print("便捷函数搜索结果:")
    print(convenience_result)


if __name__ == "__main__":
    demo_search_interface()