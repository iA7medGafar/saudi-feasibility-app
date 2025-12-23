import streamlit as st
from google import genai
import pandas as pd
import time
from docx import Document
from io import BytesIO
import requests
from streamlit_lottie import st_lottie

# ==============================================================================
# 1. إعدادات الصفحة
# ==============================================================================
st.set_page_config(page_title="منصة جدوى | Jadwa", page_icon="📊", layout="wide")

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# أنيميشن (روبوت ومستندات)
lottie_analyzing = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json")

# ==============================================================================
# 2. التصميم (THEME FIX) - حل مشكلة الألوان
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');

    /* 1. إجبار الخلفية على اللون الداكن */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Tajawal', sans-serif;
    }

    /* 2. تصحيح ألوان النصوص */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #FAFAFA !important;
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* 3. تصميم البطاقات (Cards) بلون رمادي غامق */
    .custom-card {
        background-color: #262730;
        border: 1px solid #3E404D;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }

    /* 4. حقول الإدخال (Inputs) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #0E1117;
        color: white;
        border: 1px solid #4B4B4B;
        border-radius: 8px;
    }

    /* 5. الأزرار */
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF0000);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    
    /* إخفاء القوائم العلوية */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. واجهة المستخدم
# ==============================================================================

# الهيدر
col1, col2 = st.columns([1, 8])
with col2:
    st.markdown("<h1>📊 منصة جدوى الذكية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; opacity: 0.8;'>اصنع دراسة جدوى كاملة لمشروعك في ثوانٍ بالذكاء الاصطناعي</p>", unsafe_allow_html=True)

# المدخلات (داخل كارد)
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    project_type = st.text_input("💡 فكرة المشروع", placeholder="مطعم، تطبيق، ورشة...")
    city = st.selectbox("📍 المدينة", ["الرياض", "جدة", "الدمام", "أخرى"])
with c2:
    capital = st.number_input("💰 رأس المال (ريال)", value=50000, step=1000)
    details = st.text_input("📝 تفاصيل إضافية", placeholder="جمهور مستهدف، موقع مميز...")

st.markdown("<br>", unsafe_allow_html=True)
btn = st.button("🚀 إنشاء الدراسة الآن")
st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 4. المنطق (Logic)
# ==============================================================================
# بدلاً من وضع المفتاح هنا، نجعله يقرأ من خزنة السيرفر
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
except:
    GEMINI_KEY = "ضع_مفتاحك_هنا_فقط_للتجربة_على_جهازك_وليس_للرفع"

if btn:
    if not GEMINI_KEY or "ضع_مفتاح" in GEMINI_KEY:
        st.error("⚠️ ضع مفتاح API")
    else:
        # عرض الأنيميشن
        if lottie_analyzing:
            st_lottie(lottie_analyzing, height=150, key="loading")
        else:
            st.info("جاري التحليل...")

        try:
            client = genai.Client(api_key=GEMINI_KEY)
            
            # الطلب
            prompt = (
                f"اكتب دراسة جدوى لمشروع: {project_type} في {city} برأس مال {capital}. "
                "افصل الأقسام بكلمة '###'. "
                "1. ملخص. 2. مالي. 3. تشغيل وتسويق."
            )
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            txt = response.text
            
            # تقسيم النص
            parts = txt.split("###")
            p1 = parts[0] if len(parts)>0 else txt
            p2 = parts[1] if len(parts)>1 else ""
            p3 = parts[2] if len(parts)>2 else ""

            st.success("✅ تم الانتهاء!")
            
            # التبويبات
            t1, t2, t3 = st.tabs(["نظرة عامة", "المالية", "الخطة"])
            
            with t1:
                st.markdown(p1)
            with t2:
                # رسم بياني
                chart_data = pd.DataFrame({'Year': ['2025', '2026', '2027'], 'Profit': [capital*0.1, capital*0.4, capital*0.8]})
                st.bar_chart(chart_data.set_index('Year'))
                st.markdown(p2)
            with t3:
                st.markdown(p3)

            # ملف الوورد
            doc = Document()
            doc.add_paragraph(txt)
            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)
            
            st.download_button("📥 تحميل الدراسة (Word)", buf, "study.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        except Exception as e:
            st.error(f"خطأ: {e}")