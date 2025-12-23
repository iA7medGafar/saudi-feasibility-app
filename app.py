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

# تحميل الأنيميشن
lottie_robot = load_lottieurl("https://lottie.host/5b632675-5735-4d37-8898-33306db02b70/3k8l9z6j7a.json")
lottie_processing = load_lottieurl("https://lottie.host/98c2e061-0027-4c3e-b762-12711827453d/k1Y5g1o5mF.json")

# ==============================================================================
# 2. تصميم CSS (Glassmorphism & Colors)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    /* خلفية الفضاء */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        font-family: 'Cairo', sans-serif;
    }

    /* النصوص */
    h1, h2, h3, h4, p, div, span, label {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        color: white !important;
    }

    /* الكروت الزجاجية */
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

    /* الحقول */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* الأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        padding: 15px 32px;
        font-size: 18px;
        font-weight: 900;
        border-radius: 50px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover { transform: translateY(-3px); }

    /* ألوان SWOT */
    .swot-box {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        font-weight: bold;
        color: white;
    }
    .s-green { background: linear-gradient(45deg, #11998e, #38ef7d); }
    .w-red { background: linear-gradient(45deg, #cb2d3e, #ef473a); }
    .o-blue { background: linear-gradient(45deg, #2980b9, #6dd5fa); }
    .t-yellow { background: linear-gradient(45deg, #f7971e, #ffd200); color: black !important; }

    #MainMenu {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. الهيدر
# ==============================================================================
col_hero1, col_hero2 = st.columns([2, 1])
with col_hero1:
    st.markdown("<h1 style='font-size: 60px; margin-bottom: 0;'>🚀 منصة جدوى</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #00d2ff !important;'>مستشارك الذكي لتحليل المشاريع</h3>", unsafe_allow_html=True)
with col_hero2:
    if lottie_robot: st_lottie(lottie_robot, height=250, key="hero_anim")

# ==============================================================================
# 4. المدخلات
# ==============================================================================
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])
with c1: project_type = st.text_input("اسم المشروع", placeholder="مطعم، تطبيق...")
with c2: city = st.selectbox("المدينة", ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "دبي", "أخرى"])
with c3: capital = st.number_input("رأس المال (ريال)", value=50000, step=5000)
details = st.text_area("تفاصيل إضافية", placeholder="اشرح الفكرة أكثر...")
st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("✨ ابدأ التحليل السحري")
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 5. المنطق (مع إصلاح الخطأ السابق)
# ==============================================================================
if generate_btn:
    try:
        GEMINI_KEY = st.secrets["GEMINI_KEY"]
    except:
        st.error
