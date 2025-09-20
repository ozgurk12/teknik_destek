import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  PersonOutline,
  EmailOutlined,
  BadgeOutlined,
  AdminPanelSettings,
  SupervisorAccount,
  Person,
  VpnKey,
  Security,
  Extension as ModuleIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Settings: React.FC = () => {
  console.log('Settings component rendering...');
  const { user, updateUserInfo } = useAuth();
  console.log('Current user in Settings:', user);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);

  // Profile form state
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const getRoleDisplay = (role: string | undefined) => {
    switch (role) {
      case 'admin':
        return { label: 'Admin', color: 'error' as const, icon: <AdminPanelSettings /> };
      case 'yonetici':
        return { label: 'Yönetici', color: 'warning' as const, icon: <SupervisorAccount /> };
      case 'kullanici':
        return { label: 'Kullanıcı', color: 'info' as const, icon: <Person /> };
      default:
        return { label: 'Kullanıcı', color: 'default' as const, icon: <Person /> };
    }
  };

  const handleProfileUpdate = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.put('/users/me', profileData);
      updateUserInfo(response.data);
      setSuccess('Profil bilgileri güncellendi');
      setIsEditingProfile(false);
    } catch (err: any) {
      console.error('Profile update error:', err);
      setError(err.response?.data?.detail || 'Profil güncellenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Yeni şifreler eşleşmiyor');
      return;
    }

    if (passwordData.new_password.length < 8) {
      setError('Yeni şifre en az 8 karakter olmalıdır');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.put('/users/me/password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      setSuccess('Şifre başarıyla güncellendi');
      setPasswordDialogOpen(false);
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (err: any) {
      console.error('Password change error:', err);
      setError(err.response?.data?.detail || 'Şifre güncellenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const roleInfo = getRoleDisplay(user?.role);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Ayarlar
      </Typography>

      {success && (
        <Alert severity="success" onClose={() => setSuccess('')} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profil Bilgileri */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Profil Bilgileri
                </Typography>
                {!isEditingProfile ? (
                  <IconButton onClick={() => setIsEditingProfile(true)} color="primary">
                    <EditIcon />
                  </IconButton>
                ) : (
                  <Box>
                    <IconButton onClick={handleProfileUpdate} color="success" disabled={loading}>
                      <CheckIcon />
                    </IconButton>
                    <IconButton onClick={() => setIsEditingProfile(false)} color="error">
                      <CloseIcon />
                    </IconButton>
                  </Box>
                )}
              </Box>

              <List>
                <ListItem>
                  <ListItemIcon>
                    <PersonOutline />
                  </ListItemIcon>
                  {isEditingProfile ? (
                    <TextField
                      fullWidth
                      label="Ad Soyad"
                      value={profileData.full_name}
                      onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                      size="small"
                    />
                  ) : (
                    <ListItemText
                      primary="Ad Soyad"
                      secondary={user?.full_name}
                    />
                  )}
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <BadgeOutlined />
                  </ListItemIcon>
                  <ListItemText
                    primary="Kullanıcı Adı"
                    secondary={user?.username}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    <EmailOutlined />
                  </ListItemIcon>
                  {isEditingProfile ? (
                    <TextField
                      fullWidth
                      label="E-posta"
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      size="small"
                    />
                  ) : (
                    <ListItemText
                      primary="E-posta"
                      secondary={user?.email}
                    />
                  )}
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    {roleInfo.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary="Yetki Seviyesi"
                    secondary={
                      <Chip
                        label={roleInfo.label}
                        color={roleInfo.color}
                        size="small"
                        sx={{ mt: 0.5 }}
                      />
                    }
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Güvenlik Ayarları */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Security sx={{ verticalAlign: 'middle', mr: 1 }} />
                Güvenlik
              </Typography>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  startIcon={<VpnKey />}
                  fullWidth
                  onClick={() => setPasswordDialogOpen(true)}
                  sx={{ mb: 2 }}
                >
                  Şifre Değiştir
                </Button>

                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Hesap Durumu
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <Chip
                      label={user?.is_active ? 'Aktif' : 'Pasif'}
                      color={user?.is_active ? 'success' : 'error'}
                      size="small"
                    />
                    {user?.is_verified && (
                      <Chip
                        label="Doğrulanmış"
                        color="primary"
                        size="small"
                      />
                    )}
                  </Box>
                </Paper>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Modül Yetkileri */}
        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ModuleIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                Modül Yetkileri
              </Typography>

              <Grid container spacing={2} sx={{ mt: 1 }}>
                {user?.modules && user.modules.length > 0 ? (
                  user.modules.map((module: any) => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={module.id}>
                      <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {module.display_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {module.description}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))
                ) : (
                  <Grid size={12}>
                    <Typography variant="body2" color="text.secondary">
                      Henüz modül yetkisi atanmamış
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Şifre Değiştirme Dialog */}
      <Dialog
        open={passwordDialogOpen}
        onClose={() => setPasswordDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Şifre Değiştir</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              type="password"
              label="Mevcut Şifre"
              value={passwordData.current_password}
              onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="password"
              label="Yeni Şifre"
              value={passwordData.new_password}
              onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
              helperText="En az 8 karakter, büyük/küçük harf ve rakam içermelidir"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="password"
              label="Yeni Şifre (Tekrar)"
              value={passwordData.confirm_password}
              onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialogOpen(false)}>
            İptal
          </Button>
          <Button
            onClick={handlePasswordChange}
            variant="contained"
            disabled={loading}
          >
            Güncelle
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;