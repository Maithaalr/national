
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f5f8fc;
    }
    .metric-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    .section-header {
        font-size: 20px;
        color: #1e3d59;
        margin-top: 20px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

col_logo, col_upload = st.columns([1, 3])
with col_logo:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=180)
    except:
        st.warning("الشعار غير متوفر!")

with col_upload:
    st.markdown("<div class='section-header'>يرجى تحميل بيانات الموظفين</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    excluded_departments = ['HC.نادي عجمان للفروسية', 'PD.الشرطة المحلية لإمارة عجمان', 'RC.الديوان الأميري']
    if 'الدائرة' in df.columns:
        df = df[~df['الدائرة'].isin(excluded_departments)]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["نظرة عامة", "تحليلات بصرية", "البيانات المفقودة", "عرض البيانات", "تحليل التوثيق"])

    with tab5:
        st.markdown("### تحليل اكتمال بيانات التوثيق للمؤسسات غير المستثناة")

        excluded_institutions = [
            "جامعة الامارات", "كلية التقنية العيا -الشارقة", "كلية التقنية العليا", "كليات التقنية",
            "كليات التقنية العيا", "كليات التقنية العليا", "كليات التقنية العليا-الشارقة",
            "كليات التقية العليا", "كلية التقنيات العليا", "كليات التقنية العليا - الشارقة", 
            "كلية تقنيات العليا دبي"
        ]

        allowed_levels = ['ماجستير', 'دكتوراه', 'بكالوريوس', 'إنجاز', 'دبلوم', 'دبلوم عالي']

        df['المؤسسة التعليمية'] = df['المؤسسة التعليمية'].astype(str).str.strip()
        df['المستوى التعليمي'] = df['المستوى التعليمي'].astype(str).str.strip()

        to_check_df = df[
            (~df['المؤسسة التعليمية'].isin(excluded_institutions)) &
            (df['المستوى التعليمي'].isin(allowed_levels))
        ].copy()

        fields_to_check = ['رقم المستند', 'رقم التحقق', 'رقم التصديق']
        to_check_df['مكتمل؟'] = to_check_df[fields_to_check].notnull().all(axis=1)

        completed = to_check_df[to_check_df['مكتمل؟']]
        missing = to_check_df[~to_check_df['مكتمل؟']]

        total = len(to_check_df)
        if total > 0:
            st.success(f"✅ عدد الموظفين الذين لديهم بيانات مكتملة: {len(completed)} ({round(len(completed)/total*100, 1)}%)")
            st.warning(f"⚠️ عدد الموظفين الذين لديهم بيانات ناقصة: {len(missing)} ({round(len(missing)/total*100, 1)}%)")
        else:
            st.info("لا توجد سجلات تنطبق عليها الشروط.")

        with st.expander("عرض الموظفين الذين بياناتهم مكتملة"):
            st.dataframe(completed)

        with st.expander("عرض الموظفين الذين لديهم نقص في الحقول"):
            st.dataframe(missing)
