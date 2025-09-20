import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Alert,
  Fab,
  Grid,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CalendarMonth as CalendarIcon,
  School as SchoolIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';
import { dailyPlanApi } from '../services/api';

const DailyPlanList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchText, setSearchText] = useState('');
  const [selectedAgeGroup, setSelectedAgeGroup] = useState('');
  const [selectedDateFrom, setSelectedDateFrom] = useState<Date | null>(null);
  const [selectedDateTo, setSelectedDateTo] = useState<Date | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch daily plans
  const { data: plans = [], isLoading, error } = useQuery({
    queryKey: ['dailyPlans', searchText, selectedAgeGroup, selectedDateFrom, selectedDateTo],
    queryFn: () => dailyPlanApi.list({
      search: searchText || undefined,
      yas_grubu: selectedAgeGroup || undefined,
      tarih_from: selectedDateFrom ? format(selectedDateFrom, 'yyyy-MM-dd') : undefined,
      tarih_to: selectedDateTo ? format(selectedDateTo, 'yyyy-MM-dd') : undefined,
    }),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => dailyPlanApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dailyPlans'] });
      setDeleteDialogOpen(false);
      setSelectedPlanId(null);
    },
  });

  // Export to DOCX
  const handleExport = async (planId: number, planName: string) => {
    try {
      const response = await dailyPlanApi.exportToDocx(planId);
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${planName}_gunluk_plan.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleDeleteClick = (planId: number) => {
    setSelectedPlanId(planId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedPlanId) {
      deleteMutation.mutate(selectedPlanId);
    }
  };

  const clearFilters = () => {
    setSearchText('');
    setSelectedAgeGroup('');
    setSelectedDateFrom(null);
    setSelectedDateTo(null);
  };

  const ageGroups = ['36-48 ay', '48-60 ay', '60-72 ay'];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Günlük Planlar
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Oluşturduğunuz günlük planları görüntüleyin ve yönetin
        </Typography>
      </Box>

      {/* Search and Filter Bar */}
      <Card sx={{ mb: 3, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField
            placeholder="Plan adı veya öğretmen ara..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ flex: 1, minWidth: 250 }}
          />

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Yaş Grubu</InputLabel>
            <Select
              value={selectedAgeGroup}
              onChange={(e) => setSelectedAgeGroup(e.target.value)}
              label="Yaş Grubu"
            >
              <MenuItem value="">Tümü</MenuItem>
              {ageGroups.map((group) => (
                <MenuItem key={group} value={group}>{group}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            onClick={() => setShowFilters(!showFilters)}
            startIcon={<FilterIcon />}
          >
            Filtreler
          </Button>

          {(searchText || selectedAgeGroup || selectedDateFrom || selectedDateTo) && (
            <Button
              variant="text"
              onClick={clearFilters}
              startIcon={<ClearIcon />}
              color="secondary"
            >
              Temizle
            </Button>
          )}
        </Box>

        {showFilters && (
          <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <DatePicker
              label="Başlangıç Tarihi"
              value={selectedDateFrom}
              onChange={setSelectedDateFrom}
              slotProps={{ textField: { size: 'small' } }}
            />
            <DatePicker
              label="Bitiş Tarihi"
              value={selectedDateTo}
              onChange={setSelectedDateTo}
              slotProps={{ textField: { size: 'small' } }}
            />
          </Box>
        )}
      </Card>

      {/* Plans Grid */}
      {isLoading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Yükleniyor...</Typography>
        </Box>
      ) : error ? (
        <Alert severity="error">Planlar yüklenirken bir hata oluştu</Alert>
      ) : plans.length === 0 ? (
        <Card sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Henüz günlük plan oluşturmadınız
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            İlk günlük planınızı oluşturmak için başlayın
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/daily-plans/new')}
          >
            Yeni Plan Oluştur
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {plans.map((plan: any) => (
            <Grid size={{ xs: 12, md: 6, lg: 4 }} key={plan.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flex: 1 }}>
                  <Typography variant="h6" gutterBottom noWrap>
                    {plan.plan_adi}
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CalendarIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {format(new Date(plan.tarih), 'dd MMMM yyyy', { locale: tr })}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <SchoolIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {plan.sinif || 'Sınıf belirtilmemiş'}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
                    <Chip label={plan.yas_grubu} size="small" color="primary" />
                    {plan.etkinlik_idleri && (
                      <Chip
                        label={`${plan.etkinlik_idleri.length} Etkinlik`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  {plan.ogretmen && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      Öğretmen: {plan.ogretmen}
                    </Typography>
                  )}
                </CardContent>

                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Box>
                    <Tooltip title="Görüntüle">
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/daily-plans/${plan.id}`)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Düzenle">
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/daily-plans/${plan.id}/edit`)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Sil">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(plan.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                  <Tooltip title="DOCX İndir">
                    <IconButton
                      size="small"
                      onClick={() => handleExport(plan.id, plan.plan_adi)}
                      color="primary"
                    >
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => navigate('/daily-plans/new')}
      >
        <AddIcon />
      </Fab>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Plan Silme Onayı</DialogTitle>
        <DialogContent>
          <Typography>
            Bu günlük planı silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>İptal</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Sil
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DailyPlanList;