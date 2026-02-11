import cv2
import numpy as np
from mediapipe import solutions
import time

# ---------------------------
# Session state
# ---------------------------

SESSION_STATE = {}

def get_state(session_id: int):
    if session_id not in SESSION_STATE:
        SESSION_STATE[session_id] = {
            "away_start": None,
            "last_event": 0.0,
            "yaw_ema": 0.0,
            "pitch_ema": 0.0
        }
    return SESSION_STATE[session_id]


# ---------------------------
# MediaPipe setup
# ---------------------------

face_detection = solutions.face_detection
face_mesh_module = solutions.face_mesh

face_detector = face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

face_mesh = face_mesh_module.FaceMesh(
    static_image_mode=False,
    refine_landmarks=True,
    max_num_faces=1
)

LANDMARK_IDS = [33, 263, 1, 61, 291, 199]

MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),        # Nose tip
    (0.0, -63.6, -12.5),   # Chin
    (-43.3, 32.7, -26.0),  # Left eye
    (43.3, 32.7, -26.0),   # Right eye
    (-28.9, -28.9, -24.1), # Left mouth
    (28.9, -28.9, -24.1)   # Right mouth
], dtype=np.float64)


# ---------------------------
# Head pose estimation
# ---------------------------

def is_looking_away(frame, landmarks):
    h, w, _ = frame.shape

    image_points = []
    for idx in LANDMARK_IDS:
        lm = landmarks[idx]
        image_points.append((lm.x * w, lm.y * h))

    image_points = np.array(image_points, dtype=np.float64)

    focal_length = w
    center = (w / 2, h / 2)

    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))

    success, rotation_vector, _ = cv2.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not success:
        return False, 0.0, 0.0

    rmat, _ = cv2.Rodrigues(rotation_vector)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

    pitch = angles[0] * 180.0
    yaw = angles[1] * 180.0

    looking_away = abs(yaw) > 20 or abs(pitch) > 15

    return looking_away, yaw, pitch


# ---------------------------
# Main analysis
# ---------------------------

def analyze_frame(image_bytes: bytes, session_id: int):
    if not image_bytes:
        return [("NO_FRAME_RECEIVED", 1)]

    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return [("INVALID_IMAGE", 1)]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    events = []

    state = get_state(session_id)
    now = time.time()

    # ---- Face detection ----
    fd_results = face_detector.process(rgb)

    if not fd_results.detections:
        return [("NO_FACE", 1)]

    detection = fd_results.detections[0]
    confidence = float(detection.score[0])

    if confidence < 0.7:
        return []

    if len(fd_results.detections) > 1:
        events.append(("MULTIPLE_FACES", 1))

    # ---- Head pose ----
    mesh_results = face_mesh.process(rgb)

    if not mesh_results.multi_face_landmarks:
        return events

    landmarks = mesh_results.multi_face_landmarks[0].landmark

    looking_away, yaw, pitch = is_looking_away(frame, landmarks)

    # ---- EMA smoothing ----
    state["yaw_ema"] = 0.7 * state["yaw_ema"] + 0.3 * yaw
    state["pitch_ema"] = 0.7 * state["pitch_ema"] + 0.3 * pitch

    yaw_s = state["yaw_ema"]
    pitch_s = state["pitch_ema"]

    away_now = abs(yaw_s) > 20 or abs(pitch_s) > 15

    # ---- Temporal logic ----
    if away_now:
        if state["away_start"] is None:
            state["away_start"] = now
    else:
        state["away_start"] = None
        return events

    duration = now - state["away_start"]

    if duration >= 2.5 and now - state["last_event"] > 10:
        events.append(("LOOKING_AWAY", 1))
        state["last_event"] = now

    return events
