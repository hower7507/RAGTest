#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级搜索系统
集成BM25关键词抽取、向量匹配、精确匹配、BRE重排序和提示词拼接
"""

import json
import re
import math
import os
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
import jieba
import jieba.analyse
from vectorize_chunks import ChunkVectorizer
import numpy as np
from datetime import datetime

class AdvancedSearchSystem:
    """
    高级搜索系统
    整合多种搜索策略：BM25关键词抽取 + 向量匹配 + 精确匹配 + BRE重排序
    """
    
    def __init__(self, 
                 vectorizer: ChunkVectorizer = None,
                 bm25_k1: float = 1.5,
                 bm25_b: float = 0.75,
                 vector_weight: float = 0.6,
                 bm25_weight: float = 0.25,
                 exact_weight: float = 0.15):
        """
        初始化高级搜索系统
        
        Args:
            vectorizer: 向量化器实例
            bm25_k1: BM25参数k1
            bm25_b: BM25参数b
            vector_weight: 向量匹配权重
            bm25_weight: BM25匹配权重
            exact_weight: 精确匹配权重
        """
        self.vectorizer = vectorizer
        self.bm25_k1 = bm25_k1
        self.bm25_b = bm25_b
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.exact_weight = exact_weight
        
        # 文档统计信息
        self.doc_count = 0
        self.avg_doc_length = 0
        self.doc_lengths = {}
        self.term_doc_freq = defaultdict(int)  # 词项文档频率
        self.documents = {}  # 存储文档内容
        
        # 初始化jieba
        jieba.initialize()
        
        # 在初始化时构建全局BM25索引
        if self.vectorizer:
            # 确保ChromaDB已初始化
            if not self.vectorizer.collection:
                try:
                    self.vectorizer.init_chromadb()
                except Exception as e:
                    print(f"ChromaDB初始化失败: {e}")
            
            # 构建BM25索引
            if self.vectorizer.collection:
                self.build_global_bm25_index()
            else:
                print("⚠️ ChromaDB未初始化，跳过BM25索引构建")
        
        print("高级搜索系统初始化完成")
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        文本预处理：分词、去停用词
        
        Args:
            text: 输入文本
            
        Returns:
            处理后的词项列表
        """
        # 基本清理
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 分词
        words = jieba.lcut(text)
        
        # 改进的停用词过滤
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        # 重要的单字符保留列表（主要是人名、地名等）
        important_single_chars = {'乔', '梁', '李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '高'}
        
        filtered_words = []
        for word in words:
            # 保留长度大于1的词
            if len(word) > 1 and word not in stop_words:
                filtered_words.append(word)
            # 保留重要的单字符
            elif len(word) == 1 and word in important_single_chars:
                filtered_words.append(word)
            # 保留数字和英文
            elif len(word) == 1 and (word.isdigit() or word.isalpha()):
                filtered_words.append(word)
        
        return filtered_words
    
    def extract_keywords_bm25(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        使用BM25算法抽取查询关键词
        
        Args:
            query: 查询文本
            top_k: 返回关键词数量
            
        Returns:
            关键词及其权重列表
        """
        # 使用jieba的TF-IDF关键词抽取（基于BM25思想）
        keywords = jieba.analyse.extract_tags(
            query, 
            topK=top_k, 
            withWeight=True,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vd', 'vn', 'a', 'ad', 'an')
        )
        
        # 补充自定义关键词抽取
        words = self.preprocess_text(query)
        word_freq = Counter(words)
        
        # 合并结果
        keyword_dict = {kw: weight for kw, weight in keywords}
        
        for word, freq in word_freq.items():
            if word not in keyword_dict and len(word) > 1:
                # 简单的权重计算
                keyword_dict[word] = freq * 0.5
        
        # 排序并返回top_k
        sorted_keywords = sorted(keyword_dict.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return sorted_keywords
    
    def build_bm25_index(self, documents: Dict[str, str]):
        """
        构建BM25索引
        
        Args:
            documents: 文档字典 {doc_id: content}
        """
        print("正在构建BM25索引...")
        
        self.documents = documents
        self.doc_count = len(documents)
        
        # 初始化BM25索引
        self.bm25_index = {}
        
        # 计算文档长度和词项统计
        total_length = 0
        term_docs = defaultdict(set)
        
        for doc_id, content in documents.items():
            words = self.preprocess_text(content)
            self.doc_lengths[doc_id] = len(words)
            total_length += len(words)
            
            # 构建文档的词项频率索引
            word_freq = Counter(words)
            self.bm25_index[doc_id] = word_freq
            
            # 统计词项出现的文档
            for word in set(words):
                term_docs[word].add(doc_id)
        
        # 计算平均文档长度
        self.avg_doc_length = total_length / self.doc_count if self.doc_count > 0 else 0
        
        # 计算词项文档频率
        for term, docs in term_docs.items():
            self.term_doc_freq[term] = len(docs)
        
        print(f"BM25索引构建完成：{self.doc_count}个文档，平均长度{self.avg_doc_length:.1f}")
        print(f"BM25索引包含{len(self.bm25_index)}个文档的词项频率信息")
    
    def calculate_bm25_score(self, query_terms: List[str], doc_id: str) -> float:
        """
        计算BM25得分
        
        Args:
            query_terms: 查询词项列表
            doc_id: 文档ID
            
        Returns:
            BM25得分
        """
        # 检查文档是否在BM25索引中
        if not hasattr(self, 'bm25_index') or not self.bm25_index:
            print(f"[DEBUG] BM25索引不存在或为空")
            return 0.0
            
        if doc_id not in self.bm25_index:
            # 改进的ID匹配策略
            matched_id = self._find_matching_bm25_id(doc_id)
            if matched_id:
                print(f"[BM25_FIX] 文档ID映射: {doc_id[:30]}... -> {matched_id[:30]}...")
                doc_id = matched_id
            else:
                print(f"[BM25_ERROR] 文档ID {doc_id[:30]}... 在BM25索引中未找到匹配，返回0分")
                return 0.0
        
        # 从BM25索引获取词频信息
        term_freq = self.bm25_index[doc_id]
        doc_length = self.doc_lengths.get(doc_id, 0)
        
        if doc_length == 0:
            return 0.0
        
        score = 0.0
        for term in query_terms:
            if term in term_freq:
                # 词频
                tf = term_freq[term]
                
                # 文档频率
                df = self.term_doc_freq.get(term, 0)
                if df == 0:
                    continue
                
                # IDF计算
                idf = math.log((self.doc_count - df + 0.5) / (df + 0.5))
                
                # BM25公式
                numerator = tf * (self.bm25_k1 + 1)
                denominator = tf + self.bm25_k1 * (1 - self.bm25_b + self.bm25_b * (doc_length / self.avg_doc_length))
                
                score += idf * (numerator / denominator)
        
        return score
    
    def _find_matching_bm25_id(self, target_id: str) -> str:
        """
        智能查找匹配的BM25索引ID
        
        Args:
            target_id: 目标文档ID
            
        Returns:
            匹配的BM25索引ID，如果没找到返回None
        """
        if not hasattr(self, 'bm25_index') or not self.bm25_index:
            return None
            
        # 0. 检查ID映射表
        if hasattr(self, '_id_mapping') and target_id in self._id_mapping:
            mapped_id = self._id_mapping[target_id]
            if mapped_id in self.bm25_index:
                return mapped_id
            
        # 1. 精确匹配
        if target_id in self.bm25_index:
            return target_id
            
        # 2. 标准化后匹配
        normalized_target = str(target_id).strip()
        if normalized_target in self.bm25_index:
            return normalized_target
            
        # 3. 子串匹配（双向）
        for bm25_id in self.bm25_index.keys():
            if target_id in bm25_id or bm25_id in target_id:
                return bm25_id
                
        # 4. 去除常见前缀/后缀后匹配
        cleaned_target = target_id.strip().replace('doc_', '').replace('chunk_', '')
        for bm25_id in self.bm25_index.keys():
            cleaned_bm25 = bm25_id.strip().replace('doc_', '').replace('chunk_', '')
            if cleaned_target == cleaned_bm25:
                return bm25_id
                
        # 5. 数字ID匹配（提取数字部分）
        import re
        target_numbers = re.findall(r'\d+', target_id)
        if target_numbers:
            target_num = target_numbers[-1]  # 使用最后一个数字
            for bm25_id in self.bm25_index.keys():
                bm25_numbers = re.findall(r'\d+', bm25_id)
                if bm25_numbers and bm25_numbers[-1] == target_num:
                    return bm25_id
                    
        return None
    
    def exact_match_score(self, query: str, document: str) -> float:
        """
        计算精确匹配得分
        
        Args:
            query: 查询文本
            document: 文档内容
            
        Returns:
            精确匹配得分
        """
        query_lower = query.lower()
        doc_lower = document.lower()
        
        score = 0.0
        
        # 完全匹配
        if query_lower in doc_lower:
            score += 1.0
        
        # 词汇匹配
        query_words = set(self.preprocess_text(query))
        doc_words = set(self.preprocess_text(document))
        
        if query_words:
            overlap = len(query_words & doc_words)
            score += overlap / len(query_words) * 0.8
        
        # 短语匹配
        query_phrases = [query[i:i+4] for i in range(len(query)-3)]
        phrase_matches = sum(1 for phrase in query_phrases if phrase in document)
        if query_phrases:
            score += phrase_matches / len(query_phrases) * 0.6
        
        return score

    def build_global_bm25_index(self):
        """
        构建全局BM25索引，确保ID格式一致性
        """
        print("正在构建全局BM25索引...")
        try:
            # 从ChromaDB获取所有文档
            if hasattr(self, 'collection') and self.collection:
                results = self.collection.get()
                documents = results['documents']
                ids = results['ids']
            elif hasattr(self, 'vectorizer') and self.vectorizer and hasattr(self.vectorizer, 'collection'):
                results = self.vectorizer.collection.get()
                documents = results['documents']
                ids = results['ids']
            else:
                print("❌ 无法访问ChromaDB collection")
                raise Exception("ChromaDB collection不可用")
            
            print(f"从ChromaDB获取到 {len(documents)} 个文档")
            
            # 标准化ID格式并构建文档字典
            normalized_docs = {}
            self._id_mapping = {}
            
            for doc_id, content in zip(ids, documents):
                # 统一ID格式，去除可能的格式差异
                normalized_id = str(doc_id).strip()
                normalized_docs[normalized_id] = content
                
                # 建立ID映射表用于调试
                if doc_id != normalized_id:
                    self._id_mapping[doc_id] = normalized_id
            
            # 构建BM25索引
            self.build_bm25_index(normalized_docs)
            
            if hasattr(self, '_id_mapping') and self._id_mapping:
                print(f"建立了 {len(self._id_mapping)} 个ID映射")
            
            print(f"全局BM25索引构建完成，包含 {len(self.bm25_index)} 个文档")
        except Exception as e:
            print(f"构建全局BM25索引失败: {e}")
            import traceback
            traceback.print_exc()
            self.bm25_index = {}
            self.doc_lengths = {}
            self.term_doc_freq = {}
            self.doc_count = 0
            self.avg_doc_length = 0
            self._id_mapping = {}

    def search_candidates(self, 
                         query: str, 
                         n_candidates: int = 50) -> List[Dict[str, Any]]:
        """
        搜索候选文档
        
        Args:
            query: 查询文本
            n_candidates: 候选文档数量
            
        Returns:
            候选文档列表
        """
        candidates = []
        
        # 提取查询关键词用于BM25计算
        keywords = self.extract_keywords_bm25(query, top_k=10)
        query_terms = [kw for kw, _ in keywords]
        
        # 1. 向量搜索
        if self.vectorizer and self.vectorizer.model:
            try:
                vector_results = self.vectorizer.search_similar_chunks(
                    query_text=query,
                    n_results=n_candidates
                )
                
                if vector_results and 'documents' in vector_results:
                    for i, (doc, metadata, doc_id) in enumerate(zip(
                        vector_results['documents'][0],
                        vector_results['metadatas'][0],
                        vector_results['ids'][0]
                    )):
                        # 计算BM25得分
                        bm25_score = self.calculate_bm25_score(query_terms, doc_id)
                        exact_score = self.exact_match_score(query, doc)
                        
                        candidates.append({
                            'id': doc_id,
                            'content': doc,
                            'metadata': metadata,
                            'vector_rank': i + 1,
                            'vector_score': 1.0 / (i + 1),  # 简单的排名得分
                            'bm25_score': bm25_score,
                            'exact_score': exact_score
                        })
                        
            except Exception as e:
                print(f"向量搜索失败: {e}")
        
        # 注释：已移除时间范围搜索补充逻辑
        
        return candidates[:n_candidates]
    
    def rerank_with_bre(self, 
                        query: str, 
                        candidates: List[Dict[str, Any]], 
                        top_k: int = 10) -> List[Dict[str, Any]]:
        """
        使用BRE（BM25 + Retrieval + Exact）进行重排序
        
        Args:
            query: 查询文本
            candidates: 候选文档列表
            top_k: 返回文档数量
            
        Returns:
            重排序后的文档列表
        """
        print(f"正在对{len(candidates)}个候选文档进行BRE重排序...")
        
        # 1. 提取查询关键词
        keywords = self.extract_keywords_bm25(query, top_k=10)
        query_terms = [kw for kw, _ in keywords]
        
        print(f"提取的关键词: {query_terms}")
        
        # 2. 使用全局BM25索引计算得分 (不再构建临时索引)
        
        # 3. 使用已计算的得分或重新计算
        scored_candidates = []
        for candidate in candidates:
            # 使用候选文档中已计算的得分，如果没有则重新计算
            vector_score = candidate.get('vector_score', 0.0)
            bm25_score = candidate.get('bm25_score')
            exact_score = candidate.get('exact_score')
            
            # 智能处理BM25分数：优先保留有效的预计算分数
            if bm25_score is None:
                bm25_score = self.calculate_bm25_score(query_terms, candidate['id'])
            elif bm25_score == 0.0:
                # 如果预计算分数为0，尝试重新计算
                recalc_bm25 = self.calculate_bm25_score(query_terms, candidate['id'])
                if recalc_bm25 > 0:
                    print(f"[BM25_FIX] 重新计算BM25分数: {bm25_score} -> {recalc_bm25}")
                    bm25_score = recalc_bm25
                    
            if exact_score is None:
                exact_score = self.exact_match_score(query, candidate['content'])
            
            scored_candidate = candidate.copy()
            scored_candidate.update({
                'final_score': 0.0,  # 将在后面计算
                'score_breakdown': {
                    'vector': vector_score,
                    'bm25': bm25_score,
                    'exact': exact_score
                }
            })
            scored_candidates.append(scored_candidate)

        # 4. 归一化BM25并计算最终得分
        all_bm25_scores = [c['score_breakdown']['bm25'] for c in scored_candidates]
        max_bm25_score = max(all_bm25_scores) if all_bm25_scores else 1.0
        if max_bm25_score == 0: max_bm25_score = 1.0

        for candidate in scored_candidates:
            scores = candidate['score_breakdown']
            norm_bm25 = scores['bm25'] / max_bm25_score
            
            final_score = (
                self.vector_weight * scores['vector'] +
                self.bm25_weight * norm_bm25 +
                self.exact_weight * scores['exact']
            )
            candidate['final_score'] = final_score
            candidate['score_breakdown']['bm25_norm'] = norm_bm25
            
            print(f"文档 {candidate['id'][:20]}... - 向量:{scores['vector']:.4f}, BM25:{scores['bm25']:.4f}({norm_bm25:.4f}), 精确:{scores['exact']:.4f}, 综合:{final_score:.4f}")

        # 5. 按最终得分排序
        reranked = sorted(scored_candidates, key=lambda x: x['final_score'], reverse=True)
        
        # 添加score键以保持兼容性
        for candidate in reranked:
            candidate['score'] = candidate['final_score']
        
        # 6. 过滤和截断
        min_threshold = 0.001  # 降低阈值，避免过度过滤有效结果
        filtered_reranked = [r for r in reranked if r['final_score'] > min_threshold]
        
        print(f"重排序完成，原始{len(reranked)}个，过滤后{len(filtered_reranked)}个，返回前{min(top_k, len(filtered_reranked))}个结果")
        
        # 输出筛选后文档的详细内容
        final_results = filtered_reranked[:top_k] if len(filtered_reranked) >= max(1, top_k // 2) else reranked[:top_k]
        
        print("\n=== 筛选后文档详细内容 ===")
        for i, doc in enumerate(final_results, 1):
            print(f"\n--- 文档 {i} ---")
            print(f"文档ID: {doc.get('id', 'N/A')}")
            print(f"综合得分: {doc.get('final_score', 0):.4f}")
            
            # 显示得分详情
            score_breakdown = doc.get('score_breakdown', {})
            if score_breakdown:
                print(f"得分详情:")
                print(f"  - 向量得分: {score_breakdown.get('vector', 0):.4f}")
                print(f"  - BM25得分: {score_breakdown.get('bm25', 0):.4f}")
                print(f"  - 精确匹配得分: {score_breakdown.get('exact', 0):.4f}")
            
            # 显示文档内容
            content = doc.get('content', '')
            print(f"文档内容: {content[:200]}{'...' if len(content) > 200 else ''}")
            
            # 显示元数据
            metadata = doc.get('metadata', {})
            if metadata:
                print(f"元数据: {metadata}")
        print("=== 文档详细内容结束 ===\n")
        
        # 如果过滤后结果太少，返回未经过滤的重排序结果
        if len(filtered_reranked) < max(1, top_k // 2):
            print(f"过滤后结果太少({len(filtered_reranked)})，返回未经过滤的重排序结果")
            return reranked[:top_k]
        
        return filtered_reranked[:top_k]
    
    def generate_prompt(self, 
                       query: str, 
                       search_results: List[Dict[str, Any]], 
                       max_context_length: int = 2000) -> str:
        """
        生成包含搜索结果的提示词
        
        Args:
            query: 用户查询
            search_results: 搜索结果
            max_context_length: 最大上下文长度
            
        Returns:
            完整的提示词
        """
        # 构建上下文
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results):
            content = result['content']
            metadata = result.get('metadata', {})
            
            # 格式化单个结果
            source_file = metadata.get('source_file', '')
            # 提取文件名（去掉路径和扩展名）
            if source_file:
                file_name = os.path.basename(source_file).replace('.txt', '').replace('_processed.json', '')
            else:
                file_name = '未知来源'
            
            # 检查是否为QA格式数据
            if 'question' in metadata and 'answer' in metadata:
                result_text = f"""[文档{i+1} - 来源文件: {file_name}]
问题: {metadata.get('question', '')}
答案: {metadata.get('answer', '')}
相关度得分: {result.get('final_score', 0):.3f}
"""
            else:
                result_text = f"""[文档{i+1} - 来源文件: {file_name}]
时间: {metadata.get('start_time', '')} - {metadata.get('end_time', '')}
说话人: {metadata.get('speakers', '未知')}
内容: {content}
相关度得分: {result.get('final_score', 0):.3f}
"""
            
            # 检查长度限制
            if current_length + len(result_text) > max_context_length:
                break
            
            context_parts.append(result_text)
            current_length += len(result_text)
        
        context = "\n".join(context_parts)
        
        # 生成完整提示词
        prompt = f"""你是一个专业的问答助手，请基于以下检索到的相关文档内容来回答用户的问题。

用户问题：{query}

相关文档内容：
{context}

请根据上述文档内容，准确、详细地回答用户的问题。如果文档中没有足够的信息来回答问题，请明确说明。回答时请：
1. 直接回答问题的核心内容
2. **必须明确标注信息来源**：引用时请使用"根据[来源文件名]的内容"格式（如：根据chap01的内容、根据chap02的内容等）
3. 如果涉及多个文档来源，请分别标明每个信息点的具体来源
4. 如果涉及多个说话人的观点，请分别说明并标注来源
5. 保持回答的客观性和准确性
6. 优先使用文件来源名称，避免使用"文档1"、"文档2"等编号

回答："""
        
        return prompt
    
    def search(self, 
               query: str, 
               top_k: int = 10,
               max_context_length: int = 2000) -> Dict[str, Any]:
        """
        执行完整的搜索流程
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            max_context_length: 最大上下文长度
            
        Returns:
            搜索结果和提示词
        """
        print(f"\n=== 开始搜索：{query} ===")
        start_time_search = datetime.now()
        
        # 1. 搜索候选文档
        candidates = self.search_candidates(
            query=query,
            n_candidates=50
        )
        
        print(f"找到{len(candidates)}个候选文档")
        
        if not candidates:
            return {
                'query': query,
                'results': [],
                'prompt': f"抱歉，没有找到与'{query}'相关的内容。",
                'search_time': 0,
                'total_candidates': 0
            }
        
        # 3. BRE重排序
        reranked_results = self.rerank_with_bre(query, candidates, top_k=top_k)
        
        # 3. 生成提示词
        prompt = self.generate_prompt(
            query=query,
            search_results=reranked_results,
            max_context_length=max_context_length
        )
        
        # 4. 计算搜索时间
        search_time = (datetime.now() - start_time_search).total_seconds()
        
        print(f"搜索完成，耗时{search_time:.2f}秒")
        
        return {
            'query': query,
            'results': reranked_results,
            'prompt': prompt,
            'search_time': search_time,
            'total_candidates': len(candidates),
            'keywords_extracted': [kw for kw, _ in self.extract_keywords_bm25(query)]
        }
    
    def batch_search(self, 
                    queries: List[str], 
                    top_k: int = 5) -> List[Dict[str, Any]]:
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
            print(f"\n处理查询 {i+1}/{len(queries)}: {query}")
            result = self.search(query, top_k=top_k)
            results.append(result)
        
        return results


def demo_advanced_search():
    """
    演示高级搜索系统
    """
    print("=== 高级搜索系统演示 ===")
    
    # 1. 初始化向量化器
    vectorizer = ChunkVectorizer(
        model_name="BAAI/bge-small-zh-v1.5",
        collection_name="qa_system_chunks"
    )
    
    try:
        # 初始化ChromaDB
        vectorizer.init_chromadb("e:\\PyProjects\\QASystem\\chroma_db")
        
        # 检查数据
        info = vectorizer.get_collection_info()
        if info.get('total_records', 0) == 0:
            print("警告: 没有找到向量数据，请先运行向量化程序")
            return
        
        print(f"加载了{info.get('total_records', 0)}条向量数据")
        
        # 加载模型
        vectorizer.load_model()
        
        # 2. 初始化搜索系统
        search_system = AdvancedSearchSystem(
            vectorizer=vectorizer,
            vector_weight=0.4,
            bm25_weight=0.3,
            exact_weight=0.3
        )
        
        # 3. 测试查询
        test_queries = [
            "自然语言处理的应用有哪些？",
            "机器学习在数据分析中的作用",
            "深度学习模型的优势",
            "人工智能技术发展趋势"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            result = search_system.search(
                query=query,
                top_k=3,
                max_context_length=1500
            )
            
            print(f"查询: {result['query']}")
            print(f"搜索时间: {result['search_time']:.2f}秒")
            print(f"候选文档数: {result['total_candidates']}")
            print(f"提取关键词: {result['keywords_extracted']}")
            
            print("\n=== 搜索结果 ===")
            for i, res in enumerate(result['results']):
                print(f"\n结果{i+1}:")
                print(f"  文档ID: {res['id']}")
                print(f"  综合得分: {res['final_score']:.3f}")
                print(f"  得分详情: 向量={res['score_breakdown']['vector']:.3f}, "
                      f"BM25={res['score_breakdown']['bm25']:.3f}, "
                      f"精确={res['score_breakdown']['exact']:.3f}")
                print(f"  时间: {res['metadata'].get('start_time', '')} - {res['metadata'].get('end_time', '')}")
                print(f"  说话人: {res['metadata'].get('speakers', '未知')}")
                print(f"  内容预览: {res['content'][:100]}...")
            
            print("\n=== 生成的提示词 ===")
            print(result['prompt'][:500] + "..." if len(result['prompt']) > 500 else result['prompt'])
            
            print("\n" + "="*60)
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_advanced_search()