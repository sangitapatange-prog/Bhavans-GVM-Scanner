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
    st.markdown("<h1 style='text-align: center; color: #202124; font-family: \"Google Sans\", Roboto, Arial;'>🏫 Bhavan's GVM Hinganghat</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #5F6368; font-family: Roboto, Arial; font-weight: 400;'>Enterprise Attendance Portal</h2>", unsafe_allow_html=True)
    
    if st.session_state['attempts'] >= 3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("🚨 SYSTEM LOCKDOWN INITIATED 🚨")
        st.warning("Unauthorized Access Detected! 3 Failed Attempts. Admin has been notified. (Refresh the page to reset)")
        st.stop()
        
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"<div style='text-align: center; color: #D93025; font-weight: bold; font-family: Roboto;'>Attempts remaining: {3 - st.session_state['attempts']}</div>", unsafe_allow_html=True)
        pin_input = st.text_input("Enter Admin PIN", type="password")
        
        if st.button("Authenticate", use_container_width=True):
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
# 💻 MAIN DASHBOARD UI (CORPORATE / GOOGLE STYLE)
# ==========================================

st.markdown("""
    <style>
    /* Google Material Design Background */
    [data-testid="stAppViewContainer"] {
        background-color: #F8F9FA;
        font-family: "Google Sans", Roboto, Arial, sans-serif;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Corporate Blue Buttons (Google Style) */
    div.stButton > button {
        background-color: #1A73E8 !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 8px 24px !important;
        font-weight: 500 !important;
        letter-spacing: 0.25px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15) !important;
    }
    div.stButton > button:hover {
        background-color: #1557B0 !important;
        box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15) !important;
    }
    
    /* Clean Inputs */
    .stSelectbox div[data-baseweb="select"], .stTextInput div[data-baseweb="input"], .stDateInput div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 4px !important;
        color: #202124 !important;
    }
    
    /* Official Metric Cards */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #DADCE0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: none;
    }
    [data-testid="stMetricValue"] {
        color: #202124 !important;
        font-weight: 400 !important;
    }
    
    /* Text Colors */
    h1, h2, h3 { color: #202124 !important; font-weight: 400 !important; }
    p, span, label { color: #5F6368 !important; }
    
    /* Table Styling */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #DADCE0;
        border-radius: 8px;
    }

    /* Titles & Developer Box */
    .school-title { font-size: 32px; font-weight: 400; color: #202124; text-align: center; margin-bottom: 5px; font-family: "Google Sans", Roboto, sans-serif;}
    .sub-title { font-size: 18px; color: #5F6368; text-align: center; margin-bottom: 30px; font-weight: 400;}
    
    /* Official ID Badge Style */
    .developer-box { background: #FFFFFF; border: 1px solid #DADCE0; border-top: 4px solid #1A73E8; padding: 15px; border-radius: 8px; text-align: center; margin-top: 20px;}
    .developer-text { font-size: 12px; margin: 0; color: #5F6368 !important; text-transform: uppercase; letter-spacing: 0.5px;}
    .developer-name { font-size: 20px; font-weight: 500; margin: 5px 0; color: #202124 !important;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) 
    st.markdown("## 🏛️ Administration")
    st.markdown("**Director:** [Shri.Ashish Kumar Sarkar]") 
    st.markdown("**Principal:** [Smt.Dharati Tamgire]")
    
    st.markdown("<div class='developer-box'><p class='developer-text'>System Architect</p><p class='developer-name'>Yatharth Deshmukh</p><p class='developer-text'>Bhavan's GVM</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 Secure Logout", use_container_width=True):
        st.session_state['authenticated'] = False
        st.rerun()

# --- MAIN PAGE HEADERS ---
st.markdown("<div class='school-title'>Bhavan's GVM, Hinganghat</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Enterprise Attendance Portal</div>", unsafe_allow_html=True)

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
    st.info("📌 System is online and waiting for incoming data.")
else:
    name_col = df.columns[0]
    date_col = [c for c in df.columns if 'date' in str(c).lower()][0]
    status_col = [c for c in df.columns if 'status' in str(c).lower()][0]

    # --- LIVE ANALYTICS COUNTERS ---
    st.markdown("### 📊 Overview")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(label="Total Personnel Scanned", value=len(df)) 
        
    with metric_col2:
        present_count = len(df[df[status_col].astype(str).str.contains('Present|ON TIME', case=False, na=False)])
        st.metric(label="On Time (Compliant)", value=present_count)
        
    with metric_col3:
        late_count = len(df[df[status_col].astype(str).str.contains('Late', case=False, na=False)])
        st.metric(label="Late (Flagged)", value=late_count)

    st.markdown("---")

    # --- SMART FILTERS ---
    st.markdown("### 🔍 Data Explorer")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        teacher_list = ["All Personnel"] + df[name_col].unique().tolist()
        selected_teacher = st.selectbox("👤 Select Personnel", teacher_list)
    with f_col2:
        selected_date = st.date_input("📅 Date Range", value=None)
    with f_col3:
        status_list = ["All", "ON TIME", "LATE"]
        selected_status = st.selectbox("🚦 Compliance Status", status_list)

    # Apply Filters
    filtered_df = df.copy()
    if selected_teacher != "All Personnel":
        filtered_df = filtered_df[filtered_df[name_col] == selected_teacher]
    if selected_date is not None:
        filtered_df = filtered_df[filtered_df[date_col].astype(str).str.contains(str(selected_date))]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df[status_col].astype(str).str.contains(selected_status, case=False, na=False)]
    
    st.markdown("---")
    
    # --- LIVE DATA TABLE ---
    if filtered_df.empty:
        st.warning("⚠️ No records found for the selected criteria.")
    else:
        st.dataframe(filtered_df.iloc[::-1], use_container_width=True, hide_index=True, height=400)
