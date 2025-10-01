import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardMedia,
  IconButton,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Container,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  VideoLibrary as VideoIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import api from '../services/api';
import { toast } from 'react-hot-toast';

interface UploadedImage {
  file: File;
  preview: string;
  url?: string;
}

const VideoGeneration: React.FC = () => {
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(30);
  const [style, setStyle] = useState('cinematic');
  const [musicGenre, setMusicGenre] = useState('');
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newImages = acceptedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));
    setImages((prev) => [...prev, ...newImages]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
    },
    maxSize: 10485760, // 10MB
    multiple: true,
  });

  const removeImage = (index: number) => {
    setImages((prev) => {
      const newImages = [...prev];
      URL.revokeObjectURL(newImages[index].preview);
      newImages.splice(index, 1);
      return newImages;
    });
  };

  const uploadImages = async () => {
    const uploadedUrls: string[] = [];

    for (const image of images) {
      if (image.url) {
        uploadedUrls.push(image.url);
        continue;
      }

      const formData = new FormData();
      formData.append('file', image.file);

      try {
        const response = await api.post('/video-generation/upload-image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        uploadedUrls.push(response.data.url);
        image.url = response.data.url;
      } catch (error) {
        console.error('Error uploading image:', error);
        throw error;
      }
    }

    return uploadedUrls;
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      toast.error('Lütfen bir başlık girin');
      return;
    }

    if (!prompt.trim()) {
      toast.error('Lütfen video için bir prompt girin');
      return;
    }

    if (images.length === 0) {
      toast.error('Lütfen en az bir görsel yükleyin');
      return;
    }

    setIsGenerating(true);
    setIsUploading(true);

    try {
      // Upload images first
      const imageUrls = await uploadImages();
      setIsUploading(false);

      // Create video generation request
      const payload = {
        title,
        prompt,
        duration,
        style,
        music_genre: musicGenre || null,
      };

      await api.post('/video-generation/', {
        ...payload,
        image_urls: imageUrls,
      });

      toast.success('Video üretim isteği başarıyla oluşturuldu!');

      // Reset form
      setTitle('');
      setPrompt('');
      setImages([]);
      setDuration(30);
      setStyle('cinematic');
      setMusicGenre('');
    } catch (error: any) {
      console.error('Error creating video generation:', error);
      toast.error(error.response?.data?.detail || 'Video üretim isteği oluşturulamadı');
    } finally {
      setIsGenerating(false);
      setIsUploading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <VideoIcon sx={{ fontSize: 36 }} />
          Video Üretimi
        </Typography>

        <Paper sx={{ p: 3, mt: 3 }}>
          <Stack spacing={3}>
            {/* Title */}
            <TextField
              fullWidth
              label="Video Başlığı"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Örn: Kış Mevsimi Eğitim Videosu"
              required
            />

            {/* Prompt */}
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Video Prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Videonun nasıl olmasını istediğinizi detaylı bir şekilde açıklayın..."
              required
            />

            {/* Video Settings */}
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Video Süresi (saniye)</InputLabel>
                <Select
                  value={duration}
                  onChange={(e) => setDuration(e.target.value as number)}
                  label="Video Süresi (saniye)"
                >
                  <MenuItem value={15}>15 saniye</MenuItem>
                  <MenuItem value={30}>30 saniye</MenuItem>
                  <MenuItem value={45}>45 saniye</MenuItem>
                  <MenuItem value={60}>60 saniye</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Video Stili</InputLabel>
                <Select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  label="Video Stili"
                >
                  <MenuItem value="cinematic">Sinematik</MenuItem>
                  <MenuItem value="animation">Animasyon</MenuItem>
                  <MenuItem value="cartoon">Çizgi Film</MenuItem>
                  <MenuItem value="realistic">Gerçekçi</MenuItem>
                  <MenuItem value="artistic">Sanatsal</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Müzik Türü (Opsiyonel)"
                value={musicGenre}
                onChange={(e) => setMusicGenre(e.target.value)}
                placeholder="Örn: Neşeli, Sakin, Klasik"
              />
            </Stack>

            {/* Image Upload */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Görseller
              </Typography>

              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <input {...getInputProps()} />
                <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  {isDragActive
                    ? 'Görselleri buraya bırakın...'
                    : 'Görselleri sürükleyip bırakın veya seçmek için tıklayın'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  PNG, JPG, JPEG, WEBP (Max: 10MB)
                </Typography>
              </Box>
            </Box>

            {/* Uploaded Images */}
            {images.length > 0 && (
              <Box>
                <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                  {images.map((image, index) => (
                    <Card key={index} sx={{ width: 200, position: 'relative' }}>
                      <CardMedia
                        component="img"
                        height="150"
                        image={image.preview}
                        alt={`Upload ${index + 1}`}
                        sx={{ objectFit: 'cover' }}
                      />
                      <IconButton
                        sx={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          backgroundColor: 'rgba(0, 0, 0, 0.6)',
                          color: 'white',
                          '&:hover': {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          },
                        }}
                        onClick={() => removeImage(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                      {image.url && (
                        <Chip
                          label="Yüklendi"
                          color="success"
                          size="small"
                          sx={{
                            position: 'absolute',
                            bottom: 8,
                            left: 8,
                          }}
                        />
                      )}
                    </Card>
                  ))}
                </Stack>
              </Box>
            )}

            {/* Submit Button */}
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                onClick={() => {
                  setTitle('');
                  setPrompt('');
                  setImages([]);
                  setDuration(30);
                  setStyle('cinematic');
                  setMusicGenre('');
                }}
                disabled={isGenerating}
              >
                Temizle
              </Button>
              <Button
                variant="contained"
                size="large"
                startIcon={isGenerating ? <CircularProgress size={20} /> : <SendIcon />}
                onClick={handleSubmit}
                disabled={isGenerating}
              >
                {isGenerating
                  ? isUploading
                    ? 'Görseller Yükleniyor...'
                    : 'Video Üretiliyor...'
                  : 'Video Üret'}
              </Button>
            </Stack>

            {/* Loading Progress */}
            {isGenerating && (
              <Box>
                <LinearProgress />
                <Alert severity="info" sx={{ mt: 2 }}>
                  Video üretim isteğiniz işleniyor. Bu işlem birkaç dakika sürebilir...
                </Alert>
              </Box>
            )}
          </Stack>
        </Paper>
      </Box>
    </Container>
  );
};

export default VideoGeneration;