import logging
from copy import deepcopy
from typing import List, Union, Literal, Dict, Any

import numpy as np

from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

FREEMOCAP_DATA_COMPONENT_TYPES = Literal["body", "right_hand", "left_hand", "face", "other"]

logger = logging.getLogger(__name__)


class FreemocapDataHandler:
    def __init__(self,
                 freemocap_data: FreemocapData):
        self.freemocap_data = freemocap_data
        self._intermediate_stages = None

    def get_trajectories(self,
                         trajectory_names: List[str],
                         components: Union[
                             List[FREEMOCAP_DATA_COMPONENT_TYPES], FREEMOCAP_DATA_COMPONENT_TYPES] = None) -> Dict[
        str, np.ndarray]:

        trajectories = {}
        if not isinstance(trajectory_names, list):
            trajectory_names = [trajectory_names]
        if components is None or isinstance(components, list):
            components = [components] * len(trajectory_names)

        for trajectory_name, component in zip(trajectory_names, components):
            trajectories[trajectory_name] = self.get_trajectory(trajectory_name, component)

        return trajectories

    def get_trajectory(self,
                       trajectory_name: str,
                       component: Literal["body", "right_hand", "left_hand", "face", "other"] = None):
        trajectories = []
        if component is None:
            if trajectory_name in self.body_names:
                trajectories.append(self.body_frame_name_xyz[:, self.body_names.index(trajectory_name)])

            if trajectory_name in self.right_hand_names:
                trajectories.append(self.right_hand_frame_name_xyz[:, self.right_hand_names.index(trajectory_name)])

            if trajectory_name in self.left_hand_names:
                trajectories.append(self.left_hand_frame_name_xyz[:, self.left_hand_names.index(trajectory_name)])

            if trajectory_name in self.face_names:
                trajectories.append(self.face_frame_name_xyz[:, self.face_names.index(trajectory_name)])

            for other_component in self.freemocap_data.other:
                if trajectory_name in other_component.trajectory_names:
                    trajectories.append(
                        other_component.data_frame_name_xyz[:, other_component.trajectory_names.index(trajectory_name)])
        if trajectories == []:
            raise ValueError(f"Trajectory {trajectory_name} not found.")
        if len(trajectories) > 1:
            raise ValueError(
                f"Trajectory {trajectory_name} found in multiple components. Specify component (body, right_hand, left_hand, face, other) to resolve ambiguity.")

        return trajectories[0]

    @property
    def metadata(self) -> Dict[Any, Any]:
        return self.freemocap_data.metadata
    @property
    def trajectories(self) -> Dict[str, np.ndarray]:
        trajectories = {}
        trajectories.update(self.body_trajectories)
        trajectories.update(self.right_hand_trajectories)
        trajectories.update(self.left_hand_trajectories)
        trajectories.update(self.face_trajectories)
        trajectories.update(self.other_trajectories)
        return trajectories

    @property
    def body_trajectories(self) -> Dict[str, np.ndarray]:
        return {trajectory_name: self.body_frame_name_xyz[:, trajectory_number]
                for trajectory_number, trajectory_name in enumerate(self.body_names)}

    @property
    def right_hand_trajectories(self) -> Dict[str, np.ndarray]:
        return {trajectory_name: self.right_hand_frame_name_xyz[:, trajectory_number]
                for trajectory_number, trajectory_name in enumerate(self.right_hand_names)}

    @property
    def left_hand_trajectories(self) -> Dict[str, np.ndarray]:
        return {trajectory_name: self.left_hand_frame_name_xyz[:, trajectory_number]
                for trajectory_number, trajectory_name in enumerate(self.left_hand_names)}

    @property
    def face_trajectories(self) -> Dict[str, np.ndarray]:
        return {trajectory_name: self.face_frame_name_xyz[:, trajectory_number]
                for trajectory_number, trajectory_name in enumerate(self.face_names)}

    @property
    def other_trajectories(self) -> Dict[str, np.ndarray]:
        trajectories = {}
        for component in self.freemocap_data.other:
            trajectories.update({trajectory_name: component.data_frame_name_xyz[:, trajectory_number]
                                 for trajectory_number, trajectory_name in enumerate(component.trajectory_names)})
        return trajectories

    @property
    def body_frame_name_xyz(self):
        return self.freemocap_data.body.data_frame_name_xyz

    @body_frame_name_xyz.setter
    def body_frame_name_xyz(self, value):
        if value.shape != self.body_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new body data ({value.shape}) does not match shape of old body data ({self.body_frame_name_xyz.shape}).")
        self.freemocap_data.body.data_frame_name_xyz = value

    @property
    def right_hand_frame_name_xyz(self):
        return self.freemocap_data.hands["right"].data_frame_name_xyz

    @right_hand_frame_name_xyz.setter
    def right_hand_frame_name_xyz(self, value):
        if value.shape != self.right_hand_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new right hand data ({value.shape}) does not match shape of old right hand data ({self.right_hand_frame_name_xyz.shape}).")
        self.freemocap_data.hands["right"].data_frame_name_xyz = value

    @property
    def left_hand_frame_name_xyz(self):
        return self.freemocap_data.hands["left"].data_frame_name_xyz

    @left_hand_frame_name_xyz.setter
    def left_hand_frame_name_xyz(self, value):
        if value.shape != self.left_hand_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new left hand data ({value.shape}) does not match shape of old left hand data ({self.left_hand_frame_name_xyz.shape}).")
        self.freemocap_data.hands["left"].data_frame_name_xyz = value

    @property
    def face_frame_name_xyz(self):
        return self.freemocap_data.face.data_frame_name_xyz

    @face_frame_name_xyz.setter
    def face_frame_name_xyz(self, value):
        if value.shape != self.face_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new face data ({value.shape}) does not match shape of old face data ({self.face_frame_name_xyz.shape}).")
        self.freemocap_data.face.data_frame_name_xyz = value

    @property
    def body_names(self):
        return self.freemocap_data.body.trajectory_names

    @property
    def right_hand_names(self):
        return self.freemocap_data.hands["right"].trajectory_names

    @property
    def left_hand_names(self):
        return self.freemocap_data.hands["left"].trajectory_names

    @property
    def face_names(self):
        return self.freemocap_data.face.trajectory_names

    @property
    def number_of_frames(self):
        return self.body_frame_name_xyz.shape[0]

    @property
    def number_of_body_trajectories(self):
        return self.body_frame_name_xyz.shape[1]

    @property
    def number_of_right_hand_trajectories(self):
        return self.right_hand_frame_name_xyz.shape[1]

    @property
    def number_of_left_hand_trajectories(self):
        return self.left_hand_frame_name_xyz.shape[1]

    @property
    def number_of_face_trajectories(self):
        return self.face_frame_name_xyz.shape[1]

    @property
    def number_of_hand_trajectories(self):
        if not self.number_of_right_hand_trajectories == self.number_of_left_hand_trajectories:
            logger.warning(f"Number of right hand trajectories ({self.number_of_right_hand_trajectories}) "
                           f"does not match number of left hand trajectories ({self.number_of_left_hand_trajectories}).")
        return self.number_of_right_hand_trajectories + self.number_of_left_hand_trajectories

    @property
    def number_of_trajectories(self):
        return (self.number_of_body_trajectories +
                self.number_of_right_hand_trajectories +
                self.number_of_left_hand_trajectories +
                self.number_of_face_trajectories)

    def mark_processing_stage(self,
                              name: str,
                              metadata: dict = None,
                              overwrite: bool = True):
        """
        Mark the current state of the data as a processing stage (e.g. "raw", "reoriented", etc.)
        """
        logger.info(f"Marking processing stage {name}")
        if self._intermediate_stages is None:
            self._intermediate_stages = {}
        if metadata is None:
            metadata = {}
        if name in self._intermediate_stages.keys() and not overwrite:
            raise ValueError(f"Processing stage {name} already exists. Set overwrite=True to overwrite.")
        self._intermediate_stages[name] = FreemocapData(**deepcopy(self.freemocap_data.__dict__))

    def get_processing_stage(self, name: str) -> "FreemocapData":
        """
        Get the data from a processing stage (e.g. "raw", "reoriented", etc.)
        """
        if self._intermediate_stages is None:
            raise ValueError("No processing stages have been marked yet.")

        return FreemocapData.from_data(**self._intermediate_stages[name])

    def __str__(self):
        return str(self.freemocap_data)

    def _rotate_component(self,
                          data_frame_name_xyz: Union[np.ndarray, List[float]],
                          rotation_matrix: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        if isinstance(data_frame_name_xyz, list):
            data_frame_name_xyz = np.array(data_frame_name_xyz)
        if isinstance(rotation_matrix, list):
            rotation_matrix = np.array(rotation_matrix)

        if rotation_matrix.shape != (3, 3):
            raise ValueError(f"Rotation matrix must be a 3x3 matrix. Got {rotation_matrix.shape} instead.")

        if data_frame_name_xyz.shape[2] == 2:
            logger.info(f"2D data detected. Adding a third dimension with zeros.")
            data_frame_name_xyz = np.concatenate(
                [data_frame_name_xyz, np.zeros((data_frame_name_xyz.shape[0], data_frame_name_xyz.shape[1], 1))],
                axis=2)

        rotated_data_frame_name_xyz = np.zeros(data_frame_name_xyz.shape)
        for frame_number in range(data_frame_name_xyz.shape[0]):
            for trajectory_number in range(data_frame_name_xyz.shape[1]):
                rotated_data_frame_name_xyz[frame_number, trajectory_number, :] = rotation_matrix @ data_frame_name_xyz[
                                                                                            frame_number,
                                                                                            trajectory_number,
                                                                                            :]
        return rotated_data_frame_name_xyz

    def apply_rotation(self, rotation_matrix: Union[np.ndarray, List[List[float]]]):
        if isinstance(rotation_matrix, list):
            rotation_matrix = np.array(rotation_matrix)
        if rotation_matrix.shape != (3, 3):
            raise ValueError(f"Rotation matrix must be a 3x3 matrix. Got {rotation_matrix.shape} instead.")
        logger.info(f"Applying rotation matrix {rotation_matrix}")
        self.body_frame_name_xyz = self._rotate_component(self.body_frame_name_xyz, rotation_matrix)
        self.right_hand_frame_name_xyz = self._rotate_component(self.right_hand_frame_name_xyz, rotation_matrix)
        self.left_hand_frame_name_xyz = self._rotate_component(self.left_hand_frame_name_xyz, rotation_matrix)
        self.face_frame_name_xyz = self._rotate_component(self.face_frame_name_xyz, rotation_matrix)
        for other_component in self.freemocap_data.other:
            other_component.data_frame_name_xyz = self._rotate_component(other_component.data_frame_name_xyz,
                                                                         rotation_matrix)

    def translate_by(self, vector: Union[np.ndarray, List[float]]):
        logger.info(f"Translating by vector {vector}")
        if isinstance(vector, list):
            vector = np.array(vector)
        if vector.shape != (3,):
            raise ValueError(f"Vector must be a 3D vector. Got {vector.shape} instead.")

        self._translate_component(self.body_frame_name_xyz, vector)
        self._translate_component(self.right_hand_frame_name_xyz, vector)
        self._translate_component(self.left_hand_frame_name_xyz, vector)
        self._translate_component(self.face_frame_name_xyz, vector)

        for other_component in self.freemocap_data.other:
            self._translate_component(other_component.data_frame_name_xyz, vector)

    def _translate_component(self, component, vector):
        component[:, :, 0] += vector[0]
        component[:, :, 1] += vector[1]
        component[:, :, 2] += vector[2]

    def apply_transform(self, transform):
        # Separate rotation matrix and translation vector
        if isinstance(transform, list):
            transform = np.array(transform)
        if transform.shape != (4, 4):
            raise ValueError(f"Transform must be a 4x4 matrix. Got {transform.shape} instead.")
        rotation_matrix = transform[:3, :3]
        translation_vector = transform[:3, 3]
        scale = transform[3, 3]

        # Apply rotation
        self.apply_rotation(rotation_matrix)

        # Apply translation
        self += translation_vector

    def add_metadata(self, metadata: dict):
        logger.info(f"Adding metadata {metadata.keys()}")
        self.freemocap_data.metadata.update(metadata)
