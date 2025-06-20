# 时间查询功能使用指南

## 概述

本系统现已支持强大的时间查询功能，可以对文档chunks进行基于时间的精确检索和分析。系统将原始时间字符串（如"00:01"）自动转换为时间戳，支持高效的时间范围查询。

## 功能特性

### 1. 时间格式支持
- **MM:SS 格式**: `"01:30"` (1分30秒)
- **HH:MM 格式**: `"10:00"` (10小时0分钟)
- **HH:MM:SS 格式**: `"01:30:45"` (1小时30分45秒)
- **自动识别**: 系统智能判断时间格式

### 2. 时间戳转换
- 原始时间字符串保留在 `start_time` 和 `end_time` 字段
- 新增时间戳字段：
  - `start_timestamp`: 开始时间戳（秒）
  - `end_timestamp`: 结束时间戳（秒）
  - `duration`: 持续时间（秒）

### 3. 查询类型

#### 3.1 纯时间范围查询
```python
# 查找10:00-11:00时间段的所有内容
results = vectorizer.search_by_time_range("10:00", "11:00", n_results=10)
```

#### 3.2 语义搜索 + 时间过滤
```python
# 在指定时间段内搜索相关内容
results = vectorizer.search_similar_chunks(
    query_text="自然语言处理",
    n_results=5,
    start_time="00:00",
    end_time="05:00"
)
```

#### 3.3 单边时间过滤
```python
# 只限制开始时间
results = vectorizer.search_similar_chunks(
    query_text="数据分析",
    start_time="10:00"  # 10分钟后的内容
)

# 只限制结束时间
results = vectorizer.search_similar_chunks(
    query_text="机器学习",
    end_time="05:00"   # 前5分钟的内容
)
```

## 使用示例

### 基本使用

```python
from vectorize_chunks import ChunkVectorizer

# 初始化向量化器
vectorizer = ChunkVectorizer()
vectorizer.load_model()
vectorizer.init_chromadb("./chroma_db")

# 1. 时间范围查询
print("=== 时间范围查询 ===")
time_results = vectorizer.search_by_time_range(
    start_time="00:00",
    end_time="05:00",
    n_results=5
)

for chunk_id, metadata in zip(time_results['ids'], time_results['metadatas']):
    print(f"Chunk: {chunk_id}")
    print(f"时间: {metadata['start_time']} - {metadata['end_time']}")
    print(f"时间戳: {metadata['start_timestamp']}s - {metadata['end_timestamp']}s")
    print(f"持续时间: {metadata['duration']}s")
    print(f"说话人: {metadata['speakers']}")
    print()

# 2. 语义搜索 + 时间过滤
print("=== 语义搜索 + 时间过滤 ===")
filtered_results = vectorizer.search_similar_chunks(
    query_text="自然语言处理技术",
    n_results=3,
    start_time="02:00",
    end_time="10:00"
)

for doc, metadata in zip(filtered_results['documents'][0], filtered_results['metadatas'][0]):
    print(f"Chunk: {metadata['chunk_id']}")
    print(f"时间: {metadata['start_time']} - {metadata['end_time']}")
    print(f"说话人: {metadata['speakers']}")
    print(f"内容: {doc[:100]}...")
    print()
```

### 高级查询示例

```python
# 查找特定说话人在特定时间段的内容
def search_speaker_in_timerange(vectorizer, speaker_name, start_time, end_time):
    # 先按时间范围查询
    time_results = vectorizer.search_by_time_range(start_time, end_time, n_results=50)
    
    # 过滤特定说话人
    speaker_chunks = []
    for chunk_id, metadata, document in zip(
        time_results['ids'], 
        time_results['metadatas'], 
        time_results.get('documents', [])
    ):
        if speaker_name in metadata.get('speakers', ''):
            speaker_chunks.append({
                'id': chunk_id,
                'metadata': metadata,
                'document': document
            })
    
    return speaker_chunks

# 使用示例
speaker_chunks = search_speaker_in_timerange(
    vectorizer, 
    "张老师", 
    "05:00", 
    "15:00"
)

print(f"张老师在5-15分钟内的发言共 {len(speaker_chunks)} 段")
```

## 时间转换工具

### 手动时间转换

```python
vectorizer = ChunkVectorizer()

# 时间字符串转时间戳
timestamp = vectorizer.time_to_seconds("01:30:45")  # 返回: 5445秒

# 时间戳转标准时间格式
time_str = vectorizer.seconds_to_time(5445)  # 返回: "01:30:45"

print(f"01:30:45 = {timestamp} 秒 = {time_str}")
```

### 支持的时间格式

| 输入格式 | 解析结果 | 时间戳（秒） | 标准格式 |
|----------|----------|--------------|----------|
| "01:30" | 1分30秒 | 90 | "00:01:30" |
| "10:00" | 10小时0分 | 36000 | "10:00:00" |
| "01:30:45" | 1小时30分45秒 | 5445 | "01:30:45" |
| "" | 无效 | 0 | "00:00:00" |

## 演示脚本

### 运行完整演示

```bash
# 运行时间查询功能演示
python time_query_demo.py
```

演示脚本包含：
1. 时间转换功能测试
2. 时间范围搜索演示
3. 语义搜索 + 时间过滤演示
4. 持续时间统计分析

### 演示输出示例

```
=== 时间转换功能演示 ===
时间字符串 -> 时间戳（秒）-> 标准时间格式
--------------------------------------------------
     00:01 ->     60 -> 00:01:00
     01:30 ->     90 -> 00:01:30
     10:00 ->  36000 -> 10:00:00
  01:30:45 ->   5445 -> 01:30:45
  23:59:59 ->  86399 -> 23:59:59
           ->      0 -> 00:00:00
   invalid ->      0 -> 00:00:00

=== 时间范围搜索演示 ===
搜索 00:00 - 05:00 时间段的内容
时间范围 00:00 - 05:00 内找到 15 个chunks

--- 前5分钟内容 (00:00 - 05:00) ---
找到 15 个chunks:
  1. chunk_1
     时间: 00:00 - 00:30
     时间戳: 0s - 30s
     说话人: 主持人
     内容: 欢迎大家来到自然语言处理课程...
```

## 性能优化

### 1. 索引优化
- 时间戳字段自动建立索引，支持高效范围查询
- 建议按时间顺序批量插入数据

### 2. 查询优化
- 优先使用时间范围过滤，再进行语义搜索
- 合理设置 `n_results` 参数，避免返回过多结果

### 3. 内存优化
- 大量数据查询时，分批处理结果
- 及时释放不需要的查询结果

## 常见问题

### Q1: 时间格式识别错误怎么办？
A: 系统会自动判断时间格式，但建议使用标准格式：
- 分钟:秒 → "MM:SS"
- 小时:分钟 → "HH:MM" 
- 小时:分钟:秒 → "HH:MM:SS"

### Q2: 如何查询跨越多个时间段的内容？
A: 可以进行多次查询后合并结果：
```python
results1 = vectorizer.search_by_time_range("00:00", "05:00")
results2 = vectorizer.search_by_time_range("10:00", "15:00")
# 合并结果
all_ids = results1['ids'] + results2['ids']
```

### Q3: 时间戳精度如何？
A: 当前精度为秒级，足够满足大多数应用场景。如需更高精度，可以修改转换函数支持毫秒。

### Q4: 如何进行持续时间统计？
A: 使用演示脚本中的持续时间分析功能，或直接查询 `duration` 字段：
```python
all_data = vectorizer.collection.get()
durations = [meta['duration'] for meta in all_data['metadatas']]
avg_duration = sum(durations) / len(durations)
```

## 更新日志

### v1.1.0 (当前版本)
- ✅ 新增时间戳转换功能
- ✅ 支持时间范围查询
- ✅ 支持语义搜索 + 时间过滤
- ✅ 新增持续时间统计
- ✅ 完整的演示脚本和文档

### 计划功能
- 🔄 支持相对时间查询（如"最近5分钟"）
- 🔄 支持时间段重叠检测
- 🔄 支持毫秒级精度
- 🔄 可视化时间分布图表