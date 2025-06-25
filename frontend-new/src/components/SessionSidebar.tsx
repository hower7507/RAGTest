import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  IconButton,
  Divider,
  Button,
  Alert,
  CircularProgress,
  Drawer,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Add as AddIcon,
  Chat as ChatIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { ApiService, type SessionInfo } from '../services/api';
import './SessionSidebar.css';

interface SessionSidebarProps {
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string | null) => void;
  onNewSession: () => void;
  open: boolean;
  onToggle: () => void;
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({
  currentSessionId,
  onSessionSelect,
  onNewSession,
  open,
  onToggle,
}) => {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // 加载会话列表
  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const sessionList = await ApiService.getSessions();
      setSessions(sessionList);
    } catch (err: any) {
      console.error('加载会话列表失败:', err);
      setError('加载会话列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      loadSessions();
    }
  }, [open]);

  // 刷新会话列表（当有新消息时）
  useEffect(() => {
    if (currentSessionId && open) {
      loadSessions();
    }
  }, [currentSessionId]);

  const handleSessionClick = (sessionId: string) => {
    onSessionSelect(sessionId);
    if (isMobile) {
      onToggle(); // 在移动端选择会话后关闭侧边栏
    }
  };

  const handleNewSession = () => {
    onNewSession();
    if (isMobile) {
      onToggle(); // 在移动端创建新会话后关闭侧边栏
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return '今天';
    } else if (diffDays === 1) {
      return '昨天';
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const sidebarContent = (
    <Box className="session-sidebar">
      {/* 头部 */}
      <Box className="sidebar-header">
        <Box className="header-content">
          <Typography variant="h6" className="sidebar-title">
            QA系统
          </Typography>
          {isMobile && (
            <IconButton onClick={onToggle} size="small">
              <CloseIcon />
            </IconButton>
          )}
        </Box>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleNewSession}
          fullWidth
          className="new-session-btn"
        >
          新建对话
        </Button>
      </Box>

      <Divider />

      {/* 会话列表 */}
      <Box className="sessions-container">
        {loading && (
          <Box className="loading-container">
            <CircularProgress size={24} />
            <Typography variant="body2" color="text.secondary">
              加载中...
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        {!loading && !error && sessions.length === 0 && (
          <Box className="empty-state">
            <ChatIcon className="empty-icon" />
            <Typography variant="body2" color="text.secondary">
              暂无对话记录
            </Typography>
          </Box>
        )}

        {!loading && !error && sessions.length > 0 && (
          <List className="sessions-list">
            {sessions.map((session) => (
              <ListItem key={session.session_id} disablePadding>
                <ListItemButton
                  selected={currentSessionId === session.session_id}
                  onClick={() => handleSessionClick(session.session_id)}
                  className="session-item"
                >
                  <ListItemText
                    primary={session.preview || 'New Chat'}
                    secondary={
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Typography variant="body2" color="text.secondary" component="span">
                          {formatDate(session.created_at)}
                        </Typography>
                        <Typography variant="body2" className="session-preview" component="span">
                          {session.preview}
                        </Typography>
                      </Box>
                    }
                    secondaryTypographyProps={{ component: 'div' }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    </Box>
  );

  if (isMobile) {
    return (
      <>
        {/* 移动端菜单按钮 */}
        {!open && (
          <IconButton
            onClick={onToggle}
            className="mobile-menu-btn"
            sx={{
              position: 'fixed',
              top: 16,
              left: 16,
              zIndex: 1200,
              backgroundColor: 'white',
              boxShadow: 2,
              '&:hover': {
                backgroundColor: 'grey.100',
              },
            }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        {/* 移动端抽屉 */}
        <Drawer
          anchor="left"
          open={open}
          onClose={onToggle}
          ModalProps={{
            keepMounted: true, // 更好的移动端性能
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
            },
          }}
        >
          {sidebarContent}
        </Drawer>
      </>
    );
  }

  // 桌面端固定侧边栏
  return (
    <Box
      className={`desktop-sidebar ${open ? 'open' : 'closed'}`}
      sx={{
        width: open ? 280 : 0,
        minWidth: open ? 280 : 0,
        maxWidth: open ? 280 : 0,
        transition: 'width 0.3s ease',
        overflow: 'hidden',
        borderRight: open ? '1px solid #e0e0e0' : 'none',
        flexShrink: 0, // 防止被压缩
      }}
    >
      {open && sidebarContent}
    </Box>
  );
};

export default SessionSidebar;