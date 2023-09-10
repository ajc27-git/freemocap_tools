import logging
from copy import deepcopy
from typing import List, Union, Literal, Dict, Any

import numpy as np

from freemocap_adapter.core_functions.empties.creation.create_virtual_trajectories import calculate_virtual_trajectories
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.helpers.put_freemocap_data_into_inertial_reference_frame import \
    get_lowest_body_trajectories, get_frame_with_lowest_velocity
from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData, ComponentData

FREEMOCAP_DATA_COMPONENT_TYPES = Literal["body", "right_hand", "left_hand", "face", "other"]

logger = logging.getLogger(__name__)


class FreemocapDataHandler:
    def __init__(self,
                 freemocap_data: FreemocapData):
        self.freemocap_data = freemocap_data
        self._intermediate_stages = None

    def add_trajectories(self,
                         trajectories: Dict[str, np.ndarray],
                         component_type: FREEMOCAP_DATA_COMPONENT_TYPES,
                         source: str = None,
                         group_name: str = None):
        
        trajectory_names = list(trajectories.keys())
        trajectory_frame_name_xyz = np.array(list(trajectories.values()))
        trajectory_frame_name_xyz = trajectory_frame_name_xyz.reshape((self.number_of_frames, len(trajectory_names), 3))
        

        if trajectory_frame_name_xyz.shape[0] != self.number_of_frames:
            raise ValueError(
                f"Number of frames ({trajectory_frame_name_xyz.shape[0]}) does not match number of frames in existing data ({self.number_of_frames}).")

        if trajectory_frame_name_xyz.shape[1] != len(trajectory_names):
            raise ValueError(
                f"Number of trajectories ({trajectory_frame_name_xyz.shape[1]}) does not match number of trajectory names ({len(trajectory_names)}).")

        if trajectory_frame_name_xyz.shape[2] != 3:
            raise ValueError(
                f"Trajectory data should have 3 dimensions. Got {trajectory_frame_name_xyz.shape[2]} instead.")

        if component_type == "body":
            # extend the body data with the new trajectories
            self.freemocap_data.body.data_frame_name_xyz = np.concatenate(
                [self.freemocap_data.body.data_frame_name_xyz, trajectory_frame_name_xyz], axis=1)
            self.freemocap_data.body.trajectory_names.extend(trajectory_names)
        elif component_type == "right_hand":
            self.freemocap_data.hands["right"].data_frame_name_xyz = np.concatenate(
                [self.freemocap_data.hands["right"].data_frame_name_xyz, trajectory_frame_name_xyz], axis=1)
            self.freemocap_data.hands["right"].trajectory_names.extend(trajectory_names)
        elif component_type == "left_hand":
            self.freemocap_data.hands["left"].data_frame_name_xyz = np.concatenate(
                [self.freemocap_data.hands["left"].data_frame_name_xyz, trajectory_frame_name_xyz], axis=1)
            self.freemocap_data.hands["left"].trajectory_names.extend(trajectory_names)
        elif component_type == "face":
            self.freemocap_data.face.data_frame_name_xyz = np.concatenate(
                [self.freemocap_data.face.data_frame_name_xyz, trajectory_frame_name_xyz], axis=1)
            self.freemocap_data.face.trajectory_names.extend(trajectory_names)
        elif component_type == "other":
            self.add_other_component(ComponentData(name=group_name if group_name is not None else "unknown",
                                                   data_frame_name_xyz=trajectory_frame_name_xyz,
                                                   data_source=source if source is not None else "unknown",
                                                   trajectory_names=trajectory_names))

    def get_trajectories(self, trajectory_names: List[str], components=None) -> Dict[str, np.ndarray]:
        if not isinstance(trajectory_names, list):
            trajectory_names = [trajectory_names]

        if components is None:
            components = [None] * len(trajectory_names)
        elif not isinstance(components, list):
            components = [components] * len(trajectory_names)

        return {name: self.get_trajectory(name, comp) for name, comp in zip(trajectory_names, components)}

    def get_trajectory(self,
                       trajectory_name: str,
                       component_type: FREEMOCAP_DATA_COMPONENT_TYPES = None):
        trajectories = []
        if component_type is None:
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
    def good_clean_frame(self) -> int:
        lowest_trajectories = get_lowest_body_trajectories(freemocap_data_handler=self)
        good_clean_frame_index = get_frame_with_lowest_velocity(lowest_trajectories)
        return good_clean_frame_index

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
    def all_frame_name_xyz(self):
        all_data = np.concatenate([self.body_frame_name_xyz,
                                   self.right_hand_frame_name_xyz,
                                   self.left_hand_frame_name_xyz,
                                   self.face_frame_name_xyz], axis=1)

        for other_component in self.freemocap_data.other:
            all_data = np.concatenate([all_data, other_component.data_frame_name_xyz], axis=1)

        if all_data.shape[0] != self.number_of_frames:
            raise ValueError(
                f"Number of frames ({self.number_of_frames}) does not match number of frames in all_frame_name_xyz ({all_data.shape[0]}).")
        if all_data.shape[1] != self.number_of_trajectories:
            raise ValueError(
                f"Number of trajectories ({self.number_of_trajectories}) does not match number of trajectories in all_frame_name_xyz ({all_data.shape[1]}).")
        if all_data.shape[2] != 3:
            raise ValueError(f"all_frame_name_xyz should have 3 dimensions. Got {all_data.shape[2]} instead.")

        return all_data

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

        self.body_frame_name_xyz = self._translate_component_data(self.body_frame_name_xyz, vector)
        self.right_hand_frame_name_xyz = self._translate_component_data(self.right_hand_frame_name_xyz, vector)
        self.left_hand_frame_name_xyz = self._translate_component_data(self.left_hand_frame_name_xyz, vector)
        self.face_frame_name_xyz = self._translate_component_data(self.face_frame_name_xyz, vector)

        for other_component in self.freemocap_data.other:
            self._translate_component_data(other_component.data_frame_name_xyz, vector)

    def _translate_component_data(self, component, vector):
        component[:, :, 0] += vector[0]
        component[:, :, 1] += vector[1]
        component[:, :, 2] += vector[2]
        return component

    def apply_transform(self, transform: Union[np.ndarray, List[List[float]]]):
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

    def extract_data_from_empties(self, empties: Dict[str, Any], stage_name: str = "from_empties"):

        try:
            import bpy
            logger.info(f"Extracting data from empties {empties.keys()}")

            body_frames = []
            right_hand_frames = []
            left_hand_frames = []
            face_frames = []
            other_data = {}

            for frame_number in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
                logger.debug(f"Extracting data from frame {frame_number}...")
                bpy.context.scene.frame_set(frame_number)

                if "body" in empties.keys():
                    body_frames.append(np.array(
                        [bpy.data.objects[empty_name].location for empty_name in empties["body"].keys()]))

                if "hands" in empties.keys():
                    right_hand_frames.append(np.array(
                        [bpy.data.objects[empty_name].location for empty_name in empties["hands"]["right"].keys()]))

                    left_hand_frames.append(np.array(
                        [bpy.data.objects[empty_name].location for empty_name in empties["hands"]["left"].keys()]))

                if "face" in empties.keys():
                    face_frames.append(np.array(
                        [bpy.data.objects[empty_name].location for empty_name in empties["face"].keys()]))

                if "other" in empties.keys():
                    for name, other_component in self.freemocap_data.other.items():
                        if name not in other_data:
                            other_data[name] = []
                        other_data[name].append(np.array(
                            [bpy.data.objects[empty_name].location for empty_name in
                             empties[other_component.name].keys()]))

            if len(body_frames) > 0:
                self.body_frame_name_xyz = np.array(body_frames)
            if len(right_hand_frames) > 0:
                self.right_hand_frame_name_xyz = np.array(right_hand_frames)
            if len(left_hand_frames) > 0:
                self.left_hand_frame_name_xyz = np.array(left_hand_frames)
            if len(face_frames) > 0:
                self.face_frame_name_xyz = np.array(face_frames)
            if len(other_data) > 0:
                for name, other_component in self.freemocap_data.other.items():
                    other_component.data_frame_name_xyz = np.array(other_data[name])

        except Exception as e:
            logger.error(f"Failed to extract data from empties {empties.keys()}")
            logger.exception(e)
            raise e
        self.mark_processing_stage(stage_name)

    def add_other_component(self, component: ComponentData):
        logger.info(f"Adding other component {component.name}")
        self.freemocap_data.other[component.name] = component

    def calculate_virtual_trajectories(self):
        logger.info(f"Calculating virtual trajectories")
        try:
            virtual_trajectories = calculate_virtual_trajectories(body_frame_name_xyz=self.body_frame_name_xyz,
                                                                  body_names=self.body_names)
            self.add_trajectories(trajectories=virtual_trajectories,
                                  component_type="body",
                                  )
        except Exception as e:
            logger.error(f"Failed to calculate virtual trajectories: {e}")
            logger.exception(e)
            raise e
