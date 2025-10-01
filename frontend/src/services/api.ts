import axios from 'axios';
import { API_BASE_URL } from '../config/api.config';

// Export API_BASE_URL for direct usage in components
export { API_BASE_URL };

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Kazanim APIs
export const kazanimApi = {
  list: (params?: any) => api.get('/kazanimlar/', { params }).then(res => res.data),
  getById: (id: number) => api.get(`/kazanimlar/${id}`).then(res => res.data),
  create: (data: any) => api.post('/kazanimlar/', data).then(res => res.data),
  update: (id: number, data: any) => api.put(`/kazanimlar/${id}`, data).then(res => res.data),
  delete: (id: number) => api.delete(`/kazanimlar/${id}`).then(res => res.data),
  getStats: () => api.get('/kazanimlar/stats/overview').then(res => res.data),
  getAgeGroups: () => api.get('/kazanimlar/options/age-groups').then(res => res.data),
  getSubjects: (ageGroup?: string) =>
    api.get('/kazanimlar/options/subjects', { params: { yas_grubu: ageGroup } }).then(res => res.data),
  searchKazanimlar: (params: any) => api.get('/kazanimlar/', { params }).then(res => res.data),
};

// Activity APIs
export const activityApi = {
  list: (params?: any) => {
    // Clean up empty string parameters
    const cleanParams = Object.entries(params || {}).reduce((acc, [key, value]) => {
      if (value !== '' && value !== undefined && value !== null) {
        acc[key] = value;
      }
      return acc;
    }, {} as any);
    return api.get('/etkinlikler/', { params: cleanParams }).then(res => res.data);
  },
  getById: (id: number) => api.get(`/etkinlikler/${id}`).then(res => res.data),
  create: (data: any) => api.post('/etkinlikler/', data).then(res => res.data),
  update: (id: number, data: any) => api.put(`/etkinlikler/${id}`, data).then(res => res.data),
  delete: (id: number) => api.delete(`/etkinlikler/${id}`).then(res => res.data),
  generate: (kazanimIds: number[], customPrompt?: string, curriculumData?: any) => {
    console.log('API Service - generate called with:', {
      kazanimIds,
      customPromptLength: customPrompt?.length,
      curriculumData
    });

    const payload: any = { kazanim_ids: kazanimIds, custom_prompt: customPrompt };

    if (curriculumData) {
      console.log('API Service - Adding curriculum data to payload');
      payload.kavramsal_beceriler = curriculumData.kavramsal_beceriler || [];
      payload.egilimler = curriculumData.egilimler || [];
      payload.sosyal_duygusal = curriculumData.sosyal_duygusal || [];
      payload.degerler = curriculumData.degerler || [];
      payload.okuryazarlik = curriculumData.okuryazarlik || [];
    } else {
      console.log('API Service - No curriculum data provided');
    }

    console.log('API Service - Final payload to backend:', payload);
    return api.post('/etkinlikler/generate', payload);
  },
  getStats: () => api.get('/etkinlikler/stats/overview').then(res => res.data),
};

// Curriculum APIs
export const curriculumApi = {
  // Bütünleşik Bileşenler
  getButunlesikBilesenler: () => api.get('/curriculum/butunlesik-bilesenler').then(res => res.data),

  // Değerler
  getDegerler: () => api.get('/curriculum/degerler').then(res => res.data),
  getDegerlerGrouped: () => api.get('/curriculum/degerler/grouped').then(res => res.data),

  // Eğilimler
  getEgilimler: () => api.get('/curriculum/egilimler').then(res => res.data),
  getEgilimlerGrouped: () => api.get('/curriculum/egilimler/grouped').then(res => res.data),

  // Kavramsal Beceriler
  getKavramsalBeceriler: () => api.get('/curriculum/kavramsal-beceriler').then(res => res.data),
  getKavramsalBecerilerGrouped: () => api.get('/curriculum/kavramsal-beceriler/grouped').then(res => res.data),

  // Süreç Bileşenleri
  getSurecBilesenleri: () => api.get('/curriculum/surec-bilesenleri').then(res => res.data),
  getSurecBilesenleriGrouped: () => api.get('/curriculum/surec-bilesenleri/grouped').then(res => res.data),
};

// Daily Plan APIs
export const dailyPlanApi = {
  list: (params?: any) => api.get('/gunluk-planlar/', { params }).then(res => res.data),
  getById: (id: number) => api.get(`/gunluk-planlar/${id}`).then(res => res.data),
  create: (data: any) => api.post('/gunluk-planlar/', data).then(res => res.data),
  createWithAI: (data: any) => {
    console.log('API: Calling POST /gunluk-planlar/generate-with-ai with:', data);
    return api.post('/gunluk-planlar/generate-with-ai', data).then(res => {
      console.log('API: Response from /generate-with-ai:', res.data);
      return res.data;
    });
  },
  update: (id: number, data: any) => api.put(`/gunluk-planlar/${id}`, data).then(res => res.data),
  delete: (id: number) => api.delete(`/gunluk-planlar/${id}`).then(res => res.data),
  exportToDocx: (id: number) => api.get(`/gunluk-planlar/${id}/export/docx`, { responseType: 'blob' }),
};

// Monthly Plan APIs
export const monthlyPlanApi = {
  list: (params?: any) => api.get('/aylik-planlar/', { params }).then(res => res.data),
  getById: (id: number) => api.get(`/aylik-planlar/${id}`).then(res => res.data),
  generateMonthlyPlan: (data: {
    yas_grubu: string;
    ay: string;
    kazanim_ids: number[];
    curriculum_ids?: number[];
    custom_instructions?: string;
  }) => {
    console.log('API: Generating monthly plan with:', data);
    return api.post('/aylik-planlar/generate', data).then(res => res.data);
  },
  update: (id: number, data: any) => api.put(`/aylik-planlar/${id}`, data).then(res => res.data),
  delete: (id: number) => {
    console.log('monthlyPlanApi.delete called with id:', id);
    return api.delete(`/aylik-planlar/${id}`).then(res => {
      console.log('Delete response:', res);
      return res.data;
    }).catch(err => {
      console.error('Delete API error:', err);
      throw err;
    });
  },
  exportMonthlyPlanDocx: (id: number) =>
    api.get(`/aylik-planlar/${id}/export-docx`, { responseType: 'blob' }).then(res => res.data),
};

export default api;