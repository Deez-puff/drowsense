from scipy.spatial import distance as dist

# ── Mouth Landmark Indices (MediaPipe Face Mesh) ──────────
# Points around the outer lips
MOUTH_POINTS = [13, 14, 78, 308, 311, 81]
# 13 = upper lip center, 14 = lower lip center
# 78 = left corner, 308 = right corner
# 311, 81 = additional upper/lower points for accuracy


def calculate_mar(landmarks, frame_width, frame_height):
    """
    Calculates Mouth Aspect Ratio (MAR).

    High MAR (~0.6+) = mouth wide open (yawning)
    Low MAR  (~0.3-) = mouth closed/normal talking
    """
    coords = []
    for idx in MOUTH_POINTS:
        lm = landmarks[idx]
        x = int(lm.x * frame_width)
        y = int(lm.y * frame_height)
        coords.append((x, y))

    # ── Vertical distance (upper lip to lower lip) ────────
    vertical = dist.euclidean(coords[0], coords[1])

    # ── Horizontal distance (left corner to right corner) ──
    horizontal = dist.euclidean(coords[2], coords[3])

    # ── MAR Formula ────────────────────────────────────────
    mar = vertical / horizontal

    return mar, coords


class YawnTracker:
    """
    Tracks how long the mouth has been open wide
    to determine if the driver is yawning.
    """
    def __init__(self, mar_threshold=0.6, consecutive_frames=15):
        self.mar_threshold      = mar_threshold
        self.consecutive_frames = consecutive_frames
        self.counter             = 0
        self.is_yawning           = False
        self.yawn_count            = 0
        self._already_counted      = False

    def update(self, mar):
        if mar > self.mar_threshold:
            self.counter += 1
            if self.counter >= self.consecutive_frames:
                self.is_yawning = True
                if not self._already_counted:
                    self.yawn_count += 1
                    self._already_counted = True
        else:
            self.counter        = 0
            self.is_yawning      = False
            self._already_counted = False

        return self.is_yawning