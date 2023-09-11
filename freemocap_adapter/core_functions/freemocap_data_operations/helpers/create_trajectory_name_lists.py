import logging

import numpy as np

logger = logging.getLogger(__name__)


def create_trajectory_name_lists(data_source: str,
                                 body_frame_name_xyz: np.ndarray,
                                 face_frame_name_xyz: np.ndarray,
                                 left_hand_frame_name_xyz: np.ndarray,
                                 right_hand_frame_name_xyz: np.ndarray):
    body_names = [f"body_{index}" for index in range(body_frame_name_xyz.shape[1])]
    right_hand_names = [f"right_hand_{index}" for index in range(right_hand_frame_name_xyz.shape[1])]
    left_hand_names = [f"left_hand_{index}" for index in range(left_hand_frame_name_xyz.shape[1])]
    face_names = [f"face_{index}" for index in range(face_frame_name_xyz.shape[1])]

    if data_source == "mediapipe":
        from freemocap_adapter.data_models.mediapipe_names.trajectory_names import MEDIAPIPE_TRAJECTORY_NAMES

        for index, name in enumerate(MEDIAPIPE_TRAJECTORY_NAMES["body"]):
            body_names[index] = f"{name}"

        for index, name in enumerate(MEDIAPIPE_TRAJECTORY_NAMES["hand"]):
            right_hand_names[index] = f"right_hand_{name}"
            left_hand_names[index] = f"left_hand_{name}"

        for index, name in enumerate(MEDIAPIPE_TRAJECTORY_NAMES["face"]):
            face_names[index] = f"{name}"
    else:
        logger.error(f"Data source {data_source} not recognized.")
        pass
    return body_names, face_names, left_hand_names, right_hand_names
