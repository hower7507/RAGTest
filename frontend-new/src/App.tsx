import { useState, useEffect } from 'react';
import {
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Alert,
  Snackbar,
  IconButton,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
} from '@mui/icons-material';
import ChatInterface from './components/ChatInterface';
import SessionSidebar from './components/SessionSidebar';
import { ApiService } from './services/api';
import './App.css';

// 创建主题
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#4caf50',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  // 使用更安全的初始化方式，避免SSR问题
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth >= 900; // md断点约为900px
  });
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [notification, setNotification] = useState<{ message: string; severity: 'success' | 'error' | 'info' } | null>(null);

  // 检查API连接状态
  useEffect(() => {
    checkConnection();
  }, []);

  // 响应式侧边栏控制，添加延迟确保准确检测
  useEffect(() => {
    const timer = setTimeout(() => {
      if (isMobile) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    }, 100); // 短暂延迟确保useMediaQuery准确检测
    
    return () => clearTimeout(timer);
  }, [isMobile]);

  const checkConnection = async () => {
    try {
      await ApiService.checkConnection();
      setConnectionStatus('connected');
    } catch (error) {
      console.error('API连接失败:', error);
      setConnectionStatus('disconnected');
    }
  };

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    setNotification({ message, severity });
  };

  const handleNewSession = () => {
    setCurrentSessionId(null);
    showNotification('已创建新会话', 'success');
  };

  const handleSessionSelect = (sessionId: string | null) => {
    setCurrentSessionId(sessionId);
    if (sessionId) {
      showNotification('已切换会话', 'info');
    }
  };

  const handleSessionChange = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* 连接状态提示 */}
        {connectionStatus === 'disconnected' && (
          <Alert 
            severity="error" 
            sx={{ 
              position: 'fixed', 
              top: 0, 
              left: 0, 
              right: 0, 
              zIndex: 9999,
              borderRadius: 0
            }}
          >
            无法连接到后端服务，请确保后端服务正在运行
          </Alert>
        )}

        {/* 侧边栏 */}
        <SessionSidebar
          currentSessionId={currentSessionId}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
          open={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />

        {/* 主内容区域 */}
        <Box sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column',
          marginTop: connectionStatus === 'disconnected' ? '48px' : 0,
          transition: 'margin-top 0.3s ease'
        }}>
          {/* 桌面端工具栏 */}
          {!isMobile && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              p: 1, 
              borderBottom: 1, 
              borderColor: 'divider',
              bgcolor: 'background.paper'
            }}>
              <IconButton
                onClick={() => setSidebarOpen(!sidebarOpen)}
                sx={{ mr: 1 }}
              >
                <MenuIcon />
              </IconButton>
            </Box>
          )}

          {/* 聊天界面 */}
          <ChatInterface
            sessionId={currentSessionId}
            onSessionChange={handleSessionChange}
          />
        </Box>

        {/* 通知 */}
        <Snackbar
          open={!!notification}
          autoHideDuration={3000}
          onClose={() => setNotification(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={() => setNotification(null)} 
            severity={notification?.severity || 'info'}
            sx={{ width: '100%' }}
          >
            {notification?.message || ''}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;
