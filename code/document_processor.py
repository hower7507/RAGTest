import re
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

class DocumentProcessor:
    """
    文档处理器：用于读取、分块和提取元数据
    支持说话人、时间戳、内容的提取和动态分割
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_content = ""
        self.segments = []
        
    def read_file(self) -> str:
        """
        读取文件内容
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.raw_content = file.read()
            print(f"成功读取文件: {self.file_path}")
            return self.raw_content
        except FileNotFoundError:
            print(f"文件未找到: {self.file_path}")
            return ""
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return ""
    
    def extract_segments(self) -> List[Dict]:
        """
        使用正则表达式提取说话人、时间戳和内容
        """
        if not self.raw_content:
            self.read_file()
        
        # 正则表达式模式：匹配"说话人X 时间戳"格式
        pattern = r'说话人(\d+)\s+(\d{1,2}:\d{2}(?::\d{2})?)'  
        
        # 分割文本
        parts = re.split(pattern, self.raw_content)
        
        segments = []
        
        # 处理分割后的部分
        for i in range(1, len(parts), 3):  # 每3个元素为一组：说话人编号、时间戳、内容
            if i + 2 < len(parts):
                speaker_id = parts[i]
                timestamp = parts[i + 1]
                content = parts[i + 2].strip()
                
                # 过滤掉空内容或只有标点符号的内容
                if content and len(content.strip()) > 0:
                    segment = {
                        'speaker_id': f"说话人{speaker_id}",
                        'timestamp': timestamp,
                        'content': content,
                        'word_count': len(content),
                        'segment_id': len(segments) + 1
                    }
                    segments.append(segment)
        
        self.segments = segments
        print(f"提取到 {len(segments)} 个有效片段")
        return segments
    
    def time_to_seconds(self, time_str: str) -> int:
        """
        将时间字符串转换为秒数
        """
        parts = time_str.split(':')
        if len(parts) == 2:  # MM:SS格式
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS格式
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    
    def dynamic_chunking(self, 
                        max_chunk_size: int = 500,
                        time_gap_threshold: int = 30,
                        speaker_change_split: bool = True) -> List[Dict]:
        """
        动态分割策略：
        1. 基于内容长度分割
        2. 基于时间间隔分割
        3. 基于说话人变化分割
        4. 保留原始元数据
        """
        if not self.segments:
            self.extract_segments()
        
        chunks = []
        current_chunk = {
            'segments': [],
            'total_words': 0,
            'start_time': None,
            'end_time': None,
            'speakers': set(),
            'chunk_id': 1
        }
        
        for i, segment in enumerate(self.segments):
            # 检查是否需要开始新的块
            should_split = False
            
            # 1. 内容长度检查
            if current_chunk['total_words'] + segment['word_count'] > max_chunk_size:
                should_split = True
                
            # 2. 时间间隔检查
            if current_chunk['segments']:
                last_segment = current_chunk['segments'][-1]
                current_time = self.time_to_seconds(segment['timestamp'])
                last_time = self.time_to_seconds(last_segment['timestamp'])
                
                if current_time - last_time > time_gap_threshold:
                    should_split = True
            
            # 3. 说话人变化检查
            if speaker_change_split and current_chunk['segments']:
                last_speaker = current_chunk['segments'][-1]['speaker_id']
                if segment['speaker_id'] != last_speaker and current_chunk['total_words'] > 100:
                    should_split = True
            
            # 如果需要分割且当前块不为空，保存当前块
            if should_split and current_chunk['segments']:
                current_chunk['speakers'] = list(current_chunk['speakers'])
                chunks.append(current_chunk.copy())
                
                # 开始新块
                current_chunk = {
                    'segments': [],
                    'total_words': 0,
                    'start_time': None,
                    'end_time': None,
                    'speakers': set(),
                    'chunk_id': len(chunks) + 1
                }
            
            # 添加当前片段到块中
            current_chunk['segments'].append(segment)
            current_chunk['total_words'] += segment['word_count']
            current_chunk['speakers'].add(segment['speaker_id'])
            
            # 更新时间范围
            if current_chunk['start_time'] is None:
                current_chunk['start_time'] = segment['timestamp']
            current_chunk['end_time'] = segment['timestamp']
        
        # 添加最后一个块
        if current_chunk['segments']:
            current_chunk['speakers'] = list(current_chunk['speakers'])
            chunks.append(current_chunk)
        
        print(f"动态分割完成，共生成 {len(chunks)} 个块")
        return chunks
    
    def save_results(self, chunks: List[Dict], output_file: str = None):
        """
        保存处理结果到JSON文件
        """
        if output_file is None:
            output_file = self.file_path.replace('.txt', '_processed.json')
        
        result = {
            'source_file': self.file_path,
            'processing_time': datetime.now().isoformat(),
            'total_segments': len(self.segments),
            'total_chunks': len(chunks),
            'chunks': chunks
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {output_file}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def print_summary(self, chunks: List[Dict]):
        """
        打印处理摘要
        """
        print("\n=== 文档处理摘要 ===")
        print(f"源文件: {self.file_path}")
        print(f"总片段数: {len(self.segments)}")
        print(f"总块数: {len(chunks)}")
        
        print("\n=== 块详情 ===")
        for chunk in chunks:
            speakers = ', '.join(chunk['speakers'])
            print(f"块 {chunk['chunk_id']}: {chunk['start_time']}-{chunk['end_time']}, "
                  f"片段数: {len(chunk['segments'])}, 字数: {chunk['total_words']}, "
                  f"说话人: {speakers}")
    
    def process_document(self, 
                        max_chunk_size: int = 500,
                        time_gap_threshold: int = 30,
                        speaker_change_split: bool = True,
                        save_output: bool = True) -> List[Dict]:
        """
        完整的文档处理流程
        """
        print("开始处理文档...")
        
        # 1. 读取文件
        self.read_file()
        
        # 2. 提取片段
        self.extract_segments()
        
        # 3. 动态分块
        chunks = self.dynamic_chunking(
            max_chunk_size=max_chunk_size,
            time_gap_threshold=time_gap_threshold,
            speaker_change_split=speaker_change_split
        )
        
        # 4. 打印摘要
        self.print_summary(chunks)
        
        # 5. 保存结果
        if save_output:
            self.save_results(chunks)
        
        return chunks


def main():
    """
    主函数：演示文档处理功能
    """
    # 文件路径
    file_path = "e:\\PyProjects\\QASystem\\data\\chap01.txt"
    
    # 创建处理器实例
    processor = DocumentProcessor(file_path)
    
    # 处理文档
    chunks = processor.process_document(
        max_chunk_size=500,      # 最大块大小（字符数）
        time_gap_threshold=30,   # 时间间隔阈值（秒）
        speaker_change_split=True # 是否在说话人变化时分割
    )
    
    # 显示前几个块的详细内容
    print("\n=== 前3个块的详细内容 ===")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- 块 {chunk['chunk_id']} ---")
        print(f"时间范围: {chunk['start_time']} - {chunk['end_time']}")
        print(f"说话人: {', '.join(chunk['speakers'])}")
        print(f"片段数: {len(chunk['segments'])}")
        print(f"总字数: {chunk['total_words']}")
        print("内容预览:")
        for segment in chunk['segments'][:2]:  # 只显示前2个片段
            print(f"  {segment['speaker_id']} {segment['timestamp']}: {segment['content'][:50]}...")


if __name__ == "__main__":
    main()