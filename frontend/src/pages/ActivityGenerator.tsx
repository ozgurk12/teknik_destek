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
  Slider,
  Snackbar,
  Stack,
  IconButton,
  Collapse,
  Divider,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoIcon from '@mui/icons-material/Info';
import { kazanimApi, activityApi, monthlyPlanApi } from '../services/api';
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

const steps = [
  { label: 'Kazanım Seçimi', description: 'Etkinliğiniz için kazanımları seçin' },
  { label: 'Müfredat Bileşenleri', description: 'Bütünleşik beceriler ve değerler seçin' },
  { label: 'Etkinlik Oluştur', description: 'AI ile etkinlik oluşturun' },
  { label: 'Tamamlandı', description: 'Etkinlik başarıyla oluşturuldu' }
];

export default function ActivityGenerator() {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [selectedKazanimIds, setSelectedKazanimIds] = useState<number[]>([]);
  const [selectedMonthlyPlanId, setSelectedMonthlyPlanId] = useState<number | null>(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [activityDuration, setActivityDuration] = useState(30);
  const [expandedKazanimId, setExpandedKazanimId] = useState<number | null>(null);
  const [generatedActivity, setGeneratedActivity] = useState<any>(null);

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

  // Handle monthly plan selection
  const handleMonthlyPlanSelect = async (planId: number) => {
    try {
      const plan = await monthlyPlanApi.getById(planId);
      setSelectedMonthlyPlanId(planId);

      let loadedCount = 0;

      // Auto-fill kazanim_ids if available
      if (plan.kazanim_ids && plan.kazanim_ids.length > 0) {
        setSelectedKazanimIds(plan.kazanim_ids);
        loadedCount += plan.kazanim_ids.length;
      }

      // Auto-fill curriculum selections from plan data
      const newCurriculumSelections: CurriculumSelections = {
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
      };

      // Parse Kavramsal Beceriler from plan
      if (plan.kavramsal_beceriler && typeof plan.kavramsal_beceriler === 'object') {
        const items = Object.values(plan.kavramsal_beceriler).flat() as string[];
        newCurriculumSelections.kavramsalBecerilerContent = items.map((item: string) => ({
          ana_beceri_kodu: item.split(' ')[0] || '',
          ana_beceri_adi: item.split(' ').slice(1).join(' ') || item,
        }));
      }

      // Parse Eğilimler from plan
      if (plan.egilimler && typeof plan.egilimler === 'object') {
        const items = Object.values(plan.egilimler).flat() as string[];
        newCurriculumSelections.egilimlerContent = items.map((item: string) => ({
          ana_egilim: item,
          ana_egilim_kodu: '',
        }));
      }

      // Parse Değerler from plan
      if (plan.degerler && typeof plan.degerler === 'object') {
        const items = Object.values(plan.degerler).flat() as string[];
        newCurriculumSelections.degerlerContent = items.map((item: string) => ({
          ana_deger_kodu: item.split(' ')[0] || '',
          ana_deger_adi: item.split(' ').slice(1).join(' ') || item,
        }));
      }

      // Parse Sosyal-Duygusal from plan
      if (plan.sosyal_duygusal_beceriler && typeof plan.sosyal_duygusal_beceriler === 'object') {
        const items = Object.values(plan.sosyal_duygusal_beceriler).flat() as string[];
        newCurriculumSelections.surecBilesenleriContent = items.map((item: string) => ({
          surec_bileseni_kodu: item.split(' ')[0] || '',
          surec_bileseni_adi: item.split(' ').slice(1).join(' ') || item,
        }));
      }

      // Parse Okuryazarlık from plan
      if (plan.okuryazarlik_becerileri && typeof plan.okuryazarlik_becerileri === 'object') {
        const items = Object.values(plan.okuryazarlik_becerileri).flat() as string[];
        newCurriculumSelections.butunlesikBilesenlerContent = items.map((item: string) => ({
          butunlesik_bilesenler: item,
        }));
      }

      setCurriculumSelections(newCurriculumSelections);

      setSnackbar({
        open: true,
        message: `Aylık plandan ${loadedCount} kazanım ve müfredat bileşenleri yüklendi`,
        severity: 'success'
      });

    } catch (error) {
      console.error('Error loading monthly plan:', error);
      setSnackbar({ open: true, message: 'Aylık plan yüklenirken hata oluştu', severity: 'error' });
    }
  };

  // Debug: Log curriculum selections whenever they change
  useEffect(() => {
    console.log('ActivityGenerator - curriculumSelections updated:', curriculumSelections);
  }, [curriculumSelections]);

  // Fetch monthly plans
  const { data: monthlyPlans } = useQuery({
    queryKey: ['monthly-plans'],
    queryFn: () => monthlyPlanApi.list(),
  });

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
  const { data: kazanimlar, isLoading: kazanimlarLoading } = useQuery({
    queryKey: ['kazanimlar', filters],
    queryFn: () => kazanimApi.list({
      ...filters,
      page_size: 100,
    }),
  });

  // Fetch selected kazanimlar details (for chips display)
  const { data: selectedKazanimlarDetails } = useQuery({
    queryKey: ['selected-kazanimlar', selectedKazanimIds],
    queryFn: async () => {
      if (selectedKazanimIds.length === 0) return [];
      // Fetch all selected kazanimlar in one request
      const response = await kazanimApi.list({
        ids: selectedKazanimIds.join(','),
        page_size: selectedKazanimIds.length,
      });
      return response?.items || [];
    },
    enabled: selectedKazanimIds.length > 0,
  });

  // Generate activity mutation
  const generateMutation = useMutation({
    mutationFn: async (params: { kazanimIds: number[], customPrompt: string, curriculumData: any }) => {
      console.log('=== MUTATION FUNCTION CALLED ===');
      console.log('Received params:', params);

      // Ensure we have all parameters
      const { kazanimIds, customPrompt, curriculumData } = params;

      console.log('Extracted values:');
      console.log('- kazanimIds:', kazanimIds);
      console.log('- customPrompt length:', customPrompt?.length);
      console.log('- curriculumData:', curriculumData);

      // Call API with all three parameters
      return activityApi.generate(kazanimIds, customPrompt, curriculumData);
    },
    onSuccess: (response) => {
      console.log('Generation successful:', response);
      if (response.data.success) {
        setGeneratedActivity(response.data.etkinlik);
        setActiveStep(3);
        setSnackbar({ open: true, message: 'Etkinlik başarıyla oluşturuldu!', severity: 'success' });
      }
    },
    onError: (error) => {
      console.error('Generation error:', error);
      setSnackbar({ open: true, message: 'Etkinlik oluşturulurken bir hata oluştu', severity: 'error' });
    }
  });

  // Prepare curriculum data for backend
  const prepareCurriculumData = () => {
    console.log('=== PREPARING CURRICULUM DATA ===');
    console.log('Current curriculumSelections:', curriculumSelections);

    const curriculumData: any = {
      kavramsal_beceriler: [],
      egilimler: [],
      sosyal_duygusal: [],
      degerler: [],
      okuryazarlik: []
    };

    // Process kavramsal beceriler
    if (curriculumSelections.kavramsalBecerilerContent && curriculumSelections.kavramsalBecerilerContent.length > 0) {
      curriculumData.kavramsal_beceriler = curriculumSelections.kavramsalBecerilerContent.map(item => {
        const kod = item.ana_beceri_kodu || '';
        const isim = item.ana_beceri_adi || '';
        return kod ? `${kod}. ${isim}` : isim;
      });
    }

    // Process egilimler
    if (curriculumSelections.egilimlerContent && curriculumSelections.egilimlerContent.length > 0) {
      curriculumData.egilimler = curriculumSelections.egilimlerContent.map(item => {
        const kod = item.ana_egilim_kodu || '';
        const isim = item.ana_egilim || '';
        return kod ? `${kod}. ${isim}` : isim;
      });
    }

    // Process sosyal duygusal (from surec bilesenleri)
    if (curriculumSelections.surecBilesenleriContent && curriculumSelections.surecBilesenleriContent.length > 0) {
      curriculumData.sosyal_duygusal = curriculumSelections.surecBilesenleriContent
        .filter(item => {
          const kod = item.surec_bileseni_kodu || '';
          return kod.includes('SDB');
        })
        .map(item => {
          const kod = item.surec_bileseni_kodu || '';
          const isim = item.surec_bileseni_adi || '';
          return `${kod}. ${isim}`;
        });
    }

    // Process degerler
    if (curriculumSelections.degerlerContent && curriculumSelections.degerlerContent.length > 0) {
      curriculumData.degerler = curriculumSelections.degerlerContent.map(item => {
        const kod = item.ana_deger_kodu || '';
        const isim = item.ana_deger_adi || '';
        return kod ? `${kod}. ${isim}` : isim;
      });
    }

    // Process okuryazarlik (from butunlesik bilesenler)
    if (curriculumSelections.butunlesikBilesenlerContent && curriculumSelections.butunlesikBilesenlerContent.length > 0) {
      curriculumData.okuryazarlik = curriculumSelections.butunlesikBilesenlerContent
        .filter(item => {
          const bilesenAdi = item.butunlesik_bilesenler || '';
          // Check for OKURYAZARLIĞI or okuryazarlık in various forms
          return bilesenAdi.toUpperCase().includes('OKURYAZAR') ||
                 bilesenAdi.startsWith('OB');  // OB codes are for Okuryazarlık Becerileri
        })
        .map(item => {
          const bilesenAdi = item.butunlesik_bilesenler || '';
          const altBilesen = item.alt_butunlesik_bilesenler || '';
          const surecBilesen = item.surec_bilesenleri || '';
          // Use surec_bilesenleri if available for more specific coding
          if (surecBilesen) {
            return surecBilesen;
          }
          return altBilesen ? `${bilesenAdi} - ${altBilesen}` : bilesenAdi;
        });
    }

    console.log('Prepared curriculumData:', curriculumData);
    return curriculumData;
  };

  const handleNext = () => {
    console.log(`=== HANDLE NEXT - Step ${activeStep} ===`);

    if (activeStep === 0) {
      // Step 0: Check if kazanim is selected
      if (selectedKazanimIds.length === 0) {
        setSnackbar({ open: true, message: 'Lütfen en az bir kazanım seçin', severity: 'error' });
        return;
      }
      setActiveStep(1);
    } else if (activeStep === 1) {
      // Step 1: Move to generation step
      setActiveStep(2);
    } else if (activeStep === 2) {
      // Step 2: Generate activity
      console.log('=== GENERATING ACTIVITY ===');

      // Prepare curriculum data
      const curriculumData = prepareCurriculumData();

      // Build custom prompt with curriculum details
      let curriculumPrompt = '';

      if (curriculumSelections.butunlesikBilesenlerContent?.length) {
        curriculumPrompt += 'BÜTÜNLEŞİK BİLEŞENLER:\n';
        curriculumSelections.butunlesikBilesenlerContent.forEach(item => {
          curriculumPrompt += `• ${item.butunlesik_bilesenler}`;
          if (item.alt_butunlesik_bilesenler) {
            curriculumPrompt += ` - ${item.alt_butunlesik_bilesenler}`;
          }
          curriculumPrompt += '\n';
        });
      }

      if (curriculumSelections.degerlerContent?.length) {
        curriculumPrompt += '\nDEĞERLER:\n';
        curriculumSelections.degerlerContent.forEach(item => {
          curriculumPrompt += `• ${item.ana_deger_adi} - ${item.alt_deger_adi}\n`;
        });
      }

      if (curriculumSelections.egilimlerContent?.length) {
        curriculumPrompt += '\nEĞİLİMLER:\n';
        curriculumSelections.egilimlerContent.forEach(item => {
          curriculumPrompt += `• ${item.ana_egilim} - ${item.alt_egilim}\n`;
        });
      }

      if (curriculumSelections.kavramsalBecerilerContent?.length) {
        curriculumPrompt += '\nKAVRAMSAL BECERİLER:\n';
        curriculumSelections.kavramsalBecerilerContent.forEach(item => {
          curriculumPrompt += `• ${item.ana_beceri_kategorisi} - ${item.ana_beceri_adi}\n`;
        });
      }

      if (curriculumSelections.surecBilesenleriContent?.length) {
        curriculumPrompt += '\nSÜREÇ BİLEŞENLERİ:\n';
        curriculumSelections.surecBilesenleriContent.forEach(item => {
          curriculumPrompt += `• ${item.surec_bileseni_kodu} - ${item.surec_bileseni_adi}\n`;
        });
      }

      const durationPrompt = `ETKİNLİK SÜRESİ: ${activityDuration} dakika olmalıdır.\n`;

      // Önemli not ekle: Kodları etkinlik metninde gösterme
      const importantNote = `\n\nÖNEMLİ: Aşağıdaki müfredat bileşenlerini etkinliğe entegre et, ancak kod referanslarını (KB1, SDB1.1.SB2, E1.3 gibi) ETKİNLİK METNİNDE YAZMA. Bu kodlar sadece senin referansın için, etkinlik metninde sadece becerileri doğal bir dille ifade et.\n\n`;

      const fullPrompt = durationPrompt +
        (curriculumPrompt ? `${customPrompt}${importantNote}SEÇİLEN MÜFREDAT BİLEŞENLERİ:\n${curriculumPrompt}` : customPrompt);

      console.log('Full prompt:', fullPrompt);
      console.log('Curriculum data to send:', curriculumData);

      // Call mutation with all parameters
      generateMutation.mutate({
        kazanimIds: selectedKazanimIds,
        customPrompt: fullPrompt,
        curriculumData: curriculumData
      });
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleKazanimToggle = (id: number) => {
    setSelectedKazanimIds((prev) =>
      prev.includes(id) ? prev.filter((k) => k !== id) : [...prev, id]
    );
  };

  const handleKazanimExpand = (id: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setExpandedKazanimId(expandedKazanimId === id ? null : id);
  };

  const handleSaveActivity = () => {
    if (generatedActivity) {
      navigate(`/activities/${generatedActivity.id}`);
    }
  };

  const handleCurriculumChange = (newSelections: CurriculumSelections) => {
    console.log('ActivityGenerator - Received curriculum change:', newSelections);
    setCurriculumSelections(newSelections);
  };

  const renderKazanimSelection = () => (
    <Box>
      {/* Monthly Plan Selector */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'primary.50', border: '2px solid', borderColor: 'primary.main' }}>
        <Typography variant="h6" gutterBottom color="primary">
          <AutoAwesomeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Hızlı Başlangıç: Aylık Plandan Yükle
        </Typography>
        <FormControl fullWidth>
          <InputLabel>Aylık Plan Seç</InputLabel>
          <Select
            value={selectedMonthlyPlanId || ''}
            label="Aylık Plan Seç"
            onChange={(e) => handleMonthlyPlanSelect(Number(e.target.value))}
          >
            <MenuItem value="">
              <em>Manuel olarak kazanım seç</em>
            </MenuItem>
            {monthlyPlans?.map((plan: any) => (
              <MenuItem key={plan.id} value={plan.id}>
                {plan.plan_adi} - {plan.yas_grubu} ({plan.ay} {plan.yil})
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        {selectedMonthlyPlanId && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Aylık plandaki kazanımlar otomatik olarak seçildi. İsterseniz manuel olarak da ekleyebilir/çıkarabilirsiniz.
          </Alert>
        )}
      </Paper>

      {/* Selected Kazanimlar Display */}
      {selectedKazanimIds.length > 0 && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'success.50' }}>
          <Typography variant="h6" gutterBottom color="success.main">
            <CheckCircleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Seçili Kazanımlar ({selectedKazanimIds.length})
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {selectedKazanimIds.map((id) => {
              // First check in selectedKazanimlarDetails, then fallback to kazanimlar list
              const selectedArray = Array.isArray(selectedKazanimlarDetails)
                ? selectedKazanimlarDetails
                : (selectedKazanimlarDetails as any)?.items || [];
              let kazanim = selectedArray.find((k: Kazanim) => k.id === id);

              if (!kazanim) {
                // Fallback to main list
                const kazanimlarArray = Array.isArray(kazanimlar) ? kazanimlar : (kazanimlar as any)?.items || [];
                kazanim = kazanimlarArray.find((k: Kazanim) => k.id === id);
              }

              return (
                <Chip
                  key={id}
                  label={kazanim ? `${kazanim.ders} - ${kazanim.ogrenme_ciktilari.substring(0, 50)}...` : `ID: ${id}`}
                  onDelete={() => handleKazanimToggle(id)}
                  color="success"
                  sx={{ mb: 1 }}
                />
              );
            })}
          </Stack>
          <Button
            size="small"
            color="error"
            onClick={() => setSelectedKazanimIds([])}
            sx={{ mt: 2 }}
          >
            Tümünü Temizle
          </Button>
        </Paper>
      )}

      {/* Selected Curriculum Display */}
      {((curriculumSelections.kavramsalBecerilerContent?.length ?? 0) > 0 ||
        (curriculumSelections.egilimlerContent?.length ?? 0) > 0 ||
        (curriculumSelections.degerlerContent?.length ?? 0) > 0 ||
        (curriculumSelections.surecBilesenleriContent?.length ?? 0) > 0 ||
        (curriculumSelections.butunlesikBilesenlerContent?.length ?? 0) > 0) && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'info.50' }}>
          <Typography variant="h6" gutterBottom color="info.main">
            <InfoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Seçili Müfredat Bileşenleri
          </Typography>

          {(curriculumSelections.kavramsalBecerilerContent?.length ?? 0) > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Kavramsal Beceriler:</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {curriculumSelections.kavramsalBecerilerContent?.map((item, index) => (
                  <Chip
                    key={index}
                    label={`${item.ana_beceri_kodu} ${item.ana_beceri_adi}`}
                    size="small"
                    onDelete={() => {
                      const newContent = [...(curriculumSelections.kavramsalBecerilerContent || [])];
                      newContent.splice(index, 1);
                      setCurriculumSelections({ ...curriculumSelections, kavramsalBecerilerContent: newContent });
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {(curriculumSelections.egilimlerContent?.length ?? 0) > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Eğilimler:</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {curriculumSelections.egilimlerContent?.map((item, index) => (
                  <Chip
                    key={index}
                    label={item.ana_egilim}
                    size="small"
                    onDelete={() => {
                      const newContent = [...(curriculumSelections.egilimlerContent || [])];
                      newContent.splice(index, 1);
                      setCurriculumSelections({ ...curriculumSelections, egilimlerContent: newContent });
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {(curriculumSelections.degerlerContent?.length ?? 0) > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Değerler:</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {curriculumSelections.degerlerContent?.map((item, index) => (
                  <Chip
                    key={index}
                    label={`${item.ana_deger_kodu} ${item.ana_deger_adi}`}
                    size="small"
                    onDelete={() => {
                      const newContent = [...(curriculumSelections.degerlerContent || [])];
                      newContent.splice(index, 1);
                      setCurriculumSelections({ ...curriculumSelections, degerlerContent: newContent });
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {(curriculumSelections.surecBilesenleriContent?.length ?? 0) > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Sosyal-Duygusal Beceriler:</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {curriculumSelections.surecBilesenleriContent?.map((item, index) => (
                  <Chip
                    key={index}
                    label={`${item.surec_bileseni_kodu} ${item.surec_bileseni_adi}`}
                    size="small"
                    onDelete={() => {
                      const newContent = [...(curriculumSelections.surecBilesenleriContent || [])];
                      newContent.splice(index, 1);
                      setCurriculumSelections({ ...curriculumSelections, surecBilesenleriContent: newContent });
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          <Button
            size="small"
            color="error"
            onClick={() => setCurriculumSelections({
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
            })}
            sx={{ mt: 1 }}
          >
            Tüm Müfredat Bileşenlerini Temizle
          </Button>
        </Paper>
      )}

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <FilterListIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Filtrele
        </Typography>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Yaş Grubu</InputLabel>
            <Select
              value={filters.yas_grubu}
              label="Yaş Grubu"
              onChange={(e) => setFilters({ ...filters, yas_grubu: e.target.value })}
            >
              <MenuItem value="">Tümü</MenuItem>
              {ageGroups?.age_groups?.map((group: string) => (
                <MenuItem key={group} value={group}>{group}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: 200 }}>
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
          <TextField
            fullWidth
            label="Ara"
            variant="outlined"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            slotProps={{
              input: {
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }
            }}
          />
        </Stack>
      </Paper>

      {/* Selected Count */}
      {selectedKazanimIds.length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {selectedKazanimIds.length} kazanım seçildi
        </Alert>
      )}

      {/* Kazanim List */}
      {kazanimlarLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Stack spacing={2}>
          {kazanimlar?.items?.map((kazanim: Kazanim) => (
            <Card
              key={kazanim.id}
                sx={{
                  cursor: 'pointer',
                  border: selectedKazanimIds.includes(kazanim.id) ? '2px solid' : '1px solid',
                  borderColor: selectedKazanimIds.includes(kazanim.id) ? 'primary.main' : 'divider',
                  bgcolor: selectedKazanimIds.includes(kazanim.id) ? 'primary.50' : 'background.paper',
                  transition: 'all 0.2s',
                  '&:hover': {
                    boxShadow: 2,
                  },
                }}
                onClick={() => handleKazanimToggle(kazanim.id)}
              >
                <CardContent>
                  <Box display="flex" alignItems="flex-start">
                    <Checkbox
                      checked={selectedKazanimIds.includes(kazanim.id)}
                      sx={{ mr: 2 }}
                    />
                    <Box flex={1}>
                      <Box display="flex" gap={1} mb={1} alignItems="center">
                        <Chip size="small" label={kazanim.yas_grubu} color="primary" />
                        <Chip size="small" label={kazanim.ders} variant="outlined" />
                        <Box flexGrow={1} />
                        <IconButton
                          size="small"
                          onClick={(e) => handleKazanimExpand(kazanim.id, e)}
                          sx={{
                            transform: expandedKazanimId === kazanim.id ? 'rotate(180deg)' : 'rotate(0deg)',
                            transition: 'transform 0.3s',
                          }}
                        >
                          <ExpandMoreIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="body1" fontWeight="medium" gutterBottom>
                        {kazanim.ogrenme_ciktilari}
                      </Typography>
                      {kazanim.alt_ogrenme_ciktilari && (
                        <Typography variant="body2" color="text.secondary">
                          {kazanim.alt_ogrenme_ciktilari}
                        </Typography>
                      )}

                      {/* Expanded Details */}
                      <Collapse in={expandedKazanimId === kazanim.id}>
                        <Divider sx={{ my: 2 }} />
                        <Box sx={{ mt: 2 }}>
                          <Stack spacing={2}>
                            {kazanim.alan_becerileri && (
                              <Box>
                                <Typography variant="subtitle2" fontWeight="bold" color="primary">
                                  Alan Becerileri:
                                </Typography>
                                <Typography variant="body2">
                                  {kazanim.alan_becerileri}
                                </Typography>
                              </Box>
                            )}

                            {kazanim.surec_bilesenleri && (
                              <Box>
                                <Typography variant="subtitle2" fontWeight="bold" color="primary">
                                  Süreç Bileşenleri:
                                </Typography>
                                <Typography variant="body2">
                                  {kazanim.surec_bilesenleri}
                                </Typography>
                              </Box>
                            )}

                            {kazanim.butunlesik_beceriler && (
                              <Box>
                                <Typography variant="subtitle2" fontWeight="bold" color="primary">
                                  Bütünleşik Beceriler:
                                </Typography>
                                <Typography variant="body2">
                                  {kazanim.butunlesik_beceriler}
                                </Typography>
                              </Box>
                            )}

                            <Box sx={{ bgcolor: 'grey.50', p: 1.5, borderRadius: 1 }}>
                              <Box display="flex" alignItems="center" gap={1} mb={1}>
                                <InfoIcon fontSize="small" color="action" />
                                <Typography variant="caption" fontWeight="medium">
                                  Kazanım Detayları
                                </Typography>
                              </Box>
                              <Stack spacing={0.5}>
                                <Typography variant="caption">
                                  <strong>Yaş Grubu:</strong> {kazanim.yas_grubu}
                                </Typography>
                                <Typography variant="caption">
                                  <strong>Ders:</strong> {kazanim.ders}
                                </Typography>
                                <Typography variant="caption">
                                  <strong>Kazanım ID:</strong> #{kazanim.id}
                                </Typography>
                              </Stack>
                            </Box>
                          </Stack>
                        </Box>
                      </Collapse>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
          ))}
        </Stack>
      )}
    </Box>
  );

  const renderCurriculumSelection = () => (
    <Box>
      <CurriculumSelector onSelectionChange={handleCurriculumChange} />
    </Box>
  );

  const renderActivityGeneration = () => (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight={400}>
      {generateMutation.isPending ? (
        <>
          <CircularProgress size={60} sx={{ mb: 3 }} />
          <Typography variant="h6" gutterBottom>
            Etkinlik oluşturuluyor...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Bu işlem birkaç saniye sürebilir
          </Typography>
        </>
      ) : (
        <Box width="100%">
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Etkinlik Detayları
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Etkinlik Süresi: {activityDuration} dakika</Typography>
              <Slider
                value={activityDuration}
                onChange={(_, newValue) => setActivityDuration(newValue as number)}
                min={10}
                max={120}
                step={5}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Özel İstekler (Opsiyonel)"
              placeholder="Örn: Müzik etkinliği olsun, drama içersin, açık havada yapılabilsin..."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              sx={{ mb: 2 }}
            />

            <Alert severity="info">
              Seçtiğiniz {selectedKazanimIds.length} kazanım ve müfredat bileşenleri ile etkinlik oluşturulacak.
            </Alert>
          </Paper>

          <Box display="flex" justifyContent="center">
            <Button
              variant="contained"
              size="large"
              startIcon={<AutoAwesomeIcon />}
              onClick={handleNext}
              disabled={generateMutation.isPending}
            >
              Etkinlik Oluştur
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );

  const renderSuccess = () => (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight={400}>
      <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
      <Typography variant="h4" gutterBottom>
        Etkinlik Başarıyla Oluşturuldu!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        {generatedActivity?.baslik}
      </Typography>
      <Button
        variant="contained"
        size="large"
        onClick={handleSaveActivity}
      >
        Etkinliği Görüntüle
      </Button>
    </Box>
  );

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderKazanimSelection();
      case 1:
        return renderCurriculumSelection();
      case 2:
        return renderActivityGeneration();
      case 3:
        return renderSuccess();
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <AutoAwesomeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        AI Etkinlik Üretici
      </Typography>

      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel>{step.label}</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {step.description}
              </Typography>

              {getStepContent(index)}

              <Box sx={{ mt: 3 }}>
                <Button
                  disabled={index === 0 || generateMutation.isPending}
                  onClick={handleBack}
                  sx={{ mr: 1 }}
                >
                  Geri
                </Button>
                {index < steps.length - 1 && (
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={generateMutation.isPending}
                  >
                    {index === steps.length - 2 ? 'Oluştur' : 'İleri'}
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
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}