#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 客户端
提供完整的 DeepSeek API 调用功能，支持流式和非流式响应
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Union, Iterator, Callable
from dataclasses import dataclass, asdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class DeepSeekConfig:
    """
    DeepSeek 配置类
    """
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.api_key:
            # 尝试从环境变量获取
            self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
            
            # 尝试从key.txt文件获取
            if not self.api_key:
                self.api_key = self._load_api_key_from_file()
    
    def _load_api_key_from_file(self) -> str:
        """从key.txt文件加载API密钥"""
        key_file = os.path.join(os.path.dirname(__file__), 'key.txt')
        if not os.path.exists(key_file):
            return ""
        
        try:
            with open(key_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析key.txt文件，查找所有API key
            lines = content.strip().split('\n')
            api_keys = []
            
            for line in lines:
                line = line.strip()
                # 查找包含"API key:"的行
                if 'API key:' in line:
                    # 提取API密钥
                    api_key = line.split('API key:')[-1].strip()
                    if api_key and api_key.startswith('sk-'):
                        api_keys.append(api_key)
            
            if api_keys:
                # 优先使用较短的API密钥（通常是更新的格式）
                # 如果有多个密钥，选择最短的那个
                selected_key = min(api_keys, key=len)
                print(f"已从key.txt加载API密钥: {selected_key[:10]}... (共找到{len(api_keys)}个密钥)")
                return selected_key
            
            print("在key.txt文件中未找到有效的API密钥")
            return ""
            
        except Exception as e:
            print(f"读取key.txt文件失败: {e}")
            return ""
    
    def validate(self) -> bool:
        """验证配置"""
        if not self.api_key:
            print("错误: 未设置 DeepSeek API Key")
            return False
        
        if self.max_tokens <= 0:
            print("错误: max_tokens 必须大于 0")
            return False
            
        if not (0 <= self.temperature <= 2):
            print("错误: temperature 必须在 0-2 之间")
            return False
            
        if not (0 <= self.top_p <= 1):
            print("错误: top_p 必须在 0-1 之间")
            return False
            
        return True


class DeepSeekClient:
    """
    DeepSeek API 客户端
    提供完整的 API 调用功能
    """
    
    def __init__(self, config: Optional[DeepSeekConfig] = None):
        """
        初始化客户端
        
        Args:
            config: DeepSeek 配置，如果为 None 则使用默认配置
        """
        self.config = config or DeepSeekConfig()
        self.session = self._create_session()
        
        # 验证配置
        if not self.config.validate():
            raise ValueError("DeepSeek 配置验证失败")
    
    def _create_session(self) -> requests.Session:
        """
        创建带重试机制的会话
        
        Returns:
            配置好的 requests.Session
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _prepare_headers(self) -> Dict[str, str]:
        """
        准备请求头
        
        Returns:
            请求头字典
        """
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _prepare_payload(self, 
                        messages: List[Dict[str, str]], 
                        stream: bool = False,
                        **kwargs) -> Dict[str, Any]:
        """
        准备请求载荷
        
        Args:
            messages: 消息列表
            stream: 是否流式响应
            **kwargs: 其他参数
            
        Returns:
            请求载荷字典
        """
        payload = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
            "stream": stream
        }
        
        # 移除 None 值
        return {k: v for k, v in payload.items() if v is not None}
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       **kwargs) -> Dict[str, Any]:
        """
        非流式聊天完成
        
        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            **kwargs: 其他参数（model, max_tokens, temperature 等）
            
        Returns:
            API 响应字典
            
        Raises:
            requests.RequestException: 请求失败
            ValueError: 响应格式错误
        """
        url = f"{self.config.base_url}/chat/completions"
        headers = self._prepare_headers()
        payload = self._prepare_payload(messages, stream=False, **kwargs)
        
        try:
            response = self.session.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"DeepSeek API 请求失败: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"DeepSeek API 响应格式错误: {e}")
    
    def chat_completion_stream(self, 
                              messages: List[Dict[str, str]], 
                              **kwargs) -> Iterator[Dict[str, Any]]:
        """
        流式聊天完成
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Yields:
            流式响应数据块
            
        Raises:
            requests.RequestException: 请求失败
        """
        url = f"{self.config.base_url}/chat/completions"
        headers = self._prepare_headers()
        payload = self._prepare_payload(messages, stream=True, **kwargs)
        
        try:
            response = self.session.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:].strip()
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"DeepSeek 流式 API 请求失败: {e}")
    
    def simple_chat(self, 
                   user_message: str, 
                   system_message: Optional[str] = None,
                   **kwargs) -> str:
        """
        简单聊天接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            **kwargs: 其他参数
            
        Returns:
            AI 回复内容
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.chat_completion(messages, **kwargs)
        
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise ValueError("DeepSeek API 响应格式异常")
    
    def simple_chat_stream(self, 
                          user_message: str, 
                          system_message: Optional[str] = None,
                          callback: Optional[Callable[[str], None]] = None,
                          **kwargs) -> str:
        """
        简单流式聊天接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            callback: 流式回调函数，接收每个文本块
            **kwargs: 其他参数
            
        Returns:
            完整的 AI 回复内容
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        full_content = ""
        
        for chunk in self.chat_completion_stream(messages, **kwargs):
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('delta', {})
                content = delta.get('content', '')
                if content:
                    full_content += content
                    if callback:
                        callback(content)
        
        return full_content
    
    def multi_turn_chat(self, 
                       conversation: List[Dict[str, str]], 
                       new_message: str,
                       **kwargs) -> tuple[str, List[Dict[str, str]]]:
        """
        多轮对话接口
        
        Args:
            conversation: 历史对话记录
            new_message: 新消息
            **kwargs: 其他参数
            
        Returns:
            (AI回复, 更新后的对话记录)
        """
        # 添加新的用户消息
        updated_conversation = conversation.copy()
        updated_conversation.append({"role": "user", "content": new_message})
        
        # 获取AI回复
        response = self.chat_completion(updated_conversation, **kwargs)
        
        if 'choices' in response and len(response['choices']) > 0:
            ai_reply = response['choices'][0]['message']['content']
            # 添加AI回复到对话记录
            updated_conversation.append({"role": "assistant", "content": ai_reply})
            return ai_reply, updated_conversation
        else:
            raise ValueError("DeepSeek API 响应格式异常")
    
    def get_usage_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取使用情况信息
        
        Args:
            response: API 响应
            
        Returns:
            使用情况信息
        """
        usage = response.get('usage', {})
        return {
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'completion_tokens': usage.get('completion_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0)
        }
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            连接是否成功
        """
        try:
            response = self.simple_chat("Hello", max_tokens=10)
            return bool(response)
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False


# === 便捷函数 ===

def create_deepseek_client(api_key: Optional[str] = None, 
                          model: str = "deepseek-chat",
                          **kwargs) -> DeepSeekClient:
    """
    创建 DeepSeek 客户端的便捷函数
    
    Args:
        api_key: API 密钥
        model: 模型名称
        **kwargs: 其他配置参数
        
    Returns:
        DeepSeek 客户端实例
    """
    config = DeepSeekConfig(api_key=api_key or "", model=model, **kwargs)
    return DeepSeekClient(config)


def quick_chat(message: str, 
              api_key: Optional[str] = None,
              system_message: Optional[str] = None,
              **kwargs) -> str:
    """
    快速聊天便捷函数
    
    Args:
        message: 用户消息
        api_key: API 密钥
        system_message: 系统消息
        **kwargs: 其他参数
        
    Returns:
        AI 回复
    """
    client = create_deepseek_client(api_key)
    return client.simple_chat(message, system_message, **kwargs)


def demo_deepseek_client():
    """
    演示 DeepSeek 客户端功能
    """
    print("=== DeepSeek 客户端演示 ===")
    
    try:
        # 1. 创建客户端
        client = create_deepseek_client()
        
        # 2. 测试连接
        print("\n=== 测试连接 ===")
        if client.test_connection():
            print("✓ 连接成功")
        else:
            print("✗ 连接失败")
            return
        
        # 3. 简单聊天
        print("\n=== 简单聊天测试 ===")
        response = client.simple_chat(
            user_message="你好，请简单介绍一下自己",
            max_tokens=100
        )
        print(f"AI回复: {response}")
        
        # 4. 流式聊天
        print("\n=== 流式聊天测试 ===")
        print("AI回复: ", end="", flush=True)
        
        def print_chunk(chunk):
            print(chunk, end="", flush=True)
        
        full_response = client.simple_chat_stream(
            user_message="请用一句话解释什么是人工智能",
            callback=print_chunk,
            max_tokens=50
        )
        print("\n")
        
        # 5. 多轮对话
        print("\n=== 多轮对话测试 ===")
        conversation = []
        
        # 第一轮
        reply1, conversation = client.multi_turn_chat(
            conversation, 
            "我想学习Python编程",
            max_tokens=80
        )
        print(f"用户: 我想学习Python编程")
        print(f"AI: {reply1}")
        
        # 第二轮
        reply2, conversation = client.multi_turn_chat(
            conversation, 
            "有什么好的学习资源推荐吗？",
            max_tokens=80
        )
        print(f"用户: 有什么好的学习资源推荐吗？")
        print(f"AI: {reply2}")
        
        print(f"\n对话轮数: {len(conversation) // 2}")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_deepseek_client()