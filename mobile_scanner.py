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
    # Direct URL se connection (Koi confusion nahi)
    client = gspread.service_account(filename='secret_key.json')
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/16uwbOt1ossNRGKAdTUgFMBi756gkE5oYPglc34a6vVM/edit').sheet1
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
                    name = names[id]
                
                # --- TIME CHECKING ---
                    if start_time <= now_time <= end_time:
                        if now_time <= late_time:
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
                            client = gspread.service_account(filename='secret_key.json')
                        # Direct Sheet ID (Brahmastra 2.0 - Yeh fail nahi hota)
                            sheet = client.open_by_key('16uwbOt1ossNRGKAdTUgFMBi756gkE5oYPglc34a6vVM').sheet1
                        
                            sheet.append_row([name, date_str, time_str, day_str, status], value_input_option='USER_ENTERED')
                            st.success("☁ Data successfully saved to Google Sheets! (Confirmed)")
                        except Exception as e:
                            st.error(f"❌ Cloud Error: {e}")
                    else:
                        st.error(f"🔴 Face Matched: {name}. Attendance window is closed. Entry Not Saved!")
                else:
                    st.error("🔴 Unknown Face! Access Denied.")

    expect Exception as e:
        st.error(f"system Error  {e}")
