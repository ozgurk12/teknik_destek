import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Container,
  Stack,
  CircularProgress,
  Button,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  AccessTime as TimeIcon,
  School as SchoolIcon,
  ContentCopy as CopyIcon,
  Visibility as VisibilityIcon,
  ExpandMore as ExpandMoreIcon,
  Description as ScriptIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

interface VideoGeneration {
  id: number;
  title: string;
  prompt: string;
  parsed_content?: any;
  ders?: string;
  konu?: string;
  yas_grubu?: string;
  video_yapisi?: string;
  kazanim_ids?: number[];
  kazanim_details?: any[];
  curriculum_ids?: number[];
  curriculum_details?: any;
  status: string;
  created_at: string;
}

const VideoGenerationList: React.FC = () => {
  const [videos, setVideos] = useState<VideoGeneration[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedScript, setSelectedScript] = useState<VideoGeneration | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await api.get('/video-generation/');
      setVideos(response.data);
    } catch (error) {
      console.error('Error fetching videos:', error);
      toast.error('Video listesi yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generated':
        return 'success';
      case 'pending':
        return 'warning';
      case 'processing':
        return 'info';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'generated':
        return 'Oluşturuldu';
      case 'pending':
        return 'Beklemede';
      case 'processing':
        return 'İşleniyor';
      case 'completed':
        return 'Tamamlandı';
      case 'failed':
        return 'Başarısız';
      default:
        return status;
    }
  };

  const handleViewScript = (video: VideoGeneration) => {
    setSelectedScript(video);
    setDialogOpen(true);
  };

  const handleCopyScript = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Metin panoya kopyalandı!');
  };

  const handleDownloadScript = (video: VideoGeneration) => {
    const content = video.prompt || '';
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${video.title || 'video-metni'}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('Metin indirildi!');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ScriptIcon sx={{ fontSize: 36 }} />
            Video Metinleri
          </Typography>
          <Button
            variant="contained"
            startIcon={<VideoIcon />}
            onClick={() => navigate('/video-script-generator')}
          >
            Yeni Video Metni Oluştur
          </Button>
        </Stack>

        {videos.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">
              Henüz video metni bulunmuyor
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {videos.map((video) => (
              <Grid size={{ xs: 12, md: 6 }} key={video.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {video.title}
                        </Typography>
                        {video.ders && (
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            📚 {video.ders}
                          </Typography>
                        )}
                        {video.konu && (
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            📝 Konu: {video.konu}
                          </Typography>
                        )}
                      </Box>

                      <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                        <Chip
                          label={getStatusText(video.status)}
                          color={getStatusColor(video.status) as any}
                          size="small"
                        />
                        {video.yas_grubu && (
                          <Chip
                            icon={<SchoolIcon />}
                            label={video.yas_grubu}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {video.video_yapisi && (
                          <Chip
                            label={video.video_yapisi}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Stack>

                      {video.prompt && (
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <Typography
                            variant="body2"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 4,
                              WebkitBoxOrient: 'vertical',
                              fontFamily: 'monospace',
                            }}
                          >
                            {video.prompt}
                          </Typography>
                        </Paper>
                      )}

                      <Stack direction="row" spacing={1} justifyContent="space-between">
                        <Typography variant="caption" color="text.secondary">
                          {new Date(video.created_at).toLocaleDateString('tr-TR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </Typography>
                        <Stack direction="row" spacing={1}>
                          <IconButton
                            size="small"
                            onClick={() => handleViewScript(video)}
                            color="primary"
                          >
                            <VisibilityIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleCopyScript(video.prompt)}
                          >
                            <CopyIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDownloadScript(video)}
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Stack>
                      </Stack>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Script View Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{selectedScript?.title}</Typography>
            <Stack direction="row" spacing={1}>
              <IconButton
                size="small"
                onClick={() => handleCopyScript(selectedScript?.prompt || '')}
              >
                <CopyIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => selectedScript && handleDownloadScript(selectedScript)}
              >
                <DownloadIcon />
              </IconButton>
            </Stack>
          </Stack>
        </DialogTitle>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Video Metni" />
            <Tab label={`Kazanımlar (${selectedScript?.kazanim_details?.length || 0})`} />
            <Tab label="Müfredat Bileşenleri" />
          </Tabs>
        </Box>
        <DialogContent dividers>
          {tabValue === 0 && selectedScript?.parsed_content ? (
            <Stack spacing={2}>
              {/* Script Info */}
              <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
                <Stack spacing={1}>
                  {selectedScript.parsed_content.subject && (
                    <Typography variant="body2">
                      <strong>Ders:</strong> {selectedScript.parsed_content.subject}
                    </Typography>
                  )}
                  {selectedScript.parsed_content.age_group && (
                    <Typography variant="body2">
                      <strong>Yaş Grubu:</strong> {selectedScript.parsed_content.age_group}
                    </Typography>
                  )}
                  {selectedScript.parsed_content.duration && (
                    <Typography variant="body2">
                      <strong>Süre:</strong> {selectedScript.parsed_content.duration}
                    </Typography>
                  )}
                  {selectedScript.parsed_content.character && (
                    <Typography variant="body2">
                      <strong>Karakter:</strong> {selectedScript.parsed_content.character}
                    </Typography>
                  )}
                </Stack>
              </Paper>

              <Divider />

              {/* Sections */}
              {selectedScript.parsed_content.sections?.map((section: any, index: number) => (
                <Accordion key={index} defaultExpanded={index === 0}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {section.section_number}. BÖLÜM: {section.title}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Stack spacing={2}>
                      {section.background && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            🎨 Arka Plan:
                          </Typography>
                          <Typography variant="body2">{section.background}</Typography>
                        </Box>
                      )}
                      {section.character && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            🗣️ Karakter:
                          </Typography>
                          <Typography variant="body2">{section.character}</Typography>
                        </Box>
                      )}
                      {section.text && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            📝 Metin:
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              whiteSpace: 'pre-wrap',
                              fontFamily: 'monospace',
                              bgcolor: 'grey.50',
                              p: 2,
                              borderRadius: 1
                            }}
                          >
                            {section.text}
                          </Typography>
                        </Box>
                      )}
                      {section.visual_cues && section.visual_cues.length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            👁️ Görsel İpuçları:
                          </Typography>
                          <Stack direction="row" spacing={1} flexWrap="wrap">
                            {section.visual_cues.map((cue: string, i: number) => (
                              <Chip key={i} label={cue} size="small" variant="outlined" />
                            ))}
                          </Stack>
                        </Box>
                      )}
                    </Stack>
                  </AccordionDetails>
                </Accordion>
              ))}

              {/* Raw Text Fallback */}
              {!selectedScript.parsed_content.sections && (
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography
                    variant="body2"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                    }}
                  >
                    {selectedScript.prompt}
                  </Typography>
                </Paper>
              )}
            </Stack>
          ) : tabValue === 0 ? (
            <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography
                variant="body2"
                sx={{
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                }}
              >
                {selectedScript?.prompt}
              </Typography>
            </Paper>
          ) : null}

          {/* Kazanımlar Tab */}
          {tabValue === 1 && (
            <Stack spacing={2}>
              {selectedScript?.kazanim_details && selectedScript.kazanim_details.length > 0 ? (
                selectedScript.kazanim_details.map((kazanim: any, index: number) => (
                  <Paper key={index} sx={{ p: 2 }}>
                    <Stack spacing={1}>
                      <Box display="flex" gap={1} alignItems="center">
                        <Chip label={kazanim.yas_grubu} size="small" color="primary" />
                        <Chip label={kazanim.ders} size="small" variant="outlined" />
                      </Box>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {kazanim.ogrenme_ciktilari}
                      </Typography>
                      {kazanim.alt_ogrenme_ciktilari && (
                        <Typography variant="body2" color="text.secondary">
                          {kazanim.alt_ogrenme_ciktilari}
                        </Typography>
                      )}
                      {kazanim.alan_becerileri && (
                        <Box>
                          <Typography variant="caption" color="primary">Alan Becerileri:</Typography>
                          <Typography variant="body2">{kazanim.alan_becerileri}</Typography>
                        </Box>
                      )}
                      {kazanim.butunlesik_beceriler && (
                        <Box>
                          <Typography variant="caption" color="primary">Bütünleşik Beceriler:</Typography>
                          <Typography variant="body2">{kazanim.butunlesik_beceriler}</Typography>
                        </Box>
                      )}
                    </Stack>
                  </Paper>
                ))
              ) : (
                <Typography color="text.secondary">Kazanım bilgisi bulunmuyor</Typography>
              )}
            </Stack>
          )}

          {/* Müfredat Bileşenleri Tab */}
          {tabValue === 2 && (
            <Stack spacing={3}>
              {selectedScript?.curriculum_details ? (
                <>
                  {/* Kavramsal Beceriler */}
                  {selectedScript.curriculum_details.kavramsal_beceriler?.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                        Kavramsal Beceriler
                      </Typography>
                      <List dense>
                        {selectedScript.curriculum_details.kavramsal_beceriler.map((item: any, i: number) => (
                          <ListItem key={i}>
                            <ListItemText
                              primary={`${item.ana_beceri_kodu}. ${item.ana_beceri_adi}`}
                              secondary={item.alt_beceri_kodu ? `${item.alt_beceri_kodu}. ${item.alt_beceri_adi}` : undefined}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Eğilimler */}
                  {selectedScript.curriculum_details.egilimler?.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                        Eğilimler
                      </Typography>
                      <List dense>
                        {selectedScript.curriculum_details.egilimler.map((item: any, i: number) => (
                          <ListItem key={i}>
                            <ListItemText
                              primary={item.ana_egilim}
                              secondary={item.alt_egilim}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Değerler */}
                  {selectedScript.curriculum_details.degerler?.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                        Değerler
                      </Typography>
                      <List dense>
                        {selectedScript.curriculum_details.degerler.map((item: any, i: number) => (
                          <ListItem key={i}>
                            <ListItemText
                              primary={`${item.ana_deger_kodu}. ${item.ana_deger_adi}`}
                              secondary={item.alt_deger_kodu ? `${item.alt_deger_kodu}. ${item.alt_deger_adi}` : undefined}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Süreç Bileşenleri */}
                  {selectedScript.curriculum_details.surec_bilesenleri?.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                        Süreç Bileşenleri
                      </Typography>
                      <List dense>
                        {selectedScript.curriculum_details.surec_bilesenleri.map((item: any, i: number) => (
                          <ListItem key={i}>
                            <ListItemText
                              primary={`${item.surec_bileseni_kodu}. ${item.surec_bileseni_adi}`}
                              secondary={item.gosterge_aciklamasi || item.gosterge_kodu}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Bütünleşik Bileşenler */}
                  {selectedScript.curriculum_details.butunlesik_bilesenler?.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                        Bütünleşik Bileşenler
                      </Typography>
                      <List dense>
                        {selectedScript.curriculum_details.butunlesik_bilesenler.map((item: any, i: number) => (
                          <ListItem key={i}>
                            <ListItemText
                              primary={item.butunlesik_bilesenler}
                              secondary={
                                <Box>
                                  {item.alt_butunlesik_bilesenler && (
                                    <Typography variant="caption" display="block">
                                      Alt: {item.alt_butunlesik_bilesenler}
                                    </Typography>
                                  )}
                                  {item.surec_bilesenleri && (
                                    <Typography variant="caption" display="block">
                                      Süreç: {item.surec_bilesenleri}
                                    </Typography>
                                  )}
                                </Box>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {!selectedScript.curriculum_details.kavramsal_beceriler?.length &&
                   !selectedScript.curriculum_details.egilimler?.length &&
                   !selectedScript.curriculum_details.degerler?.length &&
                   !selectedScript.curriculum_details.surec_bilesenleri?.length &&
                   !selectedScript.curriculum_details.butunlesik_bilesenler?.length && (
                    <Typography color="text.secondary">Müfredat bileşeni bilgisi bulunmuyor</Typography>
                  )}
                </>
              ) : (
                <Typography color="text.secondary">Müfredat bileşeni bilgisi bulunmuyor</Typography>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Kapat</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default VideoGenerationList;