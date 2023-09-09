import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

from freemocap_adapter.data_models.freemocap_data.freemocap_data_stats import FreemocapDataStats

logger = logging.getLogger(__name__)


@dataclass
class DataPaths:
    body_npy: Path
    right_hand_npy: Path
    left_hand_npy: Path
    face_npy: Path

    @classmethod
    def from_recording_folder(cls, path: str):
        recording_path = Path(path)
        output_data_path = recording_path / "output_data"
        return cls(
            body_npy=output_data_path / "mediapipe_body_3d_xyz.npy",
            right_hand_npy=output_data_path / "mediapipe_right_hand_3d_xyz.npy",
            left_hand_npy=output_data_path / "mediapipe_left_hand_3d_xyz.npy",
            face_npy=output_data_path / "mediapipe_face_3d_xyz.npy"
        )


@dataclass
class FreemocapData:
    body_fr_mar_xyz: np.ndarray
    right_hand_fr_mar_xyz: np.ndarray
    left_hand_fr_mar_xyz: np.ndarray
    face_fr_mar_xyz: np.ndarray

    data_source: str
    body_names: List[str]
    right_hand_names: List[str]
    left_hand_names: List[str]
    face_names: List[str]

    @property
    def number_of_frames(self):
        return self.body_fr_mar_xyz.shape[0]

    @property
    def number_of_body_markers(self):
        return self.body_fr_mar_xyz.shape[1]

    @property
    def number_of_right_hand_markers(self):
        return self.right_hand_fr_mar_xyz.shape[1]

    @property
    def number_of_left_hand_markers(self):
        return self.left_hand_fr_mar_xyz.shape[1]

    @property
    def number_of_face_markers(self):
        return self.face_fr_mar_xyz.shape[1]

    @property
    def number_of_hand_markers(self):
        if not self.number_of_right_hand_markers == self.number_of_left_hand_markers:
            logger.warning(f"Number of right hand markers ({self.number_of_right_hand_markers}) "
                           f"does not match number of left hand markers ({self.number_of_left_hand_markers}).")
        return self.number_of_right_hand_markers + self.number_of_left_hand_markers

    @property
    def number_of_markers(self):
        return (self.number_of_body_markers +
                self.number_of_right_hand_markers +
                self.number_of_left_hand_markers +
                self.number_of_face_markers)

    @classmethod
    def from_data(cls,
                  body_fr_mar_xyz: np.ndarray,
                  right_hand_fr_mar_xyz: np.ndarray,
                  left_hand_fr_mar_xyz: np.ndarray,
                  face_fr_mar_xyz: np.ndarray,
                  data_source: str = "mediapipe",
                  **kwargs) -> "FreemocapData":

        (body_names,
         face_names,
         left_hand_names,
         right_hand_names) = cls._create_trajecory_name_lists(data_source=data_source,
                                                              body_fr_mar_xyz=body_fr_mar_xyz,
                                                              right_hand_fr_mar_xyz=right_hand_fr_mar_xyz,
                                                              left_hand_fr_mar_xyz=left_hand_fr_mar_xyz,
                                                              face_fr_mar_xyz=face_fr_mar_xyz,
                                                              )
        instance = cls(
            body_fr_mar_xyz=body_fr_mar_xyz,
            right_hand_fr_mar_xyz=right_hand_fr_mar_xyz,
            left_hand_fr_mar_xyz=left_hand_fr_mar_xyz,
            face_fr_mar_xyz=face_fr_mar_xyz,
            data_source=data_source,
            body_names=body_names,
            right_hand_names=right_hand_names,
            left_hand_names=left_hand_names,
            face_names=face_names,
        )
        return instance

    @classmethod
    def from_data_paths(cls,
                        data_paths: DataPaths,
                        scale: float = 1000,
                        **kwargs):
        return cls.from_data(
            body_fr_mar_xyz=np.load(str(data_paths.body_npy)) / scale,
            right_hand_fr_mar_xyz=np.load(str(data_paths.right_hand_npy)) / scale,
            left_hand_fr_mar_xyz=np.load(str(data_paths.left_hand_npy)) / scale,
            face_fr_mar_xyz=np.load(str(data_paths.face_npy)) / scale,
            **kwargs
        )

    @classmethod
    def from_recording_path(cls,
                            recording_path: str,
                            **kwargs):
        data_paths = DataPaths.from_recording_folder(recording_path)
        logger.info(f"Loading data from paths {data_paths}")
        return cls.from_data_paths(data_paths=data_paths, **kwargs)

    @classmethod
    def _create_trajecory_name_lists(cls,
                                     data_source: str,
                                     body_fr_mar_xyz: np.ndarray,
                                     face_fr_mar_xyz: np.ndarray,
                                     left_hand_fr_mar_xyz: np.ndarray,
                                     right_hand_fr_mar_xyz: np.ndarray):
        if data_source == "mediapipe":
            from freemocap_adapter.data_models.mediapipe_names.trajectory_names import MEDIAPIPE_TRAJECTORY_NAMES
            body_names = MEDIAPIPE_TRAJECTORY_NAMES["body"]
            right_hand_names = [f"right_hand_{name}" for name in MEDIAPIPE_TRAJECTORY_NAMES["hand"]]
            left_hand_names = [f"left_hand_{name}" for name in MEDIAPIPE_TRAJECTORY_NAMES["hand"]]
            face_names = []
            for index in range(face_fr_mar_xyz.shape[1]):
                if index < len(MEDIAPIPE_TRAJECTORY_NAMES["face"]):
                    face_names.append(f"face_{MEDIAPIPE_TRAJECTORY_NAMES['face'][index]}")
                else:
                    face_names.append(f"face_{index}")
        else:
            logger.error(f"Data source {data_source} not recognized.")
            body_names = [f"body_{index}" for index in range(body_fr_mar_xyz.shape[1])]
            right_hand_names = [f"right_hand_{index}" for index in range(right_hand_fr_mar_xyz.shape[1])]
            left_hand_names = [f"left_hand_{index}" for index in range(left_hand_fr_mar_xyz.shape[1])]
            face_names = [f"face_{index}" for index in range(face_fr_mar_xyz.shape[1])]
            pass
        return body_names, face_names, left_hand_names, right_hand_names

    def __str__(self):
        return str(FreemocapDataStats.from_freemocap_data(self))


if __name__ == "__main__":
    from freemocap_adapter.core_functions.setup_scene.get_path_to_sample_data import get_path_to_sample_data

    recording_path = get_path_to_sample_data()
    freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path,
                                                       type="original")
    freemocap_data *= 2
    freemocap_data.mark_processing_stage("doubled")

    freemocap_data += 1e9
    freemocap_data.mark_processing_stage("added 1e9")

    freemocap_data -= 1e9
    freemocap_data.mark_processing_stage("subtracted 1e9")

    freemocap_data /= 2
    freemocap_data.mark_processing_stage("halved")

    freemocap_data.apply_rotation(np.eye(3).T)
    freemocap_data.mark_processing_stage("rotated")

    freemocap_data.apply_transform(np.eye(4).T)
    freemocap_data.mark_processing_stage("transformed")

    print(str(freemocap_data))
