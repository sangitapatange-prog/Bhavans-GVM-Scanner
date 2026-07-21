import streamlit as st
import cv2
import numpy as np
import os
from datetime import datetime, time, timedelta, timezone
import gspread
import json
import pickle
import urllib.request

# --- Page Config ---
st.set_page_config(page_title="Bhavan's GVM - Smart Scanner", page_icon="📷")
st.markdown("<h2 style='text-align: center; color: #ff4b4b; font-weight: 900;'>Bhavan's GVM Web Scanner</h2><p style='text-align: center; color: #6B7280; font-size: 18px; margin-top: -15px; font-weight: bold; letter-spacing: 1px;'>Engineered by Yatharth Deshmukh</p>", unsafe_allow_html=True)
st.info("⚡ 128-D AI + QR DUAL-AUTH ACTIVE: Scan Face or Show QR.")

# --- Google Sheets Setup ---
def connect_to_sheets():
    creds_dict = json.loads(st.secrets["GOOGLE_KEY"])
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/16uwbOt1ossNRGKAdTUgFMBI756gkE5oYPglc34a6vVM/edit?gid=0#gid=0').get_worksheet(0)
    return sheet

# --- Model Downloader & Loader (Failsafe) ---
models_dir = "models"
if not os.path.exists(models_dir): os.makedirs(models_dir)
files_to_download = {
    "deploy.prototxt": "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    "res10_300x300_ssd_iter_140000.caffemodel": "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel",
    "openface_nn4.small2.v1.t7": "https://raw.githubusercontent.com/pyannote/pyannote-data/master/openface.nn4.small2.v1.t7"
}
for filename, url in files_to_download.items():
    filepath = os.path.join(models_dir, filename)
    if not os.path.exists(filepath):
        urllib.request.urlretrieve(url, filepath)

try:
    detector = cv2.dnn.readNetFromCaffe(f"{models_dir}/deploy.prototxt", f"{models_dir}/res10_300x300_ssd_iter_140000.caffemodel")
    embedder = cv2.dnn.readNetFromTorch(f"{models_dir}/openface_nn4.small2.v1.t7")
except Exception as e:
    st.error(f"❌ AI Core Loading Error: {e}")
    st.stop()

# --- Load Encodings & QR ---
ENCODINGS_FILE = "encodings.pickle"
qr_decoder = cv2.QRCodeDetector()

if not os.path.exists(ENCODINGS_FILE):
    st.warning("⚠️ Face data (encodings.pickle) missing! Only QR Code will work.")
    known_data = {"encodings": [], "names": []}
else:
    with open(ENCODINGS_FILE, "rb") as f:
        known_data = pickle.load(f)

# --- THE MASTER ATTENDANCE LOGIC ---
def process_attendance(name, method_used):
    ist_time = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist_time)
    now_time = now.time()
    
    morning_start, morning_late, morning_end = time(20, 0), time(20, 30), time(21, 30)
    evening_start, evening_end = time(22, 0), time(23, 0)

    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_str = now.strftime("%A")

    try:
        sheet = connect_to_sheets()
        existing_data = sheet.get_all_values()
        
        row_found, row_index = False, -1
        for i, row in enumerate(existing_data):
            if len(row) >= 2 and row[0] == name and row[1] == date_str:
                row_found, row_index = True, i + 1 
                break
                
        if morning_start <= now_time <= morning_end:
            if row_found:
                st.warning(f"⚠️ {name}, Morning IN already marked! ({method_used})")
            else:
                status = "Present" if now_time <= morning_late else "Late"
                if status == "Present": 
                    st.success(f"✅ {method_used} MATCHED: {name} (ON TIME!)"); st.balloons()
                else: 
                    st.warning(f"⏰ {method_used} MATCHED: {name} (LATE MARK!)")
                sheet.append_row([name, date_str, time_str, "---", day_str, status], value_input_option='USER_ENTERED')
                
        elif evening_start <= now_time <= evening_end:
            if not row_found:
                st.error(f"🔴 {name}, Morning attendance missing! Cannot mark OUT.")
            elif len(existing_data[row_index-1]) >= 4 and existing_data[row_index-1][3] != "---":
                st.warning(f"⚠️ {name}, Evening OUT time already marked! ({method_used})")
            else:
                sheet.update_cell(row_index, 4, time_str)
                st.success(f"✅ {method_used} MATCHED: {name} (EVENING OUT)")
        else:
            st.error(f"🔴 Scanned: {name}. Attendance window is CLOSED.")
            
    except Exception as e:
        st.error(f"❌ MAIN ERROR: {e}")

# --- Dual Scanner Input ---
img_file = st.camera_input("")

if img_file is not None:
    bytes_data = img_file.getvalue()
    frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    (h, w) = frame.shape[:2]

    # 1. TRY QR CODE FIRST
    qr_data, bbox, _ = qr_decoder.detectAndDecode(frame)
    if qr_data:
        process_attendance(qr_data, "QR CODE")
    
    # 2. IF NO QR, TRY 128-D FACE RECOGNITION
    else:
        imageBlob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=False, crop=False)
        detector.setInput(imageBlob)
        detections = detector.forward()

        face_matched = False
        if len(detections) > 0:
            i = np.argmax(detections[0, 0, :, 2])
            confidence = detections[0, 0, i, 2]
            
            if confidence > 0.5: # Face Found
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                startX, startY = max(0, startX), max(0, startY)
                endX, endY = min(w, endX), min(h, endY)
                
                face = frame[startY:endY, startX:endX]
                faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                vec = embedder.forward().flatten()
                
                # Compare 128-D Encodings
                name = "Unknown"
                min_dist = 0.6 # Tolerance Threshold
                
                if len(known_data["encodings"]) > 0:
                    for j, known_vec in enumerate(known_data["encodings"]):
                        dist = np.linalg.norm(vec - known_vec)
                        if dist < min_dist:
                            min_dist = dist
                            name = known_data["names"][j]

                if name != "Unknown":
                    process_attendance(name, "128-D FACE")
                    face_matched = True

        if not face_matched:
            st.warning("🔴 No valid Face or QR recognized. Please come closer.")
