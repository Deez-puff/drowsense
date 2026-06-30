from ultralytics import YOLO

# ── COCO Class ID for Cell Phone ──────────────────────────
PHONE_CLASS_ID = 67   # 'cell phone' in YOLO's default COCO classes


def load_phone_model():
    """
    Loads the pretrained YOLOv8 model.
    Downloads automatically the first time it's used.
    """
    model = YOLO('yolov8n.pt')
    return model


def detect_phone(model, frame, confidence_threshold=0.4):
    """
    Runs YOLO detection on a frame and checks if a phone is present.

    Returns:
        phone_detected (bool)
        boxes (list of bounding boxes for drawing)
    """
    results = model(frame, verbose=False)

    phone_detected = False
    boxes = []

    for result in results:
        for box in result.boxes:
            class_id   = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id == PHONE_CLASS_ID and confidence > confidence_threshold:
                phone_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((x1, y1, x2, y2, confidence))

    return phone_detected, boxes


class PhoneUsageTracker:
    """
    Tracks how long a phone has been visible in frame
    to confirm phone usage (avoids false positives from a quick flash).
    """
    def __init__(self, consecutive_frames=8):
        self.consecutive_frames = consecutive_frames
        self.counter              = 0
        self.is_using_phone        = False

    def update(self, phone_detected):
        if phone_detected:
            self.counter += 1
            if self.counter >= self.consecutive_frames:
                self.is_using_phone = True
        else:
            self.counter        = 0
            self.is_using_phone   = False

        return self.is_using_phone