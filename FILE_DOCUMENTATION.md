# QA System - 文件说明文档

本文档详细说明了QA智能问答系统项目中所有文件和目录的作用与功能。

## 项目根目录文件

### 配置和说明文件
- **README.md** - 项目主要说明文档，包含完整的技术架构和实现细节
- **requirements.txt** - Python项目依赖包列表
- **plan.txt** - 项目开发计划和进度记录
- **Note.txt** - 开发过程中的笔记和备忘
- **Note2.txt** - 额外的开发笔记

### 提示词文件
- **prompt_final_answer.txt** - 最终回答生成的提示词模板
- **prompt_test_rank.txt** - 测试排序功能的提示词

### 数据处理脚本
- **clean_json_files_by_word_count.py** - 根据字数清理JSON文件的脚本
- **migrate_chap02_data.py** - 迁移第二章数据的脚本
- **migrate_to_code_db.py** - 将数据迁移到代码数据库的脚本
- **reprocess_chap02.py** - 重新处理第二章数据的脚本

### 调试和检查脚本
- **debug_bm25_tokenization.py** - 调试BM25分词问题的脚本
- **debug_chap02_detection.py** - 调试第二章检测问题的脚本
- **check_code_collections.py** - 检查代码集合的脚本
- **check_collections.py** - 检查数据集合的脚本
- **check_metadata_structure.py** - 检查元数据结构的脚本
- **fix_search_issues.py** - 修复搜索问题的脚本
- **verify_chap02_fix.py** - 验证第二章修复的脚本

### 测试脚本
- **test_backend_chap02.py** - 测试后端第二章功能
- **test_backend_comprehensive.py** - 后端综合测试
- **test_backend_search_logic.py** - 测试后端搜索逻辑
- **test_final_workflow.py** - 测试最终工作流程
- **test_fixes.py** - 测试修复功能
- **test_new_config.py** - 测试新配置
- **test_no_time_params.py** - 测试无时间参数情况
- **test_parameter_passing.py** - 测试参数传递
- **test_search_interface.py** - 测试搜索接口
- **test_search_interface_direct.py** - 直接测试搜索接口
- **test_time_parameter_issue.py** - 测试时间参数问题
- **test_top_k_10_with_sources.py** - 测试top-k为10的搜索结果
- **test_vector_search_only.py** - 仅测试向量搜索
- **test_vectorizer_direct.py** - 直接测试向量化器

## 主要目录结构

### /chroma_db/ - 向量数据库存储目录
- **chroma.sqlite3** - ChromaDB的SQLite数据库文件
- **61bedd45-94d0-4456-b94e-bf236bd109b3/** - 向量索引数据目录
  - **data_level0.bin** - 0级数据文件
  - **header.bin** - 头部信息文件
  - **length.bin** - 长度信息文件
  - **link_lists.bin** - 链接列表文件
- **71474215-e949-4bcb-b4be-7da88b3502d0/** - 另一个向量索引数据目录
- **c1f982a3-f648-433a-aa93-a3539f661959/** - 第三个向量索引数据目录

### /code/ - 核心代码目录

#### 核心系统文件
- **chat_backend.py** - FastAPI后端服务主文件，提供聊天API接口
- **advanced_search_system.py** - 高级搜索系统，集成多种搜索策略
- **search_interface.py** - 搜索系统统一接口
- **multi_stage_query.py** - 多阶段查询系统
- **vectorize_chunks.py** - 文档块向量化处理
- **dimension_analyzer.py** - 查询维度分析器
- **context_manager.py** - 上下文管理器

#### DeepSeek集成
- **deepseek_client.py** - DeepSeek API客户端
- **deepseek_config_presets.py** - DeepSeek配置预设
- **deepseek_usage_examples.py** - DeepSeek使用示例

#### 配置和工具
- **search_config.py** - 搜索系统配置管理
- **health_check.py** - 系统健康检查
- **document_processor.py** - 文档处理器
- **qa_document_processor.py** - 问答文档处理器
- **process_plain_text.py** - 纯文本处理

#### 数据管理
- **run_vectorization.py** - 运行向量化处理的脚本
- **backup_qa_system_chunks.py** - 备份QA系统数据块
- **restore_qa_system_chunks_20250620_193010.py** - 恢复特定日期的数据备份
- **clean_database_by_word_count.py** - 根据字数清理数据库
- **clean_main_database.py** - 清理主数据库
- **clean_session_qa_chunks.py** - 清理会话QA数据块

#### 分析和检查工具
- **analyze_chromadb_format.py** - 分析ChromaDB格式
- **analyze_qa_system_chunks.py** - 分析QA系统数据块
- **check_both_chromadb_dirs.py** - 检查两个ChromaDB目录
- **check_chromadb.py** - 检查ChromaDB状态
- **check_main_collections.py** - 检查主要集合
- **check_session_collections.py** - 检查会话集合

#### 导出和迁移
- **export_chap01_chunks.py** - 导出第一章数据块
- **export_session_collections.py** - 导出会话集合
- **delete_session_collections.py** - 删除会话集合
- **fix_score_key_issue.py** - 修复评分键问题

#### 演示和测试
- **demo_qa_system.py** - QA系统演示程序
- **test_backend_query.py** - 测试后端查询功能

#### 配置文件
- **requirements.txt** - Python依赖包列表
- **stopword.txt** - 中文停用词列表
- **key.txt** - API密钥文件（应保密）

#### 文档文件
- **README_DeepSeek.md** - DeepSeek集成说明文档
- **SEARCH_SYSTEM_README.md** - 搜索系统说明文档
- **TIME_QUERY_README.md** - 时间查询功能说明文档

#### 数据文件
- **chap01_chunks_export_20250620_184250.txt** - 第一章数据块导出文件
- **main_qa_system_chunks_export_20250620_192607.txt** - 主QA系统数据块导出文件
- **qa_system_chunks_backup_20250620_193010.json** - QA系统数据块JSON备份
- **qa_system_chunks_full_backup_20250620_193010.pkl** - QA系统数据块完整备份（pickle格式）
- **qiaoliang_contact_search_results_20250620_152419.json** - 特定搜索结果文件
- **chromadb_dirs_report_20250620_190156.txt** - ChromaDB目录报告

#### 子目录
- **/chroma_db/** - 代码目录下的ChromaDB数据库
  - 包含多个UUID命名的向量索引目录
  - **chroma.sqlite3** - 数据库文件
- **/demo_cache/** - 演示缓存目录
  - **/embeddings/** - 嵌入向量缓存
  - **/results/** - 结果缓存
- **/session_collections_export/** - 会话集合导出目录
  - **export_summary_20250620_191505.txt** - 导出摘要
  - **session_collection_chat_conversations_20250620_191505.txt** - 聊天对话集合
  - **session_collection_qa_chunks_20250620_191505.txt** - QA数据块集合
  - **session_collection_qa_collection_20250620_191505.txt** - QA集合
  - **session_collection_qa_demo_collection_20250620_191505.txt** - QA演示集合
- **/__pycache__/** - Python字节码缓存目录
  - 包含所有Python模块的编译缓存文件

### /data/ - 数据目录

#### 原始文档
- **chap01.docx** - 第一章Word文档
- **chap01.txt** - 第一章文本文件
- **chap02.docx** - 第二章Word文档
- **chap02.txt** - 第二章文本文件
- **chap03.docx** - 第三章Word文档

#### 处理后数据
- **chap01_processed.json** - 第一章处理后的JSON数据
- **chap01_processed_backup.json** - 第一章处理数据备份
- **chap02_processed.json** - 第二章处理后的JSON数据
- **chap02_processed_backup.json** - 第二章处理数据备份

#### 配置文件
- **custom_dict.txt** - 自定义词典文件

#### 子目录
- **/example/** - 示例数据目录

### /docx/ - 文档资料目录
- **NLP_Chap16.pptx** - 自然语言处理第16章PPT
- **数字教师项目_业务需求说明书_v0.1.doc** - 数字教师项目需求文档
- **自然语言处理课程期终考察_技术方案_组名_v0.1.pptx** - 课程技术方案PPT
- **自然语言处理课程期终考察_设计文档_组名_v0.1.docx** - 课程设计文档

### /frontend-new/ - 前端项目目录

#### 配置文件
- **package.json** - Node.js项目配置和依赖
- **package-lock.json** - 依赖版本锁定文件
- **vite.config.ts** - Vite构建工具配置
- **tsconfig.json** - TypeScript主配置
- **tsconfig.app.json** - 应用TypeScript配置
- **tsconfig.node.json** - Node.js TypeScript配置
- **eslint.config.js** - ESLint代码规范配置
- **.gitignore** - Git忽略文件配置
- **README.md** - 前端项目说明文档
- **index.html** - HTML入口文件

#### 源代码目录 /src/
- **main.tsx** - React应用入口文件
- **App.tsx** - 主应用组件
- **App.css** - 主应用样式
- **index.css** - 全局样式
- **vite-env.d.ts** - Vite环境类型定义

##### 子目录
- **/components/** - React组件目录
  - 包含ChatInterface、SessionSidebar等核心组件
- **/services/** - 服务层目录
  - 包含API调用和数据处理服务
- **/assets/** - 静态资源目录

#### 公共资源目录 /public/
- **vite.svg** - Vite图标文件

### /notebooks/ - Jupyter笔记本目录
- **install_packages.ipynb** - 包安装指南笔记本

### /tests/ - 测试目录
（目录存在但具体内容需要进一步查看）

## 文件命名规范说明

### 时间戳文件
项目中包含多个带时间戳的文件，格式为 `YYYYMMDD_HHMMSS`：
- **20250620_184250** - 2025年6月20日 18:42:50
- **20250620_191505** - 2025年6月20日 19:15:05
- **20250620_192607** - 2025年6月20日 19:26:07
- **20250620_193010** - 2025年6月20日 19:30:10

这些时间戳表示数据导出、备份或处理的具体时间。

### UUID目录
ChromaDB使用UUID作为集合标识符：
- **61bedd45-94d0-4456-b94e-bf236bd109b3**
- **71474215-e949-4bcb-b4be-7da88b3502d0**
- **c1f982a3-f648-433a-aa93-a3539f661959**
- **7338003d-9131-4142-87f8-1648ae100195**
- **7ca6d77b-c09f-464f-925b-c78d7199a514**
- **90d2eb54-fff7-4d55-82e7-e9a46addf3f4**
- **c65cc963-659f-442f-b394-fd4b86ab7006**

每个UUID对应一个向量集合，包含该集合的索引和数据文件。

## 核心功能模块说明

### 1. 搜索系统模块
- **advanced_search_system.py** - 核心搜索引擎
- **search_interface.py** - 搜索接口封装
- **search_config.py** - 搜索配置管理
- **multi_stage_query.py** - 多阶段查询处理

### 2. 向量化模块
- **vectorize_chunks.py** - 文档向量化
- **run_vectorization.py** - 向量化执行脚本

### 3. 文档处理模块
- **document_processor.py** - 通用文档处理
- **qa_document_processor.py** - QA专用文档处理
- **process_plain_text.py** - 纯文本处理

### 4. AI集成模块
- **deepseek_client.py** - DeepSeek API客户端
- **deepseek_config_presets.py** - 配置预设
- **dimension_analyzer.py** - 智能维度分析

### 5. 数据管理模块
- **backup_qa_system_chunks.py** - 数据备份
- **clean_*.py** - 数据清理脚本
- **export_*.py** - 数据导出脚本

### 6. 前端界面模块
- **frontend-new/** - React前端应用
- 提供用户交互界面和实时聊天功能

### 7. 测试模块
- **test_*.py** - 各种功能测试脚本
- 覆盖搜索、后端、接口等核心功能

## 开发和维护说明

### 数据备份策略
项目采用多层备份策略：
1. **JSON格式备份** - 便于查看和编辑
2. **Pickle格式备份** - 保持Python对象完整性
3. **文本导出** - 便于人工检查和分析
4. **时间戳命名** - 便于版本管理和回滚

### 配置管理
- **requirements.txt** - Python依赖管理
- **package.json** - Node.js依赖管理
- **search_config.py** - 搜索参数配置
- **deepseek_config_presets.py** - AI模型配置

### 日志和监控
- 各模块包含详细的日志输出
- 健康检查脚本监控系统状态
- 测试脚本验证功能正确性

### 安全考虑
- **key.txt** - API密钥文件（需要保密）
- **.gitignore** - 防止敏感文件提交
- 输入验证和错误处理机制

## 总结

本QA智能问答系统是一个完整的企业级应用，包含：
- **后端服务**：基于FastAPI的RESTful API
- **前端界面**：基于React的现代化Web界面
- **AI集成**：DeepSeek大语言模型集成
- **向量检索**：ChromaDB向量数据库
- **多模态搜索**：向量搜索+关键词搜索+精确匹配
- **完整测试**：覆盖各个功能模块的测试套件
- **数据管理**：完善的备份、清理、导出机制
- **配置管理**：灵活的参数配置和预设管理

项目结构清晰，模块化程度高，便于维护和扩展。所有文件都有明确的职责分工，支持从开发、测试到生产部署的完整流程。