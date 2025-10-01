import React, { useState, useEffect } from 'react';
import {
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Checkbox,
  FormGroup,
  FormControlLabel,
  Chip,
  Paper,
  CircularProgress,
  TextField,
  InputAdornment,
  Alert,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useQuery } from '@tanstack/react-query';
import { curriculumApi } from '../services/api';

interface CurriculumSelectorProps {
  onSelectionChange: (selections: CurriculumSelections) => void;
}

export interface CurriculumSelections {
  butunlesikBilesenler: number[];
  degerler: number[];
  egilimler: number[];
  kavramsalBeceriler: number[];
  surecBilesenleri: number[];
  // İçerikler için yeni alanlar
  butunlesikBilesenlerContent?: any[];
  degerlerContent?: any[];
  egilimlerContent?: any[];
  kavramsalBecerilerContent?: any[];
  surecBilesenleriContent?: any[];
}

const CurriculumSelector: React.FC<CurriculumSelectorProps> = ({ onSelectionChange }) => {
  const [selections, setSelections] = useState<CurriculumSelections>({
    butunlesikBilesenler: [],
    degerler: [],
    egilimler: [],
    kavramsalBeceriler: [],
    surecBilesenleri: [],
    butunlesikBilesenlerContent: [],
    degerlerContent: [],
    egilimlerContent: [],
    kavramsalBecerilerContent: [],
    surecBilesenleriContent: [],
  });

  const [searchTerm, setSearchTerm] = useState<string>('');

  // Fetch all curriculum data
  const { data: butunlesikBilesenler, isLoading: loadingBB } = useQuery({
    queryKey: ['butunlesik-bilesenler'],
    queryFn: curriculumApi.getButunlesikBilesenler,
  });

  const { data: degerler, isLoading: loadingDegerler } = useQuery({
    queryKey: ['degerler'],
    queryFn: curriculumApi.getDegerler,
  });

  const { data: egilimler, isLoading: loadingEgilimler } = useQuery({
    queryKey: ['egilimler'],
    queryFn: curriculumApi.getEgilimler,
  });

  const { data: kavramsalBeceriler, isLoading: loadingKB } = useQuery({
    queryKey: ['kavramsal-beceriler'],
    queryFn: curriculumApi.getKavramsalBeceriler,
  });

  const { data: surecBilesenleri, isLoading: loadingSB } = useQuery({
    queryKey: ['surec-bilesenleri'],
    queryFn: curriculumApi.getSurecBilesenleri,
  });

  const isLoading = loadingBB || loadingDegerler || loadingEgilimler || loadingKB || loadingSB;

  // Debug logging
  useEffect(() => {
    console.log('Curriculum Data:', {
      butunlesikBilesenler: butunlesikBilesenler?.length || 0,
      degerler: degerler?.length || 0,
      egilimler: egilimler?.length || 0,
      kavramsalBeceriler: kavramsalBeceriler?.length || 0,
      surecBilesenleri: surecBilesenleri?.length || 0,
    });
  }, [butunlesikBilesenler, degerler, egilimler, kavramsalBeceriler, surecBilesenleri]);

  useEffect(() => {
    onSelectionChange(selections);
  }, [selections, onSelectionChange]);

  const handleToggle = (category: keyof CurriculumSelections, id: number, item: any) => {
    console.log('CurriculumSelector - handleToggle called:', { category, id, item });

    setSelections(prev => {
      const idCategory = category;
      const contentCategory = `${category}Content` as keyof CurriculumSelections;

      console.log('CurriculumSelector - Current state:', {
        idCategory,
        contentCategory,
        currentIdList: prev[idCategory],
        currentContentList: prev[contentCategory]
      });

      const currentIdList = prev[idCategory] as number[];
      const currentContentList = prev[contentCategory] as any[] || [];

      const isSelected = currentIdList.includes(id);

      let newIdList: number[];
      let newContentList: any[];

      if (isSelected) {
        // Remove
        newIdList = currentIdList.filter((itemId: number) => itemId !== id);
        newContentList = currentContentList.filter((content: any) => content.id !== id);
        console.log('CurriculumSelector - Removing item:', id);
      } else {
        // Add
        newIdList = [...currentIdList, id];
        newContentList = [...currentContentList, item];
        console.log('CurriculumSelector - Adding item:', { id, item });
      }

      const newState = {
        ...prev,
        [idCategory]: newIdList,
        [contentCategory]: newContentList
      };

      console.log('CurriculumSelector - New state:', newState);
      return newState;
    });
  };

  const getSelectedCount = () => {
    // Sadece ID listelerini say, Content listelerini sayma
    return selections.butunlesikBilesenler.length +
           selections.degerler.length +
           selections.egilimler.length +
           selections.kavramsalBeceriler.length +
           selections.surecBilesenleri.length;
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  // Get selected items summary
  const getSelectedSummary = () => {
    const summary: string[] = [];
    if (selections.butunlesikBilesenlerContent?.length) {
      summary.push(`${selections.butunlesikBilesenlerContent.length} Bütünleşik Bileşen`);
    }
    if (selections.degerlerContent?.length) {
      summary.push(`${selections.degerlerContent.length} Değer`);
    }
    if (selections.egilimlerContent?.length) {
      summary.push(`${selections.egilimlerContent.length} Eğilim`);
    }
    if (selections.kavramsalBecerilerContent?.length) {
      summary.push(`${selections.kavramsalBecerilerContent.length} Kavramsal Beceri`);
    }
    if (selections.surecBilesenleriContent?.length) {
      summary.push(`${selections.surecBilesenleriContent.length} Süreç Bileşeni`);
    }
    return summary;
  };

  // Filter items based on search term
  const filterItems = (items: any[], searchFields: string[]) => {
    if (!searchTerm) return items;
    return items?.filter(item => {
      const searchLower = searchTerm.toLowerCase();
      return searchFields.some(field =>
        item[field]?.toLowerCase().includes(searchLower)
      );
    });
  };

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Müfredat Seçimleri
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Etkinlik oluştururken kullanılacak müfredat bileşenlerini seçin
        </Typography>

        {/* Search Field */}
        <TextField
          fullWidth
          size="small"
          placeholder="Müfredat öğelerinde ara..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mt: 2, mb: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />

        {/* Selected Items Summary */}
        {getSelectedCount() > 0 && (
          <Alert
            severity="info"
            icon={<CheckCircleIcon />}
            sx={{ mb: 2 }}
          >
            <Typography variant="body2" fontWeight="medium">
              Seçilen Öğeler: {getSelectedSummary().join(', ')}
            </Typography>

            {/* Bütünleşik Bileşenler */}
            {selections.butunlesikBilesenlerContent && selections.butunlesikBilesenlerContent.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" display="block" fontWeight="bold">
                  Bütünleşik Bileşenler:
                </Typography>
                {selections.butunlesikBilesenlerContent.slice(0, 3).map((item, idx) => (
                  <Typography key={idx} variant="caption" display="block">
                    • {item.butunlesik_bilesenler}
                    {item.alt_butunlesik_bilesenler && ` - ${item.alt_butunlesik_bilesenler}`}
                  </Typography>
                ))}
                {selections.butunlesikBilesenlerContent.length > 3 && (
                  <Typography variant="caption" display="block" color="text.secondary">
                    ...ve {selections.butunlesikBilesenlerContent.length - 3} öğe daha
                  </Typography>
                )}
              </Box>
            )}

            {/* Değerler */}
            {selections.degerlerContent && selections.degerlerContent.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" display="block" fontWeight="bold">
                  Değerler:
                </Typography>
                {selections.degerlerContent.slice(0, 3).map((item, idx) => (
                  <Typography key={idx} variant="caption" display="block">
                    • {item.ana_deger_adi} - {item.alt_deger_adi}
                  </Typography>
                ))}
                {selections.degerlerContent.length > 3 && (
                  <Typography variant="caption" display="block" color="text.secondary">
                    ...ve {selections.degerlerContent.length - 3} öğe daha
                  </Typography>
                )}
              </Box>
            )}

            {/* Eğilimler */}
            {selections.egilimlerContent && selections.egilimlerContent.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" display="block" fontWeight="bold">
                  Eğilimler:
                </Typography>
                {selections.egilimlerContent.slice(0, 3).map((item, idx) => (
                  <Typography key={idx} variant="caption" display="block">
                    • {item.ana_egilim} - {item.alt_egilim}
                  </Typography>
                ))}
                {selections.egilimlerContent.length > 3 && (
                  <Typography variant="caption" display="block" color="text.secondary">
                    ...ve {selections.egilimlerContent.length - 3} öğe daha
                  </Typography>
                )}
              </Box>
            )}

            {/* Kavramsal Beceriler */}
            {selections.kavramsalBecerilerContent && selections.kavramsalBecerilerContent.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" display="block" fontWeight="bold">
                  Kavramsal Beceriler:
                </Typography>
                {selections.kavramsalBecerilerContent.slice(0, 3).map((item, idx) => (
                  <Typography key={idx} variant="caption" display="block">
                    • {item.ana_beceri_kategorisi} - {item.ana_beceri_adi}
                  </Typography>
                ))}
                {selections.kavramsalBecerilerContent.length > 3 && (
                  <Typography variant="caption" display="block" color="text.secondary">
                    ...ve {selections.kavramsalBecerilerContent.length - 3} öğe daha
                  </Typography>
                )}
              </Box>
            )}

            {/* Süreç Bileşenleri */}
            {selections.surecBilesenleriContent && selections.surecBilesenleriContent.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" display="block" fontWeight="bold">
                  Süreç Bileşenleri:
                </Typography>
                {selections.surecBilesenleriContent.slice(0, 3).map((item, idx) => (
                  <Typography key={idx} variant="caption" display="block">
                    • {item.surec_bileseni_kodu} - {item.surec_bileseni_adi}
                  </Typography>
                ))}
                {selections.surecBilesenleriContent.length > 3 && (
                  <Typography variant="caption" display="block" color="text.secondary">
                    ...ve {selections.surecBilesenleriContent.length - 3} öğe daha
                  </Typography>
                )}
              </Box>
            )}
          </Alert>
        )}

        <Box mt={2}>
          <Chip
            label={`Toplam ${getSelectedCount()} öğe seçildi`}
            color="primary"
            variant={getSelectedCount() > 0 ? "filled" : "outlined"}
          />
        </Box>
      </Paper>

      {/* Bütünleşik Bileşenler */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography>Bütünleşik Bileşenler</Typography>
            {selections.butunlesikBilesenler.length > 0 && (
              <Chip size="small" label={selections.butunlesikBilesenler.length} />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {filterItems(butunlesikBilesenler, ['butunlesik_bilesenler', 'alt_butunlesik_bilesenler'])?.map((item: any) => (
              <FormControlLabel
                key={item.id}
                control={
                  <Checkbox
                    checked={selections.butunlesikBilesenler.includes(item.id)}
                    onChange={() => handleToggle('butunlesikBilesenler', item.id, item)}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2">{item.butunlesik_bilesenler}</Typography>
                    {item.alt_butunlesik_bilesenler && (
                      <Typography variant="caption" color="text.secondary">
                        {item.alt_butunlesik_bilesenler}
                      </Typography>
                    )}
                  </Box>
                }
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>

      {/* Değerler */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography>Değerler</Typography>
            {selections.degerler.length > 0 && (
              <Chip size="small" label={selections.degerler.length} />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {filterItems(degerler, ['ana_deger_adi', 'alt_deger_adi', 'davranis_gostergesi_aciklamasi'])?.map((item: any) => (
              <FormControlLabel
                key={item.id}
                control={
                  <Checkbox
                    checked={selections.degerler.includes(item.id)}
                    onChange={() => handleToggle('degerler', item.id, item)}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2">
                      {item.ana_deger_adi} - {item.alt_deger_adi}
                    </Typography>
                    {item.davranis_gostergesi_aciklamasi && (
                      <Typography variant="caption" color="text.secondary">
                        {item.davranis_gostergesi_aciklamasi}
                      </Typography>
                    )}
                  </Box>
                }
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>

      {/* Eğilimler */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography>Eğilimler</Typography>
            {selections.egilimler.length > 0 && (
              <Chip size="small" label={selections.egilimler.length} />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {filterItems(egilimler, ['ana_egilim', 'alt_egilim'])?.map((item: any) => (
              <FormControlLabel
                key={item.id}
                control={
                  <Checkbox
                    checked={selections.egilimler.includes(item.id)}
                    onChange={() => handleToggle('egilimler', item.id, item)}
                  />
                }
                label={
                  <Typography variant="body2">
                    {item.ana_egilim} - {item.alt_egilim}
                  </Typography>
                }
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>

      {/* Kavramsal Beceriler */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography>Kavramsal Beceriler</Typography>
            {selections.kavramsalBeceriler.length > 0 && (
              <Chip size="small" label={selections.kavramsalBeceriler.length} />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {filterItems(kavramsalBeceriler, ['ana_beceri_kategorisi', 'ana_beceri_adi', 'aciklama'])?.map((item: any) => (
              <FormControlLabel
                key={item.id}
                control={
                  <Checkbox
                    checked={selections.kavramsalBeceriler.includes(item.id)}
                    onChange={() => handleToggle('kavramsalBeceriler', item.id, item)}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2">
                      {item.ana_beceri_kategorisi} - {item.ana_beceri_adi}
                    </Typography>
                    {item.aciklama && (
                      <Typography variant="caption" color="text.secondary">
                        {item.aciklama}
                      </Typography>
                    )}
                  </Box>
                }
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>

      {/* Süreç Bileşenleri */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography>Süreç Bileşenleri</Typography>
            {selections.surecBilesenleri.length > 0 && (
              <Chip size="small" label={selections.surecBilesenleri.length} />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <FormGroup>
            {filterItems(surecBilesenleri, ['surec_bileseni_kodu', 'surec_bileseni_adi', 'gosterge_aciklamasi'])?.map((item: any) => (
              <FormControlLabel
                key={item.id}
                control={
                  <Checkbox
                    checked={selections.surecBilesenleri.includes(item.id)}
                    onChange={() => handleToggle('surecBilesenleri', item.id, item)}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2">
                      {item.surec_bileseni_kodu} - {item.surec_bileseni_adi}
                    </Typography>
                    {item.gosterge_aciklamasi && (
                      <Typography variant="caption" color="text.secondary">
                        {item.gosterge_aciklamasi}
                      </Typography>
                    )}
                  </Box>
                }
              />
            ))}
          </FormGroup>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default CurriculumSelector;