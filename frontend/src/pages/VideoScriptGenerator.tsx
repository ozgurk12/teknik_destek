import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Container,
  CircularProgress,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Alert,
  Chip,
  Checkbox,
  Divider,
  Collapse,
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Send as SendIcon,
  School as SchoolIcon,
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  ContentCopy as CopyIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import api from '../services/api';
import { toast } from 'react-hot-toast';
import { useQuery } from '@tanstack/react-query';
import CurriculumSelector from '../components/CurriculumSelector';

interface Kazanim {
  id: number;
  yas_grubu: string;
  ders: string;
  alan_becerileri: string;
  butunlesik_beceriler: string;
  surec_bilesenleri: string;
  ogrenme_ciktilari: string;
  alt_ogrenme_ciktilari: string;
}

interface CurriculumSelections {
  butunlesikBilesenler: number[];
  butunlesikBilesenlerContent?: any[];
  degerler: number[];
  degerlerContent?: any[];
  egilimler: number[];
  egilimlerContent?: any[];
  kavramsalBeceriler: number[];
  kavramsalBecerilerContent?: any[];
  surecBilesenleri: number[];
  surecBilesenleriContent?: any[];
}

const kazanimApi = {
  list: async (params: any) => {
    const response = await api.get('/kazanimlar/', { params });
    return response.data;
  },
  getAgeGroups: async () => {
    const response = await api.get('/kazanimlar/age-groups');
    return response.data;
  },
  getSubjects: async (ageGroup?: string) => {
    const params = ageGroup ? { yas_grubu: ageGroup } : {};
    const response = await api.get('/kazanimlar/subjects', { params });
    return response.data;
  },
};

const VideoScriptGenerator: React.FC = () => {
  const [yasGrubu, setYasGrubu] = useState('');
  const [videoYapisi, setVideoYapisi] = useState('2 bölüm');
  const [bolumSonuEtkinligi, setBolumSonuEtkinligi] = useState('');
  const [vurguNoktalari, setVurguNoktalari] = useState('');
  const [kacinilacaklar, setKacinilacaklar] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');

  const [selectedKazanimIds, setSelectedKazanimIds] = useState<number[]>([]);
  const [expandedKazanimId, setExpandedKazanimId] = useState<number | null>(null);
  const [curriculumSelections, setCurriculumSelections] = useState<CurriculumSelections>({
    butunlesikBilesenler: [],
    degerler: [],
    egilimler: [],
    kavramsalBeceriler: [],
    surecBilesenleri: [],
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedScript, setGeneratedScript] = useState('');
  const [scriptId, setScriptId] = useState<number | null>(null);

  const [filters, setFilters] = useState({
    yas_grubu: '',
    ders: '',
    search: '',
  });

  const [showCurriculum, setShowCurriculum] = useState(false);

  // Fetch age groups
  const { data: ageGroups } = useQuery({
    queryKey: ['ageGroups'],
    queryFn: kazanimApi.getAgeGroups,
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

  // Set yaş grubu from filters when changed
  useEffect(() => {
    if (filters.yas_grubu) {
      setYasGrubu(filters.yas_grubu);
    }
  }, [filters.yas_grubu]);

  const handleKazanimToggle = (id: number) => {
    setSelectedKazanimIds((prev) =>
      prev.includes(id) ? prev.filter((k) => k !== id) : [...prev, id]
    );
  };

  const handleKazanimExpand = (id: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setExpandedKazanimId(expandedKazanimId === id ? null : id);
  };

  const handleCurriculumChange = (newSelections: CurriculumSelections) => {
    setCurriculumSelections(newSelections);
  };

  const prepareCurriculumData = () => {
    const curriculumData: any = {
      kavramsal_beceriler: [],
      egilimler: [],
      sosyal_duygusal: [],
      degerler: [],
      okuryazarlik: []
    };

    // Process kavramsal beceriler
    if (curriculumSelections.kavramsalBecerilerContent?.length) {
      curriculumData.kavramsal_beceriler = curriculumSelections.kavramsalBecerilerContent.map(item => {
        const kod = item.ana_beceri_kodu || '';
        const isim = item.ana_beceri_adi || '';
        return kod ? `${kod}. ${isim}` : isim;
      });
    }

    // Process egilimler
    if (curriculumSelections.egilimlerContent?.length) {
      curriculumData.egilimler = curriculumSelections.egilimlerContent.map(item => {
        const kod = item.ana_egilim_kodu || '';
        const isim = item.ana_egilim || '';
        return kod ? `${kod}. ${isim}` : isim;
      });
    }

    // Process sosyal duygusal
    if (curriculumSelections.surecBilesenleriContent?.length) {
      curriculumData.sosyal_duygusal = curriculumSelections.surecBilesenleriContent
        .filter(item => (item.surec_bileseni_kodu || '').includes('SDB'))
        .map(item => `${item.surec_bileseni_kodu}. ${item.surec_bileseni_adi}`);
    }

    // Process degerler
    if (curriculumSelections.degerlerContent?.length) {
      curriculumData.degerler = curriculumSelections.degerlerContent.map(item => {
        const kod = item.ana_deger_kodu || '';
        const isim = item.ana_deger_adi || '';
        return kod ? `${kod}. ${isim}` : isim;
      });
    }

    // Process okuryazarlik
    if (curriculumSelections.butunlesikBilesenlerContent?.length) {
      curriculumData.okuryazarlik = curriculumSelections.butunlesikBilesenlerContent
        .filter(item => {
          const bilesenAdi = item.butunlesik_bilesenler || '';
          return bilesenAdi.toUpperCase().includes('OKURYAZAR') || bilesenAdi.startsWith('OB');
        })
        .map(item => {
          const surecBilesen = item.surec_bilesenleri || '';
          const altBilesen = item.alt_butunlesik_bilesenler || '';
          const bilesenAdi = item.butunlesik_bilesenler || '';
          return surecBilesen || (altBilesen ? `${bilesenAdi} - ${altBilesen}` : bilesenAdi);
        });
    }

    return curriculumData;
  };

  const handleGenerateScript = async () => {
    if (selectedKazanimIds.length === 0) {
      toast.error('Lütfen en az bir kazanım seçin');
      return;
    }

    setIsGenerating(true);
    setGeneratedScript('');
    setScriptId(null);

    try {
      // Prepare curriculum data
      const curriculumData = prepareCurriculumData();

      // Get all selected curriculum IDs
      const allCurriculumIds = [
        ...curriculumSelections.butunlesikBilesenler,
        ...curriculumSelections.degerler,
        ...curriculumSelections.egilimler,
        ...curriculumSelections.kavramsalBeceriler,
        ...curriculumSelections.surecBilesenleri,
      ];

      const response = await api.post('/video-generation/generate-script', {
        yas_grubu: yasGrubu || filters.yas_grubu,
        kazanim_ids: selectedKazanimIds,
        curriculum_ids: allCurriculumIds,
        video_yapisi: videoYapisi,
        bolum_sonu_etkinligi: bolumSonuEtkinligi,
        vurgu_noktalari: vurguNoktalari,
        kacinilacaklar: kacinilacaklar,
        custom_instructions: customInstructions,
      });

      setGeneratedScript(response.data.script);
      setScriptId(response.data.id);
      toast.success('Video metni başarıyla oluşturuldu!');
    } catch (error: any) {
      console.error('Error generating script:', error);
      toast.error(error.response?.data?.detail || 'Video metni oluşturulurken hata oluştu');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopyScript = () => {
    navigator.clipboard.writeText(generatedScript);
    toast.success('Metin panoya kopyalandı!');
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <VideoIcon fontSize="large" />
          Konu Anlatım Videosu Metni Oluştur
        </Typography>

        {/* Kazanım Seçimi */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            <SchoolIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Kazanım Seçimi
          </Typography>

          {/* Filters */}
          <Stack spacing={2} sx={{ mb: 3 }}>
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
          </Stack>

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
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
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
                                    <Typography variant="subtitle2" color="primary">Alan Becerileri:</Typography>
                                    <Typography variant="body2">{kazanim.alan_becerileri}</Typography>
                                  </Box>
                                )}
                                {kazanim.butunlesik_beceriler && (
                                  <Box>
                                    <Typography variant="subtitle2" color="primary">Bütünleşik Beceriler:</Typography>
                                    <Typography variant="body2">{kazanim.butunlesik_beceriler}</Typography>
                                  </Box>
                                )}
                                {kazanim.surec_bilesenleri && (
                                  <Box>
                                    <Typography variant="subtitle2" color="primary">Süreç Bileşenleri:</Typography>
                                    <Typography variant="body2">{kazanim.surec_bilesenleri}</Typography>
                                  </Box>
                                )}
                              </Stack>
                            </Box>
                          </Collapse>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          )}
        </Paper>

        {/* Curriculum Seçimi */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Müfredat Bileşenleri
            </Typography>
            <Button
              onClick={() => setShowCurriculum(!showCurriculum)}
              endIcon={<ExpandMoreIcon sx={{
                transform: showCurriculum ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s'
              }} />}
            >
              {showCurriculum ? 'Gizle' : 'Göster'}
            </Button>
          </Box>

          <Collapse in={showCurriculum}>
            <CurriculumSelector
              onSelectionChange={handleCurriculumChange}
            />
          </Collapse>

          {!showCurriculum && (
            <Alert severity="info">
              Müfredat bileşenlerini seçmek için yukarıdaki "Göster" butonuna tıklayın
            </Alert>
          )}
        </Paper>

        {/* İsteğe Bağlı Detaylar */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">İçerik Detayları ve Özel İstekler (İsteğe Bağlı)</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={3}>
              <FormControl fullWidth>
                <InputLabel>Video Bölüm Sayısı</InputLabel>
                <Select
                  value={videoYapisi}
                  label="Video Bölüm Sayısı"
                  onChange={(e) => setVideoYapisi(e.target.value)}
                >
                  <MenuItem value="1 bölüm">1 Bölüm</MenuItem>
                  <MenuItem value="2 bölüm">2 Bölüm (Önerilen)</MenuItem>
                  <MenuItem value="3 bölüm">3 Bölüm</MenuItem>
                  <MenuItem value="4 bölüm">4 Bölüm</MenuItem>
                  <MenuItem value="5 bölüm">5 Bölüm</MenuItem>
                </Select>
              </FormControl>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Her bölüm yaklaşık 2-3 dakika sürer. 2 bölüm (4-5 dakika) okul öncesi yaş grubu için idealdir.
              </Typography>

              <TextField
                fullWidth
                multiline
                rows={2}
                label="Bölüm Sonu Etkinliği"
                value={bolumSonuEtkinligi}
                onChange={(e) => setBolumSonuEtkinligi(e.target.value)}
                placeholder="Örn: 1. bölüm bir oyunla bitsin, 2. bölüm yaratıcı bir soruyla bitsin"
                helperText="Bölümlerin nasıl bitmesini istersiniz?"
              />

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Vurgulanmasını İstediğiniz Özel Noktalar"
                value={vurguNoktalari}
                onChange={(e) => setVurguNoktalari(e.target.value)}
                placeholder="Örn: 3 rakamının yazımını kelebek kanadına benzeterek anlat"
                helperText="Konuyu işlerken özellikle vurgulamamı istediğiniz noktalar"
              />

              <TextField
                fullWidth
                multiline
                rows={2}
                label="Kaçınılmasını İstediğiniz Noktalar"
                value={kacinilacaklar}
                onChange={(e) => setKacinilacaklar(e.target.value)}
                placeholder="Örn: Yaramaz rüzgar gibi betimlemeler kullanma"
                helperText="Metinde kesinlikle kullanmamamı istediğiniz kelime, örnek veya temalar"
              />

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Özel Talimatlar"
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder="Varsa ek talimatlarınız..."
              />
            </Stack>
          </AccordionDetails>
        </Accordion>

        {/* Generate Button */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleGenerateScript}
            disabled={isGenerating || selectedKazanimIds.length === 0}
            startIcon={isGenerating ? <CircularProgress size={20} /> : <SendIcon />}
          >
            {isGenerating ? 'Video Metni Oluşturuluyor...' : 'Video Metni Oluştur'}
          </Button>
        </Box>

        {/* Generated Script */}
        {generatedScript && (
          <Card sx={{ mt: 4 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Oluşturulan Video Metni</Typography>
                <Stack direction="row" spacing={1}>
                  <IconButton onClick={handleCopyScript} size="small" color="primary">
                    <Tooltip title="Kopyala">
                      <CopyIcon />
                    </Tooltip>
                  </IconButton>
                </Stack>
              </Box>
              <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 600, overflow: 'auto' }}>
                <Typography
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                  }}
                >
                  {generatedScript}
                </Typography>
              </Paper>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  );
};

export default VideoScriptGenerator;