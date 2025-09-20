import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  School as SchoolIcon,
  ListAlt as ListAltIcon,
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { kazanimApi, activityApi } from '../services/api';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0', '#ffb347'];

const Statistics: React.FC = () => {
  const { data: kazanimStats, isLoading: kazanimLoading } = useQuery({
    queryKey: ['kazanim-stats'],
    queryFn: () => kazanimApi.getStats(),
  });

  const { data: activityStats, isLoading: activityLoading } = useQuery({
    queryKey: ['activity-stats'],
    queryFn: () => activityApi.getStats(),
  });

  const StatCard = ({ title, value, icon, color, subtitle }: any) => (
    <Card
      sx={{
        height: '100%',
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        borderTop: `4px solid ${color}`,
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h3" fontWeight="bold" color={color}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              bgcolor: `${color}20`,
              p: 1.5,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {React.cloneElement(icon, { sx: { fontSize: 32, color } })}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (kazanimLoading || activityLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  const pieData = activityStats?.data?.generation_type
    ? [
        { name: 'AI Üretilen', value: activityStats.data.generation_type.ai_generated },
        { name: 'Manuel', value: activityStats.data.generation_type.manual },
      ]
    : [];

  const radarData = kazanimStats?.data?.by_subject?.slice(0, 6).map((item: any) => ({
    subject: item.ders,
    value: item.count,
  })) || [];

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        İstatistikler
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Sistem genelindeki kazanım ve etkinlik istatistiklerini görüntüleyin.
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Toplam Kazanım"
            value={kazanimStats?.data?.total || 0}
            icon={<SchoolIcon />}
            color="#667eea"
            subtitle="Maarif Model"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Toplam Etkinlik"
            value={activityStats?.data?.total || 0}
            icon={<ListAltIcon />}
            color="#764ba2"
            subtitle="Oluşturulan"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="AI Üretim Oranı"
            value={
              activityStats?.data?.total
                ? `${Math.round(
                    (activityStats.data.generation_type.ai_generated /
                      activityStats.data.total) *
                      100
                  )}%`
                : '0%'
            }
            icon={<AutoAwesomeIcon />}
            color="#f59e0b"
            subtitle="Yapay Zeka"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Ortalama Süre"
            value="30"
            icon={<TrendingUpIcon />}
            color="#10b981"
            subtitle="Dakika"
          />
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* Age Group Distribution */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Yaş Grubu Dağılımı (Kazanımlar)
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={kazanimStats?.data?.by_age_group || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="yas_grubu" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#667eea" name="Kazanım Sayısı" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Activity Generation Type */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Etkinlik Oluşturma Tipi
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Subject Distribution Radar */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Ders Dağılımı (Radar)
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis />
                <Radar
                  name="Kazanım Sayısı"
                  dataKey="value"
                  stroke="#667eea"
                  fill="#667eea"
                  fillOpacity={0.6}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Activity Field Distribution */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Etkinlik Alan Dağılımı
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart
                data={activityStats?.data?.by_field || []}
                layout="horizontal"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="alan_adi" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#764ba2" name="Etkinlik Sayısı" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Top Subjects */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              En Çok Kazanım İçeren Dersler
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={kazanimStats?.data?.by_subject?.slice(0, 10) || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ders" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" name="Kazanım Sayısı">
                  {(kazanimStats?.data?.by_subject?.slice(0, 10) || []).map(
                    (entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    )
                  )}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Summary Table */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Özet Tablo
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Kazanım Detayları
                </Typography>
                <Box sx={{ pl: 2 }}>
                  {kazanimStats?.data?.by_age_group?.map((item: any) => (
                    <Box key={item.yas_grubu} display="flex" justifyContent="space-between" py={0.5}>
                      <Typography variant="body2">{item.yas_grubu} ay:</Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {item.count} kazanım
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Etkinlik Detayları
                </Typography>
                <Box sx={{ pl: 2 }}>
                  <Box display="flex" justifyContent="space-between" py={0.5}>
                    <Typography variant="body2">AI ile Oluşturulan:</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {activityStats?.data?.generation_type?.ai_generated || 0}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" py={0.5}>
                    <Typography variant="body2">Manuel Oluşturulan:</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {activityStats?.data?.generation_type?.manual || 0}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" py={0.5}>
                    <Typography variant="body2">Toplam:</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {activityStats?.data?.total || 0}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Statistics;