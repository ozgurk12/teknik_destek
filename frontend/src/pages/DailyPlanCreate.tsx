import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Stepper,
  Step,
  StepLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  IconButton,
  Divider,
  Collapse,
  CircularProgress,
  Grid,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Save as SaveIcon,
  School as SchoolIcon,
  Timer as TimerIcon,
  Category as CategoryIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { activityApi, dailyPlanApi } from '../services/api';

const steps = ['Temel Bilgiler', 'Etkinlik Seçimi', 'AI ile Oluşturma'];

interface DailyPlanData {
  plan_adi: string;
  tarih: Date | null;
  yas_grubu: string;
  etkinlik_idleri: number[];
  kavramlar: string;
  sozcukler: string;
  materyaller: string;
  egitim_ortamlari: string;
  gune_baslama: string;
  ogrenme_merkezleri: string;
  beslenme_toplanma: string;
  degerlendirme: string;
  zenginlestirme: string;
  destekleme: string;
  aile_katilimi: string;
  toplum_katilimi: string;
  notlar: string;
}

const DailyPlanCreate: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [expandedActivities, setExpandedActivities] = useState<number[]>([]);
  const [planData, setPlanData] = useState<DailyPlanData>({
    plan_adi: '',
    tarih: new Date(),
    yas_grubu: '',
    etkinlik_idleri: [],
    kavramlar: '',
    sozcukler: '',
    materyaller: '',
    egitim_ortamlari: '',
    gune_baslama: '',
    ogrenme_merkezleri: '',
    beslenme_toplanma: '',
    degerlendirme: '',
    zenginlestirme: '',
    destekleme: '',
    aile_katilimi: '',
    toplum_katilimi: '',
    notlar: '',
  });

  // Fetch activities
  const { data: activities = [], isLoading: activitiesLoading } = useQuery({
    queryKey: ['activities', planData.yas_grubu, activeStep],
    queryFn: async () => {
      console.log('Fetching activities for:', planData.yas_grubu);
      // Tüm etkinlikleri getir, sonra filtreleme yapabiliriz
      const result = await activityApi.list({ page_size: 100 }); // Get more activities
      console.log('All activities received:', result);

      // Handle paginated response
      const activities = result?.items || result || [];

      // Yaş grubuna göre filtrele
      if (planData.yas_grubu && Array.isArray(activities)) {
        const filtered = activities.filter((act: any) =>
          act.yas_grubu === planData.yas_grubu ||
          act.yas_grubu === `** ${planData.yas_grubu}`
        );
        console.log('Filtered activities:', filtered);
        return filtered;
      }
      return Array.isArray(activities) ? activities : [];
    },
    enabled: activeStep === 1,
    staleTime: 0,
    refetchOnMount: true,
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => {
      console.log('Calling createWithAI with data:', data);
      return dailyPlanApi.createWithAI(data);
    },
    onSuccess: (response) => {
      console.log('AI plan created successfully:', response);
      navigate(`/daily-plans/${response.id}`);
    },
    onError: (error) => {
      console.error('Error creating AI plan:', error);
    },
  });

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      // Submit the form
      const submitData = {
        ...planData,
        tarih: planData.tarih ? format(planData.tarih, 'yyyy-MM-dd') : null,
      };
      createMutation.mutate(submitData);
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleActivityToggle = (activityId: number) => {
    setPlanData((prev) => ({
      ...prev,
      etkinlik_idleri: prev.etkinlik_idleri.includes(activityId)
        ? prev.etkinlik_idleri.filter((id) => id !== activityId)
        : [...prev.etkinlik_idleri, activityId],
    }));
  };

  const toggleActivityExpand = (activityId: number) => {
    setExpandedActivities((prev) =>
      prev.includes(activityId)
        ? prev.filter((id) => id !== activityId)
        : [...prev, activityId]
    );
  };

  const updatePlanData = (field: keyof DailyPlanData, value: any) => {
    setPlanData((prev) => ({ ...prev, [field]: value }));
  };

  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return planData.plan_adi && planData.tarih && planData.yas_grubu;
      case 1:
        return planData.etkinlik_idleri.length > 0;
      default:
        return true;
    }
  };

  const ageGroups = ['36-48 ay', '48-60 ay', '60-72 ay'];

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Plan Adı"
                value={planData.plan_adi}
                onChange={(e) => updatePlanData('plan_adi', e.target.value)}
                required
                helperText="Günlük planınız için açıklayıcı bir isim girin"
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <DatePicker
                label="Tarih"
                value={planData.tarih}
                onChange={(date) => updatePlanData('tarih', date)}
                slotProps={{ textField: { fullWidth: true, required: true } }}
              />
            </Grid>
            <Grid size={12}>
              <FormControl fullWidth required>
                <InputLabel>Yaş Grubu</InputLabel>
                <Select
                  value={planData.yas_grubu}
                  onChange={(e) => updatePlanData('yas_grubu', e.target.value)}
                  label="Yaş Grubu"
                >
                  {ageGroups.map((group) => (
                    <MenuItem key={group} value={group}>{group}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              Günlük planınızda kullanmak istediğiniz etkinlikleri seçin. Seçtiğiniz etkinliklerden
              kazanımlar ve müfredat bileşenleri otomatik olarak çıkarılacaktır.
            </Alert>
            {!planData.yas_grubu ? (
              <Alert severity="warning">
                Lütfen önce yaş grubu seçin.
              </Alert>
            ) : activitiesLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : !activities || !Array.isArray(activities) || activities.length === 0 ? (
              <Alert severity="warning">
                {planData.yas_grubu} yaş grubu için etkinlik bulunamadı.
                Önce etkinlik oluşturmanız gerekiyor.
              </Alert>
            ) : (
              <List>
                {Array.isArray(activities) && activities.map((activity: any) => (
                  <React.Fragment key={activity.id}>
                    <ListItem>
                      <ListItemIcon>
                        <Checkbox
                          checked={planData.etkinlik_idleri.includes(activity.id)}
                          onChange={() => handleActivityToggle(activity.id)}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1">{activity.etkinlik_adi}</Typography>
                            <Chip
                              label={activity.alan_adi}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Chip
                              label={`${activity.sure} dk`}
                              size="small"
                              icon={<TimerIcon />}
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                              {activity.etkinlik_amaci}
                            </Typography>
                          </Box>
                        }
                      />
                      <IconButton
                        onClick={() => toggleActivityExpand(activity.id)}
                        size="small"
                      >
                        {expandedActivities.includes(activity.id) ? (
                          <ExpandLessIcon />
                        ) : (
                          <ExpandMoreIcon />
                        )}
                      </IconButton>
                    </ListItem>
                    <Collapse in={expandedActivities.includes(activity.id)}>
                      <Box sx={{ pl: 9, pr: 3, pb: 2 }}>
                        <Typography variant="body2" paragraph>
                          <strong>Materyaller:</strong> {activity.materyaller}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Uygulama Süreci:</strong> {activity.uygulama_sureci}
                        </Typography>
                      </Box>
                    </Collapse>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            )}
            {planData.etkinlik_idleri.length > 0 && (
              <Alert severity="success" sx={{ mt: 2 }}>
                {planData.etkinlik_idleri.length} etkinlik seçildi
              </Alert>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                AI ile Günlük Plan Oluşturma
              </Typography>
              <Typography variant="body2">
                Seçtiğiniz etkinlikler ve kazanımlar kullanılarak AI tarafından otomatik olarak günlük plan oluşturulacaktır.
              </Typography>
            </Alert>

            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Plan Özeti
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="body2" color="text.secondary">Plan Adı:</Typography>
                  <Typography variant="body1" fontWeight="bold">{planData.plan_adi}</Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="body2" color="text.secondary">Tarih:</Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {planData.tarih ? format(planData.tarih, 'dd.MM.yyyy') : '-'}
                  </Typography>
                </Grid>
                <Grid size={6}>
                  <Typography variant="body2" color="text.secondary">Yaş Grubu:</Typography>
                  <Typography variant="body1" fontWeight="bold">{planData.yas_grubu}</Typography>
                </Grid>
                <Grid size={6}>
                  <Typography variant="body2" color="text.secondary">Seçilen Etkinlik Sayısı:</Typography>
                  <Typography variant="body1" fontWeight="bold">{planData.etkinlik_idleri.length}</Typography>
                </Grid>
              </Grid>
            </Paper>

            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                AI Tarafından Oluşturulacak İçerikler
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon><CheckIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Kavramlar ve Sözcükler"
                    secondary="Etkinliklerde ele alınacak kavramlar ve öğretilecek yeni sözcükler"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="İçerik Çerçevesi"
                    secondary="Materyaller, eğitim ortamları"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Öğrenme-Öğretme Yaşantıları"
                    secondary="Güne başlama, öğrenme merkezleri, beslenme rutinleri, değerlendirme"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Farklılaştırma"
                    secondary="Zenginleştirme ve destekleme aktiviteleri"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color="primary" /></ListItemIcon>
                  <ListItemText
                    primary="Aile ve Toplum Katılımı"
                    secondary="Aile ve toplum katılımı önerileri"
                  />
                </ListItem>
              </List>
            </Paper>

            {createMutation.isPending && (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 3 }}>
                <CircularProgress sx={{ mr: 2 }} />
                <Typography>AI günlük planınızı oluşturuyor...</Typography>
              </Box>
            )}
          </Box>
        );


      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/daily-plans')}
          sx={{ mb: 2 }}
        >
          Geri Dön
        </Button>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Yeni Günlük Plan Oluştur
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Adım adım günlük planınızı oluşturun
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ minHeight: 400 }}>
            {renderStepContent()}
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              startIcon={<ArrowBackIcon />}
            >
              Önceki
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={!isStepValid() || createMutation.isPending}
              endIcon={activeStep === steps.length - 1 ? <SaveIcon /> : <ArrowForwardIcon />}
            >
              {activeStep === steps.length - 1 ? 'Oluştur' : 'Sonraki'}
            </Button>
          </Box>

          {createMutation.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Plan oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.
            </Alert>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default DailyPlanCreate;