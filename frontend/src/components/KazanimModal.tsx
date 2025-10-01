import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Grid,
} from '@mui/material';
import { Kazanim } from '../types';

interface KazanimModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: any) => Promise<void>;
  kazanim?: Kazanim | null;
  ageGroups?: string[];
  subjects?: string[];
}

const KazanimModal: React.FC<KazanimModalProps> = ({
  open,
  onClose,
  onSave,
  kazanim,
  ageGroups = [],
  subjects = [],
}) => {
  const [formData, setFormData] = useState({
    yas_grubu: '',
    ders: '',
    alan_becerileri: '',
    butunlesik_beceriler: '',
    surec_bilesenleri: '',
    ogrenme_ciktilari: '',
    alt_ogrenme_ciktilari: '',
  });
  const [newDersName, setNewDersName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (kazanim) {
      setFormData({
        yas_grubu: kazanim.yas_grubu || '',
        ders: kazanim.ders || '',
        alan_becerileri: kazanim.alan_becerileri || '',
        butunlesik_beceriler: kazanim.butunlesik_beceriler || '',
        surec_bilesenleri: kazanim.surec_bilesenleri || '',
        ogrenme_ciktilari: kazanim.ogrenme_ciktilari || '',
        alt_ogrenme_ciktilari: kazanim.alt_ogrenme_ciktilari || '',
      });
    } else {
      setFormData({
        yas_grubu: '',
        ders: '',
        alan_becerileri: '',
        butunlesik_beceriler: '',
        surec_bilesenleri: '',
        ogrenme_ciktilari: '',
        alt_ogrenme_ciktilari: '',
      });
    }
    setNewDersName(''); // Reset new course name when modal data changes
  }, [kazanim]);

  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
    const finalFormData = { ...formData };

    // If new course is selected, use the new course name
    if (formData.ders === 'YENI_DERS') {
      if (!newDersName.trim()) {
        setError('Yeni ders adı giriniz');
        return;
      }
      finalFormData.ders = newDersName.trim();
    }

    if (!finalFormData.yas_grubu || !finalFormData.ders) {
      setError('Yaş grubu ve ders alanları zorunludur');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await onSave(finalFormData);
      onClose();
      setNewDersName(''); // Reset new course name
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { maxHeight: '90vh' }
      }}
    >
      <DialogTitle>
        {kazanim ? 'Kazanım Düzenle' : 'Yeni Kazanım Ekle'}
      </DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth required>
              <InputLabel>Yaş Grubu</InputLabel>
              <Select
                name="yas_grubu"
                value={formData.yas_grubu}
                onChange={handleChange}
                label="Yaş Grubu"
              >
                {ageGroups.map((age) => (
                  <MenuItem key={age} value={age}>
                    {age}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControl fullWidth required>
              <InputLabel>Ders</InputLabel>
              <Select
                name="ders"
                value={formData.ders}
                onChange={handleChange}
                label="Ders"
              >
                {subjects.map((subject) => (
                  <MenuItem key={subject} value={subject}>
                    {subject}
                  </MenuItem>
                ))}
                <MenuItem value="YENI_DERS">+ Yeni Ders Ekle</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          {formData.ders === 'YENI_DERS' && (
            <Grid size={12}>
              <TextField
                fullWidth
                label="Yeni Ders Adı"
                name="newDersName"
                value={newDersName}
                onChange={(e) => setNewDersName(e.target.value)}
                required
              />
            </Grid>
          )}
          <Grid size={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Alan Becerileri"
              name="alan_becerileri"
              value={formData.alan_becerileri}
              onChange={handleChange}
            />
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Bütünleşik Beceriler"
              name="butunlesik_beceriler"
              value={formData.butunlesik_beceriler}
              onChange={handleChange}
            />
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Süreç Bileşenleri"
              name="surec_bilesenleri"
              value={formData.surec_bilesenleri}
              onChange={handleChange}
            />
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Öğrenme Çıktıları"
              name="ogrenme_ciktilari"
              value={formData.ogrenme_ciktilari}
              onChange={handleChange}
            />
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Alt Öğrenme Çıktıları"
              name="alt_ogrenme_ciktilari"
              value={formData.alt_ogrenme_ciktilari}
              onChange={handleChange}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          İptal
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
        >
          {loading ? 'Kaydediliyor...' : (kazanim ? 'Güncelle' : 'Ekle')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KazanimModal;