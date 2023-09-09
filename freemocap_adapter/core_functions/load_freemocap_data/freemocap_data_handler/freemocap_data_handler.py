from copy import deepcopy

import numpy as np

from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData
from freemocap_adapter.data_models.freemocap_data.freemocap_data_stats import FreemocapDataStats


class FreemocapDataHandler:
    def __init__(self, freemocap_data: FreemocapData):
        self.freemocap_data = freemocap_data
        self._intermediate_stages = None

    def mark_processing_stage(self, name: str, overwrite: bool = True):
        """
        Mark the current state of the data as a processing stage (e.g. "raw", "reoriented", etc.)
        """
        if self._intermediate_stages is None:
            self._intermediate_stages = {}
        if name in self._intermediate_stages.keys() and not overwrite:
            raise ValueError(f"Processing stage {name} already exists. Set overwrite=True to overwrite.")
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

    def __add__(self, other: float):
        self.body_fr_mar_xyz += other
        self.right_hand_fr_mar_xyz += other
        self.left_hand_fr_mar_xyz += other
        self.face_fr_mar_xyz += other
        return self

    def __sub__(self, other: float):
        self.body_fr_mar_xyz -= other
        self.right_hand_fr_mar_xyz -= other
        self.left_hand_fr_mar_xyz -= other
        self.face_fr_mar_xyz -= other
        return self

    def __mul__(self, other: float):
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
            return FreemocapData(body_fr_mar_xyz=body_fr_mar_xyz,
                                 right_hand_fr_mar_xyz=right_hand_fr_mar_xyz,
                                 left_hand_fr_mar_xyz=left_hand_fr_mar_xyz,
                                 face_fr_mar_xyz=face_fr_mar_xyz,
                                 data_source=self.data_source,
                                 body_names=self.body_names,
                                 right_hand_names=self.right_hand_names,
                                 left_hand_names=self.left_hand_names,
                                 face_names=self.face_names,
                                 )

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
