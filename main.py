import cv2
import mediapipe as mp
import sys
sys.path.append('src')
from eye_detector import get_average_ear, DrowsinessTracker
from yawn_detector import calculate_mar, YawnTracker
from distraction_detector import get_head_pose, DistractionTracker
from phone_detector import load_phone_model, detect_phone, PhoneUsageTracker
from alert_system import ArduinoAlert

# ── Initialize MediaPipe Face Mesh ────────────────────────
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ── Load YOLO Phone Detection Model ───────────────────────
print("⏳ Loading YOLO model...")
phone_model = load_phone_model()
print("✅ YOLO model loaded!")

# ── Connect to Arduino ────────────────────────────────────
arduino_alert = ArduinoAlert(port='COM7', baud_rate=9600)

# ── Initialize Trackers ───────────────────────────────────
drowsy_tracker       = DrowsinessTracker(ear_threshold=0.21, consecutive_frames=20)
yawn_tracker         = YawnTracker(mar_threshold=0.6, consecutive_frames=15)
distraction_tracker  = DistractionTracker(yaw_threshold=20, pitch_threshold=15, consecutive_frames=20)
phone_tracker        = PhoneUsageTracker(consecutive_frames=8)

# ── Open Webcam ────────────────────────────────────────────
cap = cv2.VideoCapture(0)
print("✅ Webcam opened! Press 'q' or ESC to quit")

frame_count = 0

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w  = frame.shape[:2]
    frame_count += 1

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results   = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # ── Eye Detection ──────────────────────────────────
        ear, left_coords, right_coords = get_average_ear(landmarks, w, h)
        is_drowsy = drowsy_tracker.update(ear)
        for (x, y) in left_coords + right_coords:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # ── Yawn Detection ─────────────────────────────────
        mar, mouth_coords = calculate_mar(landmarks, w, h)
        is_yawning = yawn_tracker.update(mar)
        for (x, y) in mouth_coords:
            cv2.circle(frame, (x, y), 2, (0, 200, 255), -1)

        # ── Head Pose / Distraction Detection ──────────────
        try:
            pitch, yaw, roll = get_head_pose(landmarks, w, h)
            is_distracted = distraction_tracker.update(pitch, yaw)
            direction      = distraction_tracker.get_direction(pitch, yaw)
        except Exception:
            is_distracted, direction = False, "Unknown"

        # ── Phone Detection (every 3rd frame for speed) ────
        if frame_count % 3 == 0:
            phone_detected, phone_boxes = detect_phone(phone_model, frame)
            is_using_phone = phone_tracker.update(phone_detected)
        else:
            phone_boxes = []
            is_using_phone = phone_tracker.is_using_phone

        # ── Draw Phone Bounding Boxes ───────────────────────
        for (x1, y1, x2, y2, conf) in phone_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(frame, f"Phone {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        # ── Display Values ─────────────────────────────────
        cv2.putText(frame, f"EAR: {ear:.3f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"MAR: {mar:.3f}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Yawns: {yawn_tracker.yawn_count}", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Head: {direction}", (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 255), 2)

        # ── Display Alerts ─────────────────────────────────
        y_offset = 170
        if is_drowsy:
            cv2.putText(frame, "DROWSY! WAKE UP!", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            y_offset += 40

        if is_yawning:
            cv2.putText(frame, "YAWNING DETECTED!", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 3)
            y_offset += 40

        if is_distracted:
            cv2.putText(frame, "DISTRACTED! EYES ON ROAD!", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 100, 255), 3)
            y_offset += 40

        if is_using_phone:
            cv2.putText(frame, "PHONE USAGE DETECTED!", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 255), 3)
            y_offset += 40

        # ── Trigger Arduino Buzzer ───────────────────────────
        any_alert = any([is_drowsy, is_yawning, is_distracted, is_using_phone])
        arduino_alert.update(any_alert)

        if not any_alert:
            cv2.putText(frame, "Status: Alert", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    else:
        cv2.putText(frame, "No Face Detected", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        arduino_alert.update(False)

    cv2.imshow("Driver Drowsiness Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

arduino_alert.close()
cap.release()
cv2.destroyAllWindows()
print("✅ Closed properly")