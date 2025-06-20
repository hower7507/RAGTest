import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { ApiService, type ConversationMessage } from '../services/api';
import './ChatInterface.css';
import './MarkdownStyles.css';

interface ChatInterfaceProps {
  sessionId: string | null;
  onSessionChange: (sessionId: string) => void;
}

interface DisplayMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: string;
  isLoading?: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, onSessionChange }) => {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 加载会话历史
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory(sessionId);
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const history = await ApiService.getSessionHistory(sessionId);
      const displayMessages: DisplayMessage[] = history.messages.map((msg: ConversationMessage) => ({
        id: msg.message_id,
        content: msg.content,
        isUser: msg.speaker_id === '用户',
        timestamp: msg.timestamp,
      }));
      setMessages(displayMessages);
      setError(null);
    } catch (err) {
      console.error('加载会话历史失败:', err);
      setError('加载会话历史失败');
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);

    // 添加用户消息
    const userDisplayMessage: DisplayMessage = {
      id: `user-${Date.now()}`,
      content: userMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userDisplayMessage]);
    setIsLoading(true);

    // 添加加载中的AI消息
    const loadingMessage: DisplayMessage = {
      id: `loading-${Date.now()}`,
      content: '正在思考中...',
      isUser: false,
      timestamp: new Date().toISOString(),
      isLoading: true,
    };

    setMessages(prev => [...prev, loadingMessage]);

    try {
      const response = await ApiService.sendMessage(userMessage, sessionId || undefined);
      
      // 如果是新会话，更新会话ID
      if (!sessionId) {
        onSessionChange(response.session_id);
      }

      // 移除加载消息，添加AI回复
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== loadingMessage.id);
        return [
          ...filtered,
          {
            id: response.message_id,
            content: response.response,
            isUser: false,
            timestamp: response.timestamp,
          }
        ];
      });

    } catch (err: any) {
      console.error('发送消息失败:', err);
      setError(err.message || '调用失败，无法提问');
      
      // 移除加载消息
      setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Box className="chat-interface">
      {/* 消息区域 */}
      <Box className="messages-container">
        {messages.length === 0 && !sessionId && (
          <Box className="welcome-message">
            <Typography variant="h5" color="text.secondary" gutterBottom>
              欢迎使用QA系统
            </Typography>
            <Typography variant="body1" color="text.secondary">
              请输入您的问题，我将为您提供帮助。
            </Typography>
          </Box>
        )}

        {messages.map((message) => (
          <Box
            key={message.id}
            className={`message-wrapper ${message.isUser ? 'user' : 'assistant'}`}
          >
            <Box className="message-avatar">
              {message.isUser ? (
                <PersonIcon className="avatar-icon user-avatar" />
              ) : (
                <BotIcon className="avatar-icon bot-avatar" />
              )}
            </Box>
            <Paper className="message-content" elevation={1}>
              <Box className="message-header">
                <Typography variant="caption" color="text.secondary">
                  {message.isUser ? '您' : 'AI助手'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatTimestamp(message.timestamp)}
                </Typography>
              </Box>
              {message.isUser ? (
                <Typography 
                  variant="body1" 
                  className={`message-text ${message.isLoading ? 'loading' : ''}`}
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {message.content}
                  {message.isLoading && (
                    <CircularProgress size={16} sx={{ ml: 1 }} />
                  )}
                </Typography>
              ) : (
                <Box className={`message-text ${message.isLoading ? 'loading' : ''}`}>
                   <div className="markdown-content">
                     <ReactMarkdown>{message.content}</ReactMarkdown>
                   </div>
                   {message.isLoading && (
                     <CircularProgress size={16} sx={{ ml: 1 }} />
                   )}
                 </Box>
              )}
            </Paper>
          </Box>
        ))}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mx: 2, mb: 1 }}>
          {error}
        </Alert>
      )}

      {/* 输入区域 */}
      <Box className="input-container">
        <Divider />
        <Box className="input-wrapper">
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题..."
            variant="outlined"
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '20px',
                backgroundColor: 'white',
              },
            }}
            InputProps={{
              endAdornment: (
                <IconButton
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  color="primary"
                  sx={{ ml: 1 }}
                >
                  {isLoading ? (
                    <CircularProgress size={24} />
                  ) : (
                    <SendIcon />
                  )}
                </IconButton>
              ),
            }}
          />
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface;