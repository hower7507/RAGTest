#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QA系统聊天后端服务
基于FastAPI + DeepSeek + ChromaDB
"""

import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings

# 导入现有的DeepSeek客户端
from deepseek_client import DeepSeekClient, DeepSeekConfig
from deepseek_config_presets import DeepSeekPresets
from health_check import generate_health_report

# 导入搜索系统
from search_interface import SearchInterface
from dimension_analyzer import DimensionAnalyzer
from multi_stage_query import MultiStageQuerySystem
from context_manager import ContextManager

# 数据模型定义
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    timestamp: str
    usage: Dict[str, Any]

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_message_at: str
    message_count: int
    preview: str  # 会话预览（前几个字符）

class ConversationMessage(BaseModel):
    message_id: str
    speaker_id: str
    content: str
    timestamp: str
    word_count: int
    metadata: Dict[str, Any]

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[ConversationMessage]
    total_messages: int

# 对话存储管理器
class ConversationStorage:
    """
    对话存储管理器
    使用ChromaDB存储对话历史，格式参考chap01处理流程
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.collection_name = "chat_conversations"
        self.init_chromadb()
    
    def init_chromadb(self):
        """
        初始化ChromaDB客户端和集合
        """
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"已连接到现有集合: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Chat conversations storage"}
                )
                print(f"已创建新集合: {self.collection_name}")
                
        except Exception as e:
            print(f"ChromaDB初始化失败: {e}")
            raise
    
    def save_message(self, session_id: str, message_id: str, speaker_id: str, 
                    content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        保存单条消息到ChromaDB
        
        Args:
            session_id: 会话ID
            message_id: 消息ID
            speaker_id: 说话人ID（"用户" 或 "AI助手"）
            content: 消息内容
            metadata: 额外的元数据
        
        Returns:
            是否保存成功
        """
        try:
            timestamp = datetime.now().isoformat()
            word_count = len(content)
            
            # 构建元数据
            full_metadata = {
                "session_id": session_id,
                "speaker_id": speaker_id,
                "timestamp": timestamp,
                "word_count": word_count,
                "message_type": "chat_message"
            }
            
            if metadata:
                full_metadata.update(metadata)
            
            # 保存到ChromaDB
            self.collection.add(
                documents=[content],
                metadatas=[full_metadata],
                ids=[message_id]
            )
            
            return True
            
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取指定会话的对话历史
        
        Args:
            session_id: 会话ID
        
        Returns:
            对话历史列表
        """
        try:
            results = self.collection.get(
                where={"session_id": session_id},
                include=["documents", "metadatas"]
            )
            
            messages = []
            for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                messages.append({
                    "message_id": results["ids"][i],
                    "speaker_id": metadata["speaker_id"],
                    "content": doc,
                    "timestamp": metadata["timestamp"],
                    "word_count": metadata["word_count"],
                    "metadata": {k: v for k, v in metadata.items() 
                               if k not in ["session_id", "speaker_id", "timestamp", "word_count"]}
                })
            
            # 按时间戳排序
            messages.sort(key=lambda x: x["timestamp"])
            return messages
            
        except Exception as e:
            print(f"获取会话历史失败: {e}")
            return []
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有会话列表
        
        Returns:
            会话信息列表
        """
        try:
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            sessions = {}
            for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                session_id = metadata["session_id"]
                timestamp = metadata["timestamp"]
                
                if session_id not in sessions:
                    sessions[session_id] = {
                        "session_id": session_id,
                        "created_at": timestamp,
                        "last_message_at": timestamp,
                        "message_count": 0,
                        "preview": ""
                    }
                
                # 更新会话信息
                sessions[session_id]["message_count"] += 1
                if timestamp > sessions[session_id]["last_message_at"]:
                    sessions[session_id]["last_message_at"] = timestamp
                
                # 设置预览（取第一条用户消息的前30个字符）
                if not sessions[session_id]["preview"] and metadata["speaker_id"] == "用户":
                    sessions[session_id]["preview"] = doc[:30] + ("..." if len(doc) > 30 else "")
            
            # 按最后消息时间排序
            session_list = list(sessions.values())
            session_list.sort(key=lambda x: x["last_message_at"], reverse=True)
            
            return session_list
            
        except Exception as e:
            print(f"获取会话列表失败: {e}")
            return []

# 创建FastAPI应用
app = FastAPI(
    title="QA系统聊天API",
    description="基于DeepSeek和ChromaDB的智能问答系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
storage = ConversationStorage()
deepseek_config = DeepSeekPresets.get_qa_system()
deepseek_client = DeepSeekClient(deepseek_config)

# 初始化搜索系统
search_interface = SearchInterface(config_name="balanced")

# 初始化多阶段查询系统
dimension_analyzer = DimensionAnalyzer(deepseek_client)
# 获取vectorizer实例用于关键词搜索
vectorizer = None
search_initialized = False
try:
    search_initialized = search_interface.initialize()
    if search_initialized:
        vectorizer = search_interface.vectorizer
        print("✅ 搜索系统初始化成功")
    else:
        print("❌ 搜索系统初始化失败")
except Exception as e:
    print(f"❌ 搜索系统初始化异常: {e}")
    search_initialized = False

multi_stage_query = MultiStageQuerySystem(search_interface, vectorizer)
# 延迟初始化context_manager，因为需要等search_interface初始化完成
context_manager = None

@app.get("/")
async def root():
    """根路径"""
    return {"message": "QA系统聊天API服务正在运行"}

@app.get("/health")
async def health_check():
    """系统健康检查端点"""
    try:
        global search_interface, deepseek_client
        
        # 生成健康检查报告
        report = generate_health_report(
            search_interface=search_interface,
            deepseek_client=deepseek_client,
            config=search_interface.config if search_interface else None
        )
        
        # 根据健康状态设置HTTP状态码
        status_code = 200
        if report['overall_status'] == 'error':
            status_code = 503  # Service Unavailable
        elif report['overall_status'] == 'degraded':
            status_code = 206  # Partial Content
        
        return JSONResponse(
            content=report,
            status_code=status_code
        )
        
    except Exception as e:
        return JSONResponse(
            content={
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': f'健康检查失败: {str(e)}'
            },
            status_code=500
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    发送消息并获取AI回复
    
    Args:
        request: 聊天请求
    
    Returns:
        AI回复
    """
    try:
        # 检查关键组件初始化状态
        global search_interface, context_manager, vectorizer, search_initialized
        
        if not search_initialized or not search_interface.initialized:
            print("⚠️ 搜索系统未正确初始化，尝试重新初始化...")
            try:
                search_initialized = search_interface.initialize()
                if search_initialized:
                    vectorizer = search_interface.vectorizer
                    print("✅ 搜索系统重新初始化成功")
                else:
                    raise HTTPException(
                        status_code=500, 
                        detail="搜索系统初始化失败，无法提供服务"
                    )
            except Exception as e:
                print(f"❌ 搜索系统重新初始化失败: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"搜索系统不可用: {str(e)}"
                )
        
        if vectorizer is None:
            print("❌ 向量化器未初始化")
            raise HTTPException(
                status_code=500, 
                detail="向量化器不可用"
            )
        
        # 生成或使用现有会话ID
        session_id = request.session_id or str(uuid.uuid4())
        user_message_id = str(uuid.uuid4())
        ai_message_id = str(uuid.uuid4())
        
        # 获取会话历史用于上下文
        history = storage.get_session_history(session_id)
        
        # 构建对话上下文
        conversation_history = []
        for msg in history[-10:]:  # 只取最近10条消息作为上下文
            role = "user" if msg["speaker_id"] == "用户" else "assistant"
            conversation_history.append({
                "role": role,
                "content": msg["content"]
            })
        
        # 添加当前用户消息
        conversation_history.append({
            "role": "user",
            "content": request.message
        })
        
        # 使用多阶段查询系统进行智能搜索
        search_start = datetime.now()
        
        # 确保搜索系统已初始化
        if not search_interface.initialized:
            search_interface.initialize()
        
        # 延迟初始化context_manager
        global context_manager
        if context_manager is None:
            try:
                if search_interface.search_system is None:
                    print("❌ 搜索系统未正确初始化，无法创建上下文管理器")
                    raise HTTPException(
                        status_code=500, 
                        detail="搜索系统未正确初始化"
                    )
                # 直接传递collection给ContextManager
                context_manager = ContextManager(
                    search_system=search_interface.search_system,
                    collection=search_interface.vectorizer.collection
                )
                print("✅ 上下文管理器初始化成功")
            except Exception as e:
                print(f"❌ 上下文管理器初始化失败: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"上下文管理器初始化失败: {str(e)}"
                )
        
        # 构建历史上下文字符串用于多轮检索
        history_context = ""
        if len(conversation_history) > 1:  # 有历史对话
            history_messages = conversation_history[:-1]  # 排除当前消息
            history_context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in history_messages[-5:]  # 只取最近5轮对话作为上下文
            ])
            print(f"构建的历史上下文: {history_context[:200]}...")  # 打印前200字符用于调试
        
        # 1. 维度分析（传递历史上下文）
        dimension_result = dimension_analyzer.analyze_query_dimensions(
            query=request.message,
            current_context=history_context
        )
        
        # 2. 多阶段搜索（传递历史上下文）
        search_results = multi_stage_query.multi_stage_search(
            query=request.message,
            current_context=history_context,
            max_results=5,  # 每个维度获取5个结果
            dimension_analysis=dimension_result
        )
        
        # 3. 上下文管理和去重
        # 从多阶段搜索结果中提取实际的搜索结果列表
        actual_search_results = search_results.get('results', []) if isinstance(search_results, dict) else search_results
        print(f"Debug: search_results type: {type(search_results)}")
        print(f"Debug: actual_search_results type: {type(actual_search_results)}")
        
        context_result = context_manager.process_search_results(
            search_results=actual_search_results,
            query=request.message,
            max_context_length=2000  # 限制上下文长度
        )
        print(f"Debug: context_result type: {type(context_result)}")
        print(f"Debug: dimension_result type: {type(dimension_result)}")
        
        # 检查context_result是否为字符串
        if isinstance(context_result, str):
            print(f"ERROR: context_result is a string: {context_result[:100]}...")
            # 如果是字符串，创建一个默认的字典结构
            context_result = {
                'processed_results': [],
                'context': '',
                'stats': {
                    'original_count': 0,
                    'deduplicated_count': 0,
                    'final_count': 0,
                    'context_length': 0
                }
            }
        
        search_time = (datetime.now() - search_start).total_seconds()
        
        # 构建增强的prompt
        enhanced_message = request.message
        if isinstance(context_result, dict) and context_result.get('context'):
            enhanced_message = f"""基于以下相关文档内容回答问题：

{context_result['context']}

问题：{request.message}

请根据上述相关内容回答问题。在回答时，如果相关内容不足以回答问题，你可以依照自身理解进行作答，并提供你的一般性建议以及正常回答，一般性建议和正常回答可以尽可能详细丰富。注意，上下文中的标识格式为[文件名-chunk编号 - 来源: 文件名]，请在回答时引用具体的文件名而不是使用"文档1"、"文档2"等通用标识。回答的结果不要包含上下文的json格式，对上下文信息进行总结作答即可。"""
        
        # 调用DeepSeek API
        start_time = datetime.now()
        # 从conversation_history中分离出历史对话和当前消息
        history_messages = conversation_history[:-1]  # 除了最后一条消息的所有历史
        current_message = enhanced_message  # 使用增强后的消息
        
        try:
            ai_response, updated_conversation = deepseek_client.multi_turn_chat(
                history_messages, 
                current_message
            )
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            ai_response = f"抱歉，我暂时无法回答您的问题。错误信息: {str(e)}"
            # 移除未使用的变量赋值
        
        end_time = datetime.now()
        
        # 构建result格式以保持兼容性
        result = {
            "content": ai_response,
            "usage": {}  # 这里可以从deepseek_client获取usage信息
        }
        
        # 确保ai_response是字符串
        if not isinstance(ai_response, str):
            ai_response = str(ai_response)
        response_time = (end_time - start_time).total_seconds()
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="调用失败")
        
        usage_info = result.get("usage", {})
        
        # 保存用户消息
        try:
            # 将列表类型转换为字符串以兼容ChromaDB
            dimensions = dimension_result.get('dimensions', []) if isinstance(dimension_result, dict) else []
            dimension_str = json.dumps(dimensions, ensure_ascii=False) if dimensions else ""
            
            user_metadata = {
                "model_config": "qa_system",
                "response_time": response_time,
                "search_time": search_time,
                "search_results_count": context_result.get('stats', {}).get('final_count', 0) if isinstance(context_result, dict) else 0,
                "dimension_analysis": dimension_str,
                "search_stages": len([stage for stage in search_results.values() if isinstance(stage, dict) and stage.get('results')]) if isinstance(search_results, dict) else 1,
                "deduplicated_count": context_result.get('stats', {}).get('deduplicated_count', 0) if isinstance(context_result, dict) else 0
            }
        except Exception as e:
            print(f"ERROR in user_metadata creation: {e}")
            print(f"context_result type: {type(context_result)}, value: {context_result}")
            print(f"dimension_result type: {type(dimension_result)}, value: {dimension_result}")
            print(f"search_results type: {type(search_results)}, value: {search_results}")
            raise
        storage.save_message(session_id, user_message_id, "用户", request.message, user_metadata)
        
        # 保存AI回复 - 展平token_usage字典
        ai_metadata = {
            "model_config": "qa_system",
            "response_time": response_time,
            "search_time": search_time,
            "search_results_count": context_result.get('stats', {}).get('final_count', 0) if isinstance(context_result, dict) else 0,
            "dimension_analysis": dimension_str,  # 使用已转换的字符串
            "search_stages": len([stage for stage in search_results.values() if isinstance(stage, dict) and stage.get('results')]) if isinstance(search_results, dict) else 1,
            "deduplicated_count": context_result.get('stats', {}).get('deduplicated_count', 0) if isinstance(context_result, dict) else 0,
            "prompt_tokens": usage_info.get("prompt_tokens", 0),
            "completion_tokens": usage_info.get("completion_tokens", 0),
            "total_tokens": usage_info.get("total_tokens", 0)
        }
        storage.save_message(session_id, ai_message_id, "AI助手", ai_response, ai_metadata)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            message_id=ai_message_id,
            timestamp=datetime.now().isoformat(),
            usage=usage_info
        )
        
    except Exception as e:
        print(f"聊天处理失败: {e}")
        raise HTTPException(status_code=500, detail="调用失败")

@app.get("/sessions", response_model=List[SessionInfo])
async def get_sessions():
    """
    获取所有会话列表
    
    Returns:
        会话信息列表
    """
    try:
        sessions = storage.get_all_sessions()
        return [SessionInfo(**session) for session in sessions]
    except Exception as e:
        print(f"获取会话列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取会话列表失败")

@app.get("/sessions/{session_id}", response_model=ConversationHistory)
async def get_session_history(session_id: str):
    """
    获取指定会话的对话历史
    
    Args:
        session_id: 会话ID
    
    Returns:
        对话历史
    """
    try:
        messages = storage.get_session_history(session_id)
        conversation_messages = [ConversationMessage(**msg) for msg in messages]
        
        return ConversationHistory(
            session_id=session_id,
            messages=conversation_messages,
            total_messages=len(conversation_messages)
        )
    except Exception as e:
        print(f"获取会话历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取会话历史失败")

@app.post("/sessions/new")
async def create_new_session():
    """
    创建新会话
    
    Returns:
        新会话ID
    """
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    print("启动QA系统聊天后端服务...")
    print("API文档地址: http://localhost:8000/docs")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=120,  # 保持连接超时120秒
        timeout_graceful_shutdown=30  # 优雅关闭超时30秒
    )