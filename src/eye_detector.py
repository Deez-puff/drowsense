import numpy as np
from scipy.spatial import distance as dist

# ── Eye Landmark Indices (MediaPipe Face Mesh) ────────────
# These are specific point numbers MediaPipe assigns to eye corners/lids
LEFT_EYE_POINTS  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_POINTS = [33, 160, 158, 133, 153, 144]


def calculate_ear(eye_points, landmarks, frame_width, frame_height):
    """
    Calculates Eye Aspect Ratio (EAR) for one eye.

    EAR formula: distance between vertical eye points
                 divided by distance between horizontal eye points

    High EAR (~0.3+) = eye open
    Low EAR  (~0.2-) = eye closed
    """
    coords = []
    for idx in eye_points:
        lm = landmarks[idx]
        x = int(lm.x * frame_width)
        y = int(lm.y * frame_height)
        coords.append((x, y))

    # ── Vertical distances ─────────────────────────────────
    vertical_1 = dist.euclidean(coords[1], coords[5])
    vertical_2 = dist.euclidean(coords[2], coords[4])

    # ── Horizontal distance ────────────────────────────────
    horizontal = dist.euclidean(coords[0], coords[3])

    # ── EAR Formula ────────────────────────────────────────
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)

    return ear, coords


def get_average_ear(landmarks, frame_width, frame_height):
    """
    Calculates average EAR using both eyes.
    """
    left_ear, left_coords   = calculate_ear(LEFT_EYE_POINTS, landmarks, frame_width, frame_height)
    right_ear, right_coords = calculate_ear(RIGHT_EYE_POINTS, landmarks, frame_width, frame_height)

    avg_ear = (left_ear + right_ear) / 2.0

    return avg_ear, left_coords, right_coords


class DrowsinessTracker:
    """
    Tracks how long eyes have been closed across frames
    to determine if the driver is drowsy.
    """
    def __init__(self, ear_threshold=0.21, consecutive_frames=20):
        self.ear_threshold      = ear_threshold
        self.consecutive_frames = consecutive_frames
        self.counter             = 0
        self.is_drowsy            = False

    def update(self, ear):
        if ear < self.ear_threshold:
            self.counter += 1
            if self.counter >= self.consecutive_frames:
                self.is_drowsy = True
        else:
            self.counter   = 0
            self.is_drowsy = False

        return self.is_drowsy