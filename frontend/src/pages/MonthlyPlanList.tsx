import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stack,
  Tooltip,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  GetApp as DownloadIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
  CalendarMonth as CalendarIcon,
  Psychology as AIIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { monthlyPlanApi } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

interface MonthlyPlan {
  id: number;
  plan_adi: string;
  yas_grubu: string;
  ay: string;
  yil: number;
  alan_becerileri: any;
  kavramsal_beceriler: any;
  egilimler: any;
  sosyal_duygusal_beceriler: any;
  degerler: any;
  okuryazarlik_becerileri: any;
  ogrenme_ciktilari: any;
  anahtar_kavramlar: string[];
  degerlendirme: any;
  ogrenme_ogretme_yasantilari: string;
  farklilastirma_zenginlestirme?: string;
  destekleme?: string;
  aile_toplum_katilimi?: string;
  ai_generated: boolean;
  ai_model?: string;
  created_at: string;
  updated_at?: string;
}

const MonthlyPlanList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedPlan, setSelectedPlan] = useState<MonthlyPlan | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [planToDelete, setPlanToDelete] = useState<number | null>(null);

  // Debug için useEffect ekleyelim
  React.useEffect(() => {
    console.log('deleteDialogOpen changed to:', deleteDialogOpen);
    console.log('planToDelete:', planToDelete);
  }, [deleteDialogOpen, planToDelete]);

  // Filters
  const [filterYasGrubu, setFilterYasGrubu] = useState('');
  const [filterAy, setFilterAy] = useState('');

  // Fetch plans
  const { data: plans, isLoading } = useQuery({
    queryKey: ['monthlyPlans', filterYasGrubu, filterAy],
    queryFn: () => monthlyPlanApi.list({
      yas_grubu: filterYasGrubu || undefined,
      ay: filterAy || undefined,
    }),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => monthlyPlanApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monthlyPlans'] });
      toast.success('Aylık plan başarıyla silindi');
      setDeleteDialogOpen(false);
      setPlanToDelete(null);
    },
    onError: (error: any) => {
      console.error('Delete error:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Plan silinirken bir hata oluştu';
      toast.error(errorMessage);
    },
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: (id: number) => monthlyPlanApi.exportMonthlyPlanDocx(id),
    onSuccess: (data, id) => {
      const plan = plans?.find((p: MonthlyPlan) => p.id === id);
      const blob = new Blob([data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${plan?.plan_adi || 'aylik_plan'}.docx`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Plan başarıyla indirildi');
    },
    onError: () => {
      toast.error('Plan indirilemedi');
    },
  });

  const handleView = (plan: MonthlyPlan) => {
    setSelectedPlan(plan);
    setViewDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    console.log('handleDelete called with id:', id);
    setPlanToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (planToDelete) {
      console.log('Deleting plan with ID:', planToDelete);
      deleteMutation.mutate(planToDelete);
    }
  };

  const handleExport = (id: number) => {
    exportMutation.mutate(id);
  };

  const aylar = [
    'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
  ];

  const yasGruplari = ['36-48', '48-60', '60-72'];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CalendarIcon color="primary" />
          Aylık Planlar
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/monthly-plan-generator')}
        >
          Yeni Plan Oluştur
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2}>
          <TextField
            select
            label="Yaş Grubu"
            value={filterYasGrubu}
            onChange={(e) => setFilterYasGrubu(e.target.value)}
            sx={{ minWidth: 150 }}
            size="small"
          >
            <MenuItem value="">Tümü</MenuItem>
            {yasGruplari.map((grup) => (
              <MenuItem key={grup} value={grup}>{grup} Ay</MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Ay"
            value={filterAy}
            onChange={(e) => setFilterAy(e.target.value)}
            sx={{ minWidth: 150 }}
            size="small"
          >
            <MenuItem value="">Tümü</MenuItem>
            {aylar.map((ay) => (
              <MenuItem key={ay} value={ay}>{ay}</MenuItem>
            ))}
          </TextField>
          {(filterYasGrubu || filterAy) && (
            <Button
              variant="outlined"
              onClick={() => {
                setFilterYasGrubu('');
                setFilterAy('');
              }}
            >
              Filtreleri Temizle
            </Button>
          )}
        </Stack>
      </Paper>

      {/* Plans Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Plan Adı</TableCell>
              <TableCell>Yaş Grubu</TableCell>
              <TableCell>Ay</TableCell>
              <TableCell>Yıl</TableCell>
              <TableCell>Oluşturma Tipi</TableCell>
              <TableCell>Oluşturma Tarihi</TableCell>
              <TableCell align="center">İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Yükleniyor...
                </TableCell>
              </TableRow>
            ) : plans?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Henüz aylık plan oluşturulmamış
                </TableCell>
              </TableRow>
            ) : (
              plans?.map((plan: MonthlyPlan) => (
                <TableRow key={plan.id} hover>
                  <TableCell>{plan.plan_adi}</TableCell>
                  <TableCell>{plan.yas_grubu} Ay</TableCell>
                  <TableCell>{plan.ay}</TableCell>
                  <TableCell>{plan.yil}</TableCell>
                  <TableCell>
                    {plan.ai_generated ? (
                      <Chip
                        icon={<AIIcon />}
                        label={`AI (${plan.ai_model || 'Gemini'})`}
                        size="small"
                        color="secondary"
                      />
                    ) : (
                      <Chip label="Manuel" size="small" />
                    )}
                  </TableCell>
                  <TableCell>{formatDate(plan.created_at)}</TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1} justifyContent="center">
                      <Tooltip title="Görüntüle">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleView(plan)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="DOCX İndir">
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleExport(plan.id)}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Sil">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            console.log('Delete IconButton clicked for plan:', plan.id);
                            handleDelete(plan.id);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* View Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SchoolIcon color="primary" />
            {selectedPlan?.plan_adi}
            {selectedPlan?.ai_generated && (
              <Chip
                icon={<AIIcon />}
                label={selectedPlan.ai_model}
                size="small"
                color="secondary"
                sx={{ ml: 'auto' }}
              />
            )}
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedPlan && (
            <Box>
              <Stack direction="row" spacing={4} sx={{ mb: 3 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Yaş Grubu</Typography>
                  <Typography variant="body1">{selectedPlan.yas_grubu} Ay</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Ay</Typography>
                  <Typography variant="body1">{selectedPlan.ay}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Yıl</Typography>
                  <Typography variant="body1">{selectedPlan.yil}</Typography>
                </Box>
              </Stack>

              <Divider sx={{ my: 2 }} />

              {/* Anahtar Kavramlar */}
              {selectedPlan.anahtar_kavramlar?.length > 0 && (
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Anahtar Kavramlar</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {selectedPlan.anahtar_kavramlar.map((kavram: string, index: number) => (
                        <Chip key={index} label={kavram} variant="outlined" />
                      ))}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Öğrenme-Öğretme Yaşantıları */}
              {selectedPlan.ogrenme_ogretme_yasantilari && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Öğrenme-Öğretme Yaşantıları</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedPlan.ogrenme_ogretme_yasantilari}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Farklılaştırma ve Zenginleştirme */}
              {selectedPlan.farklilastirma_zenginlestirme && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Farklılaştırma ve Zenginleştirme</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedPlan.farklilastirma_zenginlestirme}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Destekleme */}
              {selectedPlan.destekleme && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Destekleme</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedPlan.destekleme}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Aile/Toplum Katılımı */}
              {selectedPlan.aile_toplum_katilimi && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Aile/Toplum Katılımı</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedPlan.aile_toplum_katilimi}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Kapat</Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => selectedPlan && handleExport(selectedPlan.id)}
          >
            DOCX İndir
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => {
          console.log('Delete dialog closing');
          setDeleteDialogOpen(false);
        }}
      >
        <DialogTitle>Plan Sil</DialogTitle>
        <DialogContent>
          <Typography>
            Bu aylık planı silmek istediğinizden emin misiniz?
            {planToDelete && ` (ID: ${planToDelete})`}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              console.log('Cancel clicked');
              setDeleteDialogOpen(false);
            }}
          >
            İptal
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={() => {
              console.log('Delete button clicked in dialog');
              confirmDelete();
            }}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Siliniyor...' : 'Sil'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MonthlyPlanList;