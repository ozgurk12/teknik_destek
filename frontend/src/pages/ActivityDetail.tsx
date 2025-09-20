import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Button,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Breadcrumbs,
  Link,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  AutoAwesome as AutoAwesomeIcon,
  Timer as TimerIcon,
  School as SchoolIcon,
  Groups as GroupsIcon,
  Place as PlaceIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { activityApi, API_BASE_URL } from '../services/api';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

const ActivityDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [reviseDialogOpen, setReviseDialogOpen] = useState(false);
  const [revisePrompt, setRevisePrompt] = useState('');

  const { data: activity, isLoading } = useQuery({
    queryKey: ['activity', id],
    queryFn: () => activityApi.getById(Number(id)),
    enabled: !!id,
  });

  // Revize etme mutation
  const reviseMutation = useMutation({
    mutationFn: (prompt: string) => {
      if (!activity?.kazanim_idleri) return Promise.reject('No kazanim IDs');
      return activityApi.generate(activity.kazanim_idleri, prompt);
    },
    onSuccess: (response) => {
      if (response.data.success) {
        queryClient.invalidateQueries({ queryKey: ['activity', id] });
        navigate(`/activities/${response.data.etkinlik.id}`);
      }
    },
  });

  const handleExportDocx = () => {
    if (!activity?.id) return;
    window.open(`${API_BASE_URL}/etkinlikler/${activity.id}/export/docx`, '_blank');
  };

  const handlePrint = () => {
    window.print();
  };

  const handleRevise = () => {
    if (revisePrompt.trim()) {
      const fullPrompt = `Bu etkinliği şu şekilde revize et: ${revisePrompt}`;
      reviseMutation.mutate(fullPrompt);
      setReviseDialogOpen(false);
      setRevisePrompt('');
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (!activity) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6">Etkinlik bulunamadı</Typography>
        <Button onClick={() => navigate('/activities')} sx={{ mt: 2 }}>
          Etkinlik Listesine Dön
        </Button>
      </Box>
    );
  }

  const activityData = activity;

  return (
    <Box>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/dashboard')}
          underline="hover"
          color="inherit"
        >
          Ana Sayfa
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/activities')}
          underline="hover"
          color="inherit"
        >
          Etkinlikler
        </Link>
        <Typography color="text.primary" variant="body2">
          {activityData.etkinlik_adi}
        </Typography>
      </Breadcrumbs>

      {/* Header Actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/activities')}
        >
          Geri
        </Button>
        <Box display="flex" gap={1}>
          {activity?.ai_generated && (
            <Button
              startIcon={<RefreshIcon />}
              variant="outlined"
              color="secondary"
              onClick={() => setReviseDialogOpen(true)}
            >
              Revize Et
            </Button>
          )}
          <Button startIcon={<EditIcon />} variant="outlined">
            Düzenle
          </Button>
          <Button startIcon={<PrintIcon />} variant="outlined" onClick={handlePrint}>
            Yazdır
          </Button>
          <Button startIcon={<DownloadIcon />} variant="outlined" onClick={handleExportDocx}>
            DOCX İndir
          </Button>
          <Button startIcon={<ShareIcon />} variant="outlined">
            Paylaş
          </Button>
        </Box>
      </Box>

      {/* Main Content */}
      <div id="activity-content">
        <Paper sx={{ p: 4 }}>
          {/* Title and Meta */}
          <Box mb={3}>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Typography variant="h4" fontWeight="bold">
                {activityData.etkinlik_adi}
              </Typography>
              {activityData.ai_generated && (
                <Chip
                  icon={<AutoAwesomeIcon />}
                  label="AI ile Oluşturuldu"
                  color="secondary"
                />
              )}
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary">
                Oluşturulma: {format(new Date(activityData.created_at), 'dd MMMM yyyy HH:mm', { locale: tr })}
              </Typography>
              {activityData.created_by_fullname && (
                <Typography variant="body2" color="text.secondary">
                  Oluşturan: <strong>{activityData.created_by_fullname}</strong> (@{activityData.created_by_username})
                </Typography>
              )}
              {activityData.custom_instructions && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Özel Talimatlar: <em>{activityData.custom_instructions}</em>
                </Typography>
              )}
            </Box>
          </Box>

          {/* Key Information */}
          <Grid container spacing={3} mb={4}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <SchoolIcon color="action" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Alan
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {activityData.alan_adi}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <GroupsIcon color="action" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Yaş Grubu
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {activityData.yas_grubu}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <TimerIcon color="action" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Süre
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {activityData.sure} dakika
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <PlaceIcon color="action" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Uygulama Yeri
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {activityData.uygulama_yeri}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Activity Sections */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Etkinlik Amacı</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {activityData.etkinlik_amaci}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Materyaller</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {activityData.materyaller}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Uygulama Süreci</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {(activityData.uygulama_sureci || activityData.giris_bolumu || activityData.gelisme_bolumu || activityData.yansima_cemberi || activityData.sonuc_bolumu) ? (
                activityData.uygulama_sureci ? (
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {activityData.uygulama_sureci}
                  </Typography>
                ) : (
                <>
                  {activityData.giris_bolumu && (
                    <Box mb={3}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Giriş
                      </Typography>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {activityData.giris_bolumu}
                      </Typography>
                    </Box>
                  )}

                  {activityData.gelisme_bolumu && (
                    <Box mb={3}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Gelişme
                      </Typography>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {activityData.gelisme_bolumu}
                      </Typography>
                    </Box>
                  )}

                  {activityData.yansima_cemberi && (
                    <Box mb={3}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Yansıma Çemberi
                      </Typography>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {activityData.yansima_cemberi}
                      </Typography>
                    </Box>
                  )}

                  {activityData.sonuc_bolumu && (
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Sonuç
                      </Typography>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {activityData.sonuc_bolumu}
                      </Typography>
                    </Box>
                  )}
                </>
              )
              ) : (
                <Typography variant="body1" color="text.secondary">
                  Uygulama süreci bilgisi mevcut değil.
                </Typography>
              )}
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Uyarlama</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {activityData.uyarlama || 'Farklı Yaş Grupları:\n• 36-48 ay: Etkinlik basitleştirilerek uygulanır, daha kısa süreli tutulur\n• 48-60 ay: Mevcut plan uygulanır\n• 60-72 ay: Etkinlik zenginleştirilerek, ek görevlerle desteklenir\n\nFarklı Ortamlar:\n• İç mekan: Sınıf ortamında masa başı veya halı alanında uygulanır\n• Dış mekan: Bahçede veya açık alanda hareket alanı genişletilerek uygulanır\n• Ev ortamı: Aile katılımı ile evde tekrar edilebilir'}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Farklılaştırma ve Kapsayıcılık</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {activityData.farklilastirma_kapsayicilik || 'Özel Gereksinimli Çocuklar:\n• Görme yetersizliği: Sesli betimlemeler, dokunsal materyaller, kabartmalı şekiller kullanılır\n• İşitme yetersizliği: Görsel ipuçları, işaret dili desteği, yazılı yönergeler verilir\n• Fiziksel yetersizlik: Erişilebilir materyaller, uyarlanmış araç-gereçler kullanılır\n• Zihinsel yetersizlik: Basitleştirilmiş yönergeler, tekrarlar, somut materyaller kullanılır\n• Otizm spektrum bozukluğu: Görsel programlar, yapılandırılmış ortam, rutinler oluşturulur\n• Dikkat eksikliği ve hiperaktivite: Kısa süreli etkinlikler, hareket araları, odaklanma destekleri sağlanır\n• Öğrenme güçlüğü: Çoklu duyusal yaklaşımlar, bireyselleştirilmiş destek verilir\n• Dil ve konuşma bozukluğu: Alternatif iletişim yöntemleri, görsel kartlar kullanılır\n\nÜstün Yetenekli Çocuklar:\n• Zenginleştirilmiş içerik ve ek görevler verilir\n• Yaratıcı düşünmeyi teşvik eden sorular sorulur\n• Liderlik rolleri ve akran öğretimi fırsatları sunulur'}
              </Typography>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Değerlendirme</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box mb={3}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Program Değerlendirmesi
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {activityData.degerlendirme_program || 'Gözlem Formu:\n• Etkinlik süresi ve akışı değerlendirilir\n• Materyallerin uygunluğu kontrol edilir\n• Çocukların ilgi düzeyi gözlemlenir\n• Etkinliğin kazanımlara ulaşma düzeyi belirlenir'}
                </Typography>
              </Box>

              <Box mb={3}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Beceriler Değerlendirmesi
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {activityData.degerlendirme_beceriler || 'Gelişim Alanları:\n• Bilişsel gelişim: Problem çözme ve analitik düşünme becerileri\n• Dil gelişimi: Kelime hazinesi ve iletişim becerileri\n• Sosyal-duygusal gelişim: İşbirliği ve empati kurma\n• Motor gelişim: İnce ve kaba motor beceriler'}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Öğrenci Değerlendirmesi
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {activityData.degerlendirme_ogrenciler || 'Bireysel Gözlem:\n• Her çocuğun etkinliğe katılım düzeyi\n• Bireysel güçlü yönler ve gelişim alanları\n• Öğrenme stilleri ve tercihler\n• İlerleme durumu ve kazanımlara ulaşma düzeyi'}
                </Typography>
              </Box>
            </AccordionDetails>
          </Accordion>

          {/* Related Learning Outcomes */}
          {activityData.kazanim_metinleri && activityData.kazanim_metinleri.length > 0 && (
            <>
              <Divider sx={{ my: 3 }} />
              <Box>
                <Typography variant="h6" gutterBottom>
                  İlişkili Kazanımlar
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  {activityData.kazanim_metinleri.map((kazanim: string, index: number) => (
                    <Chip
                      key={index}
                      label={kazanim}
                      variant="outlined"
                      sx={{ justifyContent: 'flex-start', height: 'auto', py: 1 }}
                    />
                  ))}
                </Box>
              </Box>
            </>
          )}
        </Paper>
      </div>

      {/* Revize Dialog */}
      <Dialog
        open={reviseDialogOpen}
        onClose={() => setReviseDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <RefreshIcon color="secondary" />
            Etkinliği Revize Et
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Etkinliği nasıl değiştirmek istediğinizi açıklayın. AI yeni bir versiyon oluşturacak.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Revize Talimatları"
            placeholder="Örn: Etkinliği dış mekanda yapılacak şekilde düzenle, müzik ekle, süreyi 45 dakikaya çıkar..."
            value={revisePrompt}
            onChange={(e) => setRevisePrompt(e.target.value)}
            helperText="Mevcut etkinlik temel alınarak yeni bir versiyon oluşturulacak"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReviseDialogOpen(false)}>İptal</Button>
          <Button
            onClick={handleRevise}
            variant="contained"
            startIcon={<AutoAwesomeIcon />}
            disabled={!revisePrompt.trim() || reviseMutation.isPending}
          >
            {reviseMutation.isPending ? 'Oluşturuluyor...' : 'Revize Et'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ActivityDetail;