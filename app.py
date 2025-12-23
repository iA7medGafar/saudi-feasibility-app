import streamlit as st
from google import genai
import pandas as pd
import time
from docx import Document
from io import BytesIO
import requests
from streamlit_lottie import st_lottie
import json
import os
from datetime import datetime

# ==============================================================================
# 1. إعدادات الصفحة
# ==============================================================================
st.set_page_config(page_title="Jadwa AI | جدوى", page_icon="🚀", layout="wide")

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# تحميل أنيميشنز (روبوت، ومال، وصاروخ)
lottie_robot = load_lottieurl("https://lottie.host/5b632675-5735-4d37-8898-33306db02b70/3k8l9z6j7a.json") # روبوت عصري
lottie_processing = load_lottieurl("https://lottie.host/98c2e061-0027-4c3e-b762-12711827453d/k1Y5g1o5mF.json") # تحليل بيانات

# ==============================================================================
# 2. حقن CSS (السر في التصميم والجمال) 🎨
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    /* 1. الخلفية المتدرجة (Gradient Background) */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        font-family: 'Cairo', sans-serif;
    }

    /* 2. النصوص والخطوط */
    h1, h2, h3, h4, p, div, span, label {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        color: white !important;
    }

    /* 3. البطاقات الزجاجية (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* 4. حقول الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00d2ff !important;
        box-shadow: 0 0 10px #00d2ff;
    }

    /* 5. الأزرار (Neon Buttons) */
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 18px;
        font-weight: 900;
        border-radius: 50px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 210, 255, 0.6);
    }

    /* 6. بطاقات SWOT الملونة */
    .swot-box {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        font-weight: bold;
        color: white;
        transition: transform 0.2s;
    }
    .swot-box:hover { transform: scale(1.02); }
    .s-green { background: linear-gradient(45deg, #11998e, #38ef7d); }
    .w-red { background: linear-gradient(45deg, #cb2d3e, #ef473a); }
    .o-blue { background: linear-gradient(45deg, #2980b9, #6dd5fa); }
    .t-yellow { background: linear-gradient(45deg, #f7971e, #ffd200); color: black !important; }

    /* إخفاء القوائم */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. الهيدر (Hero Section)
# ==============================================================================

# تقسيم الشاشة: نص يمين، وأنيميشن يسار
col_hero1, col_hero2 = st.columns([2, 1])

with col_hero1:
    st.markdown("<h1 style='font-size: 60px; margin-bottom: 0;'>🚀 منصة جدوى</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #00d2ff !important;'>مستشارك الذكي لتحليل المشاريع</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; opacity: 0.8;'>حول فكرتك إلى دراسة جدوى احترافية في ثوانٍ باستخدام الذكاء الاصطناعي.. مجاناً وبدون تعقيد.</p>", unsafe_allow_html=True)

with col_hero2:
    if lottie_robot:
        st_lottie(lottie_robot, height=250, key="hero_anim")

# ==============================================================================
# 4. منطقة الإدخال (داخل كارد زجاجي)
# ==============================================================================
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("#### 💡 ابدأ رحلتك هنا", unsafe_allow_html=True)

col_in1, col_in2, col_in3 = st.columns([1, 1, 1])
with col_in1:
    project_type = st.text_input("اسم المشروع", placeholder="مثال: مغسلة سيارات متنقلة")
with col_in2:
    city = st.selectbox("المدينة", ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "دبي", "أخرى"])
with col_in3:
    capital = st.number_input("رأس المال (ريال)", value=50000, step=5000)

details = st.text_area("تفاصيل إضافية (اختياري)", placeholder="اشرح فكرتك أكثر لنعطيك نتائج أدق...")

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("✨ ابدأ التحليل السحري")
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 5. المنطق والذكاء الاصطناعي
# ==============================================================================
if generate_btn:
    # التحقق من المفتاح
    try:
        GEMINI_KEY = st.secrets["GEMINI_KEY"]
    except:
        st.error("⚠️ الرجاء وضع مفتاح API في الإعدادات")
        st.stop()

    if not project_type:
        st.warning("⚠️ الرجاء كتابة اسم المشروع")
    else:
        # أنيميشن التحميل
        with st.container():
            col_load1, col_load2, col_load3 = st.columns([1,2,1])
            with col_load2:
                if lottie_processing:
                    st_lottie(lottie_processing, height=150, key="loading")
                st.markdown("<h4 style='text-align: center;'>جاري استشارة الخبراء الرقميين...</h4>", unsafe_allow_html=True)

        try:
            client = genai.Client(api_key=GEMINI_KEY)
            
            # نفس المنطق الموفر (طلب واحد JSON)
            prompt = (
                f"أنت خبير اقتصادي ومستشار أعمال. حلل مشروع {project_type} في {city} برأس مال {capital}. "
                "المطلوب: إرجاع النتيجة بصيغة JSON Valid فقط (بدون ```json). "
                "الهيكل:\n"
                "{\n"
                '  "summary": "ملخص تنفيذي جذاب...",\n'
                '  "swot": {"s": "...", "w": "...", "o": "...", "t": "..."},\n'
                '  "financials": {"years": ["2025", "2026", "2027"], "revenue": [10, 20, 30], "profit": [1, 5, 10]},\n'
                '  "plan": "خطة العمل..."\n'
                "}"
            )

            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            # إصلاح بسيط في حال جاء النص فيه شوائب
            if "{" not in clean_json: raise Exception("Invalid JSON")
            
            data = json.loads(clean_json)
            
            # استخراج البيانات
            summary = data.get("summary", "")
            swot = data.get("swot", {})
            fin = data.get("financials", {})
            plan = data.get("plan", "")

            # عرض النتائج في شكل Tabs أنيقة
            st.markdown("---")
            st.markdown("## 📊 تقرير الجدوى الشامل")
            
            tab1, tab2, tab3, tab4 = st.tabs(["📄 الملخص", "💎 التحليل الرباعي", "💰 الأرقام", "⚙️ الخطة"])
            
            with tab1:
                st.markdown(f"<div class='glass-card'>{summary}</div>", unsafe_allow_html=True)
            
            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"<div class='swot-box s-green'>💪 القوة: {swot.get('s')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='swot-box w-red'>⚠️ الضعف: {swot.get('w')}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='swot-box o-blue'>🌟 الفرص: {swot.get('o')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='swot-box t-yellow'>🛡️ التهديدات: {swot.get('t')}</div>", unsafe_allow_html=True)

            with tab3:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                df = pd.DataFrame({
                    "السنة": fin.get("years", []),
                    "الأرباح": fin.get("profit", []),
                    "الإيرادات": fin.get("revenue", [])
                })
                st.bar_chart(df.set_index("السنة"))
                
                # عرض الأرقام الكبيرة
                profit = fin.get("profit", [0])[-1]
                st.metric("الأرباح المتوقعة (السنة الثالثة)", f"{profit:,} SAR", "نظرة مستقبلية")
                st.markdown("</div>", unsafe_allow_html=True)

            with tab4:
                 st.markdown(f"<div class='glass-card'>{plan}</div>", unsafe_allow_html=True)

            # زر التحميل
            doc = Document()
            doc.add_heading(f'دراسة جدوى: {project_type}', 0)
            doc.add_paragraph(summary)
            doc.add_heading('الخطة', 1)
            doc.add_paragraph(plan)
            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 تحميل الملف (Word)",
                data=buf,
                file_name="Jadwa_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
            st.balloons()

        except Exception as e:
            if "429" in str(e):
                st.warning("🚦 النظام مشغول قليلاً، حاول مرة أخرى بعد 10 ثوانٍ.")
            else:
                st.error(f"حدث خطأ: {e}")
