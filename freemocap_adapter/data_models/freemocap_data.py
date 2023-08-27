from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class DataPaths:
    body_npy: Path
    right_hand_npy: Path
    left_hand_npy: Path
    face_npy: Path

    @classmethod
    def from_recording_folder(cls, path:str):
        recording_path = Path(path)
        output_data_path = recording_path / "output_data"
        return cls(
        body_npy = output_data_path / "mediapipe_body_3d_xyz.npy",
        right_hand_npy = output_data_path / "mediapipe_right_hand_3d_xyz.npy",
        left_hand_npy = output_data_path / "mediapipe_left_hand_3d_xyz.npy",
        face_npy = output_data_path / "mediapipe_face_3d_xyz.npy"
        )


@dataclass
class FreeMoCapData:
    body_fr_mar_xyz: np.ndarray
    right_hand_fr_mar_xyz: np.ndarray
    left_hand_fr_mar_xyz: np.ndarray
    face_fr_mar_xyz: np.ndarray

    @classmethod
    def from_data_paths(cls, data_paths: DataPaths, scale: float = 1000):
        return cls(
            body_fr_mar_xyz=np.load(str(data_paths.body_npy)) / scale,
            right_hand_fr_mar_xyz=np.load(str(data_paths.right_hand_npy)) / scale,
            left_hand_fr_mar_xyz=np.load(str(data_paths.left_hand_npy)) / scale,
            face_fr_mar_xyz=np.load(str(data_paths.face_npy)) / scale,
        )

    @classmethod
    def from_recording_path(cls, recording_path: str, scale: float = 1000):
        data_paths = DataPaths.from_recording_folder(recording_path)
        return cls.from_data_paths(data_paths=data_paths, scale=scale)
