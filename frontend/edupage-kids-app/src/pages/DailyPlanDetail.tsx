import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Paper,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  CalendarMonth as CalendarIcon,
  School as SchoolIcon,
  Person as PersonIcon,
  ExpandMore as ExpandMoreIcon,
  Timer as TimerIcon,
  Category as CategoryIcon,
  Print as PrintIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';
import { dailyPlanApi } from '../services/api';

const DailyPlanDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [expandedSections, setExpandedSections] = useState<string[]>([
    'header',
    'curriculum',
    'content',
    'learning',
    'assessment',
    'differentiation',
    'family'
  ]);

  // Fetch plan details
  const { data: plan, isLoading, error } = useQuery({
    queryKey: ['dailyPlan', id],
    queryFn: () => dailyPlanApi.getById(Number(id)),
    enabled: !!id,
  });

  const handleExport = async () => {
    if (!plan) return;
    try {
      const response = await dailyPlanApi.exportToDocx(plan.id);
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${plan.plan_adi}_gunluk_plan.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSectionToggle = (section: string) => {
    setExpandedSections((prev) =>
      prev.includes(section)
        ? prev.filter((s) => s !== section)
        : [...prev, section]
    );
  };

  const renderSkillsList = (skills: any, title: string) => {
    if (!skills) return null;

    // Handle array format (for kavramsal_beceriler and egilimler)
    if (Array.isArray(skills) && skills.length > 0) {
      return (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}>
            {title}
          </Typography>
          <List dense sx={{ pl: 2 }}>
            {skills.map((item: string, index: number) => (
              <ListItem key={index} sx={{ py: 0.5 }}>
                <Typography variant="body2">• {item}</Typography>
              </ListItem>
            ))}
          </List>
        </Box>
      );
    }

    // Handle object format (for alan_becerileri and others)
    if (typeof skills === 'object' && !Array.isArray(skills)) {
      return (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}>
            {title}
          </Typography>
          {Object.entries(skills).map(([category, items]: [string, any]) => (
            <Box key={category} sx={{ mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                {category}
              </Typography>
              {Array.isArray(items) ? (
                <List dense sx={{ pl: 2 }}>
                  {items.map((item: string, index: number) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <Typography variant="body2">• {item}</Typography>
                    </ListItem>
                  ))}
                </List>
              ) : typeof items === 'object' ? (
                Object.entries(items).map(([subCat, subItems]: [string, any]) => (
                  <Box key={subCat} sx={{ pl: 2, mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 'medium', mb: 0.5 }}>
                      {subCat}:
                    </Typography>
                    {Array.isArray(subItems) && (
                      <List dense sx={{ pl: 2 }}>
                        {subItems.map((subItem: string, idx: number) => (
                          <ListItem key={idx} sx={{ py: 0.25 }}>
                            <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                              - {subItem}
                            </Typography>
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </Box>
                ))
              ) : (
                <Typography variant="body2" sx={{ pl: 2 }}>{items}</Typography>
              )}
            </Box>
          ))}
        </Box>
      );
    }

    return null;
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>Yükleniyor...</Typography>
      </Container>
    );
  }

  if (error || !plan) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Plan yüklenirken bir hata oluştu</Alert>
      </Container>
    );
  }

  // Parse JSON fields if they're strings
  const parseJsonField = (field: any) => {
    if (typeof field === 'string') {
      try {
        return JSON.parse(field);
      } catch {
        return field;
      }
    }
    return field;
  };

  const programlarArasiBilesenler = parseJsonField(plan.programlar_arasi_bilesenler);
  const ogrenmeOgretmeYasantilari = parseJsonField(plan.ogrenme_ogretme_yasantilari);
  const icerikCercevesi = parseJsonField(plan.icerik_cercevesi);
  const farklilastirma = parseJsonField(plan.farklilastirma);
  const aileToplumKatilimi = parseJsonField(plan.aile_toplum_katilimi);

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header Actions */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/daily-plans')}
        >
          Geri Dön
        </Button>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/daily-plans/${id}/edit`)}
          >
            Düzenle
          </Button>
          <Button
            variant="outlined"
            startIcon={<PrintIcon />}
            onClick={handlePrint}
            sx={{ display: { xs: 'none', md: 'inline-flex' } }}
          >
            Yazdır
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
          >
            DOCX İndir
          </Button>
        </Box>
      </Box>

      {/* Plan Header - MEB Format */}
      <Card sx={{ mb: 3, backgroundColor: '#f5f5f5' }}>
        <CardContent>
          <Typography
            variant="h4"
            align="center"
            sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}
          >
            MEB MAARİF MODELİ OKUL ÖNCESİ EĞİTİM PROGRAMI
          </Typography>
          <Typography
            variant="h5"
            align="center"
            sx={{ mb: 3, fontWeight: 'bold' }}
          >
            GÜNLÜK PLAN
          </Typography>

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 4 }}>
              <Typography variant="body1">
                <strong>Plan Adı:</strong> {plan.plan_adi}
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Typography variant="body1">
                <strong>Tarih:</strong> {format(new Date(plan.tarih), 'dd MMMM yyyy', { locale: tr })}
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Typography variant="body1">
                <strong>Yaş Grubu:</strong> {plan.yas_grubu}
              </Typography>
            </Grid>
            {plan.sinif && (
              <Grid size={{ xs: 12, md: 4 }}>
                <Typography variant="body1">
                  <strong>Sınıf:</strong> {plan.sinif}
                </Typography>
              </Grid>
            )}
            {plan.ogretmen && (
              <Grid size={{ xs: 12, md: 4 }}>
                <Typography variant="body1">
                  <strong>Öğretmen:</strong> {plan.ogretmen}
                </Typography>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* 1. Alan Becerileri */}
      <Accordion
        expanded={expandedSections.includes('curriculum')}
        onChange={() => handleSectionToggle('curriculum')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            1. MÜFREDAT BİLEŞENLERİ
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid size={12}>
              {renderSkillsList(parseJsonField(plan.alan_becerileri), 'Alan Becerileri')}
            </Grid>
            <Grid size={12}>
              {renderSkillsList(parseJsonField(plan.kavramsal_beceriler), 'Kavramsal Beceriler')}
            </Grid>
            <Grid size={12}>
              {renderSkillsList(parseJsonField(plan.egilimler), 'Eğilimler')}
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* 2. Programlar Arası Bileşenler */}
      {programlarArasiBilesenler && (
        <Accordion
          expanded={expandedSections.includes('cross-curricular')}
          onChange={() => handleSectionToggle('cross-curricular')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              2. PROGRAMLAR ARASI BİLEŞENLER
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {renderSkillsList(programlarArasiBilesenler, '')}
          </AccordionDetails>
        </Accordion>
      )}

      {/* 3. Öğrenme Çıktıları ve Süreç Bileşenleri */}
      <Accordion
        expanded={expandedSections.includes('outcomes')}
        onChange={() => handleSectionToggle('outcomes')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            3. ÖĞRENME ÇIKTILARI VE SÜREÇ BİLEŞENLERİ
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          {renderSkillsList(
            parseJsonField(plan.ogrenme_ciktilari_surec_bilesenleri) || parseJsonField(plan.ogrenme_ciktilari),
            ''
          )}
        </AccordionDetails>
      </Accordion>

      {/* 4. İçerik Çerçevesi */}
      <Accordion
        expanded={expandedSections.includes('content')}
        onChange={() => handleSectionToggle('content')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            4. İÇERİK ÇERÇEVESİ
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            {icerikCercevesi ? (
              <>
                {icerikCercevesi.kavramlar && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Kavramlar
                      </Typography>
                      <Typography variant="body2">{icerikCercevesi.kavramlar}</Typography>
                    </Paper>
                  </Grid>
                )}
                {icerikCercevesi.sozcukler && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Sözcükler
                      </Typography>
                      <Typography variant="body2">{icerikCercevesi.sozcukler}</Typography>
                    </Paper>
                  </Grid>
                )}
                {icerikCercevesi.semboller && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Semboller
                      </Typography>
                      <Typography variant="body2">{icerikCercevesi.semboller}</Typography>
                    </Paper>
                  </Grid>
                )}
                {icerikCercevesi.materyaller && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Materyaller
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {icerikCercevesi.materyaller}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {icerikCercevesi.egitim_ortamlari && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Eğitim/Öğrenme Ortamları
                      </Typography>
                      <Typography variant="body2">{icerikCercevesi.egitim_ortamlari}</Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            ) : (
              <>
                {plan.kavramlar && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Kavramlar
                      </Typography>
                      <Typography variant="body2">{plan.kavramlar}</Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.sozcukler && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Sözcükler
                      </Typography>
                      <Typography variant="body2">{plan.sozcukler}</Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.materyaller && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Materyaller
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {plan.materyaller}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.egitim_ortamlari && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        Eğitim/Öğrenme Ortamları
                      </Typography>
                      <Typography variant="body2">{plan.egitim_ortamlari}</Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* 5. Öğrenme-Öğretme Yaşantıları */}
      <Accordion
        expanded={expandedSections.includes('learning')}
        onChange={() => handleSectionToggle('learning')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            5. ÖĞRENME-ÖĞRETME YAŞANTILARI
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            {ogrenmeOgretmeYasantilari ? (
              <>
                {ogrenmeOgretmeYasantilari.gune_baslama && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#fff8e1' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        GÜNE BAŞLAMA ZAMANI
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {ogrenmeOgretmeYasantilari.gune_baslama}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {ogrenmeOgretmeYasantilari.ogrenme_merkezleri && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#e3f2fd' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        ÖĞRENME MERKEZLERİNDE OYUN
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {ogrenmeOgretmeYasantilari.ogrenme_merkezleri}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {ogrenmeOgretmeYasantilari.beslenme_toplanma && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#f3e5f5' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        BESLENME, TOPLANMA, TEMİZLİK
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {ogrenmeOgretmeYasantilari.beslenme_toplanma}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {ogrenmeOgretmeYasantilari.etkinlikler && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#e8f5e9' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        ETKİNLİKLER
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {typeof ogrenmeOgretmeYasantilari.etkinlikler === 'string'
                          ? ogrenmeOgretmeYasantilari.etkinlikler
                          : JSON.stringify(ogrenmeOgretmeYasantilari.etkinlikler, null, 2)}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {ogrenmeOgretmeYasantilari.degerlendirme && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#fce4ec' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        DEĞERLENDİRME
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {ogrenmeOgretmeYasantilari.degerlendirme}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {ogrenmeOgretmeYasantilari.gunun_degerlendirmesi && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#fff3e0' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        GÜNÜN DEĞERLENDİRMESİ
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {ogrenmeOgretmeYasantilari.gunun_degerlendirmesi}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            ) : (
              <>
                {plan.gune_baslama && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#fff8e1' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        GÜNE BAŞLAMA ZAMANI
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {plan.gune_baslama}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.ogrenme_merkezleri && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#e3f2fd' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        ÖĞRENME MERKEZLERİNDE OYUN
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {plan.ogrenme_merkezleri}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.beslenme_toplanma && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#f3e5f5' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        BESLENME, TOPLANMA, TEMİZLİK
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {plan.beslenme_toplanma}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.etkinlikler && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#e8f5e9' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        ETKİNLİKLER
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {typeof plan.etkinlikler === 'string'
                          ? plan.etkinlikler
                          : JSON.stringify(plan.etkinlikler, null, 2)}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.degerlendirme && (
                  <Grid size={12}>
                    <Paper sx={{ p: 3, backgroundColor: '#fce4ec' }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        DEĞERLENDİRME
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="body1" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                        {plan.degerlendirme}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* 6. Farklılaştırma */}
      <Accordion
        expanded={expandedSections.includes('differentiation')}
        onChange={() => handleSectionToggle('differentiation')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            6. FARKLILASTIRMA
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            {farklilastirma ? (
              <>
                {farklilastirma.zenginlestirme && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#e8eaf6' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        ZENGİNLEŞTİRME
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {farklilastirma.zenginlestirme}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {farklilastirma.destekleme && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fff9c4' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        DESTEKLEME
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {farklilastirma.destekleme}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            ) : (
              <>
                {plan.zenginlestirme && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#e8eaf6' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        ZENGİNLEŞTİRME
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {plan.zenginlestirme}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.destekleme && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#fff9c4' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        DESTEKLEME
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {plan.destekleme}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* 7. Aile/Toplum Katılımı */}
      <Accordion
        expanded={expandedSections.includes('family')}
        onChange={() => handleSectionToggle('family')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            7. AİLE/TOPLUM KATILIMI
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            {aileToplumKatilimi ? (
              <>
                {aileToplumKatilimi.aile_katilimi && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#c8e6c9' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        AİLE KATILIMI
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {aileToplumKatilimi.aile_katilimi}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {aileToplumKatilimi.toplum_katilimi && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#ffccbc' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        TOPLUM KATILIMI
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {aileToplumKatilimi.toplum_katilimi}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            ) : (
              <>
                {plan.aile_katilimi && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#c8e6c9' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        AİLE KATILIMI
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {plan.aile_katilimi}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {plan.toplum_katilimi && (
                  <Grid size={12}>
                    <Paper sx={{ p: 2, backgroundColor: '#ffccbc' }}>
                      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                        TOPLUM KATILIMI
                      </Typography>
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                        {plan.toplum_katilimi}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Öğretmen Notları */}
      {plan.notlar && (
        <Card sx={{ mt: 2, backgroundColor: '#f5f5f5' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              ÖĞRETMEN NOTLARI
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
              {plan.notlar}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Print Styles */}
      <style>
        {`
          @media print {
            .MuiContainer-root {
              max-width: 100% !important;
            }
            .MuiAccordion-root {
              box-shadow: none !important;
            }
            .MuiAccordionSummary-root {
              display: none !important;
            }
            .MuiAccordionDetails-root {
              padding: 0 !important;
            }
            .MuiButton-root {
              display: none !important;
            }
            .MuiPaper-root {
              box-shadow: none !important;
              border: 1px solid #ddd !important;
            }
          }
        `}
      </style>
    </Container>
  );
};

export default DailyPlanDetail;