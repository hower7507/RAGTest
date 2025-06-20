import json
import re
from datetime import datetime
from typing import List, Dict, Set
from collections import Counter
import jieba
import jieba.analyse

class QADocumentProcessor:
    """
    问答对文档处理器
    专门处理问答格式的文档，为每个问答对提取关键词标签
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.qa_pairs = []
        
        # 初始化jieba分词
        jieba.initialize()
        
        # 停用词列表
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> Set[str]:
        """
        加载停用词列表
        """
        stopwords = set()
        try:
            with open('e:\\PyProjects\\QASystem\\code\\stopword.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    stopwords.add(line.strip())
        except FileNotFoundError:
            # 如果没有停用词文件，使用默认停用词
            stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        return stopwords
    
    def read_file(self):
        """
        读取文件内容
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read().strip()
            print(f"成功读取文件: {self.file_path}")
        except Exception as e:
            print(f"读取文件时出错: {e}")
            raise
    
    def extract_qa_pairs(self):
        """
        提取问答对
        假设格式为：问题和答案在连续的行中
        """
        lines = self.content.split('\n')
        current_qa = {'question': '', 'answer': ''}
        qa_pairs = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行
            if not line:
                i += 1
                continue
            
            # 检查是否是问题（以问号结尾或包含疑问词）
            if self._is_question(line):
                # 如果之前有未完成的问答对，先保存
                if current_qa['question'] and current_qa['answer']:
                    qa_pairs.append(current_qa.copy())
                
                # 开始新的问答对
                current_qa = {'question': line, 'answer': ''}
                
                # 查找答案（下一个非空行开始，直到下一个问题或文件结束）
                i += 1
                answer_lines = []
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        i += 1
                        continue
                    
                    # 如果遇到下一个问题，停止收集答案
                    if self._is_question(next_line):
                        break
                    
                    answer_lines.append(next_line)
                    i += 1
                
                current_qa['answer'] = ' '.join(answer_lines)
                
                # 不要增加i，因为我们可能遇到了下一个问题
                continue
            else:
                # 如果不是问题，可能是答案的一部分
                if current_qa['question'] and not current_qa['answer']:
                    current_qa['answer'] = line
                elif current_qa['answer']:
                    current_qa['answer'] += ' ' + line
                i += 1
        
        # 添加最后一个问答对
        if current_qa['question'] and current_qa['answer']:
            qa_pairs.append(current_qa)
        
        self.qa_pairs = qa_pairs
        print(f"提取到 {len(qa_pairs)} 个问答对")
    
    def _is_question(self, text: str) -> bool:
        """
        判断文本是否是问题
        """
        # 检查是否以问号结尾
        if text.endswith('？') or text.endswith('?'):
            return True
        
        # 检查是否包含疑问词
        question_words = ['什么', '怎么', '为什么', '如何', '哪里', '哪个', '谁', '何时', '多少', '是否']
        for word in question_words:
            if word in text:
                return True
        
        return False
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        从文本中提取关键词
        """
        # 使用jieba的TF-IDF提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
        
        # 过滤停用词
        filtered_keywords = [kw for kw in keywords if kw not in self.stopwords and len(kw) > 1]
        
        return filtered_keywords[:top_k]
    
    def create_chunks(self) -> List[Dict]:
        """
        为每个问答对创建一个chunk，并提取关键词标签
        """
        chunks = []
        
        for i, qa_pair in enumerate(self.qa_pairs):
            # 合并问题和答案用于关键词提取
            combined_text = qa_pair['question'] + ' ' + qa_pair['answer']
            
            # 提取关键词
            keywords = self.extract_keywords(combined_text, top_k=8)
            
            # 计算字数
            word_count = len(combined_text)
            
            # 创建chunk
            chunk = {
                'chunk_id': i + 1,
                'question': qa_pair['question'],
                'answer': qa_pair['answer'],
                'combined_content': combined_text,
                'keywords': keywords,
                'word_count': word_count,
                'chunk_type': 'qa_pair'
            }
            
            chunks.append(chunk)
        
        print(f"创建了 {len(chunks)} 个问答对chunk")
        return chunks
    
    def save_results(self, chunks: List[Dict], output_file: str = None):
        """
        保存处理结果到JSON文件
        """
        if output_file is None:
            output_file = self.file_path.replace('.txt', '_qa_processed.json')
        
        result = {
            'source_file': self.file_path,
            'processing_time': datetime.now().isoformat(),
            'total_qa_pairs': len(self.qa_pairs),
            'total_chunks': len(chunks),
            'chunk_type': 'qa_pairs',
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
        print("\n=== 问答对文档处理摘要 ===")
        print(f"源文件: {self.file_path}")
        print(f"总问答对数: {len(self.qa_pairs)}")
        print(f"总chunk数: {len(chunks)}")
        
        print("\n=== 问答对详情 ===")
        for chunk in chunks[:5]:  # 只显示前5个
            print(f"\nChunk {chunk['chunk_id']}:")
            print(f"问题: {chunk['question'][:50]}...")
            print(f"答案: {chunk['answer'][:50]}...")
            print(f"关键词: {', '.join(chunk['keywords'])}")
            print(f"字数: {chunk['word_count']}")
    
    def process_document(self, save_output: bool = True) -> List[Dict]:
        """
        完整的问答对文档处理流程
        """
        print("开始处理问答对文档...")
        
        # 1. 读取文件
        self.read_file()
        
        # 2. 提取问答对
        self.extract_qa_pairs()
        
        # 3. 创建chunks并提取关键词
        chunks = self.create_chunks()
        
        # 4. 打印摘要
        self.print_summary(chunks)
        
        # 5. 保存结果
        if save_output:
            self.save_results(chunks)
        
        return chunks


def main():
    """
    主函数：演示问答对文档处理功能
    """
    # 文件路径
    file_path = "e:\\PyProjects\\QASystem\\data\\chap02.txt"
    
    # 创建处理器实例
    processor = QADocumentProcessor(file_path)
    
    # 处理文档
    chunks = processor.process_document(save_output=True)
    
    # 显示详细内容
    print("\n=== 所有问答对的详细内容 ===")
    for chunk in chunks:
        print(f"\n--- Chunk {chunk['chunk_id']} ---")
        print(f"问题: {chunk['question']}")
        print(f"答案: {chunk['answer']}")
        print(f"关键词: {', '.join(chunk['keywords'])}")
        print(f"字数: {chunk['word_count']}")


if __name__ == "__main__":
    main()