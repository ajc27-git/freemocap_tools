import logging
from copy import deepcopy
from pathlib import Path
from typing import List, Union, Literal, Dict, Any

import numpy as np

from freemocap_adapter.core_functions.empties.creation.create_virtual_trajectories import calculate_virtual_trajectories
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.helpers.estimate_good_frame import \
    estimate_good_frame
from freemocap_adapter.data_models.freemocap_data.freemocap_data_model import FreemocapData
from freemocap_adapter.data_models.freemocap_data.helpers.freemocap_component_data import FreemocapComponentData

FREEMOCAP_DATA_COMPONENT_TYPES = Literal["body", "right_hand", "left_hand", "face", "other"]

logger = logging.getLogger(__name__)


class FreemocapDataHandler:
    def __init__(self,
                 freemocap_data: FreemocapData):

        self.freemocap_data = freemocap_data
        self._intermediate_stages = None
        self.mark_processing_stage(name="original_from_file")

    @classmethod
    def from_recording_path(cls,
                            recording_path: Union[str, Path],
                            ) -> "FreemocapDataHandler":
        cls._validate_recording_path(recording_path=recording_path)
        freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)
        return cls(freemocap_data=freemocap_data)

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
    def center_of_mass_trajectory(self) -> np.ndarray:
        return self.freemocap_data.other["center_of_mass"].data

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
    def center_of_mass_frame_name_xyz(self):
        # add a dummy "name" dimenstion to self.center_of_mass_trajectory so it can be used with stuff made for standard trajectories

        com_frame_frame_xyz = np.expand_dims(self.center_of_mass_trajectory, axis=1)
        if com_frame_frame_xyz.shape[0] != self.number_of_frames:
            raise ValueError(
                f"Number of frames ({self.number_of_frames}) does not match number of frames in center_of_mass_frame_name_xyz ({com_frame_frame_xyz.shape[0]}).")
        if com_frame_frame_xyz.shape[1] != 1:
            raise ValueError(
                f"Number of trajectories ({1}) does not match number of trajectories in center_of_mass_frame_name_xyz ({com_frame_frame_xyz.shape[1]}).")
        if com_frame_frame_xyz.shape[2] != 3:
            raise ValueError(
                f"center_of_mass_frame_name_xyz should have 3 dimensions. Got {com_frame_frame_xyz.shape[2]} instead.")
        return com_frame_frame_xyz

    @property
    def body_frame_name_xyz(self):
        return self.freemocap_data.body.data

    @body_frame_name_xyz.setter
    def body_frame_name_xyz(self, value):
        if value.shape != self.body_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new body data ({value.shape}) does not match shape of old body data ({self.body_frame_name_xyz.shape}).")
        self.freemocap_data.body.data = value

    @property
    def right_hand_frame_name_xyz(self):
        return self.freemocap_data.hands["right"].data

    @right_hand_frame_name_xyz.setter
    def right_hand_frame_name_xyz(self, value):
        if value.shape != self.right_hand_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new right hand data ({value.shape}) does not match shape of old right hand data ({self.right_hand_frame_name_xyz.shape}).")
        self.freemocap_data.hands["right"].data = value

    @property
    def left_hand_frame_name_xyz(self):
        return self.freemocap_data.hands["left"].data

    @left_hand_frame_name_xyz.setter
    def left_hand_frame_name_xyz(self, value):
        if value.shape != self.left_hand_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new left hand data ({value.shape}) does not match shape of old left hand data ({self.left_hand_frame_name_xyz.shape}).")
        self.freemocap_data.hands["left"].data = value

    @property
    def face_frame_name_xyz(self):
        return self.freemocap_data.face.data

    @face_frame_name_xyz.setter
    def face_frame_name_xyz(self, value):
        if value.shape != self.face_frame_name_xyz.shape:
            raise ValueError(
                f"Shape of new face data ({value.shape}) does not match shape of old face data ({self.face_frame_name_xyz.shape}).")
        self.freemocap_data.face.data = value

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
    def number_of_frames(self) -> int:
        frame_counts = self._collect_frame_counts()
        self._validate_frame_counts(frame_counts)
        return frame_counts['body']

    def add_trajectory(self,
                       trajectory: np.ndarray,
                       trajectory_name: str,
                       component_type: FREEMOCAP_DATA_COMPONENT_TYPES,
                       source: str = None,
                       group_name: str = None):
        if trajectory.shape[0] != self.number_of_frames:
            raise ValueError(
                f"Number of frames ({trajectory.shape[0]}) does not match number of frames in existing data ({self.number_of_frames}).")

        if len(trajectory.shape) == 2:
            num_dimensions = trajectory.shape[1]
            trajectory = np.expand_dims(trajectory,
                                        axis=1)  # add a dummy "name" dimenstion to trajectory so it can be concatenated with other trajectories
        if len(trajectory.shape) == 3:
            num_dimensions = trajectory.shape[2]

        if num_dimensions != 3:
            raise ValueError(
                f"Trajectory data should have 3 dimensions. Got {trajectory.shape[2]} instead.")

        if component_type == "body":
            self.freemocap_data.body.data = np.concatenate([self.body_frame_name_xyz, trajectory], axis=1)
            self.freemocap_data.body.trajectory_names.append(trajectory_name)
        elif component_type == "right_hand":
            self.freemocap_data.hands["right"].data = np.concatenate([self.right_hand_frame_name_xyz, trajectory],
                                                                     axis=1)
            self.freemocap_data.hands["right"].trajectory_names.append(trajectory_name)
        elif component_type == "left_hand":
            self.freemocap_data.hands["left"].data = np.concatenate([self.left_hand_frame_name_xyz, trajectory], axis=1)
            self.freemocap_data.hands["left"].trajectory_names.append(trajectory_name)
        elif component_type == "face":
            self.freemocap_data.face.data = np.concatenate([self.face_frame_name_xyz, trajectory], axis=1)
            self.freemocap_data.face.trajectory_names.append(trajectory_name)
        elif component_type == "other":
            for other_component in self.freemocap_data.other.values():
                if other_component.name == group_name:
                    other_component.data = np.concatenate([other_component.data, trajectory], axis=1)
                    other_component.trajectory_names.append(trajectory_name)
                    return

    def add_trajectories(self,
                         trajectories: Dict[str, np.ndarray],
                         component_type: Union[FREEMOCAP_DATA_COMPONENT_TYPES, List[FREEMOCAP_DATA_COMPONENT_TYPES]],
                         source: str = None,
                         group_name: str = None):

        if not isinstance(component_type, list):
            component_types = [component_type] * len(trajectories)
        else:
            component_types = component_type

        for trajectory_number, trajectory_dict in enumerate(trajectories.items()):
            trajectory_name, trajectory = trajectory_dict

            self.add_trajectory(trajectory=trajectory,
                                trajectory_name=trajectory_name,
                                component_type=component_types[trajectory_number],
                                source=source,
                                group_name=group_name)
        #
        #
        # if component_type == "body":
        #     # extend the body data with the new trajectories
        #     self.freemocap_data.body.data = np.concatenate(
        #         [self.freemocap_data.body.data, incoming_trajectory_frame_name_xyz], axis=1)
        #     self.freemocap_data.body.trajectory_names.extend(incoming_trajectory_names)
        # elif component_type == "right_hand":
        #     self.freemocap_data.hands["right"].data = np.concatenate(
        #         [self.freemocap_data.hands["right"].data, incoming_trajectory_frame_name_xyz], axis=1)
        #     self.freemocap_data.hands["right"].trajectory_names.extend(incoming_trajectory_names)
        # elif component_type == "left_hand":
        #     self.freemocap_data.hands["left"].data = np.concatenate(
        #         [self.freemocap_data.hands["left"].data, incoming_trajectory_frame_name_xyz], axis=1)
        #     self.freemocap_data.hands["left"].trajectory_names.extend(incoming_trajectory_names)
        # elif component_type == "face":
        #     self.freemocap_data.face.data = np.concatenate(
        #         [self.freemocap_data.face.data, incoming_trajectory_frame_name_xyz], axis=1)
        #     self.freemocap_data.face.trajectory_names.extend(incoming_trajectory_names)
        # elif component_type == "other":
        #     self.add_other_component(FreemocapComponentData(name=group_name if group_name is not None else "unknown",
        #                                                     data=incoming_trajectory_frame_name_xyz,
        #                                                     data_source=source if source is not None else "unknown",
        #                                                     trajectory_names=incoming_trajectory_names))

    def get_trajectories(self, trajectory_names: List[str], components=None, with_error: bool = False) -> Union[
        Dict[str, np.ndarray], Dict[str, Dict[str, np.ndarray]]]:
        
        if not isinstance(trajectory_names, list):
            trajectory_names = [trajectory_names]

        if components is None:
            components = [None] * len(trajectory_names)
        elif not isinstance(components, list):
            components = [components] * len(trajectory_names)

        return {name: self.get_trajectory(name=name,
                                          component_type=component,
                                          with_error=with_error) for
                name, component in zip(trajectory_names, components)}

    def get_trajectory(self,
                       name: str,
                       component_type: FREEMOCAP_DATA_COMPONENT_TYPES = None,
                       with_error: bool = False) -> Union[np.ndarray, Dict[str, np.ndarray]]:


        trajectories = []
        errors = []
        if component_type is None:
            if name in self.body_names:
                trajectories.append(self.body_frame_name_xyz[:, self.body_names.index(name), :])
                if with_error:
                    errors.append(self.freemocap_data.body.error[:, self.body_names.index(name)])

            if name in self.right_hand_names:
                trajectories.append(self.right_hand_frame_name_xyz[:, self.right_hand_names.index(name), :])
                if with_error:
                    errors.append(self.freemocap_data.hands["right"].error[:, self.right_hand_names.index(name)])

            if name in self.left_hand_names:
                trajectories.append(self.left_hand_frame_name_xyz[:, self.left_hand_names.index(name), :])
                if with_error:
                    errors.append(self.freemocap_data.hands["left"].error[:, self.left_hand_names.index(name)])

            if name in self.face_names:
                trajectories.append(self.face_frame_name_xyz[:, self.face_names.index(name), :])
                if with_error:
                    errors.append(self.freemocap_data.face.error[:, self.face_names.index(name)])

            for other_component in self.freemocap_data.other.values():
                if name in other_component.trajectory_names:
                    if len(other_component.data.shape) == 3:
                        trajectories.append(
                            other_component.data[:, other_component.trajectory_names.index(name), :])
                    elif len(other_component.data.shape) == 2:
                        trajectories.append(
                            other_component.data[:, other_component.trajectory_names.index(name)])
                    else:
                        raise ValueError(
                            f"Data shape {other_component.data.shape} is not supported. Should be 2 or 3 dimensional.")

                    if with_error and other_component.error is not None:
                        errors.append(
                            other_component.error[:, other_component.trajectory_names.index(name)])
                    else:
                        errors.append(None)
        if trajectories == []:
            raise ValueError(f"Trajectory {name} not found.")

        if len(trajectories) > 1:
            raise ValueError(
                f"Trajectory {name} found in multiple components. Specify component (body, right_hand, left_hand, face, other) to resolve ambiguity.")

        if not with_error:
            return trajectories[0]
        else:
            return {"trajectory": trajectories[0], "error": errors[0]}

    def _collect_frame_counts(self) -> dict:
        frame_counts = {
            'body': self.body_frame_name_xyz.shape[0],
            'right_hand': self.right_hand_frame_name_xyz.shape[0],
            'left_hand': self.left_hand_frame_name_xyz.shape[0],
            'face': self.face_frame_name_xyz.shape[0],
            'other': [other_component.data.shape[0] for other_component in self.freemocap_data.other.values()],
        }
        return frame_counts

    def _validate_frame_counts(self, frame_counts: dict):
        body_frame_count = frame_counts['body']
        are_frame_counts_equal = all(
            body_frame_count == frame_count
            for frame_count in frame_counts.values()
            if isinstance(frame_count, int)
        )
        are_other_frame_counts_equal = all(
            body_frame_count == frame_count
            for frame_count in frame_counts['other']
        )
        if not (are_frame_counts_equal and are_other_frame_counts_equal):
            raise ValueError(f"Number of frames do not match: {frame_counts}")

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

        for name, other_component in self.freemocap_data.other.items():
            other_component.data = self._rotate_component(other_component.data, rotation_matrix)

    def _rotate_component(self,
                          data_frame_name_xyz: Union[np.ndarray, List[float]],
                          rotation_matrix: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        if isinstance(data_frame_name_xyz, list):
            data_frame_name_xyz = np.array(data_frame_name_xyz)
        if isinstance(rotation_matrix, list):
            rotation_matrix = np.array(rotation_matrix)

        if rotation_matrix.shape != (3, 3):
            raise ValueError(f"Rotation matrix must be a 3x3 matrix. Got {rotation_matrix.shape} instead.")

        if data_frame_name_xyz.shape[-1] == 2:
            logger.info(f"2D data detected. Adding a third dimension with zeros.")
            data_frame_name_xyz = np.concatenate(
                [data_frame_name_xyz, np.zeros((data_frame_name_xyz.shape[0], data_frame_name_xyz.shape[1], 1))],
                axis=2)

        rotated_data_frame_name_xyz = np.zeros(data_frame_name_xyz.shape)
        for frame_number in range(data_frame_name_xyz.shape[0]):
            if len(data_frame_name_xyz.shape) == 2:
                rotated_data_frame_name_xyz[frame_number, :] = rotation_matrix @ data_frame_name_xyz[frame_number, :]
            elif len(data_frame_name_xyz.shape) == 3:
                for trajectory_number in range(data_frame_name_xyz.shape[1]):
                    rotated_data_frame_name_xyz[frame_number, trajectory_number,
                    :] = rotation_matrix @ data_frame_name_xyz[
                                           frame_number,
                                           trajectory_number,
                                           :]
        return rotated_data_frame_name_xyz

    def apply_translation(self, vector: Union[np.ndarray, List[float]]):
        logger.info(f"Translating by vector {vector}")
        if isinstance(vector, list):
            vector = np.array(vector)
        if vector.shape != (3,):
            raise ValueError(f"Vector must be a 3D vector. Got {vector.shape} instead.")

        self.body_frame_name_xyz = self._translate_component_data(self.body_frame_name_xyz, vector)
        self.right_hand_frame_name_xyz = self._translate_component_data(self.right_hand_frame_name_xyz, vector)
        self.left_hand_frame_name_xyz = self._translate_component_data(self.left_hand_frame_name_xyz, vector)
        self.face_frame_name_xyz = self._translate_component_data(self.face_frame_name_xyz, vector)

        for name, other_component in self.freemocap_data.other.items():
            self._translate_component_data(other_component.data, vector)

    def _translate_component_data(self, component: np.ndarray, vector: np.ndarray):
        if len(component.shape) == 2:
            component[:, 0] += vector[0]
            component[:, 1] += vector[1]
            component[:, 2] += vector[2]
        elif len(component.shape) == 3:
            component[:, :, 0] += vector[0]
            component[:, :, 1] += vector[1]
            component[:, :, 2] += vector[2]
        else:
            raise ValueError(f"Component data must have 2 or 3 dimensions. Got {component.shape[2]} instead.")
        return component

    def apply_scale(self, scale):
        logger.info(f"Applying scale {scale}")
        self.body_frame_name_xyz *= scale
        self.right_hand_frame_name_xyz *= scale
        self.left_hand_frame_name_xyz *= scale
        self.face_frame_name_xyz *= scale
        for other_component in self.freemocap_data.other:
            other_component.data_frame_name_xyz *= scale

    def apply_affine_transformations(self, transform: Union[np.ndarray, List[List[float]]]):
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
        self.apply_translation(translation_vector)

        # Apply scale
        self.apply_scale(scale)

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
            other_components_frames = {}

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
                    for other_name, other_component in self.freemocap_data.other.items():    
                        if not other_name in other_components.keys():
                            other_components[other_name] = []
                        other_components_frames[other_name].append(np.ndarray(bpy.data.objects[other_name].location))
                           
            if len(body_frames) > 0:
                self.body_frame_name_xyz = np.array(body_frames)
            if len(right_hand_frames) > 0:
                self.right_hand_frame_name_xyz = np.array(right_hand_frames)
            if len(left_hand_frames) > 0:
                self.left_hand_frame_name_xyz = np.array(left_hand_frames)
            if len(face_frames) > 0:
                self.face_frame_name_xyz = np.array(face_frames)
            if len(other_components_frames) > 0:
                for other_name, other_component_frames in other_components_frames.items():
                    self.freemocap_data.other[other_name].data = np.array(other_component_frames)
                    
        except Exception as e:
            logger.error(f"Failed to extract data from empties {empties.keys()}")
            logger.exception(e)
            raise e
        
        self.mark_processing_stage(stage_name)

    def add_other_component(self, component: FreemocapComponentData):
        logger.info(f"Adding other component {component.name}")
        self.freemocap_data.other[component.name] = component
        self.mark_processing_stage(f"added_{component.name}")

    def calculate_virtual_trajectories(self):
        logger.info(f"Calculating virtual trajectories")
        try:
            virtual_trajectories = calculate_virtual_trajectories(body_frame_name_xyz=self.body_frame_name_xyz,
                                                                  body_names=self.body_names)
            self.add_trajectories(trajectories=virtual_trajectories,
                                  component_type="body",
                                  )
            self.mark_processing_stage("added_virtual_trajectories")

        except Exception as e:
            logger.error(f"Failed to calculate virtual trajectories: {e}")
            logger.exception(e)
            raise e

    @staticmethod
    def _validate_recording_path(recording_path: Union[str, Path]):
        if recording_path == "":
            logger.error("No recording path specified")
            raise FileNotFoundError("No recording path specified")
        if not Path(recording_path).exists():
            logger.error(f"Recording path {recording_path} does not exist")
            raise FileNotFoundError(f"Recording path {recording_path} does not exist")

    def put_data_in_inertial_reference_frame(self):

        logger.info(
            f"Putting freemocap data in inertial reference frame...")

        ground_reference_trajectories_with_error = self.get_trajectories(
            trajectory_names=["right_heel", "left_heel", "right_foot_index", "left_foot_index"],
            with_error=True)

        good_frame = estimate_good_frame(trajectories_with_error=ground_reference_trajectories_with_error)
        original_reference_trajectories = {trajectory_name: trajectory["trajectory"][good_frame, :]
                                           for trajectory_name, trajectory in
                                           ground_reference_trajectories_with_error.items()}

        center_reference_point = np.nanmean(list(original_reference_trajectories.values()), axis=0)

        x_forward_reference_points = []
        for trajectory in self.get_trajectories(trajectory_names=["left_foot_index", "right_foot_index"]).values():
            x_forward_reference_points.append(trajectory[good_frame, :])
        x_forward_reference_point = np.nanmean(x_forward_reference_points, axis=0)

        y_leftward_reference_points = []
        for trajectory in self.get_trajectories(trajectory_names=["left_heel", "left_foot_index"]).values():
            y_leftward_reference_points.append(trajectory[good_frame, :])
        y_leftward_reference_point = np.nanmean(y_leftward_reference_points, axis=0)

        z_upward_reference_point = self.get_trajectory("head_center")[good_frame, :]

        x_forward = x_forward_reference_point - center_reference_point
        y_left = y_leftward_reference_point - center_reference_point
        z_up = z_upward_reference_point - center_reference_point

        # Make them orthogonal
        z_hat = np.cross(x_forward, y_left)
        y_hat = np.cross(x_forward, z_hat)
        x_hat = np.cross(y_hat, z_hat)

        # Normalize them
        x_hat = x_hat / np.linalg.norm(x_hat)
        y_hat = y_hat / np.linalg.norm(y_hat)
        z_hat = z_hat / np.linalg.norm(z_hat)

        rotation_matrix = np.array([x_hat, y_hat, z_hat])

        assert np.allclose(np.linalg.norm(x_hat), 1), "x_hat is not normalized"
        assert np.allclose(np.linalg.norm(y_hat), 1), "y_hat is not normalized"
        assert np.allclose(np.linalg.norm(z_hat), 1), "z_hat is not normalized"
        assert np.allclose(np.dot(z_hat, y_hat), 0), "z_hat is not orthogonal to y_hat"
        assert np.allclose(np.dot(z_hat, x_hat), 0), "z_hat is not orthogonal to x_hat"
        assert np.allclose(np.dot(y_hat, x_hat), 0), "y_hat is not orthogonal to x_hat"
        assert np.allclose(rotation_matrix @ x_hat, [1, 0, 0]), "x_hat is not rotated to [1, 0, 0]"
        assert np.allclose(rotation_matrix @ y_hat, [0, 1, 0]), "y_hat is not rotated to [0, 1, 0]"
        assert np.allclose(rotation_matrix @ z_hat, [0, 0, 1]), "z_hat is not rotated to [0, 0, 1]"
        assert np.allclose(np.cross(x_hat, y_hat), z_hat), "Vectors do not follow right-hand rule"
        assert np.allclose(np.linalg.det(rotation_matrix), 1), "rotation matrix is not a rotation matrix"

        self.apply_translation(-center_reference_point)
        self.mark_processing_stage("translated_to_origin")
        self.apply_rotation(rotation_matrix=rotation_matrix)
        self.mark_processing_stage("inertial_reference_frame")

        logger.success(
            "Finished putting freemocap data in inertial reference frame.\n freemocap_data(after):\n{self}")

    def get_body_trajectories_closest_to_the_ground(self) -> Dict[str, np.ndarray]:
        body_names = self.body_names

        # checking for markers from the ground up!
        body_parts_from_low_to_high = [
            ("feet", ["right_heel", "left_heel", "right_foot_index", "left_foot_index"]),
            ("ankle", ["right_ankle", "left_ankle"]),
            ("knee", ["right_knee", "left_knee"]),
            ("hip", ["right_hip", "left_hip"]),
            ("shoulder", ["right_shoulder", "left_shoulder"]),
            ("head", ["nose", "right_eye_inner", "right_eye",
                      "right_eye_outer", "left_eye_inner",
                      "left_eye", "left_eye_outer",
                      "right_ear", "left_ear",
                      "mouth_right", "mouth_left"]),
        ]

        for part_name, part_list in body_parts_from_low_to_high:
            if all([part in body_names for part in part_list]):
                logger.debug(f"Trying to use {part_name} trajectories to define ground plane.")
                part_trajectories = self.get_trajectories(part_list)

                for trajectory_name, trajectory in part_trajectories.items():
                    if np.isnan(trajectory).all():
                        logger.warning(
                            f"Trajectory {trajectory_name} is all nan. Removing from lowest body trajectories.")
                        del part_trajectories[trajectory_name]

                if len(part_trajectories) < 2:
                    logger.debug(f"Found less than 2 {part_name} trajectories. Trying next part..")
                else:
                    logger.info(f"Found {part_name} trajectories. Using {part_name} as lowest body trajectories.")
                    return part_trajectories

        logger.error(f"Found less than 2 head trajectories. Cannot find lowest body trajectories!")
        raise Exception("Cannot find lowest body trajectories!")
