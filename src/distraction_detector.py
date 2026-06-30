import numpy as np
import cv2

# ── Key Landmark Points for Head Pose Estimation ──────────
NOSE_TIP    = 1
CHIN        = 199
LEFT_EYE    = 33
RIGHT_EYE   = 263
LEFT_MOUTH  = 61
RIGHT_MOUTH = 291


def get_head_pose(landmarks, frame_width, frame_height):
    """
    Estimates head pose (looking straight, left, right, up, down)
    using key facial landmarks and solvePnP.

    Returns the rotation angles (pitch, yaw, roll) in degrees.
    """
    # ── 2D Image Points (from detected landmarks) ─────────
    image_points = np.array([
        (landmarks[NOSE_TIP].x * frame_width,    landmarks[NOSE_TIP].y * frame_height),
        (landmarks[CHIN].x * frame_width,        landmarks[CHIN].y * frame_height),
        (landmarks[LEFT_EYE].x * frame_width,    landmarks[LEFT_EYE].y * frame_height),
        (landmarks[RIGHT_EYE].x * frame_width,   landmarks[RIGHT_EYE].y * frame_height),
        (landmarks[LEFT_MOUTH].x * frame_width,  landmarks[LEFT_MOUTH].y * frame_height),
        (landmarks[RIGHT_MOUTH].x * frame_width, landmarks[RIGHT_MOUTH].y * frame_height)
    ], dtype="double")

    # ── 3D Model Points (generic average face model) ──────
    model_points = np.array([
        (0.0, 0.0, 0.0),          # Nose tip
        (0.0, -330.0, -65.0),     # Chin
        (-225.0, 170.0, -135.0),  # Left eye
        (225.0, 170.0, -135.0),   # Right eye
        (-150.0, -150.0, -125.0), # Left mouth corner
        (150.0, -150.0, -125.0)   # Right mouth corner
    ])

    # ── Camera Matrix (approximate) ────────────────────────
    focal_length = frame_width
    center       = (frame_width / 2, frame_height / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    dist_coeffs = np.zeros((4, 1))

    # ── Solve for Rotation ──────────────────────────────────
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs
    )

    # ── Convert Rotation Vector to Angles ──────────────────
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    angles = cv2.RQDecomp3x3(rotation_matrix)[0]

    pitch, yaw, roll = angles[0], angles[1], angles[2]

# ── Normalize pitch (fixes 180° wraparound issue) ─────────
    if pitch > 90:
        pitch -= 180
    elif pitch < -90:
        pitch += 180

    return pitch, yaw, roll

class DistractionTracker:
    """
    Tracks head pose over time to detect if the driver
    is looking away from the road for too long.
    """
    def __init__(self, yaw_threshold=20, pitch_threshold=15, consecutive_frames=20):
        self.yaw_threshold       = yaw_threshold
        self.pitch_threshold     = pitch_threshold
        self.consecutive_frames  = consecutive_frames
        self.counter              = 0
        self.is_distracted         = False

    def update(self, pitch, yaw):
        looking_away = abs(yaw) > self.yaw_threshold or abs(pitch) > self.pitch_threshold

        if looking_away:
            self.counter += 1
            if self.counter >= self.consecutive_frames:
                self.is_distracted = True
        else:
            self.counter        = 0
            self.is_distracted   = False

        return self.is_distracted

    def get_direction(self, pitch, yaw):
        if yaw > self.yaw_threshold:
            return "Looking Right"
        elif yaw < -self.yaw_threshold:
            return "Looking Left"
        elif pitch > self.pitch_threshold:
            return "Looking Down"
        elif pitch < -self.pitch_threshold:
            return "Looking Up"
        else:
            return "Looking Straight"