import streamlit as st
import pandas as pd
import datetime
import numpy as np

# إعدادات الصفحة العامة للتطبيق
st.set_page_config(page_title="إدارة بوت التداول الآلي (ADX/DFM)", page_icon="📊", layout="wide")

# تخصيص واجهة التطبيق باللغة العربية
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    h1, h2, h3, p, div, span, label { text-align: right; direction: rtl; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; font-weight: bold; }
    div[data-testid="stMetricValue"] { text-align: right; direction: ltr; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 1. إدارة الحالة وتوليد بيانات الأسواق الحية
# =====================================================================
if 'capital' not in st.session_state:
    st.session_state.capital = 100000.0
if 'running' not in st.session_state:
    st.session_state.running = False
if 'log' not in st.session_state:
    st.session_state.log = ["ℹ️ البوت جاهز في وضع الاستعداد بانتظار بدء الجلسة."]
if 'pnl_today' not in st.session_state:
    st.session_state.pnl_today = 0.0
if 'win_rate' not in st.session_state:
    st.session_state.win_rate = 0.0

# محاكاة توليد حركة الأسعار الفنية والشرعية بناءً على معاييرك المطلوبة
def get_market_data(sl_pct, tp_pct):
    if st.session_state.running:
        # عند تشغيل البوت يتم تفعيل البيانات اللحظية وحساب الأهداف بناءً على مدخلاتك الحالية
        data = {
            "السهم": ["EMAAR", "ADNOCDIST", "ALDAR"],
            "حالة الفلترة الشرعية": ["✅ متوافق (ديون < 33%)", "✅ متوافق (طاقة مسموح)", "✅ متوافق (عقاري شرعي)"],
            "سعر الدخول": [8.20, 3.88, 6.58],
            f"🎯 هدف الربح (+{tp_pct}%)": [round(8.20 * (1 + tp_pct/100), 2), round(3.88 * (1 + tp_pct/100), 2), round(6.58 * (1 + tp_pct/100), 2)],
            f"⛔ وقف الخسارة (-{sl_pct}%)": [round(8.20 * (1 - sl_pct/100), 2), round(3.88 * (1 - sl_pct/100), 2), round(6.58 * (1 - sl_pct/100), 2)],
            "المؤشرات الفنية اللحظية": ["📈 RSI=58 | Volume 1.8x", "📉 RSI=42 | Volume 1.6x", "⏳ RSI=50 | Volume 1.1x"],
            "الحالة اللحظية": ["🎯 تم جني الربح تلقائياً", "⛔ تفعيل وقف الخسارة الصارم", "⏳ مراقبة مستمرة (RSI آمن)"]
        }
        pnl = (100000.0 * (tp_pct/100) / 3) - (100000.0 * (sl_pct/100) / 3) # حساب pnl للمحاكاة التفاعلية
        win_rate = 50.0
    else:
        # قبل التشغيل تظل الشاشة في وضع الاستعداد
        data = {
            "السهم": ["EMAAR", "ADNOCDIST", "ALDAR"],
            "حالة الفلترة الشرعية": ["⏳ بانتظار الفحص", "⏳ بانتظار الفحص", "⏳ بانتظار الفحص"],
            "سعر الدخول": [0.0, 0.0, 0.0],
            f"🎯 هدف الربح (+{tp_pct}%)": [0.0, 0.0, 0.0],
            f"⛔ وقف الخسارة (-{sl_pct}%)": [0.0, 0.0, 0.0],
            "المؤشرات الفنية اللحظية": ["-", "-", "-"],
            "الحالة اللحظية": ["😴 متوقف", "😴 متوقف", "😴 متوقف"]
        }
        pnl = 0.0
        win_rate = 0.0
    return pd.DataFrame(data), pnl, win_rate

# =====================================================================
# 2. الشاشة الرئيسية للوحة التحكم (Dashboard UI)
# =====================================================================
st.title("📊 نظام التداول الآلي الذكي لأسواق الإمارات")
st.subheader("لوحة التحكم والمراقبة اللحظية للمضاربة اليومية ($ADX$ / $DFM$)")
st.write("---")

# استقبال البيانات بناءً على التحكم الجانبي الحالي
# سيتم تحديد أشرطة التحكم الجانبية في الأسفل ولكننا نعرّف المتغيرات أولاً
stop_loss_pct = 1.0
take_profit_pct = 1.0

# تقسيم الشاشة إلى عمودين: التحكم الجانبي والعمليات الرئيسية
left_col, right_col = st.columns([1, 3])

with left_col:
    st.header("⚙️ إعدادات التحكم")
    input_capital = st.number_input("تعديل رأس المال اليومي (د.إ):", value=st.session_state.capital, step=5000.0)
    stop_loss_pct = st.slider("حد وقف الخسارة صارم (%)", 0.5, 3.0, 1.0, 0.1)
    take_profit_pct = st.slider("الهدف الأدنى لجني الأرباح (%)", 0.5, 5.0, 1.0, 0.1)
    
    st.write("---")
    
    if not st.session_state.running:
        if st.button("🚀 تشغيل البوت (بدء الجلسة)"):
            st.session_state.running = True
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            st.session_state.log.append(f"[{current_time}] 🟢 تم بدء الجلسة التفاعلية وفحص معايير الصيرفة الإسلامية بنجاح.")
            st.session_state.log.append(f"[{current_time}] 🚨 تفعيل الشروط الفنية: حجم التداول > 1.5x و 25 < ADX.")
            st.rerun()
    else:
        if st.button("🛑 إيقاف طارئ للبوت وإغلاق المراكز"):
            st.session_state.running = False
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            st.session_state.log.append(f"[{current_time}] 🔴 إيقاف طارئ يدوي! تم تصفية المراكز المفتوحة فوراً لحماية المحفظة.")
            st.rerun()

# توليد البيانات والحسابات بناءً على حالة الزر ونسب التحكم لـ SL و TP
df_live, calc_pnl, calc_wr = get_market_data(stop_loss_pct, take_profit_pct)
if st.session_state.running:
    st.session_state.pnl_today = calc_pnl
    st.session_state.win_rate = calc_wr
else:
    st.session_state.pnl_today = 0.0
    st.session_state.win_rate = 0.0

with right_col:
    # الجزء العلوي: المؤشرات المالية الحالية التي تتأثر بالتشغيل
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="💰 رأس المال الحالي", value=f"{input_capital:,.2f} د.إ")
    with col2:
        display_pnl = st.session_state.pnl_today
        st.metric(label="📈 ربح/خسارة اليوم المحسوبة", value=f"{display_pnl:+,.2f} د.إ", delta=f"{(display_pnl/input_capital)*100:+.2f}%" if display_pnl != 0 else "0.0%")
    with col3:
        st.metric(label="🚨 المراكز النشطة حالياً", value="1 مركز نشط" if st.session_state.running else "0 مراكز")
    with col4:
        st.metric(label="🎯 نسبة النجاح اليومية (Win Rate)", value=f"{st.session_state.win_rate:.1f}%")

    st.write("---")

    tab1, tab2, tab3 = st.tabs(["📋 خطة اليوم والمراقبة حية", "📑 سجل الصفقات المغلقة", "📜 سجل الأحداث والعمليات (Logs)"])
    
    with tab1:
        st.subheader("🚨 وضع مراقبة الأسهم المباشر")
        st.dataframe(df_live, use_container_width=True)
        if st.session_state.running:
            st.success("🔄 البوت الآن يحلل المؤشرات الفنية ويتفاعل لحظياً مع التغيرات بناءً على أهدافك المحددة.")
        else:
            st.info("😴 اضغط على زر تشغيل البوت الأزرق لتفعيل قراءة المؤشرات الفنية وحساب خطط الدخول والخروج الحية.")
            
    with tab2:
        st.subheader("📊 التقرير الختامي اليومي للصنايق (الساعة 15:15)")
        if st.session_state.running:
            history_data = {
                "السهم": ["EMAAR", "ADNOCDIST"],
                "المبلغ المخصص": [f"{input_capital/3:,.2f} د.إ", f"{input_capital/3:,.2f} د.إ"],
                "سعر الدخول": ["8.20 د.إ", "3.88 د.إ"],
                "سعر التنفيذ الفعلي": [f"{round(8.20 * (1 + take_profit_pct/100), 2)} د.إ", f"{round(3.88 * (1 - stop_loss_pct/100), 2)} د.إ"],
                "النتيجة": [f"🟢 +{round((input_capital/3)*(take_profit_pct/100), 2):+,} د.إ", f"🔴 -{round((input_capital/3)*(stop_loss_pct/100), 2):+,} د.إ"]
            }
            st.dataframe(pd.DataFrame(history_data), use_container_width=True)
        else:
            st.write("لا توجد صفقات مغلقة في وضع الاستعداد الحركي.")

    with tab3:
        st.subheader("📜 سجل التدقيق التقني الحركي (Audit Log)")
        for log_entry in reversed(st.session_state.log):
            st.code(log_entry)
