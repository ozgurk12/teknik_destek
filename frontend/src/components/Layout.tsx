import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Avatar,
  Menu,
  MenuItem as MuiMenuItem,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Dashboard as DashboardIcon,
  AutoAwesome as AutoAwesomeIcon,
  ListAlt as ListAltIcon,
  School as SchoolIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  CalendarMonth as CalendarMonthIcon,
  SupervisorAccount as SupervisorAccountIcon,
  AdminPanelSettings as AdminPanelSettingsIcon,
  VideoLibrary as VideoIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 260;

interface MenuItem {
  text: string;
  icon: React.ReactNode;
  path: string;
  badge?: string;
  module?: string;
  roles?: string[];
}

const Layout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasModule, hasRole } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [open, setOpen] = useState(!isMobile);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
  };

  const menuItems: MenuItem[] = [
    { text: 'Ana Sayfa', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Etkinlik Oluştur', icon: <AutoAwesomeIcon />, path: '/activity-generator', badge: 'YENİ', module: 'etkinlik_olusturma' },
    { text: 'Etkinlikler', icon: <ListAltIcon />, path: '/activities', module: 'etkinlik_olusturma' },
    { text: 'Günlük Planlar', icon: <CalendarMonthIcon />, path: '/daily-plans', badge: 'YENİ', module: 'gunluk_plan' },
    { text: 'Aylık Plan Oluştur', icon: <CalendarMonthIcon />, path: '/monthly-plan-generator', badge: 'YENİ', module: 'aylik_plan' },
    { text: 'Aylık Planlar', icon: <ListAltIcon />, path: '/monthly-plans', module: 'aylik_plan' },
    { text: 'Video Oluştur', icon: <VideoIcon />, path: '/video-generation', badge: 'YENİ', module: 'video_generation' },
    { text: 'Videolar', icon: <VideoIcon />, path: '/video-list', module: 'video_generation' },
    { text: 'Video Metni Oluştur', icon: <VideoIcon />, path: '/video-script-generator', badge: 'YENİ', module: 'video_generation' },
    { text: 'Video Metinleri', icon: <VideoIcon />, path: '/video-scripts', module: 'video_generation' },
    { text: 'Kazanımlar', icon: <SchoolIcon />, path: '/kazanimlar', module: 'kazanim_yonetimi' },
    { text: 'İstatistikler', icon: <BarChartIcon />, path: '/statistics', module: 'raporlama' },
    { text: 'Kullanıcı Yönetimi', icon: <SupervisorAccountIcon />, path: '/users', roles: ['admin', 'yonetici'] },
    { text: 'Ayarlar', icon: <SettingsIcon />, path: '/settings' },
  ].filter(item => {
    if (item.module && !hasModule(item.module)) return false;
    if (item.roles && !hasRole(item.roles)) return false;
    return true;
  });

  const getRoleIcon = () => {
    if (!user) return <PersonIcon />;
    switch (user.role) {
      case 'admin':
        return <AdminPanelSettingsIcon />;
      case 'yonetici':
        return <SupervisorAccountIcon />;
      default:
        return <PersonIcon />;
    }
  };

  const getRoleColor = () => {
    if (!user) return 'default';
    switch (user.role) {
      case 'admin':
        return 'error.main';
      case 'yonetici':
        return 'warning.main';
      default:
        return 'info.main';
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      

      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${open ? drawerWidth : 0}px)` },
          ml: { md: `${open ? drawerWidth : 0}px` },
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerToggle}
            edge="start"
            sx={{ mr: 2 }}
          >
            {open ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
          
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6" noWrap component="div">
              EduPage Kids - Etkinlik Planlama Sistemi
            </Typography>
            {user && (
              <Chip
                label={user.role === 'admin' ? 'Admin' : user.role === 'yonetici' ? 'Yönetici' : 'Kullanıcı'}
                size="small"
                sx={{ bgcolor: getRoleColor(), color: 'white' }}
              />
            )}
          </Box>

          <IconButton
            onClick={handleMenuClick}
            sx={{ ml: 2 }}
          >
            <Avatar sx={{ bgcolor: getRoleColor() }}>
              {getRoleIcon()}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MuiMenuItem disabled>
              <ListItemIcon>
                <PersonIcon fontSize="small" />
              </ListItemIcon>
              <Box>
                <Typography variant="body2">{user?.full_name}</Typography>
                <Typography variant="caption" color="text.secondary">@{user?.username}</Typography>
              </Box>
            </MuiMenuItem>
            <MuiMenuItem
              onClick={(e) => {
                e.preventDefault();
                handleMenuClose();
                setTimeout(() => {
                  navigate('/settings');
                }, 0);
              }}
            >
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              Ayarlar
            </MuiMenuItem>
            <Divider />
            <MuiMenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Çıkış Yap
            </MuiMenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            borderRight: 'none',
            boxShadow: '2px 0 8px rgba(0,0,0,0.05)',
          },
        }}
        variant={isMobile ? 'temporary' : 'persistent'}
        anchor="left"
        open={open}
        onClose={handleDrawerToggle}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: theme.spacing(3),
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}
        >
          <Typography variant="h5" fontWeight="bold">
            🎨 EduPage Kids
          </Typography>
        </Box>
        
        <Divider />
        
        <List sx={{ px: 2, py: 1 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => {
                  navigate(item.path);
                }}
                selected={location.pathname === item.path}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.primary.main,
                    color: 'white',
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                    '&:hover': {
                      backgroundColor: theme.palette.primary.dark,
                    },
                  },
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover,
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: location.pathname === item.path ? 'white' : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
                {item.badge && (
                  <Chip
                    label={item.badge}
                    size="small"
                    color="secondary"
                    sx={{ ml: 1 }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          width: { md: `calc(100% - ${open ? drawerWidth : 0}px)` },
          ml: { md: `${open ? drawerWidth : 0}px` },
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          minHeight: '100vh',
          mt: 8,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;