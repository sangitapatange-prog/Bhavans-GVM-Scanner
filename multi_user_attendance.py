import cv2
import os
import numpy as np
import subprocess
import qrcode
import pickle
import urllib.request
import time # ⚡ NEW: Time library for automation

# ==========================================
# 📂 FOLDERS & AI MODELS SETUP
# ==========================================
if not os.path.exists('Teacher_QRs'): os.makedirs('Teacher_QRs')
if not os.path.exists('models'): os.makedirs('models')

files_to_download = {
    "deploy.prototxt": "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    "res10_300x300_ssd_iter_140000.caffemodel": "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel",
    "openface_nn4.small2.v1.t7": "https://raw.githubusercontent.com/pyannote/pyannote-data/master/openface.nn4.small2.v1.t7"
}

for filename, url in files_to_download.items():
    filepath = os.path.join("models", filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)

# --- LOAD DEEP LEARNING ENGINES ---
detector = cv2.dnn.readNetFromCaffe("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel")
embedder = cv2.dnn.readNetFromTorch("models/openface_nn4.small2.v1.t7")
ENCODINGS_FILE = "encodings.pickle"

# ==========================================
# ☁️ CLOUD SYNC & GOOGLE SHEETS
# ==========================================
def sync_to_cloud():
    print("\n[NETWORK] Pushing 128-D Encodings to GitHub...")
    try:
        subprocess.run(["git", "add", ENCODINGS_FILE, "names_mapping.txt", "Teacher_QRs/"], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-Sync: New Face Registered"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ [SUCCESS] Cloud updated! Streamlit will now recognize this person.")
    except Exception as e:
        print(f"❌ GitHub Push Error: {e}")

def load_names():
    names = {}
    if os.path.exists('names_mapping.txt'):
        with open('names_mapping.txt', 'r') as f:
            for line in f:
                if ',' in line:
                    id_str, name = line.strip().split(',')
                    names[int(id_str)] = name
    return names

def save_name(user_id, name):
    with open('names_mapping.txt', 'a') as f:
        f.write(f"{user_id},{name}\n")

# ==========================================
# 📸 AUTOMATED 10-SEC REGISTRATION ENGINE
# ==========================================
def register_face():
    names = load_names()
    name = input("\nEnter the Teacher/Staff Name: ")
    user_id = len(names) + 1
    save_name(user_id, name)
    
    # 1. BRAHMASTRA QR GENERATOR
    print(f"[SYSTEM] Generating Backup QR Code for {name}...")
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(name)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_filename = f"Teacher_QRs/{name}_QR.png"
    img.save(qr_filename)
    
    # 2. LOAD EXISTING ENCODINGS
    data = {"encodings": [], "names": []}
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)

    # 3. AUTO-TIMER CAPTURE LOGIC
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Auto AI Registration", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Auto AI Registration", cv2.WND_PROP_TOPMOST, 1)
    
    print(f"📸 Camera opening! Auto-capturing in 10 seconds...")
    
    start_time = time.time()
    timer_duration = 10 # ⚡ 10 Seconds setup time

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        elapsed_time = time.time() - start_time
        remaining_time = int(timer_duration - elapsed_time)
        
        # Display the visual countdown
        if remaining_time > 0:
            cv2.putText(frame, f"Adjust your face! Capturing in: {remaining_time}s", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            cv2.imshow("Auto AI Registration", frame)
            cv2.waitKey(1)
        
        # Timer hits 0 -> Capture and Process instantly
        else:
            cv2.putText(frame, "SCANNING NOW... PLEASE HOLD STILL!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Auto AI Registration", frame)
            cv2.waitKey(1)
            
            (h, w) = frame.shape[:2]
            imageBlob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=False, crop=False)
            detector.setInput(imageBlob)
            detections = detector.forward()

            face_found = False
            if len(detections) > 0:
                i = np.argmax(detections[0, 0, :, 2])
                confidence = detections[0, 0, i, 2]
                
                if confidence > 0.5:
                    face_found = True
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    startX, startY = max(0, startX), max(0, startY)
                    endX, endY = min(w, endX), min(h, endY)
                    face = frame[startY:endY, startX:endX]
                    
                    faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                    embedder.setInput(faceBlob)
                    vec = embedder.forward()

                    data["names"].append(name)
                    data["encodings"].append(vec.flatten())
                    
                    with open(ENCODINGS_FILE, "wb") as f:
                        pickle.dump(data, f)
                    
                    print(f"\n✅ [SUCCESS] 128-D Facial Blueprint locked for {name}!")
                    break # Exit loop instantly after successful capture
            
            # If no face is found at exactly 10 seconds, it will keep retrying every frame until it finds one.
            if not face_found:
                cv2.putText(frame, "No face detected! Look at camera...", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Auto AI Registration", frame)
                cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()
    
    # Push to cloud automatically
    sync_to_cloud()

if __name__ == "__main__":
    print("======================================================")
    print("   BHAVAN'S GVM - AUTO AI REGISTRATION ENGINE         ")
    print("      Engineered by: YATHARTH DESHMUKH                ")
    print("======================================================")
    print("1. Register New Staff (Face + QR)")
    choice = input("Enter choice (1): ")
    if choice == '1': register_face()