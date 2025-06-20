#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 配置预设
提供不同场景下的预设配置
"""

from deepseek_client import DeepSeekConfig
from typing import Dict


class DeepSeekPresets:
    """
    DeepSeek 配置预设类
    """
    
    @staticmethod
    def get_default() -> DeepSeekConfig:
        """
        默认配置
        适用于一般对话场景
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=4096,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    @staticmethod
    def get_creative() -> DeepSeekConfig:
        """
        创意配置
        适用于创意写作、头脑风暴等场景
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=4096,
            temperature=1.2,
            top_p=0.95,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
    
    @staticmethod
    def get_precise() -> DeepSeekConfig:
        """
        精确配置
        适用于技术问答、代码生成等需要准确性的场景
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=4096,
            temperature=0.1,
            top_p=0.8,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    @staticmethod
    def get_balanced() -> DeepSeekConfig:
        """
        平衡配置
        在创意和准确性之间取得平衡
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=4096,
            temperature=0.5,
            top_p=0.85,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
    
    @staticmethod
    def get_qa_system() -> DeepSeekConfig:
        """
        问答系统配置
        专门为QA系统优化，注重准确性和相关性
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=2048,
            temperature=0.3,
            top_p=0.8,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    @staticmethod
    def get_search_optimization() -> DeepSeekConfig:
        """
        搜索优化配置
        用于搜索结果的重排序和优化
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=1024,
            temperature=0.2,
            top_p=0.75,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    @staticmethod
    def get_conversation() -> DeepSeekConfig:
        """
        对话配置
        适用于多轮对话场景
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=2048,
            temperature=0.6,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.2
        )
    
    @staticmethod
    def get_summarization() -> DeepSeekConfig:
        """
        摘要配置
        适用于文本摘要任务
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=1024,
            temperature=0.3,
            top_p=0.8,
            frequency_penalty=0.1,
            presence_penalty=0.0
        )
    
    @staticmethod
    def get_fast_response() -> DeepSeekConfig:
        """
        快速响应配置
        适用于需要快速响应的场景
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=512,
            temperature=0.4,
            top_p=0.8,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=30
        )
    
    @staticmethod
    def get_long_context() -> DeepSeekConfig:
        """
        长上下文配置
        适用于需要处理长文本的场景
        """
        return DeepSeekConfig(
            model="deepseek-chat",
            max_tokens=8192,
            temperature=0.5,
            top_p=0.85,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            timeout=120
        )
    
    @staticmethod
    def get_all_presets() -> Dict[str, DeepSeekConfig]:
        """
        获取所有预设配置
        
        Returns:
            包含所有预设配置的字典
        """
        return {
            "default": DeepSeekPresets.get_default(),
            "creative": DeepSeekPresets.get_creative(),
            "precise": DeepSeekPresets.get_precise(),
            "balanced": DeepSeekPresets.get_balanced(),
            "qa_system": DeepSeekPresets.get_qa_system(),
            "search_optimization": DeepSeekPresets.get_search_optimization(),
            "conversation": DeepSeekPresets.get_conversation(),
            "summarization": DeepSeekPresets.get_summarization(),
            "fast_response": DeepSeekPresets.get_fast_response(),
            "long_context": DeepSeekPresets.get_long_context()
        }
    
    @staticmethod
    def print_all_presets():
        """
        打印所有预设配置的信息
        """
        presets = DeepSeekPresets.get_all_presets()
        
        print("=== DeepSeek 配置预设 ===")
        for name, config in presets.items():
            print(f"\n{name.upper()}:")
            print(f"  模型: {config.model}")
            print(f"  最大令牌: {config.max_tokens}")
            print(f"  温度: {config.temperature}")
            print(f"  Top-p: {config.top_p}")
            print(f"  频率惩罚: {config.frequency_penalty}")
            print(f"  存在惩罚: {config.presence_penalty}")
            print(f"  超时: {config.timeout}秒")


def load_preset(preset_name: str) -> DeepSeekConfig:
    """
    加载指定的预设配置
    
    Args:
        preset_name: 预设名称
        
    Returns:
        DeepSeek 配置
        
    Raises:
        ValueError: 预设名称不存在
    """
    presets = DeepSeekPresets.get_all_presets()
    
    if preset_name not in presets:
        available = ", ".join(presets.keys())
        raise ValueError(f"预设 '{preset_name}' 不存在。可用预设: {available}")
    
    return presets[preset_name]


def demo_presets():
    """
    演示预设配置
    """
    from deepseek_client import DeepSeekClient
    
    print("=== DeepSeek 预设配置演示 ===")
    
    # 显示所有预设
    DeepSeekPresets.print_all_presets()
    
    # 测试不同预设
    test_message = "请简单解释什么是机器学习"
    
    presets_to_test = ["precise", "creative", "balanced"]
    
    for preset_name in presets_to_test:
        print(f"\n{'='*50}")
        print(f"测试预设: {preset_name.upper()}")
        
        try:
            config = load_preset(preset_name)
            client = DeepSeekClient(config)
            
            if client.test_connection():
                response = client.simple_chat(
                    test_message,
                    max_tokens=100
                )
                print(f"回复: {response}")
            else:
                print("连接失败，跳过测试")
                
        except Exception as e:
            print(f"测试失败: {e}")


if __name__ == "__main__":
    demo_presets()