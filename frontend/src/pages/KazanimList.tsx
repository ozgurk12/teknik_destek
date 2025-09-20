import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  Pagination,
  Skeleton,
  IconButton,
  Menu,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  School as SchoolIcon,
  Groups as GroupsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { kazanimApi } from '../services/api';
import { Kazanim } from '../types';
import KazanimModal from '../components/KazanimModal';

const KazanimList: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [filters, setFilters] = useState({
    yas_grubu: '',
    ders: '',
    search: '',
  });
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedKazanim, setSelectedKazanim] = useState<Kazanim | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuKazanim, setMenuKazanim] = useState<Kazanim | null>(null);

  // Fetch age groups
  const { data: ageGroups } = useQuery({
    queryKey: ['age-groups'],
    queryFn: () => kazanimApi.getAgeGroups(),
  });

  // Fetch subjects
  const { data: subjects } = useQuery({
    queryKey: ['subjects', filters.yas_grubu],
    queryFn: () => kazanimApi.getSubjects(filters.yas_grubu),
  });

  // Fetch kazanimlar
  const { data: kazanimlar, isLoading } = useQuery({
    queryKey: ['kazanimlar', page, filters],
    queryFn: () => kazanimApi.list({
      page,
      page_size: viewMode === 'table' ? 50 : 12,
      ...filters,
    }),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: kazanimApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kazanimlar'] });
      setModalOpen(false);
      setSelectedKazanim(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      kazanimApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kazanimlar'] });
      setModalOpen(false);
      setSelectedKazanim(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: kazanimApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kazanimlar'] });
      handleMenuClose();
    },
  });

  const handleSave = async (data: any) => {
    if (selectedKazanim) {
      await updateMutation.mutateAsync({ id: selectedKazanim.id, data });
    } else {
      await createMutation.mutateAsync(data);
    }
  };

  const handleEdit = (kazanim: Kazanim) => {
    setSelectedKazanim(kazanim);
    setModalOpen(true);
    handleMenuClose();
  };

  const handleDelete = (kazanim: Kazanim) => {
    if (window.confirm(`"${kazanim.ogrenme_ciktilari}" kazanımını silmek istediğinize emin misiniz?`)) {
      deleteMutation.mutate(kazanim.id);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>, kazanim: Kazanim) => {
    setAnchorEl(event.currentTarget);
    setMenuKazanim(kazanim);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuKazanim(null);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'yas_grubu', headerName: 'Yaş Grubu', width: 100 },
    { field: 'ders', headerName: 'Ders', width: 120 },
    { field: 'alan_becerileri', headerName: 'Alan Becerileri', width: 200 },
    { field: 'ogrenme_ciktilari', headerName: 'Öğrenme Çıktıları', flex: 1 },
    { field: 'alt_ogrenme_ciktilari', headerName: 'Alt Öğrenme Çıktıları', flex: 1 },
    {
      field: 'actions',
      headerName: 'İşlemler',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleEdit(params.row)}
            color="primary"
          >
            <EditIcon fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleDelete(params.row)}
            color="error"
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      ),
    },
  ];

  const KazanimCard = ({ kazanim }: { kazanim: Kazanim }) => (
    <Card
      sx={{
        height: '100%',
        transition: 'all 0.3s',
        '&:hover': {
          boxShadow: 3,
        },
        position: 'relative',
      }}
    >
      <IconButton
        sx={{ position: 'absolute', top: 8, right: 8 }}
        onClick={(e) => handleMenuOpen(e, kazanim)}
      >
        <MoreVertIcon />
      </IconButton>
      <CardContent>
        <Box display="flex" gap={1} mb={2}>
          <Chip
            size="small"
            icon={<GroupsIcon />}
            label={kazanim.yas_grubu}
            color="primary"
          />
          <Chip
            size="small"
            icon={<SchoolIcon />}
            label={kazanim.ders}
            variant="outlined"
          />
        </Box>

        {kazanim.alan_becerileri && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            <strong>Alan Becerileri:</strong> {kazanim.alan_becerileri}
          </Typography>
        )}

        {kazanim.ogrenme_ciktilari && (
          <Typography variant="body2" gutterBottom>
            <strong>Öğrenme Çıktıları:</strong> {kazanim.ogrenme_ciktilari}
          </Typography>
        )}

        {kazanim.alt_ogrenme_ciktilari && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
            }}
          >
            <strong>Alt Çıktılar:</strong> {kazanim.alt_ogrenme_ciktilari}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Kazanımlar
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Maarif Model Okul Öncesi kazanımlarını inceleyin ve filtreleyin.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setSelectedKazanim(null);
            setModalOpen(true);
          }}
        >
          Yeni Kazanım Ekle
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, md: 4 }}>
            <TextField
              fullWidth
              placeholder="Kazanım ara..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
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
              <InputLabel>Yaş Grubu</InputLabel>
              <Select
                value={filters.yas_grubu}
                label="Yaş Grubu"
                onChange={(e) => setFilters({ ...filters, yas_grubu: e.target.value })}
              >
                <MenuItem value="">Tümü</MenuItem>
                {ageGroups?.age_groups?.map((age: string) => (
                  <MenuItem key={age} value={age}>{age}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Ders</InputLabel>
              <Select
                value={filters.ders}
                label="Ders"
                onChange={(e) => setFilters({ ...filters, ders: e.target.value })}
              >
                <MenuItem value="">Tümü</MenuItem>
                {subjects?.subjects?.map((subject: string) => (
                  <MenuItem key={subject} value={subject}>{subject}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterListIcon />}
              onClick={() => setFilters({ yas_grubu: '', ders: '', search: '' })}
            >
              Temizle
            </Button>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Görünüm</InputLabel>
              <Select
                value={viewMode}
                label="Görünüm"
                onChange={(e) => setViewMode(e.target.value as 'grid' | 'table')}
              >
                <MenuItem value="grid">Kart</MenuItem>
                <MenuItem value="table">Tablo</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Stats */}
      {kazanimlar && (
        <Box mb={3}>
          <Typography variant="body2" color="text.secondary">
            Toplam {kazanimlar.total} kazanım bulundu
          </Typography>
        </Box>
      )}

      {/* Content */}
      {isLoading ? (
        <Grid container spacing={2}>
          {[...Array(6)].map((_, index) => (
            <Grid size={{ xs: 12, md: viewMode === 'grid' ? 6 : 12 }} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="text" width="80%" />
                  <Skeleton variant="text" width="100%" />
                  <Skeleton variant="text" width="90%" />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : viewMode === 'table' ? (
        <Paper sx={{ height: 600, width: '100%' }}>
          <DataGrid
            rows={kazanimlar?.items || []}
            columns={columns}
            pageSizeOptions={[25, 50, 100]}
            checkboxSelection
            disableRowSelectionOnClick
          />
        </Paper>
      ) : (
        <>
          <Grid container spacing={2}>
            {kazanimlar?.items?.map((kazanim: Kazanim) => (
              <Grid size={{ xs: 12, md: 6 }} key={kazanim.id}>
                <KazanimCard kazanim={kazanim} />
              </Grid>
            ))}
          </Grid>

          {kazanimlar?.items && kazanimlar.items.length > 0 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={Math.ceil(kazanimlar.total / 12)}
                page={page}
                onChange={(_, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {kazanimlar?.items?.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Kazanım bulunamadı
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Arama kriterlerinize uygun kazanım bulunmamaktadır.
          </Typography>
        </Paper>
      )}

      {/* Kazanim Modal */}
      <KazanimModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedKazanim(null);
        }}
        onSave={handleSave}
        kazanim={selectedKazanim}
        ageGroups={ageGroups?.age_groups || []}
        subjects={subjects?.subjects || []}
      />

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => menuKazanim && handleEdit(menuKazanim)}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} /> Düzenle
        </MenuItem>
        <MenuItem onClick={() => menuKazanim && handleDelete(menuKazanim)}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} /> Sil
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default KazanimList;