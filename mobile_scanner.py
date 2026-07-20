import streamlit as st
import cv2
import numpy as np
import os
from datetime import datetime, time, timedelta, timezone
import gspread
import json

# --- Page Config ---
st.set_page_config(page_title="Bhavan's GVM - Smart Scanner", page_icon="📷")
st.markdown("<h2 style='text-align: center; color: #ff4b4b; font-weight: 900;'>Bhavan's GVM Web Scanner</h2><p style='text-align: center; color: #6B7280; font-size: 18px; margin-top: -15px; font-weight: bold; letter-spacing: 1px;'>Engineered by Yatharth Deshmukh</p>", unsafe_allow_html=True)
st.info("⚡ DUAL-AUTH ACTIVE: Scan your Face or show your QR Code.")

# --- Google Sheets Setup ---
def connect_to_sheets():
    creds_dict = json.loads(st.secrets["GOOGLE_KEY"])
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/16uwbOt1ossNRGKAdTUgFMBI756gkE5oYPglc34a6vVM/edit?gid=0#gid=0').get_worksheet(0)
    return sheet

# --- Face & QR Setup ---
cascade_path = 'haarcascade_frontalface_default.xml'
if not os.path.exists(cascade_path):
    import urllib.request
    urllib.request.urlretrieve('https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml', cascade_path)

face_cascade = cv2.CascadeClassifier(cascade_path)
recognizer = cv2.face.LBPHFaceRecognizer_create()
qr_decoder = cv2.QRCodeDetector() # 🔥 THE BRAHMASTRA ENGINE

current_folder = os.path.dirname(os.path.abspath(__file__))
trainer_file = os.path.join(current_folder, 'trainer.yml')

if not os.path.exists(trainer_file):
    st.warning("⚠️ Face data (trainer.yml) missing from server! Only QR Code will work.")
else:
    try:
        recognizer.read(trainer_file)
    except Exception as e:
        st.error(f"❌ Face data corrupt: {e}. Only QR Code will work.")

def load_names():
    names = {}
    if os.path.exists('names_mapping.txt'):
        with open('names_mapping.txt', 'r') as f:
            for line in f:
                if ',' in line:
                    id_str, name = line.strip().split(',')
                    names[int(id_str)] = name
    return names

names_map = load_names()

# --- THE MASTER ATTENDANCE LOGIC (Reusable) ---
def process_attendance(name, method_used):
    ist_time = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist_time)
    now_time = now.time()
    
    morning_start = time(13, 0)
    morning_late = time(14, 30)
    morning_end = time(15, 30)
    
    evening_start = time(17, 0)
    evening_end = time(18, 0)

    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_str = now.strftime("%A")

    try:
        sheet = connect_to_sheets()
        existing_data = sheet.get_all_values()
        
        row_found = False
        row_index = -1
        
        for i, row in enumerate(existing_data):
            if len(row) >= 2 and row[0] == name and row[1] == date_str:
                row_found = True
                row_index = i + 1 
                break
                
        if morning_start <= now_time <= morning_end:
            if row_found:
                st.warning(f"⚠️ {name}, your Morning IN attendance is already marked! ({method_used})")
            else:
                if now_time <= morning_late:
                    status = "Present"
                    st.success(f"✅ {method_used} MATCHED: {name} (ON TIME!)")
                    st.balloons()
                else:
                    status = "Late"
                    st.warning(f"⏰ {method_used} MATCHED: {name} (LATE MARK!)")
                
                sheet.append_row([name, date_str, time_str, "---", day_str, status], value_input_option='USER_ENTERED')
                st.success("☀️ Morning attendance marked successfully.")
                
        elif evening_start <= now_time <= evening_end:
            if not row_found:
                st.error(f"🔴 {name}, your Morning attendance is missing! Cannot mark OUT time.")
            else:
                if len(existing_data[row_index-1]) >= 4 and existing_data[row_index-1][3] != "---":
                    st.warning(f"⚠️ {name}, your Evening OUT time is already marked! ({method_used})")
                else:
                    st.success(f"✅ {method_used} MATCHED: {name} (EVENING OUT)")
                    sheet.update_cell(row_index, 4, time_str)
                    st.success("🌙 Evening attendance updated successfully.")
        else:
            st.error(f"🔴 Scanned: {name}. Attendance window is currently CLOSED please try again at appropriate time")
            
    except Exception as e:
        st.error(f"❌ MAIN ERROR: {e}")

# --- Dual Scanner Input ---
img_file = st.camera_input("")

if img_file is not None:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)

    # 1. TRY SCANNING FOR QR CODE FIRST (Instant Match)
    qr_data, bbox, _ = qr_decoder.detectAndDecode(cv2_img)
    
    if qr_data:
        # QR Code successfully read!
        process_attendance(qr_data, "QR CODE")
    
    # 2. IF NO QR CODE, TRY FACE RECOGNITION
    else:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        
        if len(faces) == 0:
            st.warning("No Face or QR Code detected! Thoda paas aakar aur achhi light mein try karein.")
        else:
            face_matched = False
            for (x, y, w, h) in faces:
                if os.path.exists(trainer_file):
                    id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                    
                    if confidence < 75: 
                        name = names_map.get(id, "Unknown")
                        if name != "Unknown":
                            process_attendance(name, "FACE")
                            face_matched = True
                            break # Match milte hi loop rok do
                else:
                    st.error("⚠️ Face Database missing. Please use QR Code.")
                    break
            
            if not face_matched and os.path.exists(trainer_file):
                st.error("🔴 Unknown Face! Access Denied. Use QR Code instead.")
