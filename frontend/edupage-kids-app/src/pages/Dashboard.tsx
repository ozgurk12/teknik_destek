import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Button,
  Chip,
  Avatar,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  School as SchoolIcon,
  ListAlt as ListAltIcon,
  TrendingUp as TrendingUpIcon,
  Timer as TimerIcon,
  Groups as GroupsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { activityApi, kazanimApi } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const { data: kazanimStats } = useQuery({
    queryKey: ['kazanim-stats'],
    queryFn: () => kazanimApi.getStats(),
  });

  const { data: activityStats } = useQuery({
    queryKey: ['activity-stats'],
    queryFn: () => activityApi.getStats(),
  });

  const { data: recentActivities } = useQuery({
    queryKey: ['recent-activities'],
    queryFn: () => activityApi.list({ page_size: 5 }),
  });

  const StatCard = ({ title, value, icon, color, onClick }: any) => (
    <Card
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s',
        '&:hover': onClick ? {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        } : {},
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        borderTop: `4px solid ${color}`,
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" fontWeight="bold" color={color}>
              {value}
            </Typography>
          </Box>
          <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Hoş Geldiniz! 👋
        </Typography>
        <Typography variant="body1" color="textSecondary">
          EduPage Kids Etkinlik Planlama Sistemine hoş geldiniz. Buradan tüm işlemlerinizi yönetebilirsiniz.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Toplam Kazanım"
            value={kazanimStats?.total || 0}
            icon={<SchoolIcon />}
            color="#667eea"
            onClick={() => navigate('/kazanimlar')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Toplam Etkinlik"
            value={activityStats?.total || 0}
            icon={<ListAltIcon />}
            color="#764ba2"
            onClick={() => navigate('/activities')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="AI Üretilen"
            value={activityStats?.generation_type?.ai_generated || 0}
            icon={<AutoAwesomeIcon />}
            color="#f59e0b"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Manuel Oluşturulan"
            value={activityStats?.generation_type?.manual || 0}
            icon={<TrendingUpIcon />}
            color="#10b981"
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Hızlı İşlemler
        </Typography>
        <Grid container spacing={2} mt={1}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AutoAwesomeIcon />}
              onClick={() => navigate('/activity-generator')}
              sx={{
                py: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              }}
            >
              Yeni Etkinlik Oluştur
            </Button>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<ListAltIcon />}
              onClick={() => navigate('/activities')}
              sx={{ py: 2 }}
            >
              Etkinlikleri Görüntüle
            </Button>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<SchoolIcon />}
              onClick={() => navigate('/kazanimlar')}
              sx={{ py: 2 }}
            >
              Kazanımları İncele
            </Button>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<TrendingUpIcon />}
              onClick={() => navigate('/statistics')}
              sx={{ py: 2 }}
            >
              İstatistikleri Gör
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Charts */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Yaş Grubu Dağılımı
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={kazanimStats?.by_age_group || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="yas_grubu" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Ders Dağılımı
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={kazanimStats?.by_subject?.slice(0, 5) || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${entry.ders}: ${entry.count}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(kazanimStats?.by_subject?.slice(0, 5) || []).map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight="bold">
            Son Eklenen Etkinlikler
          </Typography>
          <Button
            size="small"
            onClick={() => navigate('/activities')}
          >
            Tümünü Gör
          </Button>
        </Box>
        
        <Grid container spacing={2}>
          {recentActivities?.items?.slice(0, 5).map((activity: any) => (
            <Grid size={12} key={activity.id}>
              <Card
                sx={{
                  cursor: 'pointer',
                  '&:hover': { boxShadow: 3 },
                }}
                onClick={() => navigate(`/activities/${activity.id}`)}
              >
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box flex={1}>
                      <Typography variant="h6" gutterBottom>
                        {activity.etkinlik_adi}
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        <Chip
                          size="small"
                          icon={<GroupsIcon />}
                          label={activity.yas_grubu}
                          variant="outlined"
                        />
                        <Chip
                          size="small"
                          icon={<SchoolIcon />}
                          label={activity.alan_adi}
                          variant="outlined"
                        />
                        <Chip
                          size="small"
                          icon={<TimerIcon />}
                          label={`${activity.sure} dk`}
                          variant="outlined"
                        />
                        {activity.ai_generated && (
                          <Chip
                            size="small"
                            icon={<AutoAwesomeIcon />}
                            label="AI"
                            color="secondary"
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
};

export default Dashboard;