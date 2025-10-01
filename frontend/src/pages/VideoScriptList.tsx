import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Stack,
  Container,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  TextField,
  InputAdornment,
  CircularProgress,
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { toast } from 'react-hot-toast';

interface VideoScript {
  id: number;
  title: string;
  ders: string;
  konu: string;
  yas_grubu: string;
  status: string;
  created_at: string;
  prompt: string; // This contains the generated script
}

const VideoScriptList: React.FC = () => {
  const navigate = useNavigate();
  const [scripts, setScripts] = useState<VideoScript[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedScript, setSelectedScript] = useState<VideoScript | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scriptToDelete, setScriptToDelete] = useState<VideoScript | null>(null);

  useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/video-generation', {
        params: {
          limit: 100,
        },
      });
      // Filter only scripts with educational content (ders field)
      const videoScripts = response.data.filter((item: any) => item.ders);
      setScripts(videoScripts);
    } catch (error) {
      console.error('Error fetching scripts:', error);
      toast.error('Video metinleri yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!scriptToDelete) return;

    try {
      await api.delete(`/video-generation/${scriptToDelete.id}`);
      toast.success('Video metni silindi');
      fetchScripts();
      setDeleteDialogOpen(false);
      setScriptToDelete(null);
    } catch (error) {
      console.error('Error deleting script:', error);
      toast.error('Video metni silinirken hata oluştu');
    }
  };

  const handleCopyScript = (script: string) => {
    navigator.clipboard.writeText(script);
    toast.success('Metin panoya kopyalandı!');
  };

  const handleExportScript = (script: VideoScript) => {
    const content = script.prompt;
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${script.title.replace(/\s+/g, '_')}_video_metni.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Video metni indirildi!');
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const filteredScripts = scripts.filter((script) =>
    script.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    script.ders?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    script.konu?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generated':
        return 'success';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'generated':
        return 'Oluşturuldu';
      case 'pending':
        return 'Bekliyor';
      case 'failed':
        return 'Başarısız';
      default:
        return status;
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <VideoIcon fontSize="large" />
            Video Metinleri
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/video-script-generator')}
          >
            Yeni Video Metni Oluştur
          </Button>
        </Box>

        <Paper sx={{ mb: 3, p: 2 }}>
          <TextField
            fullWidth
            placeholder="Video metinlerinde ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Paper>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Başlık</TableCell>
                  <TableCell>Ders</TableCell>
                  <TableCell>Konu</TableCell>
                  <TableCell>Yaş Grubu</TableCell>
                  <TableCell>Durum</TableCell>
                  <TableCell>Oluşturulma Tarihi</TableCell>
                  <TableCell align="center">İşlemler</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredScripts
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((script) => (
                    <TableRow key={script.id}>
                      <TableCell>{script.title}</TableCell>
                      <TableCell>{script.ders || '-'}</TableCell>
                      <TableCell>{script.konu || '-'}</TableCell>
                      <TableCell>{script.yas_grubu || '-'}</TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(script.status)}
                          color={getStatusColor(script.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(script.created_at).toLocaleDateString('tr-TR')}
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} justifyContent="center">
                          <Tooltip title="Görüntüle">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedScript(script);
                                setViewDialogOpen(true);
                              }}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Kopyala">
                            <IconButton
                              size="small"
                              onClick={() => handleCopyScript(script.prompt)}
                            >
                              <CopyIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="İndir">
                            <IconButton
                              size="small"
                              onClick={() => handleExportScript(script)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Sil">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => {
                                setScriptToDelete(script);
                                setDeleteDialogOpen(true);
                              }}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={filteredScripts.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              labelRowsPerPage="Sayfa başına satır:"
            />
          </TableContainer>
        )}

        {/* View Dialog */}
        <Dialog
          open={viewDialogOpen}
          onClose={() => setViewDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {selectedScript?.title}
          </DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Ders</Typography>
                <Typography>{selectedScript?.ders}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Konu</Typography>
                <Typography>{selectedScript?.konu}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Yaş Grubu</Typography>
                <Typography>{selectedScript?.yas_grubu}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Video Metni
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 400, overflow: 'auto' }}>
                  <Typography
                    component="pre"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                      fontSize: '0.85rem',
                    }}
                  >
                    {selectedScript?.prompt}
                  </Typography>
                </Paper>
              </Box>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => handleCopyScript(selectedScript?.prompt || '')}>
              Kopyala
            </Button>
            <Button onClick={() => setViewDialogOpen(false)}>
              Kapat
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteDialogOpen}
          onClose={() => setDeleteDialogOpen(false)}
        >
          <DialogTitle>Video Metnini Sil</DialogTitle>
          <DialogContent>
            <Typography>
              "{scriptToDelete?.title}" başlıklı video metnini silmek istediğinizden emin misiniz?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>İptal</Button>
            <Button onClick={handleDelete} color="error" variant="contained">
              Sil
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default VideoScriptList;