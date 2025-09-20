import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Pagination,
  Paper,
  Skeleton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  AutoAwesome as AutoAwesomeIcon,
  Timer as TimerIcon,
  School as SchoolIcon,
  Groups as GroupsIcon,
  Add as AddIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { activityApi, API_BASE_URL } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Activity } from '../types';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

const ActivityList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    alan_adi: '',
    yas_grubu: '',
    ai_generated: '',
  });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // Fetch activities
  const { data: activitiesData, isLoading } = useQuery({
    queryKey: ['activities', page, searchTerm, filters],
    queryFn: () => activityApi.list({
      page,
      page_size: 12,
      search: searchTerm,
      ...filters,
    }),
  });

  const activities = activitiesData?.items || [];
  const totalPages = activitiesData?.total_pages || 1;

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => activityApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities'] });
      setDeleteDialogOpen(false);
      setSelectedActivity(null);
    },
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, activity: Activity) => {
    setAnchorEl(event.currentTarget);
    setSelectedActivity(activity);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleView = () => {
    if (selectedActivity) {
      navigate(`/activities/${selectedActivity.id}`);
    }
    handleMenuClose();
  };

  const handleEdit = () => {
    if (selectedActivity) {
      navigate(`/activities/${selectedActivity.id}/edit`);
    }
    handleMenuClose();
  };

  const handleDelete = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const confirmDelete = () => {
    if (selectedActivity) {
      deleteMutation.mutate(selectedActivity.id);
    }
  };

  const handleDownloadDocx = () => {
    if (selectedActivity) {
      window.open(`${API_BASE_URL}/etkinlikler/${selectedActivity.id}/export/docx`, '_blank');
    }
    handleMenuClose();
  };

  const ActivityCard = ({ activity }: { activity: Activity }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        },
      }}
      onClick={() => navigate(`/activities/${activity.id}`)}
    >
      <CardContent sx={{ flex: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h6" gutterBottom sx={{ flex: 1, pr: 1 }}>
            {activity.etkinlik_adi}
          </Typography>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleMenuOpen(e, activity);
            }}
          >
            <MoreVertIcon />
          </IconButton>
        </Box>

        <Box display="flex" gap={0.5} flexWrap="wrap" mb={2}>
          {activity.ai_generated && (
            <Chip
              size="small"
              icon={<AutoAwesomeIcon />}
              label="AI"
              color="secondary"
              sx={{ fontSize: '0.75rem' }}
            />
          )}
          <Chip
            size="small"
            icon={<GroupsIcon />}
            label={activity.yas_grubu}
            variant="outlined"
            sx={{ fontSize: '0.75rem' }}
          />
          <Chip
            size="small"
            icon={<SchoolIcon />}
            label={activity.alan_adi}
            variant="outlined"
            sx={{ fontSize: '0.75rem' }}
          />
          <Chip
            size="small"
            icon={<TimerIcon />}
            label={`${activity.sure} dk`}
            variant="outlined"
            sx={{ fontSize: '0.75rem' }}
          />
        </Box>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            mb: 2,
          }}
        >
          {activity.etkinlik_amaci}
        </Typography>

        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="caption" color="text.secondary">
            {format(new Date(activity.created_at), 'dd MMMM yyyy HH:mm', { locale: tr })}
          </Typography>
          {activity.created_by_fullname && (
            <Typography variant="caption" color="primary" fontWeight="medium">
              {activity.created_by_fullname}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Etkinlikler
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/activity-generator')}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          }}
        >
          Yeni Etkinlik
        </Button>
      </Box>

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, md: 4 }}>
            <TextField
              fullWidth
              placeholder="Etkinlik ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Alan</InputLabel>
              <Select
                value={filters.alan_adi}
                label="Alan"
                onChange={(e) => setFilters({ ...filters, alan_adi: e.target.value })}
              >
                <MenuItem value="">Tümü</MenuItem>
                <MenuItem value="Türkçe">Türkçe</MenuItem>
                <MenuItem value="Matematik">Matematik</MenuItem>
                <MenuItem value="Fen">Fen</MenuItem>
                <MenuItem value="Sanat">Sanat</MenuItem>
                <MenuItem value="Müzik">Müzik</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Yaş Grubu</InputLabel>
              <Select
                value={filters.yas_grubu}
                label="Yaş Grubu"
                onChange={(e) => setFilters({ ...filters, yas_grubu: e.target.value })}
              >
                <MenuItem value="">Tümü</MenuItem>
                <MenuItem value="36-48">36-48 ay</MenuItem>
                <MenuItem value="48-60">48-60 ay</MenuItem>
                <MenuItem value="60-72">60-72 ay</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Oluşturma Tipi</InputLabel>
              <Select
                value={filters.ai_generated}
                label="Oluşturma Tipi"
                onChange={(e) => setFilters({ ...filters, ai_generated: e.target.value })}
              >
                <MenuItem value="">Tümü</MenuItem>
                <MenuItem value="true">AI Üretilen</MenuItem>
                <MenuItem value="false">Manuel</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterListIcon />}
              onClick={() => {
                setFilters({ alan_adi: '', yas_grubu: '', ai_generated: '' });
                setSearchTerm('');
              }}
            >
              Temizle
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Activity Grid */}
      {isLoading ? (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="80%" height={32} />
                  <Skeleton variant="text" width="60%" />
                  <Skeleton variant="rectangular" height={60} sx={{ mt: 1 }} />
                  <Skeleton variant="text" width="40%" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <>
          <Grid container spacing={3}>
            {activities.map((activity: Activity) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={activity.id}>
                <ActivityCard activity={activity} />
              </Grid>
            ))}
          </Grid>

          {activities.length === 0 && !isLoading && (
            <Paper sx={{ p: 4, textAlign: 'center', mt: 4 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Etkinlik bulunamadı
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Arama kriterlerinize uygun etkinlik bulunmamaktadır.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/activity-generator')}
              >
                İlk Etkinliği Oluştur
              </Button>
            </Paper>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, value) => setPage(value)}
                color="primary"
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </>
      )}

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleView}>
          <VisibilityIcon sx={{ mr: 1 }} fontSize="small" />
          Görüntüle
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <EditIcon sx={{ mr: 1 }} fontSize="small" />
          Düzenle
        </MenuItem>
        <MenuItem onClick={handleDownloadDocx}>
          <DownloadIcon sx={{ mr: 1 }} fontSize="small" />
          DOCX İndir
        </MenuItem>
        <MenuItem>
          <ShareIcon sx={{ mr: 1 }} fontSize="small" />
          Paylaş
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} fontSize="small" />
          Sil
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Etkinliği Sil</DialogTitle>
        <DialogContent>
          <Typography>
            "{selectedActivity?.etkinlik_adi}" etkinliğini silmek istediğinizden emin misiniz?
            Bu işlem geri alınamaz.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>İptal</Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            Sil
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ActivityList;