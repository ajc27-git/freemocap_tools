import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Any, Dict, Optional, Union

import numpy as np

from freemocap_adapter.data_models.freemocap_data.freemocap_data_stats import FreemocapDataStats
from freemocap_adapter.data_models.freemocap_data.helpers.create_trajectory_name_lists import \
    create_trajectory_name_lists

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
class ComponentData:
    component_name: str
    data_frame_name_xyz: np.ndarray
    data_source: str
    trajectory_names: List[str]


@dataclass
class FreemocapData:
    body: ComponentData
    hands: Dict[str, ComponentData]
    face: ComponentData
    other: Optional[Dict[str, ComponentData]]
    metadata: Optional[Dict[Any, Any]]



    @classmethod
    def from_data(cls,
                  body_frame_name_xyz: np.ndarray,
                  right_hand_frame_name_xyz: np.ndarray,
                  left_hand_frame_name_xyz: np.ndarray,
                  face_frame_name_xyz: np.ndarray,
                  data_source: str = "mediapipe",
                  other: Optional[Dict[str, Union[ComponentData, Dict[str, Any]]]] = None,
                  metadata: Dict[Any, Any] = None) -> "FreemocapData":
        (body_names,
         face_names,
         left_hand_names,
         right_hand_names) = create_trajectory_name_lists(data_source=data_source,
                                                          body_frame_name_xyz=body_frame_name_xyz,
                                                          face_frame_name_xyz=face_frame_name_xyz,
                                                          left_hand_frame_name_xyz=left_hand_frame_name_xyz,
                                                          right_hand_frame_name_xyz=right_hand_frame_name_xyz)

        if metadata is None:
            metadata = {}

        if other is None:
            other = {}

        for name, component in other.items():
            if isinstance(component, ComponentData):
                pass
            elif isinstance(component, dict):
                if not "component_name" in component.keys():
                    component["component_name"] = name
                other[name] = ComponentData(**component)
            else:
                raise ValueError(f"Component: {name} type not recognized (type: {type(component)}")

        return cls(
            body=ComponentData(component_name="body",
                               data_frame_name_xyz=body_frame_name_xyz,
                               data_source=data_source,
                               trajectory_names=body_names),

            hands={"right": ComponentData(component_name="right_hand",
                                          data_frame_name_xyz=right_hand_frame_name_xyz,
                                          data_source=data_source,
                                          trajectory_names=right_hand_names),
                   "left": ComponentData(component_name="left_hand",
                                         data_frame_name_xyz=left_hand_frame_name_xyz,
                                         data_source=data_source,
                                         trajectory_names=left_hand_names)},
            face=ComponentData(component_name="face",
                               data_frame_name_xyz=face_frame_name_xyz,
                               data_source=data_source,
                               trajectory_names=face_names),
            other=other,
            metadata=metadata,
        )

    @classmethod
    def from_data_paths(cls,
                        data_paths: DataPaths,
                        scale: float = 1000,
                        **kwargs):
        return cls.from_data(
            body_frame_name_xyz=np.load(str(data_paths.body_npy)) / scale,
            right_hand_frame_name_xyz=np.load(str(data_paths.right_hand_npy)) / scale,
            left_hand_frame_name_xyz=np.load(str(data_paths.left_hand_npy)) / scale,
            face_frame_name_xyz=np.load(str(data_paths.face_npy)) / scale,
            **kwargs
        )

    @classmethod
    def from_recording_path(cls,
                            recording_path: str,
                            **kwargs):
        data_paths = DataPaths.from_recording_folder(recording_path)
        logger.info(f"Loading data from paths {data_paths}")
        return cls.from_data_paths(data_paths=data_paths, **kwargs)

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
