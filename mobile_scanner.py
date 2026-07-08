import streamlit as st
import cv2
import numpy as np
from PIL import Image
from datetime import datetime, time, timedelta, timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

st.set_page_config(page_title="Bhavan's GVM - Smart Scanner", page_icon="📸")

st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>Bhavan's GVM Web Scanner (Cloud)</h2>", unsafe_allow_html=True)
st.info("click on the camera button to scan the face:")

# --- Google Sheets Connection Setup ---
def connect_to_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('secret_key.json', scope)
    client = gspread.authorize(creds)
    # Apni sheet ka exact naam yahan likha hai
    sheet = client.open('Bhavans_GVM_Attendance').sheet1
    return sheet

img_file = st.camera_input("")

if img_file is not None:
    try:
        face_cascade = cascade_path = 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            import urllib.request
            urllib.request.urlretrieve('https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml', cascade_path)
        face_cascade = cv2.CascadeClassifier(cascade_path)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('trainer.yml')

        # Apni list update rakhna
        names = ['None', 'Yatharth', 'Papa', 'Milk man'] 

        img = Image.open(img_file)
        img_array = np.array(img)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) == 0:
            st.error("❌ please come closer! to scan the face.")
        else:
            for (x, y, w, h) in faces:
                id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

                if confidence < 65:
                    name = names[id] if id < len(names) else f"Unknown ({id})"
                    
                    # --- ADVANCED TIME & LATE MARK LOGIC ---
                    ist_time = timezone(timedelta(hours=5, minutes=30))
                    now = datetime.now(ist_time)
                    now_time = now.time()
                    
                    # TIMINGS: Test karne ke liye isko abhi ke time ke hisaab se change kar lena!
                    start_time = time(13, 15)  # Window Opens
                    late_time = time(13, 45)   # Late Mark Starts
                    end_time = time(13, 59)    # Window Closes
                    
                    if start_time <= now_time <= end_time:
                        if now_time < late_time:
                            status = "Present"
                            st.success(f"✅ FACE MATCHED: {name} (ON TIME!)")
                            st.balloons()
                        else:
                            status = "Late"
                            st.warning(f"⏰ FACE MATCHED: {name} (LATE MARK!)")
                            
                        # --- CLOUD MEIN SAVE KARNA (Google Sheets) ---
                        date_str = now.strftime("%Y-%m-%d")
                        time_str = now.strftime("%H:%M:%S")
                        day_str = now.strftime("%A")
                        
                        try:
                            sheet = connect_to_sheets()
                            # Excel ki jagah ab direct Google Sheet mein row add hogi
                            sheet.append_row([name, date_str, time_str, day_str, status])
                            st.success("☁️ Data successfully saved to Google Sheets!")
                        except Exception as e:
                            st.error(f"❌ Cloud Error: {e}")
                        
                    else:
                        st.error(f"🛑 Face Matched: {name}. attendance window is closed. Entry Not Saved!")
                    
                else:
                    st.error("🛑 Unknown Face! Access Denied.")
                    
    except Exception as e:
        st.error(f"System Error: {e}")
