import axios from 'axios';

// API基础配置
const API_BASE_URL = 'http://localhost:8000';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 增加到120秒，适应复杂AI查询处理
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// 数据类型定义
export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  message_id: string;
  timestamp: string;
  usage: Record<string, any>;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_message_at: string;
  message_count: number;
  preview: string;
}

export interface ConversationMessage {
  message_id: string;
  speaker_id: string;
  content: string;
  timestamp: string;
  word_count: number;
  metadata: Record<string, any>;
}

export interface ConversationHistory {
  session_id: string;
  messages: ConversationMessage[];
  total_messages: number;
}

// API服务类
export class ApiService {
  /**
   * 发送聊天消息
   */
  static async sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    try {
      const payload: ChatMessage = {
        message,
        ...(sessionId && { session_id: sessionId })
      };
      
      const response = await apiClient.post<ChatResponse>('/chat', payload);
      return response.data;
    } catch (error) {
      console.error('发送消息失败:', error);
      throw new Error('调用失败，无法提问');
    }
  }

  /**
   * 获取所有会话列表
   */
  static async getSessions(): Promise<SessionInfo[]> {
    try {
      const response = await apiClient.get<SessionInfo[]>('/sessions');
      return response.data;
    } catch (error) {
      console.error('获取会话列表失败:', error);
      throw new Error('获取会话列表失败');
    }
  }

  /**
   * 获取指定会话的对话历史
   */
  static async getSessionHistory(sessionId: string): Promise<ConversationHistory> {
    try {
      const response = await apiClient.get<ConversationHistory>(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('获取会话历史失败:', error);
      throw new Error('获取会话历史失败');
    }
  }

  /**
   * 创建新会话
   */
  static async createNewSession(): Promise<{ session_id: string }> {
    try {
      const response = await apiClient.post<{ session_id: string }>('/sessions/new');
      return response.data;
    } catch (error) {
      console.error('创建新会话失败:', error);
      throw new Error('创建新会话失败');
    }
  }

  /**
   * 测试API连接
   */
  static async testConnection(): Promise<boolean> {
    try {
      const response = await apiClient.get('/');
      return response.status === 200;
    } catch (error) {
      console.error('API连接测试失败:', error);
      return false;
    }
  }

  /**
   * 检查API连接
   */
  static async checkConnection(): Promise<void> {
    try {
      const response = await apiClient.get('/');
      if (response.status !== 200) {
        throw new Error('API连接失败');
      }
    } catch (error) {
      console.error('API连接检查失败:', error);
      throw error;
    }
  }
}

export default ApiService;