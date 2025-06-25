import json
import chromadb
from FlagEmbedding import FlagModel
from typing import List, Dict, Any
import os
from datetime import datetime, timedelta
import re

class ChunkVectorizer:
    """
    文档块向量化器：使用FlagEmbedding对文档块进行向量化并存储到ChromaDB
    支持时间戳转换，便于时间范围查询
    """
    
    def __init__(self, model_name: str = "e:\\PyProjects\\QASystem\\code\\model", collection_name: str = "qa_system_chunks"):
        """
        初始化向量化器
        
        Args:
            model_name: FlagEmbedding模型名称或本地路径
            collection_name: ChromaDB集合名称
        """
        self.model_name = model_name
        self.collection_name = collection_name
        self.model = None
        self.client = None
        self.collection = None
        
    def load_model(self):
        """
        加载FlagEmbedding模型
        """
        try:
            print(f"正在加载模型: {self.model_name}")
            self.model = FlagModel(self.model_name, 
                                 query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                                 use_fp16=True)  # 使用fp16加速
            print("模型加载成功")
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("请确保已安装FlagEmbedding: pip install FlagEmbedding")
            raise
    
    def init_chromadb(self, persist_directory: str = "./chroma_db"):
        """
        初始化ChromaDB客户端和集合
        
        Args:
            persist_directory: ChromaDB持久化目录
        """
        try:
            print(f"正在初始化ChromaDB，持久化目录: {persist_directory}")
            
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # 获取或创建集合
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"找到现有集合: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "QA System document chunks with embeddings"}
                )
                print(f"创建新集合: {self.collection_name}")
                
        except Exception as e:
            print(f"ChromaDB初始化失败: {e}")
            print("请确保已安装chromadb: pip install chromadb")
            raise
    
    def load_processed_data(self, json_file_path: str) -> Dict[str, Any]:
        """
        加载处理后的JSON数据
        支持传统的对话数据和问答对数据
        
        Args:
            json_file_path: JSON文件路径
            
        Returns:
            加载的数据字典
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"成功加载数据文件: {json_file_path}")
            print(f"总块数: {data.get('total_chunks', 0)}")
            
            # 检查数据类型
            chunk_type = data.get('chunk_type', 'traditional')
            print(f"数据类型: {chunk_type}")
            
            return data
        except FileNotFoundError:
            print(f"文件未找到: {json_file_path}")
            raise
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            raise
    
    def extract_chunk_content(self, chunk: Dict[str, Any]) -> str:
        """
        从块中提取文本内容
        支持传统对话格式和问答对格式
        
        Args:
            chunk: 单个chunk数据
            
        Returns:
            拼接后的完整文本
        """
        # 检查是否是问答对格式
        if chunk.get('chunk_type') == 'qa_pair':
            # 问答对格式：使用combined_content
            return chunk.get('combined_content', '')
        elif 'segments' in chunk:
            # 传统格式：包含多个片段
            segments = chunk.get('segments', [])
            content_parts = []
            
            for segment in segments:
                content = segment.get('content', '').strip()
                if content:
                    content_parts.append(content)
            
            # 使用空格连接各个segment的内容
            full_content = ' '.join(content_parts)
            return full_content
        else:
            # 简化格式：直接包含内容
            return chunk.get('content', '')
    
    def time_to_seconds(self, time_str: str) -> int:
        """
        将时间字符串转换为秒数时间戳
        
        Args:
            time_str: 时间字符串，格式如 "00:01:30" 或 "01:30"
            
        Returns:
            秒数时间戳
        """
        if not time_str or time_str.strip() == '':
            return 0
            
        try:
            # 清理时间字符串
            time_str = time_str.strip()
            
            # 支持多种时间格式
            if re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):  # HH:MM:SS
                parts = time_str.split(':')
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            elif re.match(r'^\d{1,2}:\d{2}$', time_str):  # MM:SS 或 HH:MM
                parts = time_str.split(':')
                if int(parts[0]) >= 60:  # 假设是 HH:MM 格式
                    hours, minutes, seconds = int(parts[0]), int(parts[1]), 0
                else:  # 假设是 MM:SS 格式
                    hours, minutes, seconds = 0, int(parts[0]), int(parts[1])
            else:
                print(f"警告: 无法解析时间格式: {time_str}")
                return 0
                
            return hours * 3600 + minutes * 60 + seconds
            
        except Exception as e:
            print(f"时间转换错误 '{time_str}': {e}")
            return 0
    
    def seconds_to_time(self, seconds: int) -> str:
        """
        将秒数时间戳转换为时间字符串
        
        Args:
            seconds: 秒数时间戳
            
        Returns:
            时间字符串，格式为 "HH:MM:SS"
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def prepare_metadata(self, chunk: Dict[str, Any], source_file: str) -> Dict[str, Any]:
        """
        准备ChromaDB存储的元数据
        支持传统对话格式和问答对格式
        
        Args:
            chunk: 单个chunk数据
            source_file: 源文件路径
            
        Returns:
            元数据字典
        """
        metadata = {
            'chunk_id': chunk.get('chunk_id', 0),
            'source_file': source_file,
            'created_at': datetime.now().isoformat()
        }
        
        chunk_type = chunk.get('chunk_type', 'traditional')
        metadata['chunk_type'] = chunk_type

        if chunk_type == 'qa_pair':
            metadata['question'] = chunk.get('question', '')
            metadata['answer'] = chunk.get('answer', '')
            metadata['keywords'] = ', '.join(chunk.get('keywords', []))
            metadata['word_count'] = chunk.get('word_count', 0)
        elif chunk_type == 'general_text':
            # 从 chunk 的元数据中获取 source
            source = chunk.get('metadata', {}).get('source', '')
            metadata['source'] = source
            metadata['word_count'] = chunk.get('word_count', 0)
        else: # traditional
            metadata['chunk_type'] = 'traditional'
            
            start_time_str = chunk.get('start_time', '')
            end_time_str = chunk.get('end_time', '')
            
            # 转换时间为时间戳
            start_timestamp = self.time_to_seconds(start_time_str)
            end_timestamp = self.time_to_seconds(end_time_str)
            
            metadata.update({
                'speakers': chunk.get('speakers', []),
                'start_time': start_time_str,  # 保留原始时间字符串
                'end_time': end_time_str,      # 保留原始时间字符串
                'start_timestamp': start_timestamp,  # 新增：开始时间戳（秒）
                'end_timestamp': end_timestamp,      # 新增：结束时间戳（秒）
                'duration': end_timestamp - start_timestamp,  # 新增：持续时间（秒）
                'total_words': chunk.get('total_words', 0),
                'segment_count': len(chunk.get('segments', []))
            })
            
            # 将speakers列表转换为字符串（ChromaDB元数据限制）
            if isinstance(metadata['speakers'], list):
                metadata['speakers'] = ', '.join(metadata['speakers'])
            
        return metadata
    
    def vectorize_chunks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        对所有chunks进行向量化
        
        Args:
            data: 完整的数据字典
            
        Returns:
            向量化结果列表
        """
        chunks = data.get('chunks', [])
        source_file = data.get('source_file', '')
        
        if not chunks:
            print("没有找到chunks数据")
            return []
        
        print(f"开始向量化 {len(chunks)} 个chunks")
        
        # 提取所有chunk的文本内容
        chunk_texts = []
        chunk_metadata_list = []
        chunk_ids = []
        
        for chunk in chunks:
            # 提取文本内容
            content = self.extract_chunk_content(chunk)
            if not content.strip():
                print(f"警告: Chunk {chunk.get('chunk_id', 'unknown')} 内容为空，跳过")
                continue
                
            chunk_texts.append(content)
            
            # 准备元数据
            metadata = self.prepare_metadata(chunk, source_file)
            chunk_metadata_list.append(metadata)
            
            # 使用chunk_id作为主键
            chunk_id = chunk.get('chunk_id')
            if not chunk_id:
                # 如果没有chunk_id，生成一个，但这通常不应该发生
                chunk_id = f"generated_id_{len(chunk_ids) + 1}"
                print(f"警告: Chunk缺少ID，已生成: {chunk_id}")
            chunk_ids.append(chunk_id)
        
        if not chunk_texts:
            print("没有有效的chunk文本内容")
            return []
        
        # 批量生成向量
        print("正在生成向量...")
        try:
            embeddings = self.model.encode(chunk_texts)
            print(f"成功生成 {len(embeddings)} 个向量")
        except Exception as e:
            print(f"向量生成失败: {e}")
            raise
        
        # 组装结果
        vectorized_chunks = []
        for i, (chunk_id, text, embedding, metadata) in enumerate(
            zip(chunk_ids, chunk_texts, embeddings, chunk_metadata_list)
        ):
            vectorized_chunk = {
                'id': chunk_id,
                'document': text,
                'embedding': embedding.tolist(),  # 转换为列表格式
                'metadata': metadata
            }
            vectorized_chunks.append(vectorized_chunk)
            
            if (i + 1) % 10 == 0:
                print(f"已处理 {i + 1}/{len(chunk_texts)} 个chunks")
        
        return vectorized_chunks
    
    def store_to_chromadb(self, vectorized_chunks: List[Dict[str, Any]]) -> bool:
        """
        将向量化结果存储到ChromaDB
        
        Args:
            vectorized_chunks: 向量化结果列表
            
        Returns:
            存储是否成功
        """
        if not vectorized_chunks:
            print("没有数据需要存储")
            return False
        
        try:
            print(f"正在存储 {len(vectorized_chunks)} 条记录到ChromaDB")
            
            # 检查是否有重复的chunk_id
            existing_ids = set()
            try:
                # 获取现有的所有ID
                existing_data = self.collection.get()
                existing_ids = set(existing_data['ids'])
                print(f"发现 {len(existing_ids)} 条现有记录")
            except:
                print("集合为空或获取现有数据失败")
            
            # 过滤掉重复的记录
            new_chunks = []
            updated_chunks = []
            
            for chunk in vectorized_chunks:
                if chunk['id'] in existing_ids:
                    updated_chunks.append(chunk)
                else:
                    new_chunks.append(chunk)
            
            # 删除需要更新的记录
            if updated_chunks:
                update_ids = [chunk['id'] for chunk in updated_chunks]
                print(f"删除 {len(update_ids)} 条重复记录")
                self.collection.delete(ids=update_ids)
            
            # 添加所有记录（新增+更新）
            all_chunks = new_chunks + updated_chunks
            
            if all_chunks:
                ids = [chunk['id'] for chunk in all_chunks]
                documents = [chunk['document'] for chunk in all_chunks]
                embeddings = [chunk['embedding'] for chunk in all_chunks]
                metadatas = [chunk['metadata'] for chunk in all_chunks]
                
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                
                print(f"成功存储 {len(new_chunks)} 条新记录")
                print(f"成功更新 {len(updated_chunks)} 条记录")
                print(f"总计处理 {len(all_chunks)} 条记录")
            
            return True
            
        except Exception as e:
            print(f"存储到ChromaDB失败: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        获取集合信息
        
        Returns:
            集合信息字典
        """
        try:
            count = self.collection.count()
            
            # 获取一些示例数据
            sample_data = self.collection.get(limit=3)
            
            info = {
                'collection_name': self.collection_name,
                'total_records': count,
                'sample_ids': sample_data.get('ids', []),
                'sample_metadata': sample_data.get('metadatas', [])
            }
            
            return info
            
        except Exception as e:
            print(f"获取集合信息失败: {e}")
            return {}
    
    def search_similar_chunks(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        搜索相似的chunks
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            # 对查询文本进行向量化
            query_embedding = self.model.encode_queries([query_text])  # 使用encode_queries进行查询编码
            
            # 在ChromaDB中搜索
            search_params = {
                "query_embeddings": query_embedding.tolist(),
                "n_results": n_results
            }
            
            results = self.collection.query(**search_params)
            
            return results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return {}
    
    def search_by_time_range(self, start_time: str, end_time: str, n_results: int = 10) -> Dict[str, Any]:
        """
        按时间范围搜索chunks
        
        Args:
            start_time: 开始时间，格式如 "10:00" 或 "01:10:30"
            end_time: 结束时间，格式如 "11:00" 或 "01:20:30"
            n_results: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            start_timestamp = self.time_to_seconds(start_time)
            end_timestamp = self.time_to_seconds(end_time)
            
            # 构建时间范围查询条件
            where_clause = {
                "$and": [
                    {"start_timestamp": {"$gte": start_timestamp}},
                    {"end_timestamp": {"$lte": end_timestamp}}
                ]
            }
            
            # 获取指定时间范围内的所有chunks
            results = self.collection.get(
                where=where_clause,
                limit=n_results
            )
            
            print(f"时间范围 {start_time} - {end_time} 内找到 {len(results.get('ids', []))} 个chunks")
            
            return results
            
        except Exception as e:
            print(f"时间范围搜索失败: {e}")
            return {}
    
    def process_and_store(self, json_file_path: str) -> bool:
        """
        完整的处理和存储流程
        
        Args:
            json_file_path: 输入JSON文件路径
            persist_directory: ChromaDB持久化目录
            
        Returns:
            处理是否成功
        """
        try:
            print(f"\n=== 开始处理文件: {json_file_path} ===")
            
            # 1. 加载数据
            data = self.load_processed_data(json_file_path)
            
            # 2. 向量化
            vectorized_chunks = self.vectorize_chunks(data)
            
            # 3. 存储到ChromaDB
            success = self.store_to_chromadb(vectorized_chunks)
            
            if success:
                print(f"=== 文件处理成功: {json_file_path} ===")
                return True
            else:
                print(f"=== 文件处理失败: {json_file_path} ===")
                return False
                
        except Exception as e:
            print(f"处理文件 {json_file_path} 失败: {e}")
            return False


def main():
    """
    主函数：演示向量化和存储功能
    """
    # 配置参数
    json_file_paths = [
        "e:\\PyProjects\\QASystem\\data\\chap01_processed.json",
        "e:\\PyProjects\\QASystem\\data\\chap02_processed.json",
        "e:\\PyProjects\\QASystem\\data\\chap03_semantic_processed.json"
    ]
    persist_directory = "e:\\PyProjects\\QASystem\\chroma_db"
    model_name = "e:\\PyProjects\\QASystem\\code\\model"
    collection_name = "qa_system_chunks"
    
    # 创建向量化器实例
    vectorizer = ChunkVectorizer(
        model_name=model_name,
        collection_name=collection_name
    )
    
    try:
        print("=== 开始文档向量化和存储流程 ===")
        
        # 1. 加载模型
        vectorizer.load_model()
        
        # 2. 初始化ChromaDB
        vectorizer.init_chromadb(persist_directory)
        
        # 3. 循环处理所有JSON文件
        all_successful = True
        for json_file_path in json_file_paths:
            success = vectorizer.process_and_store(json_file_path)
            if not success:
                all_successful = False
        
        if all_successful:
            print("\n=== 所有文件处理完成 ===")
        else:
            print("\n=== 操作中有部分文件处理失败 ===")
            
        # 4. 显示最终集合信息
        info = vectorizer.get_collection_info()
        print("\n=== 最终集合信息 ===")
        print(f"集合名称: {info.get('collection_name', 'unknown')}")
        print(f"总记录数: {info.get('total_records', 0)}")
        
        # 示例：搜索相似的chunks
        print("\n=== 示例搜索 ===")
        query_text = "DeepSeek的优势是什么？"
        search_results = vectorizer.search_similar_chunks(query_text, n_results=3)
        
        if search_results and search_results.get('ids', [[]])[0]:
            print(f"查询 '{query_text}' 的结果:")
            for i, (doc, metadata, distance) in enumerate(zip(
                search_results['documents'][0],
                search_results['metadatas'][0],
                search_results['distances'][0]
            )):
                print(f"  结果 {i+1}:")
                print(f"    Chunk ID: {metadata.get('chunk_id', 'unknown')}")
                print(f"    内容: {doc[:100]}...")
                print(f"    距离: {distance:.4f}")
        else:
            print("搜索无结果")

    except Exception as e:
        print(f"主流程发生严重错误: {e}")

if __name__ == "__main__":
    main()