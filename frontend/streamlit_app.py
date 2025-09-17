import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="EduPage Kids - Etkinlik Oluşturucu",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 3rem;
    }
    .activity-card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def fetch_kazanimlar(yas_grubu=None, ders=None, search=None):
    """Fetch learning outcomes from API"""
    params = {}
    if yas_grubu:
        params['yas_grubu'] = yas_grubu
    if ders:
        params['ders'] = ders
    if search:
        params['search'] = search
    params['page_size'] = 100
    
    try:
        response = requests.get(f"{API_BASE_URL}/kazanimlar", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"API bağlantı hatası: {str(e)}")
        return None

def fetch_age_groups():
    """Fetch available age groups"""
    try:
        response = requests.get(f"{API_BASE_URL}/kazanimlar/options/age-groups")
        if response.status_code == 200:
            return response.json()['age_groups']
        return []
    except:
        return []

def fetch_subjects(yas_grubu=None):
    """Fetch available subjects"""
    params = {'yas_grubu': yas_grubu} if yas_grubu else {}
    try:
        response = requests.get(f"{API_BASE_URL}/kazanimlar/options/subjects", params=params)
        if response.status_code == 200:
            return response.json()['subjects']
        return []
    except:
        return []

def generate_activity(kazanim_ids):
    """Generate activity using selected learning outcomes"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/etkinlikler/generate",
            json={"kazanim_ids": kazanim_ids}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Etkinlik oluşturma hatası: {str(e)}")
        return None

def fetch_activities():
    """Fetch existing activities"""
    try:
        response = requests.get(f"{API_BASE_URL}/etkinlikler", params={"page_size": 50})
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def main():
    # Header
    st.markdown('<h1 class="main-header">🎨 EduPage Kids Etkinlik Oluşturucu</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Maarif Model Kazanımlarına Uygun Etkinlik Planlama Sistemi</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Menü")
        page = st.radio(
            "Sayfa Seçin",
            ["🆕 Yeni Etkinlik Oluştur", "📚 Etkinlik Listesi", "📊 İstatistikler"]
        )
    
    if page == "🆕 Yeni Etkinlik Oluştur":
        create_activity_page()
    elif page == "📚 Etkinlik Listesi":
        activity_list_page()
    else:
        statistics_page()

def create_activity_page():
    """Page for creating new activities"""
    st.header("🆕 Yeni Etkinlik Oluştur")
    
    # Step 1: Filter Kazanımlar
    st.subheader("1️⃣ Kazanım Filtrele")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age_groups = fetch_age_groups()
        selected_age = st.selectbox(
            "Yaş Grubu",
            ["Tümü"] + age_groups,
            help="Yaş grubuna göre filtrele"
        )
    
    with col2:
        subjects = fetch_subjects(selected_age if selected_age != "Tümü" else None)
        selected_subject = st.selectbox(
            "Ders/Alan",
            ["Tümü"] + subjects,
            help="Derse göre filtrele"
        )
    
    with col3:
        search_term = st.text_input(
            "Arama",
            placeholder="Kazanım ara...",
            help="Kazanım içeriğinde arama yap"
        )
    
    # Fetch and display kazanımlar
    kazanimlar_data = fetch_kazanimlar(
        yas_grubu=selected_age if selected_age != "Tümü" else None,
        ders=selected_subject if selected_subject != "Tümü" else None,
        search=search_term if search_term else None
    )
    
    if kazanimlar_data:
        st.subheader("2️⃣ Kazanım Seç")
        st.info(f"📚 Toplam {kazanimlar_data['total']} kazanım bulundu")
        
        # Display kazanımlar as checkboxes
        selected_kazanimlar = []
        
        # Create columns for better layout
        for item in kazanimlar_data['items'][:20]:  # Show first 20
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.checkbox("", key=f"kaz_{item['id']}"):
                    selected_kazanimlar.append(item['id'])
            with col2:
                st.markdown(f"""
                <div class="activity-card">
                    <strong>{item['yas_grubu']} - {item['ders']}</strong><br>
                    {item['ogrenme_ciktilari'] if item['ogrenme_ciktilari'] else 'Açıklama yok'}
                </div>
                """, unsafe_allow_html=True)
        
        if selected_kazanimlar:
            st.subheader("3️⃣ Etkinlik Oluştur")
            st.success(f"✅ {len(selected_kazanimlar)} kazanım seçildi")
            
            if st.button("🎨 Etkinlik Oluştur", type="primary", use_container_width=True):
                with st.spinner("⏳ Yapay zeka etkinlik oluşturuyor..."):
                    result = generate_activity(selected_kazanimlar)
                    
                    if result and result['success']:
                        st.balloons()
                        st.markdown('<div class="success-message">✅ Etkinlik başarıyla oluşturuldu!</div>', unsafe_allow_html=True)
                        
                        # Display generated activity
                        activity = result['etkinlik']
                        
                        st.markdown("---")
                        st.header(f"📋 {activity['etkinlik_adi']}")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Alan", activity['alan_adi'])
                        with col2:
                            st.metric("Yaş Grubu", activity['yas_grubu'])
                        with col3:
                            st.metric("Süre", f"{activity['sure']} dk")
                        with col4:
                            st.metric("Yer", activity['uygulama_yeri'])
                        
                        # Activity details in tabs
                        tab1, tab2, tab3, tab4, tab5 = st.tabs([
                            "📌 Amaç & Materyal",
                            "🎯 Uygulama Süreci",
                            "🔄 Uyarlama",
                            "📊 Değerlendirme",
                            "💾 Kaydet"
                        ])
                        
                        with tab1:
                            st.subheader("Etkinliğin Amacı")
                            st.write(activity['etkinlik_amaci'])
                            
                            st.subheader("Materyaller")
                            st.write(activity['materyaller'])
                        
                        with tab2:
                            st.subheader("Uygulama Süreci")
                            st.write(activity['uygulama_sureci'])
                        
                        with tab3:
                            st.subheader("Uyarlama")
                            st.write(activity['uyarlama'])
                            
                            st.subheader("Farklılaştırma ve Kapsayıcılık")
                            st.write(activity['farklilastirma_kapsayicilik'])
                        
                        with tab4:
                            st.subheader("Program Değerlendirmesi")
                            st.write(activity['degerlendirme_program'])
                            
                            st.subheader("Beceriler Değerlendirmesi")
                            st.write(activity['degerlendirme_beceriler'])
                            
                            st.subheader("Öğrenci Değerlendirmesi")
                            st.write(activity['degerlendirme_ogrenciler'])
                        
                        with tab5:
                            st.success("✅ Etkinlik otomatik olarak veritabanına kaydedildi!")
                            
                            # Download as JSON
                            st.download_button(
                                label="📥 JSON Olarak İndir",
                                data=json.dumps(activity, ensure_ascii=False, indent=2),
                                file_name=f"etkinlik_{activity['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    else:
                        st.markdown('<div class="error-message">❌ Etkinlik oluşturulamadı!</div>', unsafe_allow_html=True)
                        if result:
                            st.error(result.get('error', 'Bilinmeyen hata'))

def activity_list_page():
    """Page for listing existing activities"""
    st.header("📚 Mevcut Etkinlikler")
    
    activities = fetch_activities()
    
    if activities:
        st.info(f"📋 Toplam {len(activities)} etkinlik bulundu")
        
        # Display activities
        for activity in activities:
            with st.expander(f"🎨 {activity['etkinlik_adi']}"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Alan", activity['alan_adi'])
                with col2:
                    st.metric("Yaş", activity['yas_grubu'])
                with col3:
                    st.metric("Süre", f"{activity['sure']} dk")
                with col4:
                    ai_badge = "🤖 AI" if activity['ai_generated'] else "✍️ Manuel"
                    st.metric("Oluşturma", ai_badge)
                
                st.subheader("Etkinlik Amacı")
                st.write(activity['etkinlik_amaci'][:300] + "..." if len(activity.get('etkinlik_amaci', '')) > 300 else activity.get('etkinlik_amaci', ''))
                
                st.caption(f"📅 Oluşturulma: {activity['created_at']}")
    else:
        st.warning("Henüz etkinlik bulunmuyor")

def statistics_page():
    """Page for displaying statistics"""
    st.header("📊 İstatistikler")
    
    # Fetch statistics
    try:
        # Kazanım stats
        kaz_response = requests.get(f"{API_BASE_URL}/kazanimlar/stats/overview")
        kaz_stats = kaz_response.json() if kaz_response.status_code == 200 else None
        
        # Activity stats
        act_response = requests.get(f"{API_BASE_URL}/etkinlikler/stats/overview")
        act_stats = act_response.json() if act_response.status_code == 200 else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📚 Kazanım İstatistikleri")
            if kaz_stats:
                st.metric("Toplam Kazanım", kaz_stats['total'])
                
                # Age group distribution
                st.write("**Yaş Grubu Dağılımı:**")
                age_df = pd.DataFrame(kaz_stats['by_age_group'])
                st.bar_chart(age_df.set_index('yas_grubu')['count'])
                
                # Subject distribution
                st.write("**Ders Dağılımı:**")
                subject_df = pd.DataFrame(kaz_stats['by_subject'])
                st.bar_chart(subject_df.set_index('ders')['count'])
        
        with col2:
            st.subheader("🎨 Etkinlik İstatistikleri")
            if act_stats:
                st.metric("Toplam Etkinlik", act_stats['total'])
                
                # Generation type
                st.write("**Oluşturma Tipi:**")
                gen_data = act_stats['generation_type']
                st.metric("AI ile Oluşturulan", gen_data['ai_generated'])
                st.metric("Manuel Oluşturulan", gen_data['manual'])
                
                # Field distribution
                if act_stats['by_field']:
                    st.write("**Alan Dağılımı:**")
                    field_df = pd.DataFrame(act_stats['by_field'])
                    st.bar_chart(field_df.set_index('alan_adi')['count'])
    
    except Exception as e:
        st.error(f"İstatistikler yüklenemedi: {str(e)}")

if __name__ == "__main__":
    main()