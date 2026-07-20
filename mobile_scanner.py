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
st.info("Click on the camera button to scan the face:")

# --- Google Sheets Connection Setup (Anti-Hack Mode) ---
def connect_to_sheets():
    # Streamlit ki tijori se secret key nikal raha hai
    creds_dict = json.loads(st.secrets["GOOGLE_KEY"])
    client = gspread.service_account_from_dict(creds_dict)
    
    # Tera original URL
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/16uwbOt1ossNRGKAdTUgFMBI756gkE5oYPglc34a6vVM/edit?gid=0#gid=0').get_worksheet(0)
    return sheet

# --- Face Recognition Setup ---
cascade_path = 'haarcascade_frontalface_default.xml'
# Cloud par file na ho toh auto-download karega
if not os.path.exists(cascade_path):
    import urllib.request
    urllib.request.urlretrieve('https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml', cascade_path)

face_cascade = cv2.CascadeClassifier(cascade_path)
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Streamlit ko file ka exact rasta (GPS) batane ki ninja technique
current_folder = os.path.dirname(os.path.abspath(__file__))
trainer_file = os.path.join(current_folder, 'trainer.yml')

if not os.path.exists(trainer_file):
    st.error("❌"The file is on GitHub, but the server can't find it!")
    st.stop() # Yeh line aage ka crash (cv2.error) hamesha ke liye rok degi
else:
    try:
        recognizer.read(trainer_file)
    except Exception as e:
        st.error(f"❌ The file was found, but OpenCV couldn't read it. (The file may be corrupted): {e}")
        st.stop()

# --- NAAM PADHNE WALA FUNCTION ---
def load_names():
    names = {}
    if os.path.exists('names_mapping.txt'):
        with open('names_mapping.txt', 'r') as f:
            for line in f:
                if ',' in line:
                    id_str, name = line.strip().split(',')
                    names[int(id_str)] = name
    return names

# Jab face match ho, toh naam list se aise uthana:
names_map = load_names()
  
# --- Camera Input ---
img_file = st.camera_input("")

if img_file is not None:
    # Convert image for OpenCV
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    if len(faces) == 0:
        st.warning("No face detected!Please move a little closer and try again in better lighting.")
    else:
        for (x, y, w, h) in faces:
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            # Agar confidence 75 se kam hai matlab AI sure hai
            if confidence < 75: 
                name = names_map.get(id, "Unknown")
                
                # --- ADVANCED DUAL-WINDOW TIME LOGIC (MORNING & EVENING) ---
                ist_time = timezone(timedelta(hours=5, minutes=30))
                now = datetime.now(ist_time)
                now_time = now.time()
                
                # TIMINGS SETUP
                morning_start = time(13, 0)   # Morning window khulegi
                morning_late = time(14, 30)   # 8:30 ke baad LATE mark
                morning_end = time(15, 30)    # Morning window band
                
                evening_start = time(17, 0)  # Evening window khulegi (4:00 PM)
                evening_end = time(18, 0)    # Evening window band (6:00 PM)

                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                day_str = now.strftime("%A")

                try:
                    sheet = connect_to_sheets()
                    existing_data = sheet.get_all_values()
                    
                    row_found = False
                    row_index = -1
                    
                    # Check kar rahe hain ki aaj subah ka scan hua hai ya nahi
                    for i, row in enumerate(existing_data):
                        if len(row) >= 2 and row[0] == name and row[1] == date_str:
                            row_found = True
                            row_index = i + 1 
                            break
                            
                    # ==========================================
                    # ☀️ SCENARIO 1: MORNING SCAN (8:00 AM to 9:30 AM)
                    # ==========================================
                    if morning_start <= now_time <= morning_end:
                        if row_found:
                            st.warning(f"⚠️ {name}, your Morning IN attendance is already marked!")
                        else:
                            if now_time <= morning_late:
                                status = "Present"
                                st.success(f"✅ FACE MATCHED: {name} (ON TIME!)")
                                st.balloons()
                            else:
                                status = "Late"
                                st.warning(f"⏰ FACE MATCHED: {name} (LATE MARK!)")
                            
                            # OUT Time ki jagah "---" daal rahe hain
                            sheet.append_row([name, date_str, time_str, "---", day_str, status], value_input_option='USER_ENTERED')
                            st.success("☀️ Morning attendance marked successfully.")
                            
                    # ==========================================
                    # 🌙 SCENARIO 2: EVENING SCAN (4:00 PM to 6:00 PM)
                    # ==========================================
                    elif evening_start <= now_time <= evening_end:
                        if not row_found:
                            st.error(f"🔴 {name}, your Morning attendance is missing! Cannot mark OUT time.")
                        else:
                            # Check kar rahe hain ki OUT time pehle se toh nahi bhara
                            if len(existing_data[row_index-1]) >= 4 and existing_data[row_index-1][3] != "---":
                                st.warning(f"⚠️ {name}, your Evening OUT time is already marked!")
                            else:
                                st.success(f"✅ FACE MATCHED: {name} (EVENING OUT)")
                                sheet.update_cell(row_index, 4, time_str) # 4th Column mein time update
                                st.success("🌙 Evening attendance updated successfully.")
                                
                    # ==========================================
                    # 🚫 SCENARIO 3: WRONG TIMING (System Closed)
                    # ==========================================
                    else:
                        st.error(f"🔴 Face Matched: {name}. Attendance window is currently CLOSED please try again at appropriate time")
                        
                except Exception as e:
                    st.error(f"❌ MAIN ERROR: {e}")
            else:
                st.error("🔴 Unknown Face! Access Denied.")
