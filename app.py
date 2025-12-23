import streamlit as st
import google.generativeai as genai  # المكتبة المستقرة
import pandas as pd
import time
import requests
from streamlit_lottie import st_lottie
import json
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
import random

# ==============================================================================
# 1. إعدادات النظام والتصميم
# ==============================================================================
st.set_page_config(
    page_title="Jadwa AI | منصة جدوى",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;700;900&display=swap');

    :root {
        --primary-color: #4facfe;
        --secondary-color: #00f2fe;
        --bg-color: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
        --text-color: #f8fafc;
    }

    * { font-family: 'Tajawal', sans-serif !important; }
    
    .stApp {
        background-color: var(--bg-color);
        background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                          radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                          radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: var(--text-color);
    }

    h1, h2, h3, h4, p, span, div, label { direction: rtl; text-align: right; color: var(--text-color) !important; }

    .glass-container {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        margin-bottom: 25px;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: #0f172a !important;
        font-weight: 900 !important;
        border: none;
        border-radius: 50px;
        padding: 15px 40px;
        font-size: 1.2rem;
        width: 100%;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover { transform: scale(1.02); }

    .swot-card { padding: 20px; border-radius: 16px; height: 100%; border: 1px solid rgba(255,255,255,0.1); text-align: right; }
    .swot-s { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05)); border-left: 5px solid #10b981; }
    .swot-w { background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05)); border-left: 5px solid #ef4444; }
    .swot-o { background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05)); border-left: 5px solid #3b82f6; }
    .swot-t { background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05)); border-left: 5px solid #f59e0b; }

    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. وظائف المساعدة (المكتبة المستقرة)
# ==============================================================================

@st.cache_data
def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code != 200: return None
        return r.json()
    except: return None

def configure_gemini():
    try:
        api_key = st.secrets["GEMINI_KEY"]
        genai.configure(api_key=api_key)
        return True
    except:
        return False

def generate_smart_content(prompt):
    """
    استخدام المكتبة المستقرة مع موديل 1.5 فلاش
    """
    # قائمة الموديلات الآمنة
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # إذا فشل فلاش، جرب برو
        try:
            time.sleep(2)
            model_backup = genai.GenerativeModel('gemini-pro')
            response = model_backup.generate_content(prompt)
            return response.text
        except:
            raise e

def create_professional_doc(data):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)

    title = doc.add_heading(f"دراسة جدوى: {data.get('project_name', 'مشروع')}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def add_arabic_paragraph(text, style='Normal'):
        p = doc.add_paragraph(text, style=style)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.bidi = True

    add_arabic_paragraph(data.get('summary', ''))
    
    doc.add_heading('تحليل SWOT', level=1).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    swot = data.get('swot', {})
    add_arabic_paragraph(f"القوة: {swot.get('s')}", 'List Bullet')
    add_arabic_paragraph(f"الضعف: {swot.get('w')}", 'List Bullet')
    add_arabic_paragraph(f"الفرص: {swot.get('o')}", 'List Bullet')
    add_arabic_paragraph(f"التهديدات: {swot.get('t')}", 'List Bullet')

    doc.add_heading('خطة العمل', level=1).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_arabic_paragraph(data.get('plan', ''))

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==============================================================================
# 3. واجهة المستخدم
# ==============================================================================

lottie_main = load_lottie("https://lottie.host/5b632675-5735-4d37-8898-33306db02b70/3k8l9z6j7a.json")
lottie_loading = load_lottie("https://lottie.host/98c2e061-0027-4c3e-b762-12711827453d/k1Y5g1o5mF.json")

c1, c2 = st.columns([0.7, 0.3])
with c1:
    st.markdown("<h1 style='font-size: 3.5rem; margin-bottom: 0;'>💎 منصة جدوى</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; opacity: 0.8;'>الجيل القادم من دراسات الجدوى المدعومة بالذكاء الاصطناعي.</p>", unsafe_allow_html=True)
with c2:
    if lottie_main: st_lottie(lottie_main, height=200, key="main_anim")

st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
col_input1, col_input2 = st.columns(2)
with col_input1:
    project_name = st.text_input("💡 اسم المشروع", placeholder="مثال: محمصة قهوة مختصة")
    capital = st.number_input("💰 رأس المال (SAR)", value=100000, step=10000, format="%d")
with col_input2:
    city = st.selectbox("📍 المدينة المستهدفة", ["الرياض", "جدة", "الدمام", "مكة المكرمة", "المدينة المنورة", "الخبر", "أخرى"])
    details = st.text_area("📝 تفاصيل إضافية", placeholder="ما الذي يميز مشروعك؟")

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("🚀 بدء التحليل الذكي")
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 4. المحرك
# ==============================================================================

if analyze_btn:
    if not configure_gemini():
        st.error("⚠️ مفتاح API غير موجود في Secrets.")
    elif not project_name:
        st.warning("⚠️ يرجى إدخال اسم المشروع.")
    else:
        status_container = st.status("جاري الاتصال بالمستشار الذكي...", expanded=True)
        
        try:
            status_container.write("🔍 جاري تحليل السوق باستخدام Gemini 1.5 Flash...")
            if lottie_loading: 
                with st.columns([1,2,1])[1]: st_lottie(lottie_loading, height=120, key="proc")
            
            prompt = f"""
            أنت خبير اقتصادي. مشروع "{project_name}" في "{city}" برأس مال {capital} ريال. التفاصيل: {details}
            
            مهم جداً: أخرج النتيجة بصيغة JSON فقط (Valid JSON). لا تكتب ```json.
            الهيكل المطلوب:
            {{
                "project_name": "{project_name}",
                "summary": "ملخص تنفيذي لا يقل عن 5 أسطر",
                "swot": {{ "s": "نقطة قوة", "w": "نقطة ضعف", "o": "فرصة", "t": "تهديد" }},
                "financials": {{
                    "years": ["2025", "2026", "2027"],
                    "revenue": [150000, 250000, 400000],
                    "profit": [20000, 60000, 120000]
                }},
                "plan": "خطة عمل مفصلة"
            }}
            """

            # استخدام الدالة المستقرة
            raw_response = generate_smart_content(prompt)
            
            status_container.write("📊 معالجة البيانات وبناء التقرير...")
            
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            # تصحيح سريع إذا بدأ النص بغير قوس
            if not clean_json.startswith("{"):
                 clean_json = clean_json[clean_json.find("{"):clean_json.rfind("}")+1]

            data = json.loads(clean_json)

            status_container.update(label="✅ تم التحليل بنجاح!", state="complete", expanded=False)
            
            st.markdown("---")
            
            tab_overview, tab_swot, tab_finance, tab_plan = st.tabs(["📄 نظرة عامة", "⚖️ SWOT", "📈 المالية", "⚙️ الخطة"])

            with tab_overview:
                st.markdown(f"<div class='glass-container'><h3>الملخص التنفيذي</h3><p>{data.get('summary','')}</p></div>", unsafe_allow_html=True)

            with tab_swot:
                swot = data.get('swot', {})
                c_s, c_w, c_o, c_t = st.columns(4)
                with c_s: st.markdown(f"<div class='swot-card swot-s'><h4>💪 القوة</h4><p>{swot.get('s')}</p></div>", unsafe_allow_html=True)
                with c_w: st.markdown(f"<div class='swot-card swot-w'><h4>⚠️ الضعف</h4><p>{swot.get('w')}</p></div>", unsafe_allow_html=True)
                with c_o: st.markdown(f"<div class='swot-card swot-o'><h4>🌟 الفرص</h4><p>{swot.get('o')}</p></div>", unsafe_allow_html=True)
                with c_t: st.markdown(f"<div class='swot-card swot-t'><h4>🛡️ التهديدات</h4><p>{swot.get('t')}</p></div>", unsafe_allow_html=True)

            with tab_finance:
                fin = data.get('financials', {})
                col_ch, col_me = st.columns([2, 1])
                with col_ch:
                    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
                    df = pd.DataFrame({"السنة": fin.get("years", []), "الإيرادات": fin.get("revenue", []), "الأرباح": fin.get("profit", [])})
                    st.bar_chart(df.set_index("السنة"), color=["#4facfe", "#00f2fe"])
                    st.markdown("</div>", unsafe_allow_html=True)
                with col_me:
                    tot_prof = sum(fin.get("profit", []))
                    roi = round((tot_prof / capital) * 100, 1) if capital else 0
                    st.markdown(f"<div class='glass-container' style='text-align:center;'><h4>إجمالي الربح</h4><h2 style='color:#10b981;'>{tot_prof:,}</h2><hr><h4>ROI</h4><h2 style='color:#4facfe;'>{roi}%</h2></div>", unsafe_allow_html=True)

            with tab_plan:
                st.markdown(f"<div class='glass-container'><h3>الخطة</h3><p>{data.get('plan','')}</p></div>", unsafe_allow_html=True)

            word_file = create_professional_doc(data)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("📥 تحميل الدراسة (Word)", word_file, f"Jadwa_{project_name}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            st.balloons()

        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
