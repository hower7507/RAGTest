import os
from vectorize_chunks import ChunkVectorizer

def main():
    """主函数，用于运行向量化流程"""
    
    # 定位到data目录
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(code_dir, '..', 'data'))
    # 使用主数据库路径，而不是会话数据库路径
    db_dir = os.path.abspath(os.path.join(code_dir, '..', 'chroma_db'))

    # 要处理的已生成的JSON文件
    json_files = [
        os.path.join(data_dir, 'chap01_processed.json'),
        os.path.join(data_dir, 'chap02_processed.json')
    ]

    # 初始化向量化器
    # 确保集合名称与系统其他部分一致
    vectorizer = ChunkVectorizer(collection_name="qa_system_chunks")
    vectorizer.load_model()
    vectorizer.init_chromadb(persist_directory=db_dir)

    # 遍历JSON文件并进行向量化和存储
    for json_file in json_files:
        vectorizer.process_and_store(json_file)

if __name__ == '__main__':
    main()