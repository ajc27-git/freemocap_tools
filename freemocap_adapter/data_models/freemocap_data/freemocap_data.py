from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from freemocap_adapter.data_models.freemocap_data.freemocap_data_stats import FreemocapDataStats




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


#TODO - need to break this up into a simple data class and a class that handles the operations.
@dataclass
class FreemocapData:
    body_fr_mar_xyz: np.ndarray
    right_hand_fr_mar_xyz: np.ndarray
    left_hand_fr_mar_xyz: np.ndarray
    face_fr_mar_xyz: np.ndarray

    _intermediate_stages = None

    @classmethod
    def from_data(cls,
                  body_fr_mar_xyz: np.ndarray,
                  right_hand_fr_mar_xyz: np.ndarray,
                  left_hand_fr_mar_xyz: np.ndarray,
                  face_fr_mar_xyz: np.ndarray,
                  type: str = "original_from_file",
                  **kwargs) -> "FreemocapData":
        instance = cls(
            body_fr_mar_xyz=body_fr_mar_xyz,
            right_hand_fr_mar_xyz=right_hand_fr_mar_xyz,
            left_hand_fr_mar_xyz=left_hand_fr_mar_xyz,
            face_fr_mar_xyz=face_fr_mar_xyz)
        instance.mark_processing_stage(type)
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
        return cls.from_data_paths(data_paths=data_paths, **kwargs)

    def mark_processing_stage(self, name: str):
        """
        Mark the current state of the data as a processing stage (e.g. "raw", "reoriented", etc.)
        """
        if self._intermediate_stages is None:
            self._intermediate_stages = {}

        self._intermediate_stages[name] = deepcopy(self.__dict__)

    def get_processing_stage(self, name: str) -> "FreemocapData":
        """
        Get the data from a processing stage (e.g. "raw", "reoriented", etc.)
        """
        if self._intermediate_stages is None:
            raise ValueError("No processing stages have been marked yet.")

        return FreemocapData.from_data(**self._intermediate_stages[name])

    def __str__(self):
        return_strings = []
        for key in self._intermediate_stages.keys():
            label = f"Processing stage: {key}\n"
            label += f"{str(FreemocapDataStats.from_freemocap_data(self.get_processing_stage(name=key)))}"
            return_strings.append(label)

        return "\n".join(return_strings)

    def __add__(self, other:float):
        self.body_fr_mar_xyz += other
        self.right_hand_fr_mar_xyz += other
        self.left_hand_fr_mar_xyz += other
        self.face_fr_mar_xyz += other
        return self

    def __sub__(self, other:float):
        self.body_fr_mar_xyz -= other
        self.right_hand_fr_mar_xyz -= other
        self.left_hand_fr_mar_xyz -= other
        self.face_fr_mar_xyz -= other
        return self

    def __mul__(self, other:float):
        self.body_fr_mar_xyz *= other
        self.right_hand_fr_mar_xyz *= other
        self.left_hand_fr_mar_xyz *= other
        self.face_fr_mar_xyz *= other
        return self

    def __truediv__(self, number: float):
        # Check if the number is not zero (to avoid division by zero)
        if number != 0:
            # Perform division
            body_fr_mar_xyz = self.body_fr_mar_xyz / number
            right_hand_fr_mar_xyz = self.right_hand_fr_mar_xyz / number
            left_hand_fr_mar_xyz = self.left_hand_fr_mar_xyz / number
            face_fr_mar_xyz = self.face_fr_mar_xyz / number

            # Create a new FreemocapData instance with the divided matrices and return
            return FreemocapData(body_fr_mar_xyz, right_hand_fr_mar_xyz, left_hand_fr_mar_xyz, face_fr_mar_xyz)

        else:
            print("Error: Division by zero.")
            return self  # Just return the current instance as is

    def _rotate_data(self, data, rotation_matrix):
        return np.dot(data, rotation_matrix.T)

    def apply_rotation(self, rotation_matrix):
        self.body_fr_mar_xyz = self._rotate_data(self.body_fr_mar_xyz, rotation_matrix)
        self.right_hand_fr_mar_xyz = self._rotate_data(self.right_hand_fr_mar_xyz, rotation_matrix)
        self.left_hand_fr_mar_xyz = self._rotate_data(self.left_hand_fr_mar_xyz, rotation_matrix)
        self.face_fr_mar_xyz = self._rotate_data(self.face_fr_mar_xyz, rotation_matrix)

    def apply_transform(self, transform):
        # Separate rotation matrix and translation vector
        rotation_matrix = transform[:3, :3]
        translation_vector = transform[:3, 3]

        # Apply rotation
        self.apply_rotation(rotation_matrix)

        # Apply translation
        self += translation_vector


if __name__ == "__main__":
    from freemocap_adapter.core_functions.load_data.get_path_to_sample_data import get_path_to_sample_data

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
