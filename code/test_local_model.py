#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地模型加载
验证BAAI/bge-small-zh-v1.5模型是否能从本地正确加载
"""

import os
import sys
from FlagEmbedding import FlagModel

def test_local_model():
    """
    测试本地模型加载
    """
    print("=== 测试本地模型加载 ===")
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "model")
    
    print(f"当前目录: {current_dir}")
    print(f"模型路径: {model_path}")
    
    # 检查模型文件是否存在
    required_files = [
        "config.json",
        "pytorch_model.bin", 
        "tokenizer.json",
        "special_tokens_map.json"
    ]
    
    print("\n检查模型文件:")
    for file_name in required_files:
        file_path = os.path.join(model_path, file_name)
        exists = os.path.exists(file_path)
        print(f"  {file_name}: {'✓' if exists else '✗'}")
        if not exists:
            print(f"    错误: 缺少文件 {file_path}")
            return False
    
    # 尝试加载模型
    try:
        print("\n正在加载本地模型...")
        model = FlagModel(
            model_path,
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
            use_fp16=True
        )
        print("✓ 模型加载成功!")
        
        # 测试编码功能
        print("\n测试编码功能...")
        test_text = "这是一个测试句子"
        embedding = model.encode([test_text])
        print(f"✓ 编码成功! 向量维度: {embedding.shape}")
        
        # 测试查询编码
        print("\n测试查询编码功能...")
        query_embedding = model.encode_queries(["测试查询"])
        print(f"✓ 查询编码成功! 向量维度: {query_embedding.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        print("\n可能的解决方案:")
        print("1. 确保模型文件完整下载")
        print("2. 检查FlagEmbedding库是否正确安装: pip install FlagEmbedding")
        print("3. 检查PyTorch是否正确安装")
        return False

def test_vectorizer_with_local_model():
    """
    测试向量化器使用本地模型
    """
    print("\n=== 测试向量化器使用本地模型 ===")
    
    try:
        from vectorize_chunks import ChunkVectorizer
        
        # 使用相对路径
        vectorizer = ChunkVectorizer(model_name="e:\\PyProjects\\QASystem\\code\\model")
        vectorizer.load_model()
        
        print("✓ 向量化器加载本地模型成功!")
        return True
        
    except Exception as e:
        print(f"✗ 向量化器加载本地模型失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试本地模型...\n")
    
    # 测试直接加载
    success1 = test_local_model()
    
    # 测试向量化器
    success2 = test_vectorizer_with_local_model()
    
    print("\n=== 测试结果 ===")
    print(f"直接加载模型: {'✓ 成功' if success1 else '✗ 失败'}")
    print(f"向量化器加载: {'✓ 成功' if success2 else '✗ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过! 本地模型配置成功!")
    else:
        print("\n❌ 部分测试失败，请检查配置")