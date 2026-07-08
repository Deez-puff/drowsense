# Drowsense

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-CV-orange?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-FaceMesh-green?style=for-the-badge)
![YOLO](https://img.shields.io/badge/YOLOv8-ObjectDetection-red?style=for-the-badge)
![Arduino](https://img.shields.io/badge/Arduino-Hardware-teal?style=for-the-badge&logo=arduino)
 
> A real-time computer vision system that detects driver drowsiness, yawning, distraction, and phone usage using webcam input, then triggers a physical buzzer alert through Arduino.

--- 

## Table of Contents  
- [About the Project](#about-the-project)
- [How It Works](#how-it-works)
- [Key Features](#key-features)
- [Hardware Setup](#hardware-setup)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup and Installation](#setup-and-installation)
- [How to Run](#how-to-run)
- [Detection Methods Explained](#detection-methods-explained)
- [Challenges and Solutions](#challenges-and-solutions)
- [Future Improvements](#future-improvements)

---

## About the Project

Driver fatigue and distraction are among the leading causes of road accidents worldwide. This project builds a real-time monitoring system that watches the driver through a webcam and detects four major risk behaviors:

- Eyes closing for extended periods (drowsiness/sleeping)
- Yawning (fatigue indicator)
- Head turning away from the road (distraction)
- Phone usage while driving

When any risk behavior is detected, the system triggers a physical buzzer connected to an Arduino board, providing an audible real-world alert rather than just an on-screen warning.

---

## How It Works

Webcam Feed
│
▼
┌─────────────────────┐
│  MediaPipe Face Mesh │  → Detects 468 facial landmarks
│                       │    in real time
└─────────────────────┘
│
├──────────────┬──────────────┬─────────────────┐
▼              ▼              ▼                 ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌─────────────┐
│ Eye      │   │ Mouth    │   │ Head Pose    │   │ YOLOv8      │
│ Aspect   │   │ Aspect   │   │ Estimation   │   │ Object      │
│ Ratio    │   │ Ratio    │   │ (solvePnP)   │   │ Detection   │
│ (EAR)    │   │ (MAR)    │   │              │   │ (Phone)     │
└──────────┘   └──────────┘   └──────────────┘   └─────────────┘
│              │              │                 │
▼              ▼              ▼                 ▼
Drowsiness     Yawning      Distraction         Phone Usage
Detected      Detected      Detected            Detected
│              │              │                 │
└──────────────┴──────────────┴─────────────────┘
│
▼
┌───────────────────────┐
│  Any Alert Triggered? │
└───────────────────────┘
│
▼
┌───────────────────────┐
│  Serial Signal to     │
│  Arduino (pyserial)   │
└───────────────────────┘
│
▼
┌───────────────────────┐
│  Physical Buzzer      │
│  Sounds (Pin 8)       │
└───────────────────────┘

---

## Key Features

| Feature | Description |
|---|---|
| 😴 Drowsiness Detection | Calculates Eye Aspect Ratio to detect prolonged eye closure |
| 🥱 Yawn Detection | Calculates Mouth Aspect Ratio to detect wide mouth opening |
| 👀 Distraction Detection | Uses head pose estimation (pitch/yaw) to detect looking away |
| 📱 Phone Usage Detection | YOLOv8 object detection identifies phones in frame |
| 🔢 Live Yawn Counter | Tracks total number of yawns during a session |
| 🔊 Physical Buzzer Alert | Arduino-controlled buzzer sounds on any detected risk behavior |
| 📹 Real-Time Dashboard | Live webcam feed with EAR, MAR, head direction, and alerts overlaid |
| ⚡ Frame-Skip Optimization | YOLO runs every 3rd frame to maintain smooth real-time performance |

---

## Hardware Setup

### Components Required
- Arduino Uno (or compatible board)
- Passive or active buzzer
- Jumper wires
- USB cable (Arduino to computer)

### Wiring

| Buzzer Pin | Arduino Pin |
|---|---|
| Positive (+) | Digital Pin 8 |
| Negative (−) | GND |

### Arduino Code

Upload this sketch to your Arduino via the Arduino IDE before running the Python application:

```cpp
const int buzzerPin = 8;

void setup() {
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
  digitalWrite(buzzerPin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();
    if (signal == '1') {
      digitalWrite(buzzerPin, HIGH);
    }
    else if (signal == '0') {
      digitalWrite(buzzerPin, LOW);
    }
  }
}
```

After uploading, note the COM port assigned to your Arduino (visible in Arduino IDE under Tools → Port) and update it in `main.py`.

---

## Project Structure
driver-drowsiness-detection/
│
├── src/                              ← Core detection modules
│  
│   ├── eye_detector.py               ← EAR calculation, drowsiness tracking
│   ├── yawn_detector.py              ← MAR calculation, yawn tracking
│   ├── distraction_detector.py       ← Head pose estimation, distraction tracking
│   ├── phone_detector.py             ← YOLOv8 phone detection
│   └── alert_system.py               ← Arduino serial communication
│
├── main.py                           ← Main application, combines all detections
├── requirements.txt                  ← Python dependencies
├── .gitignore                        ← Files excluded from Git
└── README.md                         ← Project documentation

---

## Tech Stack

| Category | Tools Used |
|---|---|
| Language | Python 3.11 |
| Computer Vision | OpenCV |
| Facial Landmark Detection | MediaPipe Face Mesh |
| Object Detection | YOLOv8 (Ultralytics) |
| Math / Geometry | NumPy, SciPy |
| Hardware Communication | PySerial |
| Hardware | Arduino Uno, Buzzer |

---

## Setup and Installation

### 1 — Clone the Repository
git clone https://github.com/Deez-puff/driver-drowsiness-detection.git
cd driver-drowsiness-detection

### 2 — Create a Python 3.11 Virtual Environment

This project requires Python 3.11 specifically, as MediaPipe's legacy Face Mesh API (`mediapipe.solutions`) is not available on newer Python versions like 3.13/3.14.
py -3.11 -m venv venv311
venv311\Scripts\activate

### 3 — Install Dependencies
pip install -r requirements.txt

### 4 — Upload Arduino Code
Open Arduino IDE, paste the sketch from the Hardware Setup section above, select your board and COM port, and click Upload.

### 5 — Update COM Port in main.py
Open `main.py` and update this line with your Arduino's COM port:
```python
arduino_alert = ArduinoAlert(port='COM7', baud_rate=9600)
```

---

## How to Run
venv311\Scripts\activate
python main.py

A window will open showing your live webcam feed with detection overlays. Press `q` or `ESC` to quit.

---

## Detection Methods Explained

### Eye Aspect Ratio (EAR) — Drowsiness Detection
EAR measures the ratio between vertical and horizontal eye landmark distances. When eyes close, the vertical distance shrinks while horizontal stays constant, causing EAR to drop. If EAR stays below 0.21 for 20 consecutive frames, drowsiness is flagged.

### Mouth Aspect Ratio (MAR) — Yawn Detection
MAR measures the ratio between vertical mouth opening and horizontal mouth width. A wide open mouth (yawning) produces a high MAR. If MAR exceeds 0.6 for 15 consecutive frames, a yawn is counted.

### Head Pose Estimation — Distraction Detection
Using six key facial landmarks (nose tip, chin, eye corners, mouth corners) combined with OpenCV's `solvePnP` function, the system calculates pitch and yaw angles representing head rotation. If yaw exceeds 20 degrees or pitch exceeds 15 degrees for 20 consecutive frames, distraction is flagged.

### YOLOv8 — Phone Usage Detection
A pretrained YOLOv8 model (trained on the COCO dataset) detects objects in each frame. If a "cell phone" object (class ID 67) is detected with confidence above 0.4 for 8 consecutive checks, phone usage is flagged.

### Arduino Buzzer Trigger
When any of the four detections is active, Python sends a '1' signal over serial (USB) to the Arduino, which turns on a buzzer connected to digital pin 8. When all alerts clear, a '0' signal turns the buzzer off.

---

## Challenges and Solutions

| Challenge | Solution |
|---|---|
| MediaPipe's `solutions` API missing on Python 3.14 | Created a dedicated Python 3.11 virtual environment, since MediaPipe's legacy API isn't published for very new Python versions |
| Head pose pitch reading ~178° when looking straight | Identified a 180° wraparound issue in OpenCV's `RQDecomp3x3` output and normalized the pitch value |
| YOLO slowing down real-time performance | Ran YOLO inference only every 3rd frame instead of every frame, maintaining smooth video while still catching phone usage |
| `playsound` library failing to install on Python 3.14 | Switched to Arduino-based physical buzzer alerts instead of software audio, which also made the project more hardware-realistic |

---

## Future Improvements

- [ ] Add data logging to record alert history with timestamps
- [ ] Add a seatbelt detection module
- [ ] Replace single-tone buzzer with different beep patterns per alert type
- [ ] Add a mobile app dashboard for fleet monitoring
- [ ] Train a custom YOLO model specifically for in-car phone usage patterns
- [ ] Add driver identification using face recognition for personalized calibration
- [ ] Package as a standalone desktop application with installer

---

## Author
Deepak Rajesh

Built as part of a personal AI/Computer Vision project — combining facial landmark analysis, object detection, and embedded hardware integration.

---

## License

This project is open source and available under the MIT License.
