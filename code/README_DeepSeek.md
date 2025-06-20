# DeepSeek 客户端使用指南

本指南介绍如何使用 DeepSeek 客户端类进行 AI 对话和各种应用场景。

## 文件结构

```
code/
├── deepseek_client.py          # DeepSeek 客户端核心类
├── deepseek_config_presets.py  # 预设配置
├── deepseek_usage_examples.py  # 使用示例
└── README_DeepSeek.md          # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API 密钥

#### 方法1: 使用 key.txt 文件（推荐）

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并获取 API 密钥
3. 将 API 密钥保存到 `code/key.txt` 文件中，格式如下：

```
name: your_project_name
API key: sk-your-api-key-here
```

**注意**: 如果文件中有多个 API 密钥，系统会自动选择最短的（通常是最新格式）。

#### 方法2: 使用环境变量

设置环境变量 `DEEPSEEK_API_KEY`：

```bash
# Windows
set DEEPSEEK_API_KEY=sk-your-api-key-here

# Linux/Mac
export DEEPSEEK_API_KEY=sk-your-api-key-here
```

#### 方法3: 手动指定

在代码中直接指定 API 密钥（不推荐用于生产环境）。

### 3. 基础使用

#### 自动加载 API 密钥（推荐）

```python
from deepseek_client import DeepSeekClient, DeepSeekConfig

# 创建配置（API密钥会自动从key.txt加载）
config = DeepSeekConfig()

# 创建客户端
client = DeepSeekClient(config)

# 简单对话
response = client.simple_chat("你好，请介绍一下你自己")
print(response)
```

#### 手动指定 API 密钥

```python
from deepseek_client import DeepSeekClient, DeepSeekConfig

# 手动指定API密钥
config = DeepSeekConfig(
    api_key="your-api-key-here",
    model="deepseek-chat"
)

# 创建客户端
client = DeepSeekClient(config)

# 简单对话
response = client.simple_chat("你好，请介绍一下你自己")
print(response)
```

## 核心组件

### DeepSeekConfig 配置类

配置类用于设置 DeepSeek API 的各种参数：

```python
from deepseek_client import DeepSeekConfig

config = DeepSeekConfig(
    api_key="your-api-key",           # API 密钥
    model="deepseek-chat",            # 模型名称
    base_url="https://api.deepseek.com",  # API 基础URL
    max_tokens=4096,                  # 最大令牌数
    temperature=0.7,                  # 温度参数 (0.0-2.0)
    top_p=0.9,                       # Top-p 参数
    frequency_penalty=0.0,           # 频率惩罚
    presence_penalty=0.0,            # 存在惩罚
    timeout=60,                      # 超时时间（秒）
    max_retries=3,                   # 最大重试次数
    retry_delay=1.0                  # 重试延迟（秒）
)
```

### DeepSeekClient 客户端类

客户端类提供了多种调用方式：

#### 1. 简单对话

```python
# 非流式对话
response = client.simple_chat("什么是机器学习？")

# 流式对话
for chunk in client.simple_chat_stream("请写一首诗"):
    print(chunk, end="", flush=True)
```

#### 2. 多轮对话

```python
conversation = [
    {"role": "user", "content": "我想学习Python"},
    {"role": "assistant", "content": "很好！你想从哪里开始？"},
    {"role": "user", "content": "从基础语法开始"}
]

response = client.multi_turn_chat(conversation)
```

#### 3. 完整 API 调用

```python
# 非流式
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100,
    temperature=0.5
)

# 流式
for chunk in client.chat_completion_stream(
    messages=[{"role": "user", "content": "Hello"}]
):
    print(chunk)
```

#### 4. 工具方法

```python
# 测试连接
if client.test_connection():
    print("连接成功")

# 获取使用信息
usage_info = client.get_usage_info()
print(f"总令牌数: {usage_info.get('total_tokens', 0)}")
```

## 预设配置

使用 `deepseek_config_presets.py` 中的预设配置：

```python
from deepseek_config_presets import DeepSeekPresets, load_preset

# 使用预设配置（API密钥会自动加载）
config = DeepSeekPresets.get_precise()  # 精确模式
config = DeepSeekPresets.get_creative() # 创意模式
config = DeepSeekPresets.get_qa_system() # 问答系统模式

# 或者通过名称加载
config = load_preset("balanced")  # 平衡模式

# 创建客户端（无需手动设置API密钥）
client = DeepSeekClient(config)

# 如果需要覆盖自动加载的API密钥
# config.api_key = "your-specific-api-key"
```

### 可用预设

| 预设名称 | 适用场景 | 特点 |
|---------|---------|------|
| `default` | 一般对话 | 平衡的参数设置 |
| `creative` | 创意写作 | 高温度，鼓励创新 |
| `precise` | 技术问答 | 低温度，注重准确性 |
| `balanced` | 通用场景 | 创意与准确性平衡 |
| `qa_system` | 问答系统 | 专为QA优化 |
| `search_optimization` | 搜索优化 | 用于搜索结果处理 |
| `conversation` | 多轮对话 | 适合对话场景 |
| `summarization` | 文本摘要 | 专为摘要任务优化 |
| `fast_response` | 快速响应 | 短令牌，快速回复 |
| `long_context` | 长文本处理 | 大令牌数，长超时 |

## 应用场景示例

### 1. 问答系统集成

```python
from deepseek_config_presets import DeepSeekPresets

def qa_with_context(question: str, search_results: list) -> str:
    """基于搜索结果回答问题"""
    config = DeepSeekPresets.get_qa_system()  # API密钥自动加载
    client = DeepSeekClient(config)
    
    context = "\n".join([f"{i+1}. {result}" for i, result in enumerate(search_results)])
    
    prompt = f"""
基于以下搜索结果回答问题：

搜索结果：
{context}

问题：{question}

请基于上述搜索结果提供准确、简洁的答案：
"""
    
    return client.simple_chat(prompt)
```

### 2. 搜索结果优化

```python
def optimize_search_results(query: str, results: list) -> str:
    """优化搜索结果排序"""
    config = DeepSeekPresets.get_search_optimization()  # API密钥自动加载
    client = DeepSeekClient(config)
    
    results_text = "\n".join([
        f"{i+1}. {r['title']} - {r['content']} (相关性: {r['score']})"
        for i, r in enumerate(results)
    ])
    
    prompt = f"""
用户查询：{query}

搜索结果：
{results_text}

请重新排序这些结果，使其更符合用户查询意图。
"""
    
    return client.simple_chat(prompt)
```

### 3. 多轮对话管理

```python
class ConversationManager:
    def __init__(self):
        config = DeepSeekPresets.get_conversation()  # API密钥自动加载
        self.client = DeepSeekClient(config)
        self.history = []
    
    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})
    
    def get_response(self) -> str:
        response = self.client.multi_turn_chat(self.history)
        self.history.append({"role": "assistant", "content": response})
        return response
    
    def clear_history(self):
        self.history = []
```

### 4. 批量文本处理

```python
def batch_summarize(texts: list) -> list:
    """批量文本摘要"""
    config = DeepSeekPresets.get_summarization()  # API密钥自动加载
    client = DeepSeekClient(config)
    summaries = []
    
    for text in texts:
        try:
            prompt = f"请为以下文本生成简洁摘要：\n\n{text}"
            summary = client.simple_chat(prompt)
            summaries.append(summary)
        except Exception as e:
            summaries.append(f"摘要失败: {e}")
    
    return summaries
```

## 错误处理

```python
from deepseek_client import DeepSeekError, DeepSeekAPIError, DeepSeekTimeoutError

try:
    response = client.simple_chat("Hello")
except DeepSeekAPIError as e:
    print(f"API错误: {e}")
except DeepSeekTimeoutError as e:
    print(f"超时错误: {e}")
except DeepSeekError as e:
    print(f"DeepSeek错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 最佳实践

### 1. API 密钥管理

```python
import os
from deepseek_client import DeepSeekConfig

# 从环境变量读取
config = DeepSeekConfig(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat"
)

# 或从配置文件读取
import json

with open("config.json", "r") as f:
    config_data = json.load(f)

config = DeepSeekConfig(**config_data)
```

### 2. 连接测试

```python
def create_client_with_test(config: DeepSeekConfig) -> DeepSeekClient:
    client = DeepSeekClient(config)
    
    if not client.test_connection():
        raise ConnectionError("无法连接到 DeepSeek API")
    
    return client
```

### 3. 重试机制

```python
import time

def robust_chat(client: DeepSeekClient, message: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return client.simple_chat(message)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # 指数退避
```

### 4. 流式处理

```python
def stream_with_callback(client: DeepSeekClient, message: str, callback=None):
    full_response = ""
    
    for chunk in client.simple_chat_stream(message):
        full_response += chunk
        if callback:
            callback(chunk)
    
    return full_response
```

## 运行示例

运行完整的使用示例：

```bash
python deepseek_usage_examples.py
```

这将启动交互式演示，您可以选择不同的示例来测试各种功能。

## 注意事项

1. **API 密钥安全**：不要在代码中硬编码 API 密钥
2. **速率限制**：注意 DeepSeek API 的调用频率限制
3. **错误处理**：始终包含适当的错误处理逻辑
4. **资源管理**：合理设置超时和重试参数
5. **成本控制**：监控 API 使用量和成本

## 故障排除

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 验证 API 密钥
   - 确认 API 端点 URL

2. **超时错误**
   - 增加超时时间
   - 检查网络稳定性
   - 减少请求复杂度

3. **API 错误**
   - 检查请求格式
   - 验证参数范围
   - 查看错误消息详情

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试连接
client = DeepSeekClient(config)
if client.test_connection():
    print("连接正常")
else:
    print("连接失败")

# 检查配置
print(client.config.to_dict())
```

## 更新日志

- v1.0.0: 初始版本，包含基础功能
- 支持流式和非流式对话
- 多种预设配置
- 完整的错误处理
- 丰富的使用示例

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个客户端库。

## 许可证

本项目采用 MIT 许可证。