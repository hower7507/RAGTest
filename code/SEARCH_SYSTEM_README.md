# 高级搜索系统使用指南

## 系统概述

本高级搜索系统集成了多种先进的搜索技术，实现了一轮搜索即可获得高质量结果的目标。系统采用**BM25关键词抽取 + 向量匹配 + 精确匹配 + BRE重排序**的综合策略，并自动生成适合大语言模型的提示词。

### 核心特性

- 🔍 **多策略融合搜索**：BM25 + 向量语义 + 精确匹配
- 🎯 **BRE智能重排序**：综合多种得分进行最优排序
- 🤖 **自动提示词生成**：为LLM对话准备完整上下文
- ⏰ **时间范围过滤**：支持按时间段精确搜索
- ⚙️ **灵活配置策略**：多种预设配置适应不同场景
- 🚀 **高性能设计**：批量搜索和便捷接口

## 系统架构

```
用户查询 → BM25关键词抽取 → 候选文档检索 → BRE重排序 → 提示词生成 → 输出结果
           ↓                    ↓              ↓
        关键词权重        向量匹配+精确匹配    综合得分排序
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 确保已完成文档向量化
python vectorize_chunks.py
```

### 2. 基本使用

```python
from search_interface import quick_search, search

# 快速搜索（返回文本结果）
result = quick_search("自然语言处理的应用", top_k=3)
print(result)

# 详细搜索（返回结构化结果）
result = search("机器学习算法", top_k=5)
print(f"找到{result['total_results']}个结果")
for res in result['results']:
    print(f"得分: {res['scores']['final_score']:.3f}")
    print(f"内容: {res['content'][:100]}...")
```

### 3. 高级功能

```python
from search_interface import SearchInterface, search_with_time

# 创建搜索接口
search_interface = SearchInterface("balanced")

# 时间过滤搜索
result = search_with_time(
    query="技术发展趋势",
    start_time="00:05",
    end_time="00:10",
    top_k=3
)

# 获取完整提示词
result = search_interface.search(
    query="深度学习原理",
    top_k=3,
    return_prompt=True
)
print("生成的提示词:")
print(result['prompt'])
```

## 配置策略

系统提供多种预设配置，适应不同搜索需求：

### 配置类型

| 配置名称 | 向量权重 | BM25权重 | 精确权重 | 适用场景 |
|---------|---------|---------|---------|----------|
| `balanced` | 0.33 | 0.33 | 0.34 | 通用场景，平衡各种匹配方式 |
| `vector` | 0.6 | 0.2 | 0.2 | 语义搜索，重视概念相似性 |
| `keyword` | 0.2 | 0.6 | 0.2 | 关键词搜索，重视词汇匹配 |
| `exact` | 0.2 | 0.2 | 0.6 | 精确搜索，重视字面匹配 |
| `fast` | 0.5 | 0.3 | 0.2 | 快速搜索，减少候选数量 |
| `comprehensive` | 0.4 | 0.3 | 0.3 | 全面搜索，更多候选结果 |

### 使用不同配置

```python
# 使用向量优先配置
vector_search = SearchInterface("vector")
result = vector_search.search("深度学习概念")

# 使用关键词优先配置
keyword_search = SearchInterface("keyword")
result = keyword_search.search("神经网络算法")

# 使用快速搜索配置
fast_search = SearchInterface("fast")
result = fast_search.search("AI应用")
```

## 搜索结果结构

### 基本结果格式

```json
{
  "query": "用户查询",
  "total_results": 5,
  "search_time": 0.15,
  "total_candidates": 50,
  "keywords_extracted": ["关键词1", "关键词2"],
  "results": [
    {
      "rank": 1,
      "document_id": "chunk_001",
      "content": "文档内容...",
      "metadata": {
        "start_time": "00:01:30",
        "end_time": "00:02:15",
        "speakers": "张三",
        "duration": 45,
        "source_file": "chap01_processed.json"
      },
      "scores": {
        "final_score": 0.856,
        "vector_score": 0.742,
        "bm25_score": 1.234,
        "exact_score": 0.680
      }
    }
  ],
  "prompt": "完整的LLM提示词..."
}
```

### 得分说明

- **final_score**: 综合得分，用于最终排序
- **vector_score**: 向量语义相似度得分
- **bm25_score**: BM25关键词匹配得分
- **exact_score**: 精确文本匹配得分

## 时间过滤功能

### 时间格式支持

- `"MM:SS"` - 分:秒格式（如 "05:30"）
- `"HH:MM:SS"` - 时:分:秒格式（如 "01:05:30"）
- `"MM"` - 纯分钟格式（如 "5"）

### 时间搜索示例

```python
# 搜索前5分钟的内容
result = search_with_time(
    query="开场介绍",
    start_time="00:00",
    end_time="05:00"
)

# 搜索特定时间段
result = search_with_time(
    query="核心观点",
    start_time="10:30",
    end_time="15:45"
)

# 搜索某时间点之后的内容
result = search_with_time(
    query="总结",
    start_time="20:00",
    end_time="99:99"  # 表示到结尾
)
```

## 批量搜索

```python
# 批量搜索多个查询
queries = [
    "自然语言处理",
    "计算机视觉",
    "推荐系统"
]

search_interface = SearchInterface("fast")
batch_results = search_interface.batch_search(queries, top_k=3)

for i, result in enumerate(batch_results):
    print(f"查询{i+1}: {queries[i]}")
    print(f"结果数: {result['total_results']}")
    print(f"搜索时间: {result['search_time']:.2f}秒")
```

## 提示词生成

系统自动生成适合大语言模型的提示词，包含：

1. **用户问题**：原始查询
2. **相关文档**：搜索到的相关内容
3. **元数据信息**：时间、说话人、相关度得分
4. **回答指导**：如何基于文档回答问题

### 提示词模板

```
你是一个专业的问答助手，请基于以下检索到的相关文档内容来回答用户的问题。

用户问题：{query}

相关文档内容：
[文档1]
时间: 00:01:30 - 00:02:15
说话人: 张三
内容: ...
相关度得分: 0.856

[文档2]
...

请根据上述文档内容，准确、详细地回答用户的问题。如果文档中没有足够的信息来回答问题，请明确说明。回答时请：
1. 直接回答问题的核心内容
2. 引用相关的文档片段作为支撑
3. 如果涉及多个说话人的观点，请分别说明
4. 保持回答的客观性和准确性

回答：
```

## 性能优化

### 搜索性能

- **候选文档数量**：默认50个，可根据需要调整
- **向量搜索**：使用高效的ChromaDB存储
- **BM25计算**：针对候选文档动态构建索引
- **批量处理**：支持批量查询优化

### 内存使用

- **模型加载**：FlagEmbedding模型按需加载
- **文档缓存**：智能缓存机制减少重复计算
- **结果限制**：可配置最大上下文长度

## 系统监控

### 获取系统信息

```python
search_interface = SearchInterface()
info = search_interface.get_system_info()

print(f"初始化状态: {info['initialized']}")
print(f"数据库记录数: {info['database']['total_records']}")
print(f"配置信息: {info['config']}")
```

### 搜索统计

每次搜索都会返回详细的统计信息：

- 搜索时间
- 候选文档数量
- 提取的关键词
- 各种得分分布

## 错误处理

### 常见错误及解决方案

1. **向量数据库未初始化**
   ```
   错误: 没有找到向量数据
   解决: 先运行 python vectorize_chunks.py
   ```

2. **模型加载失败**
   ```
   错误: 模型加载失败
   解决: 检查网络连接，确保能下载BAAI/bge-small-zh-v1.5模型
   ```

3. **搜索结果为空**
   ```
   原因: 查询与文档内容相关性太低
   解决: 尝试不同的查询词或调整搜索配置
   ```

## 扩展开发

### 自定义配置

```python
from search_config import SearchConfig

# 创建自定义配置
custom_config = SearchConfig(
    vector_weight=0.5,
    bm25_weight=0.3,
    exact_weight=0.2,
    max_candidates=30,
    default_top_k=3
)

# 验证配置
if custom_config.validate():
    search_interface = SearchInterface()
    search_interface.config = custom_config
```

### 添加新的搜索策略

可以在 `AdvancedSearchSystem` 类中添加新的搜索方法：

```python
def custom_search_strategy(self, query: str, candidates: List[Dict]) -> List[Dict]:
    # 实现自定义搜索逻辑
    pass
```

## 与LLM集成

### DeepSeek集成示例

```python
import openai
from search_interface import search

# 配置DeepSeek API
client = openai.OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

# 搜索并生成回答
def ask_question(question: str) -> str:
    # 1. 搜索相关文档
    search_result = search(question, top_k=3)
    
    if 'error' in search_result:
        return f"搜索失败: {search_result['error']}"
    
    # 2. 使用生成的提示词调用LLM
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": search_result['prompt']}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# 使用示例
answer = ask_question("深度学习的基本原理是什么？")
print(answer)
```

## 演示和测试

### 运行完整演示

```bash
# 运行搜索系统演示
python search_demo.py
```

演示包含：
- 基本搜索功能
- 时间过滤搜索
- 不同配置对比
- 批量搜索
- 提示词生成
- 便捷函数使用
- 性能分析

### 单独测试组件

```bash
# 测试搜索配置
python search_config.py

# 测试搜索接口
python search_interface.py

# 测试高级搜索系统
python advanced_search_system.py
```

## 最佳实践

### 查询优化

1. **使用具体的关键词**：避免过于抽象的查询
2. **适当的查询长度**：3-15个字符通常效果最好
3. **结合时间过滤**：当知道大概时间范围时使用
4. **选择合适的配置**：根据搜索目标选择配置策略

### 性能优化

1. **合理设置top_k**：通常3-10个结果足够
2. **使用快速配置**：对于实时应用使用"fast"配置
3. **批量搜索**：多个查询时使用批量接口
4. **缓存结果**：对于重复查询考虑缓存

### 结果解释

1. **关注综合得分**：final_score反映整体相关性
2. **分析得分构成**：了解匹配的主要来源
3. **检查时间信息**：确认结果的时间相关性
4. **验证说话人**：多人对话时注意说话人信息

## 总结

本高级搜索系统通过融合多种搜索技术，实现了高质量的一轮搜索效果。系统具有以下优势：

- ✅ **搜索质量高**：多策略融合确保结果相关性
- ✅ **使用简单**：便捷的接口和预设配置
- ✅ **功能丰富**：时间过滤、批量搜索、提示词生成
- ✅ **性能优秀**：高效的算法和优化策略
- ✅ **扩展性强**：灵活的配置和扩展接口
- ✅ **LLM就绪**：自动生成适合大模型的提示词

现在可以将此搜索系统与DeepSeek等大语言模型集成，构建完整的问答系统！