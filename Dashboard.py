import streamlit as st
import gspread
import pandas as pd
import json
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bhavan's GVM - Admin Dashboard", page_icon="🏫", layout="wide")

# ==========================================
# 🔒 SECURITY SYSTEM (PIN AUTHENTICATION)
# ==========================================
try:
    ADMIN_PIN = str(st.secrets["ADMIN_PIN"])
except:
    ADMIN_PIN = "0000"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'attempts' not in st.session_state:
    st.session_state['attempts'] = 0

# --- LOGIN SCREEN ---
if not st.session_state['authenticated']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00F0FF; text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);'>🏫 Bhavan's GVM Hinganghat</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #94A3B8;'>Secure System Access</h2>", unsafe_allow_html=True)
    
    if st.session_state['attempts'] >= 3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("🚨 SYSTEM LOCKDOWN INITIATED 🚨")
        st.warning("Unauthorized Access Detected! 3 Failed Attempts. Admin has been notified. (Refresh the page to reset)")
        st.stop()
        
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"<div style='text-align: center; color: #FF003C; font-weight: bold;'>Attempts remaining: {3 - st.session_state['attempts']}</div>", unsafe_allow_html=True)
        pin_input = st.text_input("Enter Admin PIN", type="password")
        
        if st.button("Unlock Dashboard", use_container_width=True):
            if pin_input == ADMIN_PIN:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.session_state['attempts'] += 1
                st.error("❌ Incorrect PIN!")
                time.sleep(1)
                st.rerun()
    st.stop()

# ==========================================
# 💻 MAIN DASHBOARD UI (DARK COMMAND CENTER)
# ==========================================

st.markdown("""
    <style>
    /* Dark Tech Background */
    [data-testid="stAppViewContainer"] {
        background-color: #0A0E17;
        color: #E2E8F0;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Neon Cyber Buttons */
    div.stButton > button {
        background-color: transparent !important;
        color: #00F0FF !important;
        border: 2px solid #00F0FF !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
    }
    div.stButton > button:hover {
        background-color: #00F0FF !important;
        color: #0A0E17 !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.6) !important;
    }
    
    /* Dark Inputs with Neon Borders */
    .stSelectbox div[data-baseweb="select"], .stTextInput div[data-baseweb="input"], .stDateInput div[data-baseweb="input"] {
        background-color: #131A2A !important;
        border: 1px solid #1E293B !important;
        color: #00F0FF !important;
    }
    
    /* Glowing Metric Cards */
    [data-testid="metric-container"] {
        background-color: #131A2A;
        border: 1px solid #38BDF8;
        border-left: 4px solid #38BDF8;
        border-radius: 4px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
    }
    [data-testid="stMetricValue"] {
        color: #00F0FF !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
    }
    
    /* Text Colors */
    h1, h2, h3 { color: #F8FAFC !important; font-weight: 800 !important; }
    p, span, label { color: #94A3B8 !important; }
    
    /* Table Styling */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        background-color: #131A2A;
        border: 1px solid #1E293B;
    }

    /* Titles & Developer Box */
    .school-title { font-size: 38px; font-weight: 900; color: #00F0FF; text-align: center; text-transform: uppercase; letter-spacing: 4px; text-shadow: 0 0 12px rgba(0, 240, 255, 0.4); margin-bottom: 0px;}
    .sub-title { font-size: 20px; color: #94A3B8; text-align: center; margin-bottom: 30px; letter-spacing: 1px;}
    .developer-box { background: #131A2A; border: 1px solid #B026FF; padding: 20px; border-radius: 4px; text-align: center; box-shadow: 0 0 20px rgba(176, 38, 255, 0.15); margin-top: 20px;}
    .developer-text { font-size: 12px; margin: 0; opacity: 0.9; text-transform: uppercase; letter-spacing: 2px; color: #94A3B8 !important;}
    .developer-name { font-size: 24px; font-weight: 900; margin: 5px 0; color: #B026FF !important; text-shadow: 0 0 10px rgba(176, 38, 255, 0.4); text-transform: uppercase;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120) 
    st.markdown("## 🏛️ COMMAND CENTER")
    st.markdown("**Director:** [Shri.Ashish Kumar Sarkar]") 
    st.markdown("**Principal:** [Smt.Dharati Tamgire]")
    
    st.markdown("<div class='developer-box'><p class='developer-text'>System Architect</p><p class='developer-name'>Yatharth Deshmukh</p><p class='developer-text'>Bhavan's GVM Alumnus</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 LOGOUT SYSTEM", use_container_width=True):
        st.session_state['authenticated'] = False
        st.rerun()

# --- MAIN PAGE HEADERS ---
st.markdown("<div class='school-title'>Bhavan's GVM, Hinganghat</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>SECURE ATTENDANCE MAINFRAME</div>", unsafe_allow_html=True)

# --- SECURE DATA CONNECTION ---
@st.cache_data(ttl=30) 
def load_data():
    try:
        try:
            client = gspread.service_account(filename='secret_key.json')
        except:
            creds_dict = json.loads(st.secrets["GOOGLE_KEY"])
            client = gspread.service_account_from_dict(creds_dict)
            
        sheet_url = 'https://docs.google.com/spreadsheets/d/16uwbOt1ossNRGKAdTUgFMBI756gkE5oYPglc34a6vVM/edit?gid=0#gid=0'
        sheet = client.open_by_url(sheet_url).get_worksheet(0)
        
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        st.error(f"❌ Cloud Connection Error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.info("📌 SYSTEM ONLINE. AWAITING DATA STREAMS...")
else:
    name_col = df.columns[0]
    date_col = [c for c in df.columns if 'date' in str(c).lower()][0]
    status_col = [c for c in df.columns if 'status' in str(c).lower()][0]

    # --- LIVE ANALYTICS COUNTERS ---
    st.markdown("### 📊 SYSTEM ANALYTICS")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(label="TOTAL SCANS", value=len(df)) 
        
    with metric_col2:
        present_count = len(df[df[status_col].astype(str).str.contains('Present|ON TIME', case=False, na=False)])
        st.metric(label="ON TIME", value=present_count)
        
    with metric_col3:
        late_count = len(df[df[status_col].astype(str).str.contains('Late', case=False, na=False)])
        st.metric(label="LATE MARKS", value=late_count)

    st.markdown("---")

    # --- SMART FILTERS ---
    st.markdown("### 🔍 DATA FILTERS")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        teacher_list = ["All Teachers"] + df[name_col].unique().tolist()
        selected_teacher = st.selectbox("👤 SELECT PERSONNEL", teacher_list)
    with f_col2:
        selected_date = st.date_input("📅 SELECT DATE", value=None)
    with f_col3:
        status_list = ["All", "ON TIME", "LATE"]
        selected_status = st.selectbox("🚦 FILTER STATUS", status_list)

    # Apply Filters
    filtered_df = df.copy()
    if selected_teacher != "All Teachers":
        filtered_df = filtered_df[filtered_df[name_col] == selected_teacher]
    if selected_date is not None:
        filtered_df = filtered_df[filtered_df[date_col].astype(str).str.contains(str(selected_date))]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df[status_col].astype(str).str.contains(selected_status, case=False, na=False)]
    
    st.markdown("---")
    
    # --- LIVE DATA TABLE ---
    if filtered_df.empty:
        st.warning("⚠️ NO LOGS DETECTED FOR CURRENT FILTER.")
    else:
        st.dataframe(filtered_df.iloc[::-1], use_container_width=True, hide_index=True, height=400)
