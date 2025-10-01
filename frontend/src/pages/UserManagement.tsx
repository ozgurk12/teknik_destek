import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Person,
  AdminPanelSettings,
  SupervisorAccount,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'admin' | 'yonetici' | 'kullanici';
  is_active: boolean;
  modules: Module[];
  created_at: string;
}

interface Module {
  id: string;
  name: string;
  display_name: string;
  description?: string;
}

const UserManagement: React.FC = () => {
  const { user: currentUser, hasRole } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    role: 'kullanici' as 'admin' | 'yonetici' | 'kullanici',
    is_active: true,
    module_ids: [] as string[],
  });

  useEffect(() => {
    fetchUsers();
    fetchModules();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/users');
      setUsers(response.data);
      setError(null);
    } catch (error: any) {
      setError('Kullanıcılar yüklenirken hata oluştu');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const response = await axios.get('/modules');
      setModules(response.data);
    } catch (error: any) {
      console.error('Modüller yüklenirken hata:', error);
    }
  };

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        email: user.email,
        username: user.username,
        full_name: user.full_name,
        password: '',
        role: user.role,
        is_active: user.is_active,
        module_ids: user.modules.map(m => m.id),
      });
    } else {
      setEditingUser(null);
      setFormData({
        email: '',
        username: '',
        full_name: '',
        password: '',
        role: 'kullanici',
        is_active: true,
        module_ids: [],
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
    setShowPassword(false);
  };

  const handleSubmit = async () => {
    try {
      if (editingUser) {
        await axios.put(`/users/${editingUser.id}`, formData);
      } else {
        await axios.post('/users', formData);
      }
      fetchUsers();
      handleCloseDialog();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'İşlem başarısız');
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!window.confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) {
      return;
    }

    try {
      await axios.delete(`/users/${userId}`);
      fetchUsers();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Silme işlemi başarısız');
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
        return <AdminPanelSettings />;
      case 'yonetici':
        return <SupervisorAccount />;
      default:
        return <Person />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'yonetici':
        return 'warning';
      default:
        return 'info';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin':
        return 'Admin';
      case 'yonetici':
        return 'Yönetici';
      default:
        return 'Kullanıcı';
    }
  };

  const canEditUser = (user: User) => {
    if (currentUser?.role === 'admin') return true;
    if (currentUser?.role === 'yonetici' && user.role === 'kullanici') return true;
    return false;
  };

  const canDeleteUser = (user: User) => {
    if (currentUser?.id === user.id) return false; // Can't delete self
    if (currentUser?.role === 'admin') return true;
    return false;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Kullanıcı Yönetimi
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          Yeni Kullanıcı
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Kullanıcı</TableCell>
              <TableCell>E-posta</TableCell>
              <TableCell>Rol</TableCell>
              <TableCell>Modüller</TableCell>
              <TableCell>Durum</TableCell>
              <TableCell align="right">İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getRoleIcon(user.role)}
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {user.full_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        @{user.username}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Chip
                    label={getRoleLabel(user.role)}
                    color={getRoleColor(user.role) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {user.modules.slice(0, 3).map((module) => (
                      <Chip
                        key={module.id}
                        label={module.display_name}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {user.modules.length > 3 && (
                      <Chip
                        label={`+${user.modules.length - 3}`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.is_active ? 'Aktif' : 'Pasif'}
                    color={user.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  {canEditUser(user) && (
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(user)}
                      color="primary"
                    >
                      <Edit />
                    </IconButton>
                  )}
                  {canDeleteUser(user) && (
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteUser(user.id)}
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingUser ? 'Kullanıcıyı Düzenle' : 'Yeni Kullanıcı'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Ad Soyad"
              fullWidth
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            />

            <TextField
              label="Kullanıcı Adı"
              fullWidth
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              disabled={!!editingUser}
            />

            <TextField
              label="E-posta"
              type="email"
              fullWidth
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />

            <TextField
              label={editingUser ? 'Yeni Şifre (boş bırakılabilir)' : 'Şifre'}
              type={showPassword ? 'text' : 'password'}
              fullWidth
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!editingUser}
              InputProps={{
                endAdornment: (
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                ),
              }}
            />

            {hasRole(['admin']) && (
              <FormControl fullWidth>
                <InputLabel>Rol</InputLabel>
                <Select
                  value={formData.role}
                  label="Rol"
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                >
                  <MenuItem value="kullanici">Kullanıcı (Öğretmen)</MenuItem>
                  <MenuItem value="yonetici">Yönetici</MenuItem>
                  {hasRole(['admin']) && <MenuItem value="admin">Admin</MenuItem>}
                </Select>
              </FormControl>
            )}

            <FormControl component="fieldset">
              <Typography variant="subtitle2" gutterBottom>
                Modül Yetkileri
              </Typography>
              <FormGroup>
                {modules.map((module) => (
                  <FormControlLabel
                    key={module.id}
                    control={
                      <Checkbox
                        checked={formData.module_ids.includes(module.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              module_ids: [...formData.module_ids, module.id],
                            });
                          } else {
                            setFormData({
                              ...formData,
                              module_ids: formData.module_ids.filter(id => id !== module.id),
                            });
                          }
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2">{module.display_name}</Typography>
                        {module.description && (
                          <Typography variant="caption" color="text.secondary">
                            {module.description}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                ))}
              </FormGroup>
            </FormControl>

            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
              }
              label="Aktif Kullanıcı"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>İptal</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingUser ? 'Güncelle' : 'Oluştur'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;