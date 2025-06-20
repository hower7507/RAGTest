import json
import os
from datetime import datetime

class PlainTextProcessor:
    """
    纯文本文档处理器。
    - 读取 .txt 文件。
    - 将文本按段落和固定大小切块。
    - 保存为与 vectorize_chunks.py 兼容的JSON格式。
    """
    
    def __init__(self, file_path: str, chunk_size: int = 400, overlap: int = 50):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.content = ""
        self.chunks = []
        self.chunk_size = chunk_size
        self.overlap = overlap

    def read_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read().strip()
            print(f"成功读取文件: {self.file_path}")
        except Exception as e:
            print(f"读取文件 '{self.file_path}' 时出错: {e}")
            raise

    def create_chunks(self):
        if not self.content:
            print("内容为空，无法创建块。")
            return

        # 先按段落分割，可以保留一些语义结构
        paragraphs = [p.strip() for p in self.content.split('\n') if p.strip()]
        
        chunk_id_counter = 1
        for para in paragraphs:
            if len(para) <= self.chunk_size:
                # 如果段落较短，直接作为一个块
                self.chunks.append({
                    'chunk_id': f"{self.file_name}-{chunk_id_counter}",
                    'content': para,
                    'word_count': len(para),
                    'chunk_type': 'general_text',
                    'metadata': {
                        'source': self.file_name
                    }
                })
                chunk_id_counter += 1
            else:
                # 如果段落太长，使用滑动窗口切分
                start = 0
                while start < len(para):
                    end = start + self.chunk_size
                    chunk_content = para[start:end]
                    
                    self.chunks.append({
                        'chunk_id': f"{self.file_name}-{chunk_id_counter}",
                        'content': chunk_content,
                        'word_count': len(chunk_content),
                        'chunk_type': 'general_text',
                        'metadata': {
                            'source': self.file_name
                        }
                    })
                    chunk_id_counter += 1
                    start += self.chunk_size - self.overlap
        
        print(f"为文件 '{self.file_name}' 创建了 {len(self.chunks)} 个块")

    def save_results(self, output_dir: str):
        if not self.chunks:
            print("没有块可以保存。")
            return

        output_filename = self.file_name.replace('.txt', '_processed.json')
        output_path = os.path.join(output_dir, output_filename)
        os.makedirs(output_dir, exist_ok=True)

        result = {
            'source_file': self.file_name,
            'processing_time': datetime.now().isoformat(),
            'total_chunks': len(self.chunks),
            'chunk_type': 'general_text', # 标记为通用文本
            'chunks': self.chunks
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {output_path}")
        except Exception as e:
            print(f"保存文件时出错: {e}")

def main():
    """主执行函数"""
    # 定位到data目录
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(code_dir, '..', 'data'))
    
    files_to_process = ['chap01.txt', 'chap02.txt', 'chap03.txt']
    
    for file_name in files_to_process:
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            print(f"\n--- 正在处理: {file_name} ---")
            processor = PlainTextProcessor(file_path)
            processor.read_file()
            processor.create_chunks()
            processor.save_results(output_dir=data_dir) # 将结果保存在data目录
        else:
            print(f"\n文件未找到: {file_path}")

if __name__ == '__main__':
    main()