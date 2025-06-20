#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 使用示例
展示如何在不同场景下使用 DeepSeek 客户端
"""

import asyncio
from typing import List, Dict, Any
from deepseek_client import DeepSeekClient, DeepSeekConfig
from deepseek_config_presets import DeepSeekPresets, load_preset


class DeepSeekUsageExamples:
    """
    DeepSeek 使用示例类
    """
    
    def __init__(self, api_key: str = None):
        """
        初始化示例类
        
        Args:
            api_key: DeepSeek API 密钥
        """
        self.api_key = api_key
    
    def basic_chat_example(self):
        """
        基础对话示例
        """
        print("=== 基础对话示例 ===")
        
        # 使用默认配置
        config = DeepSeekPresets.get_default()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        try:
            # 简单对话
            response = client.simple_chat("你好，请介绍一下你自己")
            print(f"AI回复: {response}")
            
        except Exception as e:
            print(f"对话失败: {e}")
    
    def streaming_chat_example(self):
        """
        流式对话示例
        """
        print("\n=== 流式对话示例 ===")
        
        config = DeepSeekPresets.get_conversation()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        try:
            print("AI回复: ", end="", flush=True)
            for chunk in client.simple_chat_stream("请写一首关于春天的短诗"):
                print(chunk, end="", flush=True)
            print()  # 换行
            
        except Exception as e:
            print(f"\n流式对话失败: {e}")
    
    def multi_turn_conversation_example(self):
        """
        多轮对话示例
        """
        print("\n=== 多轮对话示例 ===")
        
        config = DeepSeekPresets.get_conversation()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        # 构建对话历史
        conversation = [
            {"role": "user", "content": "我想学习Python编程"},
            {"role": "assistant", "content": "很好！Python是一门优秀的编程语言。你想从哪个方面开始学习呢？"},
            {"role": "user", "content": "我想学习数据分析"}
        ]
        
        try:
            response = client.multi_turn_chat(conversation)
            print(f"AI回复: {response}")
            
        except Exception as e:
            print(f"多轮对话失败: {e}")
    
    def qa_system_example(self):
        """
        问答系统示例
        """
        print("\n=== 问答系统示例 ===")
        
        config = DeepSeekPresets.get_qa_system()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        # 模拟搜索结果
        search_results = [
            "机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习。",
            "机器学习算法通过分析数据来识别模式，并使用这些模式来做出预测或决策。",
            "常见的机器学习类型包括监督学习、无监督学习和强化学习。"
        ]
        
        question = "什么是机器学习？"
        context = "\n".join([f"{i+1}. {result}" for i, result in enumerate(search_results)])
        
        prompt = f"""
基于以下搜索结果回答问题：

搜索结果：
{context}

问题：{question}

请基于上述搜索结果提供准确、简洁的答案：
"""
        
        try:
            response = client.simple_chat(prompt)
            print(f"问答结果: {response}")
            
        except Exception as e:
            print(f"问答失败: {e}")
    
    def search_optimization_example(self):
        """
        搜索优化示例
        """
        print("\n=== 搜索优化示例 ===")
        
        config = DeepSeekPresets.get_search_optimization()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        # 模拟搜索结果
        search_results = [
            {"title": "Python基础教程", "content": "Python是一种高级编程语言...", "score": 0.8},
            {"title": "机器学习入门", "content": "机器学习是AI的重要分支...", "score": 0.6},
            {"title": "数据科学指南", "content": "数据科学结合了统计学...", "score": 0.7}
        ]
        
        query = "Python机器学习"
        
        prompt = f"""
用户查询：{query}

搜索结果：
{chr(10).join([f"{i+1}. 标题：{r['title']}，内容：{r['content']}，相关性：{r['score']}" for i, r in enumerate(search_results)])}

请根据用户查询重新排序这些搜索结果，并解释排序理由。返回格式：
1. 最相关的结果
2. 次相关的结果
3. 最不相关的结果

排序理由：...
"""
        
        try:
            response = client.simple_chat(prompt)
            print(f"搜索优化结果: {response}")
            
        except Exception as e:
            print(f"搜索优化失败: {e}")
    
    def summarization_example(self):
        """
        文本摘要示例
        """
        print("\n=== 文本摘要示例 ===")
        
        config = DeepSeekPresets.get_summarization()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        long_text = """
人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，
并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、
语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，
应用领域也不断扩大，可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
人工智能可以对人的意识、思维的信息过程的模拟。人工智能不是人的智能，但能像人那样思考、
也可能超过人的智能。
"""
        
        prompt = f"""
请为以下文本生成一个简洁的摘要（不超过50字）：

{long_text}

摘要：
"""
        
        try:
            response = client.simple_chat(prompt)
            print(f"摘要结果: {response}")
            
        except Exception as e:
            print(f"摘要失败: {e}")
    
    def creative_writing_example(self):
        """
        创意写作示例
        """
        print("\n=== 创意写作示例 ===")
        
        config = DeepSeekPresets.get_creative()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        try:
            response = client.simple_chat(
                "请写一个关于AI助手帮助程序员解决bug的有趣小故事（100字以内）"
            )
            print(f"创意故事: {response}")
            
        except Exception as e:
            print(f"创意写作失败: {e}")
    
    def code_generation_example(self):
        """
        代码生成示例
        """
        print("\n=== 代码生成示例 ===")
        
        config = DeepSeekPresets.get_precise()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        try:
            response = client.simple_chat(
                "请写一个Python函数，用于计算两个列表的交集，要求包含注释和示例用法"
            )
            print(f"生成的代码:\n{response}")
            
        except Exception as e:
            print(f"代码生成失败: {e}")
    
    def batch_processing_example(self):
        """
        批量处理示例
        """
        print("\n=== 批量处理示例 ===")
        
        config = DeepSeekPresets.get_fast_response()
        if self.api_key:
            config.api_key = self.api_key
        
        client = DeepSeekClient(config)
        
        questions = [
            "什么是Python？",
            "什么是机器学习？",
            "什么是深度学习？"
        ]
        
        print("批量处理问题...")
        for i, question in enumerate(questions, 1):
            try:
                response = client.simple_chat(f"请用一句话回答：{question}")
                print(f"{i}. 问题：{question}")
                print(f"   答案：{response}")
                
            except Exception as e:
                print(f"{i}. 问题：{question}")
                print(f"   错误：{e}")
    
    def error_handling_example(self):
        """
        错误处理示例
        """
        print("\n=== 错误处理示例 ===")
        
        # 使用无效的API密钥测试错误处理
        config = DeepSeekPresets.get_default()
        config.api_key = "invalid_key"
        
        client = DeepSeekClient(config)
        
        try:
            response = client.simple_chat("测试消息")
            print(f"意外成功: {response}")
            
        except Exception as e:
            print(f"预期的错误: {type(e).__name__}: {e}")
            
        # 测试连接
        print("\n测试连接状态...")
        if client.test_connection():
            print("连接成功")
        else:
            print("连接失败")
    
    def run_all_examples(self):
        """
        运行所有示例
        """
        print("=== DeepSeek 使用示例演示 ===")
        print("注意：需要有效的API密钥才能正常运行")
        
        examples = [
            self.basic_chat_example,
            self.streaming_chat_example,
            self.multi_turn_conversation_example,
            self.qa_system_example,
            self.search_optimization_example,
            self.summarization_example,
            self.creative_writing_example,
            self.code_generation_example,
            self.batch_processing_example,
            self.error_handling_example
        ]
        
        for example in examples:
            try:
                example()
            except Exception as e:
                print(f"示例 {example.__name__} 执行失败: {e}")
            print("-" * 50)


def interactive_demo():
    """
    交互式演示
    """
    print("=== DeepSeek 交互式演示 ===")
    print("请选择要运行的示例：")
    print("1. 基础对话")
    print("2. 流式对话")
    print("3. 多轮对话")
    print("4. 问答系统")
    print("5. 搜索优化")
    print("6. 文本摘要")
    print("7. 创意写作")
    print("8. 代码生成")
    print("9. 批量处理")
    print("10. 错误处理")
    print("11. 运行所有示例")
    print("0. 退出")
    
    api_key = input("\n请输入您的DeepSeek API密钥（可选，按回车跳过）: ").strip()
    if not api_key:
        api_key = None
        print("未提供API密钥，某些示例可能无法正常运行")
    
    examples = DeepSeekUsageExamples(api_key)
    
    while True:
        try:
            choice = input("\n请选择 (0-11): ").strip()
            
            if choice == "0":
                print("退出演示")
                break
            elif choice == "1":
                examples.basic_chat_example()
            elif choice == "2":
                examples.streaming_chat_example()
            elif choice == "3":
                examples.multi_turn_conversation_example()
            elif choice == "4":
                examples.qa_system_example()
            elif choice == "5":
                examples.search_optimization_example()
            elif choice == "6":
                examples.summarization_example()
            elif choice == "7":
                examples.creative_writing_example()
            elif choice == "8":
                examples.code_generation_example()
            elif choice == "9":
                examples.batch_processing_example()
            elif choice == "10":
                examples.error_handling_example()
            elif choice == "11":
                examples.run_all_examples()
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n用户中断，退出演示")
            break
        except Exception as e:
            print(f"执行错误: {e}")


if __name__ == "__main__":
    interactive_demo()