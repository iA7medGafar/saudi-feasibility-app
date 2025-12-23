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
# 1. إعدادات الصفحة والتصميم
# ==============================================================================
st.set_page_config(page_title="Jadwa Pro | جدوى برو", page_icon="💎", layout="wide")

# دالة لتحميل الأنيميشن
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_loading = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json")
lottie_money = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_tij7s3.json")

# CSS لتصميم لوحة تحكم وتصحيح الألوان
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');

    /* الإعدادات العامة */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Tajawal', sans-serif;
    }
    
    h1, h2, h3, p, div, span {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* بطاقات SWOT */
    .swot-card {
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
        height: 100%;
    }
    .strength { background-color: #2ecc71; }
    .weakness { background-color: #e74c3c; }
    .opportunity { background-color: #3498db; }
    .threat { background-color: #f1c40f; color: black !important; }

    /* تحسين الجداول */
    .dataframe {
        direction: rtl;
        width: 100%; 
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. نظام حفظ البيانات (Data Collection) 📊
# ==============================================================================
DATA_FILE = "users_data.csv"

def save_user_data(project, city, capital):
    """حفظ بيانات المشروع في ملف CSV محلي"""
    new_data = pd.DataFrame({
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
        "Project": [project],
        "City": [city],
        "Capital": [capital]
    })
    
    if not os.path.exists(DATA_FILE):
        new_data.to_csv(DATA_FILE, index=False)
    else:
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)

# ==============================================================================
# 3. الواجهة الجانبية (Sidebar)
# ==============================================================================
with st.sidebar:
    st.title("💎 جدوى برو")
    st.markdown("---")
    
    project_type = st.text_input("💡 فكرة المشروع", "متجر عطور إلكتروني")
    city = st.selectbox("📍 المدينة", ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "القصيم", "دبي", "أخرى"])
    capital = st.number_input("💰 رأس المال (ريال)", value=50000, step=5000)
    details = st.text_area("📝 تفاصيل إضافية")
    
    st.markdown("---")
    generate_btn = st.button("🚀 تحليل شامل (AI)")
    
    # منطقة الادمن (لتحميل بيانات العملاء)
    with st.expander("🔒 منطقة الإدارة"):
        admin_pass = st.text_input("كود المدير", type="password")
        if admin_pass == "1234": # يمكنك تغيير كلمة السر
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE)
                st.dataframe(df)
                st.download_button("📥 تحميل بيانات العملاء", df.to_csv().encode('utf-8'), "clients.csv")
            else:
                st.write("لا توجد بيانات بعد.")

# ==============================================================================
# 4. المنطق الرئيسي (Main Logic)
# ==============================================================================

# الهيدر
col1, col2 = st.columns([1, 5])
with col2:
    st.title(f"تحليل مشروع: {project_type}")
    st.caption(f"دراسة جدوى ذكية للسوق في {city}")

if generate_btn:
    # جلب المفتاح من الأسرار
    try:
        GEMINI_KEY = st.secrets["GEMINI_KEY"]
    except:
        st.error("⚠️ الرجاء وضع مفتاح API في الـ Secrets")
        st.stop()

    # حفظ البيانات (تجميع الـ Leads)
    save_user_data(project_type, city, capital)

    # عرض التحميل
    with st.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st_lottie(lottie_loading, height=200)
            st.info("جاري استخراج البيانات المالية وتحليل السوق...")

    try:
        client = genai.Client(api_key=GEMINI_KEY)
        
        # ---------------------------------------------------------
        # الطلب الأول: الدراسة النصية + تحليل SWOT
        # ---------------------------------------------------------
        prompt_text = (
            f"اكتب دراسة جدوى لمشروع {project_type} في {city} برأس مال {capital}. "
            "التنسيق المطلوب:\n"
            "1. ابدأ بملخص تنفيذي.\n"
            "2. ثم اكتب فاصل '###SWOT###'.\n"
            "3. ثم اكتب تحليل SWOT في 4 نقاط قصيرة جداً (نقطة لكل سطر): القوة، الضعف، الفرص، التهديدات.\n"
            "4. ثم اكتب فاصل '###PLAN###'.\n"
            "5. ثم اكتب الخطة التشغيلية والتسويقية."
        )
        
        response_text = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_text)
        full_text = response_text.text
        
        # معالجة النصوص وتقسيمها
        parts = full_text.split("###SWOT###")
        summary_section = parts[0]
        remaining = parts[1] if len(parts) > 1 else ""
        
        parts2 = remaining.split("###PLAN###")
        swot_section = parts2[0] if len(parts2) > 0 else ""
        plan_section = parts2[1] if len(parts2) > 1 else ""

        # ---------------------------------------------------------
        # الطلب الثاني: البيانات المالية (JSON) - لعمل شارت حقيقي
        # ---------------------------------------------------------
        prompt_json = (
            f"لمشروع {project_type} برأس مال {capital}. "
            "أعطني توقعات مالية لـ 3 سنوات بصيغة JSON فقط. "
            "الشكل المطلوب: "
            '{ "years": ["2025", "2026", "2027"], "revenue": [100, 200, 300], "profit": [10, 50, 90] } '
            "لا تكتب أي نص آخر غير كود JSON."
        )
        response_json = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_json)
        
        # تنظيف الـ JSON
        json_str = response_json.text.replace("```json", "").replace("```", "").strip()
        financial_data = json.loads(json_str)

        # =========================================================
        # عرض النتائج (Dashboard)
        # =========================================================
        st.success("✅ تم الانتهاء من الدراسة!")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📄 الملخص", "⚖️ تحليل SWOT", "💰 الماليات", "⚙️ الخطة"])

        with tab1:
            st.markdown(summary_section)

        with tab2:
            st.subheader("تحليل نقاط القوة والضعف")
            # محاولة بسيطة لاستخراج نقاط SWOT من النص
            swot_lines = [line for line in swot_section.split('\n') if line.strip()]
            
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f'<div class="swot-card strength"><h4>💪 نقاط القوة</h4><p>{swot_lines[0] if len(swot_lines)>0 else "مشروع واعد"}</p></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="swot-card weakness"><h4>⚠️ نقاط الضعف</h4><p>{swot_lines[1] if len(swot_lines)>1 else "يحتاج تسويق قوي"}</p></div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div class="swot-card opportunity"><h4>🌟 الفرص</h4><p>{swot_lines[2] if len(swot_lines)>2 else "نمو السوق السعودي"}</p></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="swot-card threat"><h4>🛡️ التهديدات</h4><p>{swot_lines[3] if len(swot_lines)>3 else "المنافسة الشديدة"}</p></div>', unsafe_allow_html=True)

        with tab3:
            col_fin1, col_fin2 = st.columns([2, 1])
            with col_fin1:
                # رسم بياني حقيقي من بيانات Gemini
                chart_df = pd.DataFrame({
                    "السنة": financial_data.get("years", ["1", "2", "3"]),
                    "الإيرادات": financial_data.get("revenue", [0,0,0]),
                    "صافي الربح": financial_data.get("profit", [0,0,0])
                })
                st.bar_chart(chart_df.set_index("السنة"))
            
            with col_fin2:
                st_lottie(lottie_money, height=150)
                total_profit = sum(financial_data.get("profit", []))
                st.metric("إجمالي الربح (3 سنوات)", f"{total_profit:,} SAR")
                roi = round((total_profit / capital) * 100, 1)
                st.metric("العائد على الاستثمار ROI", f"{roi}%")

        with tab4:
            st.markdown(plan_section)

        # ---------------------------------------------------------
        # إنشاء ملف Word
        # ---------------------------------------------------------
        doc = Document()
        doc.add_heading(f'دراسة جدوى: {project_type}', 0)
        doc.add_heading('الملخص التنفيذي', level=1)
        doc.add_paragraph(summary_section)
        doc.add_heading('تحليل SWOT', level=1)
        doc.add_paragraph(swot_section)
        doc.add_heading('الخطة التشغيلية', level=1)
        doc.add_paragraph(plan_section)
        
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        st.markdown("---")
        st.download_button(
            label="📥 تحميل الدراسة كاملة (Word Docx)",
            data=buffer,
            file_name=f"Jadwa_{project_type}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء التحليل: {e}")
