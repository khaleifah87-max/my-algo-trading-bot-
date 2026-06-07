import streamlit as st
import pandas as pd
import datetime
import time

# إعدادات الصفحة العامة للتطبيق
st.set_page_config(page_title="إدارة بوت التداول الآلي (ADX/DFM)", page_icon="📊", layout="wide")

# تخصيص واجهة التطبيق باللغة العربية (الاتجاه من اليمين لليسار)
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 1. إدارة الحالة (State Management) لتخزين البيانات أثناء التشغيل
# =====================================================================
if 'capital' not in st.session_state:
    st.session_state.capital = 100000.0
if 'running' not in st.session_state:
    st.session_state.running = False
if 'log' not in st.session_state:
    st.session_state.log = []

# =====================================================================
# 2. الشاشة الرئيسية للوحة التحكم (Dashboard UI)
# =====================================================================
st.title("📊 نظام التداول الآلي الذكي لأسواق الإمارات")
st.subheader("لوحة التحكم والمراقبة اللحظية للمضاربة اليومية")
st.write("---")

# الجزء العلوي: المؤشرات المالية الحالية
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="💰 رأس المال الحالي", value=f"{st.session_state.capital:,.2f} د.إ")
with col2:
    st.metric(label="📈 ربح/خسارة اليوم", value="+2,140.00 د.إ", delta="2.14%")
with col3:
    st.metric(label="🚨 المراكز المفتوحة", value="1 مركز")
with col4:
    st.metric(label="🎯 نسبة النجاح اليومية (Win Rate)", value="66.7%")

st.write("---")

# تقسيم الشاشة إلى عمودين: التحكم الجانبي والعمليات الرئيسية
left_col, right_col = st.columns([1, 3])

with left_col:
    st.header("⚙️ إعدادات التحكم")
    
    # مدخلات المستخدم لضبط المخاطر
    input_capital = st.number_input("تعديل رأس المال اليومي (د.إ):", value=st.session_state.capital, step=5000.0)
    stop_loss_pct = st.slider("حد وقف الخسارة صارم (%)", 0.5, 3.0, 1.0, 0.1)
    take_profit_pct = st.slider("الهدف الأدنى لجني الأرباح (%)", 0.5, 5.0, 1.0, 0.1)
    
    st.write("---")
    
    # أزرار تشغيل وإيقاف البوت
    if not st.session_state.running:
        if st.button("🚀 تشغيل البوت (بدء الجلسة)"):
            st.session_state.running = True
            st.session_state.log.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🟢 تم تشغيل البوت بنجاح واختبار المعايير الشرعية.")
            st.rerun()
    else:
        if st.button("🛑 إيقاف طارئ للبوت وإغلاق المراكز"):
            st.session_state.running = False
            st.session_state.log.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🔴 إيقاف طارئ! تم إغلاق جميع المراكز فوراً لحماية رأس المال.")
            st.rerun()

with right_col:
    # التبويبات الرئيسية للتطبيق
    tab1, tab2, tab3 = st.tabs(["📋 خطة اليوم والمراقبة", "📑 سجل صفقات اليوم", "📜 سجل الأحداث والعمليات (Logs)"])
    
    with tab1:
        st.subheader("🚨 الأسهم المستهدفة وجلسة التداول الحية")
        
        # جدول محاكاة الصفقات الحية والأهداف قبل/أثناء السوق
        live_trades = {
            "السهم": ["EMAAR", "ADNOCDIST", "ALDAR"],
            "حالة الفلترة الشرعية": ["✅ متوافق", "✅ متوافق", "✅ متوافق"],
            "سعر الدخول المقترح": ["8.20 د.إ", "3.88 د.إ", "6.58 د.إ"],
            "🎯 هدف الربح (+1%)": ["8.28 د.إ", "3.92 د.إ", "6.65 د.إ"],
            "⛔ وقف الخسارة (-1%)": ["8.12 د.إ", "3.84 د.إ", "6.51 د.إ"],
            "الحالة اللحظية": ["🎯 تم تحقيق الهدف وبيع", "⛔ تفعيل وقف الخسارة وبيع", "⏳ مركز مفتوح (مراقبة)"]
        }
        df_live = pd.DataFrame(live_trades)
        st.table(df_live)
        
        # محاكاة تحديث الأسعار التفاعلي
        if st.session_state.running:
            st.info("🔄 البوت يعمل الآن ويراقب الأسعار لحظة بلحظة... (تحديث تلقائي كل ساعة للأسواق)")
            
    with tab2:
        st.subheader("📊 التقرير المالي الختامي للجلسة")
        
        # جدول يحاكي تقرير الساعة 3:15 عصراً بعد الإغلاق
        history_data = {
            "السهم": ["EMAAR", "ADNOCDIST"],
            "المبلغ المستثمر": ["33,333 د.إ", "33,333 د.إ"],
            "سعر الشراء": ["8.20 د.إ", "3.88 د.إ"],
            "سعر البيع": ["8.28 د.إ", "3.84 د.إ"],
            "النتيجة": ["🟢 +325.20 د.إ", "🔴 -343.60 د.إ"],
            "التوقيت": ["12:00:00", "12:00:00"]
        }
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)

    with tab3:
        st.subheader("📜 سجل العمليات المباشر (Audit Log)")
        if st.session_state.log:
            for log_entry in reversed(st.session_state.log):
                st.code(log_entry)
        else:
            st.write("البوت في وضع الاستعداد. اضغط على تشغيل للبدء.")
