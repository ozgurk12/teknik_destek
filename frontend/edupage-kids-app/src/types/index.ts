export interface Kazanim {
  id: number;
  yas_grubu: string;
  ders: string;
  alan_becerileri?: string;
  butunlesik_beceriler?: string;
  surec_bilesenleri?: string;
  ogrenme_ciktilari?: string;
  alt_ogrenme_ciktilari?: string;
  created_at: string;
  updated_at?: string;
}

export interface Activity {
  id: number;
  etkinlik_adi: string;
  alan_adi?: string;
  yas_grubu?: string;
  sure?: number;
  uygulama_yeri?: string;
  etkinlik_amaci?: string;
  materyaller?: string;
  uygulama_sureci?: string;
  giris_bolumu?: string;
  gelisme_bolumu?: string;
  yansima_cemberi?: string;
  sonuc_bolumu?: string;
  uyarlama?: string;
  farklilastirma_kapsayicilik?: string;
  degerlendirme_program?: string;
  degerlendirme_beceriler?: string;
  degerlendirme_ogrenciler?: string;
  kazanim_idleri?: number[];
  kazanim_metinleri?: string[];
  custom_instructions?: string;
  created_at: string;
  updated_at?: string;
  created_by_id?: string;
  created_by_username?: string;
  created_by_fullname?: string;
  ai_generated: boolean;
  prompt_used?: string;
  model_version?: string;
}

export interface KazanimListResponse {
  total: number;
  items: Kazanim[];
  page: number;
  page_size: number;
}

export interface Statistics {
  total: number;
  by_age_group: Array<{ yas_grubu: string; count: number }>;
  by_subject: Array<{ ders: string; count: number }>;
}

export interface ActivityStatistics {
  total: number;
  generation_type: {
    ai_generated: number;
    manual: number;
  };
  by_field: Array<{ alan_adi: string; count: number }>;
  by_age_group: Array<{ yas_grubu: string; count: number }>;
}