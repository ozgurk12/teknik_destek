import { useState, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  Card,
  CardContent,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Snackbar,
  Stack,
  IconButton,
  Collapse,
  Divider,
  Grid,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoIcon from '@mui/icons-material/Info';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import DownloadIcon from '@mui/icons-material/Download';
import { kazanimApi, monthlyPlanApi } from '../services/api';
import CurriculumSelector, { CurriculumSelections } from '../components/CurriculumSelector';

interface Kazanim {
  id: number;
  yas_grubu: string;
  ders: string;
  alan_becerileri: string;
  butunlesik_beceriler: string | null;
  butunlesik_bilesenler: string | null;
  surec_bilesenleri: string | null;
  ogrenme_ciktilari: string;
  alt_ogrenme_ciktilari: string | null;
}

const months = [
  'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
];

const steps = [
  { label: 'Plan Bilgileri', description: 'Yaş grubu ve ay seçimi' },
  { label: 'Kazanım Seçimi', description: 'Aylık plan için kazanımları seçin' },
  { label: 'Müfredat Bileşenleri', description: 'Bütünleşik beceriler ve değerler seçin' },
  { label: 'Aylık Plan Oluştur', description: 'AI ile aylık plan oluşturun' },
  { label: 'Tamamlandı', description: 'Aylık plan başarıyla oluşturuldu' }
];

export default function MonthlyPlanGenerator() {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [selectedKazanimIds, setSelectedKazanimIds] = useState<number[]>([]);
  const [customInstructions, setCustomInstructions] = useState('');
  const [expandedKazanimId, setExpandedKazanimId] = useState<number | null>(null);
  const [generatedPlan, setGeneratedPlan] = useState<any>(null);

  // Plan info state
  const [planInfo, setPlanInfo] = useState({
    yas_grubu: '',
    ay: '',
  });

  // Curriculum selections state
  const [curriculumSelections, setCurriculumSelections] = useState<CurriculumSelections>({
    butunlesikBilesenler: [],
    degerler: [],
    egilimler: [],
    kavramsalBeceriler: [],
    surecBilesenleri: [],
    // Content arrays
    butunlesikBilesenlerContent: [],
    degerlerContent: [],
    egilimlerContent: [],
    kavramsalBecerilerContent: [],
    surecBilesenleriContent: []
  });

  const [filters, setFilters] = useState({
    yas_grubu: '',
    ders: '',
    search: '',
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // Fetch age groups
  const { data: ageGroups } = useQuery({
    queryKey: ['age-groups'],
    queryFn: () => kazanimApi.getAgeGroups(),
  });

  // Fetch subjects based on selected age group
  const { data: subjects } = useQuery({
    queryKey: ['subjects', filters.yas_grubu],
    queryFn: () => kazanimApi.getSubjects(filters.yas_grubu),
    enabled: !!filters.yas_grubu,
  });

  // Fetch kazanımlar
  const { data: kazanimlar, isLoading: kazanimlarLoading } = useQuery({
    queryKey: ['kazanimlar', filters],
    queryFn: () => kazanimApi.searchKazanimlar(filters),
    enabled: !!filters.yas_grubu,
  });

  // Generate monthly plan mutation
  const generatePlanMutation = useMutation({
    mutationFn: async () => {
      const curriculumIds = [
        ...curriculumSelections.butunlesikBilesenler,
        ...curriculumSelections.degerler,
        ...curriculumSelections.egilimler,
        ...curriculumSelections.kavramsalBeceriler,
        ...curriculumSelections.surecBilesenleri
      ];

      return monthlyPlanApi.generateMonthlyPlan({
        yas_grubu: planInfo.yas_grubu,
        ay: planInfo.ay,
        kazanim_ids: selectedKazanimIds,
        curriculum_ids: curriculumIds,
        custom_instructions: customInstructions || undefined
      });
    },
    onSuccess: (data) => {
      setGeneratedPlan(data);
      setActiveStep(4);
      setSnackbar({ open: true, message: 'Aylık plan başarıyla oluşturuldu!', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Plan oluşturulurken hata oluştu',
        severity: 'error'
      });
    }
  });

  const handleNext = () => {
    if (activeStep === 0 && (!planInfo.yas_grubu || !planInfo.ay)) {
      setSnackbar({ open: true, message: 'Yaş grubu ve ay seçimi yapmalısınız', severity: 'error' });
      return;
    }
    if (activeStep === 1 && selectedKazanimIds.length === 0) {
      setSnackbar({ open: true, message: 'En az bir kazanım seçmelisiniz', severity: 'error' });
      return;
    }
    if (activeStep === 3) {
      generatePlanMutation.mutate();
      return;
    }
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleKazanimToggle = (kazanimId: number) => {
    setSelectedKazanimIds((prev) => {
      if (prev.includes(kazanimId)) {
        return prev.filter((id) => id !== kazanimId);
      }
      return [...prev, kazanimId];
    });
  };

  const handleDownloadDocx = async () => {
    if (!generatedPlan?.id) return;

    try {
      const blob = await monthlyPlanApi.exportMonthlyPlanDocx(generatedPlan.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${generatedPlan.plan_adi}.docx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setSnackbar({ open: true, message: 'DOCX indirme hatası', severity: 'error' });
    }
  };

  // Set filters when plan info changes
  useEffect(() => {
    if (planInfo.yas_grubu) {
      setFilters(prev => ({ ...prev, yas_grubu: planInfo.yas_grubu }));
    }
  }, [planInfo.yas_grubu]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CalendarMonthIcon />
        Aylık Plan Oluşturucu
      </Typography>

      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel>{step.label}</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {step.description}
              </Typography>

              {/* Step 0: Plan Info */}
              {index === 0 && (
                <Box sx={{ mb: 2 }}>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <FormControl fullWidth>
                        <InputLabel>Yaş Grubu</InputLabel>
                        <Select
                          value={planInfo.yas_grubu}
                          onChange={(e) => setPlanInfo({ ...planInfo, yas_grubu: e.target.value })}
                          label="Yaş Grubu"
                        >
                          {ageGroups?.age_groups?.map((group: string) => (
                            <MenuItem key={group} value={group}>{group}</MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <FormControl fullWidth>
                        <InputLabel>Ay</InputLabel>
                        <Select
                          value={planInfo.ay}
                          onChange={(e) => setPlanInfo({ ...planInfo, ay: e.target.value })}
                          label="Ay"
                        >
                          {months.map((month: string) => (
                            <MenuItem key={month} value={month}>{month}</MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Step 1: Kazanım Selection */}
              {index === 1 && (
                <Box sx={{ mb: 2 }}>
                  <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                    <FormControl size="small" sx={{ minWidth: 200 }}>
                      <InputLabel>Ders</InputLabel>
                      <Select
                        value={filters.ders}
                        onChange={(e) => setFilters({ ...filters, ders: e.target.value })}
                        label="Ders"
                      >
                        <MenuItem value="">Tümü</MenuItem>
                        {subjects?.subjects?.map((subject: string) => (
                          <MenuItem key={subject} value={subject}>{subject}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    <TextField
                      size="small"
                      placeholder="Kazanım ara..."
                      value={filters.search}
                      onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                      InputProps={{
                        startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                      }}
                      sx={{ flexGrow: 1 }}
                    />
                  </Stack>

                  {kazanimlarLoading ? (
                    <CircularProgress />
                  ) : (
                    <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                      {(Array.isArray(kazanimlar) ? kazanimlar : kazanimlar?.items || [])?.map((kazanim: Kazanim) => (
                        <Card
                          key={kazanim.id}
                          sx={{
                            mb: 1,
                            borderLeft: selectedKazanimIds.includes(kazanim.id)
                              ? '4px solid #4caf50'
                              : '4px solid transparent',
                            backgroundColor: selectedKazanimIds.includes(kazanim.id)
                              ? 'action.hover'
                              : 'background.paper',
                          }}
                        >
                          <CardContent sx={{ py: 1 }}>
                            <Stack direction="row" alignItems="flex-start" spacing={2}>
                              <Checkbox
                                checked={selectedKazanimIds.includes(kazanim.id)}
                                onChange={() => handleKazanimToggle(kazanim.id)}
                              />
                              <Box sx={{ flexGrow: 1 }}>
                                <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                                  <Chip label={kazanim.ders} size="small" color="primary" />
                                  <Chip label={kazanim.yas_grubu} size="small" />
                                </Stack>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                  {kazanim.alan_becerileri}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                  {kazanim.ogrenme_ciktilari}
                                </Typography>

                                <IconButton
                                  size="small"
                                  onClick={() => setExpandedKazanimId(expandedKazanimId === kazanim.id ? null : kazanim.id)}
                                  sx={{ mt: 1 }}
                                >
                                  <ExpandMoreIcon
                                    sx={{
                                      transform: expandedKazanimId === kazanim.id ? 'rotate(180deg)' : 'none',
                                      transition: 'transform 0.3s',
                                    }}
                                  />
                                </IconButton>

                                <Collapse in={expandedKazanimId === kazanim.id}>
                                  <Box sx={{ mt: 2 }}>
                                    {kazanim.alt_ogrenme_ciktilari && (
                                      <Typography variant="caption" component="div">
                                        <strong>Alt Öğrenme Çıktıları:</strong> {kazanim.alt_ogrenme_ciktilari}
                                      </Typography>
                                    )}
                                    {kazanim.butunlesik_beceriler && (
                                      <Typography variant="caption" component="div" sx={{ mt: 1 }}>
                                        <strong>Bütünleşik Beceriler:</strong> {kazanim.butunlesik_beceriler}
                                      </Typography>
                                    )}
                                  </Box>
                                </Collapse>
                              </Box>
                            </Stack>
                          </CardContent>
                        </Card>
                      ))}
                    </Box>
                  )}

                  <Alert severity="info" sx={{ mt: 2 }}>
                    {selectedKazanimIds.length} kazanım seçildi
                  </Alert>
                </Box>
              )}

              {/* Step 2: Curriculum Components */}
              {index === 2 && (
                <Box sx={{ mb: 2 }}>
                  <CurriculumSelector
                    onSelectionChange={setCurriculumSelections}
                  />
                </Box>
              )}

              {/* Step 3: Generate Plan */}
              {index === 3 && (
                <Box sx={{ mb: 2 }}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Özel Talimatlar (İsteğe Bağlı)"
                    placeholder="AI'ya vermek istediğiniz özel talimatlar..."
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    sx={{ mb: 2 }}
                  />

                  <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Özet:
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • Yaş Grubu: {planInfo.yas_grubu}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • Ay: {planInfo.ay}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • {selectedKazanimIds.length} kazanım seçildi
                    </Typography>
                    {curriculumSelections && (
                      <>
                        {curriculumSelections.butunlesikBilesenler.length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            • {curriculumSelections.butunlesikBilesenler.length} bütünleşik bileşen
                          </Typography>
                        )}
                        {curriculumSelections.degerler.length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            • {curriculumSelections.degerler.length} değer
                          </Typography>
                        )}
                      </>
                    )}
                  </Paper>

                  {generatePlanMutation.isPending && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                      <CircularProgress size={24} sx={{ mr: 2 }} />
                      <Typography>Aylık plan oluşturuluyor...</Typography>
                    </Box>
                  )}
                </Box>
              )}

              {/* Step 4: Completed */}
              {index === 4 && generatedPlan && (
                <Box sx={{ mb: 2 }}>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      {generatedPlan.plan_adi}
                    </Typography>
                    başarıyla oluşturuldu!
                  </Alert>

                  <Stack direction="row" spacing={2}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={() => navigate('/monthly-plans')}
                    >
                      Aylık Planları Görüntüle
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownloadDocx}
                    >
                      DOCX İndir
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setActiveStep(0);
                        setSelectedKazanimIds([]);
                        setGeneratedPlan(null);
                        setPlanInfo({ yas_grubu: '', ay: '' });
                        setCurriculumSelections({
                          butunlesikBilesenler: [],
                          degerler: [],
                          egilimler: [],
                          kavramsalBeceriler: [],
                          surecBilesenleri: [],
                          butunlesikBilesenlerContent: [],
                          degerlerContent: [],
                          egilimlerContent: [],
                          kavramsalBecerilerContent: [],
                          surecBilesenleriContent: []
                        });
                      }}
                    >
                      Yeni Plan Oluştur
                    </Button>
                  </Stack>
                </Box>
              )}

              {/* Navigation Buttons */}
              <Box sx={{ mt: 2 }}>
                <Button
                  disabled={activeStep === 0 || activeStep === 4}
                  onClick={handleBack}
                  sx={{ mr: 1 }}
                >
                  Geri
                </Button>
                {activeStep < 3 && (
                  <Button
                    variant="contained"
                    onClick={handleNext}
                  >
                    İleri
                  </Button>
                )}
                {activeStep === 3 && (
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<AutoAwesomeIcon />}
                    onClick={handleNext}
                    disabled={generatePlanMutation.isPending}
                  >
                    Aylık Plan Oluştur
                  </Button>
                )}
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}