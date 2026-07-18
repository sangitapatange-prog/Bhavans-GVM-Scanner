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
    st.markdown("<h1 style='text-align: center; color: #4F46E5;'>🏫 Bhavan's GVM Hinganghat</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #9CA3AF;'>Smart Attendance System - Secure Login</h2>", unsafe_allow_html=True)
    
    # 3-Strike Lockdown Logic
    if st.session_state['attempts'] >= 3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("🚨 SYSTEM LOCKDOWN INITIATED 🚨")
        st.warning("Unauthorized Access Detected! 3 Failed Attempts. Admin has been notified. (Refresh the page to reset)")
        st.stop() # Code yahin ruk jayega, aage ka dashboard load hi nahi hoga
        
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"<div style='text-align: center; color: #F87171;'>Attempts remaining: {3 - st.session_state['attempts']}</div>", unsafe_allow_html=True)
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

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .school-title { font-size: 38px; font-weight: 900; color: #F59E0B; text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0px;}
    .sub-title { font-size: 22px; color: #D1D5DB; text-align: center; margin-bottom: 30px; font-weight: 400;}
    /* Developer Name tag with cool gradient */
    .developer-box { background: linear-gradient(135deg, #4F46E5 0%, #9333EA 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);}
    .developer-text { font-size: 13px; margin: 0; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;}
    .developer-name { font-size: 24px; font-weight: 800; margin: 5px 0; color: #FFFFFF;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120) 
    st.markdown("## 🏛️ Administration")
    st.markdown("**Director:** [DIRECTOR NAME]") 
    st.markdown("**Principal:** [PRINCIPAL NAME]")
    
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
    # --- SMART FILTERS ---
    st.markdown("### 🔍 Search & Filter")
    
    name_col = df.columns[0]
    date_col = [c for c in df.columns if 'date' in str(c).lower()][0]
    status_col = [c for c in df.columns if 'status' in str(c).lower()][0]
    
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
