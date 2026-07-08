import streamlit as st
import cv2
import numpy as np
import os
from datetime import datetime, time, timedelta, timezone
import gspread

# --- Page Config ---
st.set_page_config(page_title="Bhavan's GVM - Smart Scanner", page_icon="📷")

st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>Bhavan's GVM Web Scanner (Cloud)</h2>", unsafe_allow_html=True)
st.info("Click on the camera button to scan the face:")

# --- Google Sheets Connection Setup ---
def connect_to_sheets():
    # Direct Sheet ID (Brahmastra 2.0 - Yeh fail nahi hota)
    client = gspread.service_account(filename='secret_key.json')
    sheet = client.open_by_key('16uwbOt1ossNRGKAdTUgFMBi756gkE5oYPglc34a6vVM').sheet1
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
    st.error("❌ File GitHub par hai, par server usko dhoondh nahi pa raha!")
    st.stop() # Yeh line aage ka crash (cv2.error) hamesha ke liye rok degi!
else:
    try:
        recognizer.read(trainer_file)
    except Exception as e:
        st.error(f"❌ File mil gayi, par OpenCV usko padh nahi pa raha (File corrupt ho sakti hai): {e}")
        st.stop()
# Names array matching IDs (Zero se shuru)
names = ['None', 'Yatharth', 'Papa', 'Milk man']

# --- Camera Input ---
img_file = st.camera_input("")

if img_file is not None:
    # Convert image for OpenCV
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    if len(faces) == 0:
        st.warning("No face detected! Thoda paas aakar aur achhi light mein try karein.")
    else:
        for (x, y, w, h) in faces:
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            # Agar confidence 75 se kam hai matlab AI sure hai
            if confidence < 75: 
                name = names[id]
                
                # --- ADVANCED TIME & LATE MARK LOGIC ---
                ist_time = timezone(timedelta(hours=5, minutes=30))
                now = datetime.now(ist_time)
                now_time = now.time()
                
                # TIMINGS: Aaj ka Test Time (3:00 PM to 5:00 PM)
                start_time = time(15, 0)   # Window Opens
                late_time = time(15, 30)   # Late Mark Starts
                end_time = time(17, 0)     # Window Closes

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
                        sheet = connect_to_sheets()
                        # USER_ENTERED lagane se Google ko lagega kisi insaan ne type kiya hai
                        sheet.append_row([name, date_str, time_str, day_str, status], value_input_option='USER_ENTERED')
                        st.success("☁ Data successfully saved to Google Sheets! (Confirmed)")
                    except Exception as e:
                        import json
                        with open('secret_key.json') as f:
                            robot_email = json.load(f).get('client_email')
                        st.error(f"❌ 404 ERROR: Google Sheet is Email ko block kar rahi hai ➔ {robot_email}")
                        st.info("Bhai, is exact email ko yahan se copy kar aur Google Sheet mein 'Share' daba kar Editor bana de.")
                else:
                    st.error(f"🔴 Face Matched: {name}. Attendance window is closed. Entry Not Saved!")
                    
            else:
                st.error("🔴 Unknown Face! Access Denied.")
