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
    # Cloud par yeh Streamlit ki tijori se secret PIN lega
    ADMIN_PIN = str(st.secrets["ADMIN_PIN"])
except:
    # Laptop par local testing ke liye dummy PIN (Kyunki local secrets file nahi hai)
    ADMIN_PIN = "0000"

# Session State variables for memory
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'attempts' not in st.session_state:
    st.session_state['attempts'] = 0

# --- LOGIN SCREEN ---
if not st.session_state['authenticated']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1D1D1F;'>🏫 Bhavan's GVM Hinganghat</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #515154;'>Smart Attendance System - Secure Login</h2>", unsafe_allow_html=True)
    
    # 3-Strike Lockdown Logic
    if st.session_state['attempts'] >= 3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("🚨 SYSTEM LOCKDOWN INITIATED 🚨")
        st.warning("Unauthorized Access Detected! 3 Failed Attempts. Admin has been notified. (Refresh the page to reset)")
        st.stop() # Code yahin ruk jayega, aage ka dashboard load hi nahi hoga
        
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"<div style='text-align: center; color: #FF3B30; font-weight: bold;'>Attempts remaining: {3 - st.session_state['attempts']}</div>", unsafe_allow_html=True)
        pin_input = st.text_input("Enter Admin PIN", type="password")
        
        if st.button("Unlock Dashboard", use_container_width=True):
            if pin_input == ADMIN_PIN:
                st.session_state['authenticated'] = True
                st.rerun() # Page ko naye state ke sath reload karega
            else:
                st.session_state['attempts'] += 1
                st.error("❌ Incorrect PIN!")
                time.sleep(1)
                st.rerun()
    st.stop() # Don't run the rest of the app if not logged in

# ==========================================
# 💻 MAIN DASHBOARD UI (Only visible if logged in)
# ==========================================

# --- Custom CSS for Premium Look (APPLE/MAC STYLE) ---
st.markdown("""
    <style>
    /* Apple Light Grey Background */
    [data-testid="stAppViewContainer"] {
        background-color: #F5F5F7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Top Header Transparent */
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Apple Style Blue Buttons with Hover Effect */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 122, 255, 0.2) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        background-color: #0056b3 !important;
        box-shadow: 0 6px 12px rgba(0, 122, 255, 0.3) !important;
    }
    
    /* Glassmorphism & Soft Shadows for Inputs */
    .stSelectbox div[data-baseweb="select"], .stTextInput div[data-baseweb="input"], .stDateInput div[data-baseweb="input"] {
        border-radius: 10px !important;
        border: 1px solid #E5E5EA !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    /* Premium Dashboard Cards (For Metrics) */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #E5E5EA;
        text-align: center;
    }
    
    /* Text Colors & Headings */
    h1, h2, h3 {
        color: #1D1D1F !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    p, span, label {
        color: #515154 !important;
    }
    
    /* Table Styling */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* Existing Title and Developer Box */
    .school-title { font-size: 38px; font-weight: 900; color: #1D1D1F; text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0px;}
    .sub-title { font-size: 22px; color: #515154; text-align: center; margin-bottom: 30px; font-weight: 400;}
    .developer-box { background: linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%); padding: 20px; border-radius: 16px; text-align: center; color: white; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,122,255,0.3);}
    .developer-text { font-size: 13px; margin: 0; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; color: #FFFFFF !important;}
    .developer-name { font-size: 24px; font-weight: 800; margin: 5px 0; color: #FFFFFF !important;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120) 
    st.markdown("## 🏛️ Administration")
    st.markdown("**Director:** [Shri.Ashish Kumar Sarkar]") 
    st.markdown("**Principal:** [Smt.Dharati Tamgire]")
    
    st.markdown("<div class='developer-box'><p class='developer-text'>System Architect</p><p class='developer-name'>Yatharth Deshmukh</p><p class='developer-text'>Bhavan's GVM Alumnus</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 Logout System", use_container_width=True):
        st.session_state['authenticated'] = False
        st.rerun()

# --- MAIN PAGE HEADERS ---
st.markdown("<div class='school-title'>Bhavan's GVM, Hinganghat</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Real-Time Smart Attendance Dashboard</div>", unsafe_allow_html=True)

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
    st.info("📌 System is online and waiting for scans.")
else:
    name_col = df.columns[0]
    date_col = [c for c in df.columns if 'date' in str(c).lower()][0]
    status_col = [c for c in df.columns if 'status' in str(c).lower()][0]

    # --- LIVE ANALYTICS COUNTERS (APPLE CARDS) ---
    st.markdown("### 📊 Live Analytics")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(label="👥 Total Scans", value=len(df)) 
        
    with metric_col2:
        present_count = len(df[df[status_col].astype(str).str.contains('Present|ON TIME', case=False, na=False)])
        st.metric(label="✅ On Time", value=present_count)
        
    with metric_col3:
        late_count = len(df[df[status_col].astype(str).str.contains('Late', case=False, na=False)])
        st.metric(label="⏰ Late Marks", value=late_count)

    st.markdown("---")

    # --- SMART FILTERS ---
    st.markdown("### 🔍 Search & Filter")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        teacher_list = ["All Teachers"] + df[name_col].unique().tolist()
        selected_teacher = st.selectbox("👤 Select Teacher", teacher_list)
    with f_col2:
        selected_date = st.date_input("📅 Select Date", value=None)
    with f_col3:
        status_list = ["All", "ON TIME", "LATE"] # 'LATE MARK!' hata kar strictly LATE kiya for better matching
        selected_status = st.selectbox("🚦 Filter by Status", status_list)

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
        st.warning("⚠️ No data found for this filter.")
    else:
        st.dataframe(filtered_df.iloc[::-1], use_container_width=True, hide_index=True, height=400)
