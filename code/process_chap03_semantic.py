import os
import json
from datetime import datetime

class Chap03SemanticProcessor:
    """
    专门针对chap03.txt的语义分块处理器。
    根据内容的逻辑结构将文档分为三个主要部分：
    1. 温习作业部分
    2. 提交作业部分  
    3. 文件命名要求部分
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.content = ""
        self.chunks = []

    def read_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read().strip()
            print(f"成功读取文件: {self.file_path}")
        except Exception as e:
            print(f"读取文件 '{self.file_path}' 时出错: {e}")
            raise

    def create_semantic_chunks(self):
        """根据语义结构创建分块"""
        if not self.content:
            print("内容为空，无法创建块。")
            return

        lines = [line.strip() for line in self.content.split('\n') if line.strip()]
        
        # 第一部分：温习作业（包含标题和三个具体任务）
        review_tasks = []
        review_tasks.append(lines[0])  # "温习作业："
        review_tasks.extend(lines[1:4])  # 三个具体的温习任务
        
        review_content = "\n".join(review_tasks)
        self.chunks.append({
            'chunk_id': f"{self.file_name}-review-tasks",
            'content': review_content,
            'word_count': len(review_content),
            'chunk_type': 'general_text',
            'metadata': {
                'source': self.file_name,
                'section': '温习作业',
                'section_type': 'review_tasks',
                'description': '课程温习作业要求，包括环境安装、NLTK资源了解和参考书复习'
            }
        })
        
        # 第二部分：提交作业（包含标题和两个具体任务）
        submission_tasks = []
        submission_tasks.append(lines[4])  # "提交作业："
        submission_tasks.extend(lines[5:7])  # 两个具体的提交任务
        
        submission_content = "\n".join(submission_tasks)
        self.chunks.append({
            'chunk_id': f"{self.file_name}-submission-tasks",
            'content': submission_content,
            'word_count': len(submission_content),
            'chunk_type': 'general_text',
            'metadata': {
                'source': self.file_name,
                'section': '提交作业',
                'section_type': 'submission_tasks',
                'description': '课程提交作业要求，包括学情调查表和读后感任务'
            }
        })
        
        # 第三部分：文件命名要求
        naming_requirements = lines[7]  # 文件命名格式要求
        
        self.chunks.append({
            'chunk_id': f"{self.file_name}-naming-requirements",
            'content': naming_requirements,
            'word_count': len(naming_requirements),
            'chunk_type': 'general_text',
            'metadata': {
                'source': self.file_name,
                'section': '文件命名要求',
                'section_type': 'naming_requirements',
                'description': '作业文件的命名格式规范和要求'
            }
        })
        
        print(f"为文件 '{self.file_name}' 创建了 {len(self.chunks)} 个语义块")
        for i, chunk in enumerate(self.chunks, 1):
            print(f"  块{i}: {chunk['metadata']['section']} ({chunk['word_count']}字)")

    def save_results(self, output_dir: str):
        if not self.chunks:
            print("没有块可以保存。")
            return

        output_filename = self.file_name.replace('.txt', '_semantic_processed.json')
        output_path = os.path.join(output_dir, output_filename)
        os.makedirs(output_dir, exist_ok=True)

        result = {
            'source_file': self.file_name,
            'processing_time': datetime.now().isoformat(),
            'processing_method': 'semantic_chunking',
            'total_chunks': len(self.chunks),
            'chunk_type': 'general_text',
            'description': '基于语义结构的分块处理，将chap03内容分为温习作业、提交作业和文件命名要求三个部分',
            'chunks': self.chunks
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"语义分块结果已保存到: {output_path}")
        except Exception as e:
            print(f"保存文件时出错: {e}")

def main():
    """主执行函数"""
    # 定位到data目录
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(code_dir, '..', 'data'))
    
    file_path = os.path.join(data_dir, 'chap03.txt')
    
    if os.path.exists(file_path):
        print(f"\n--- 正在进行chap03.txt的语义分块处理 ---")
        processor = Chap03SemanticProcessor(file_path)
        processor.read_file()
        processor.create_semantic_chunks()
        processor.save_results(output_dir=data_dir)
    else:
        print(f"\n文件未找到: {file_path}")

if __name__ == '__main__':
    main()