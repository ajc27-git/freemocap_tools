import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import numpy as np

from freemocap_adapter.core_functions.freemocap_data_operations.helpers.create_trajectory_name_lists import \
    create_trajectory_name_lists
from freemocap_adapter.data_models.freemocap_data.helpers.freemocap_data_stats import FreemocapDataStats
from freemocap_adapter.data_models.freemocap_data.helpers.freemocap_component_data import FreemocapComponentData
from freemocap_adapter.data_models.freemocap_data.helpers.freemocap_data_paths import FreemocapDataPaths

logger = logging.getLogger(__name__)


@dataclass
class FreemocapData:
    body: FreemocapComponentData
    hands: Dict[str, FreemocapComponentData]
    face: FreemocapComponentData
    other: Optional[Dict[str, FreemocapComponentData]]
    metadata: Optional[Dict[Any, Any]]

    @classmethod
    def from_data(cls,
                  body_frame_name_xyz: np.ndarray,
                  right_hand_frame_name_xyz: np.ndarray,
                  left_hand_frame_name_xyz: np.ndarray,
                  face_frame_name_xyz: np.ndarray,
                  data_source: str = "mediapipe",
                  other: Optional[Dict[str, Union[FreemocapComponentData, Dict[str, Any]]]] = None,
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
            if isinstance(component, FreemocapComponentData):
                pass
            elif isinstance(component, dict):
                if not "component_name" in component.keys():
                    component["component_name"] = name
                    try:
                        other[name] = FreemocapComponentData(**component)
                    except TypeError as e:
                        logger.error(f"Error creating FreemocapComponentData from dict {component}")
                        raise e
            else:
                raise ValueError(f"Component: {name} type not recognized (type: {type(component)}")

        return cls(
            body=FreemocapComponentData(name="body",
                                        data=body_frame_name_xyz,
                                        data_source=data_source,
                                        trajectory_names=body_names),

            hands={"right": FreemocapComponentData(name="right_hand",
                                                   data=right_hand_frame_name_xyz,
                                                   data_source=data_source,
                                                   trajectory_names=right_hand_names),
                   "left": FreemocapComponentData(name="left_hand",
                                                  data=left_hand_frame_name_xyz,
                                                  data_source=data_source,
                                                  trajectory_names=left_hand_names)},
            face=FreemocapComponentData(name="face",
                                        data=face_frame_name_xyz,
                                        data_source=data_source,
                                        trajectory_names=face_names),
            other=other,
            metadata=metadata,
        )

    @classmethod
    def from_data_paths(cls,
                        data_paths: FreemocapDataPaths,
                        scale: float = 1000,
                        **kwargs):
        if "metadata" in kwargs.keys():
            metadata = kwargs["metadata"]
        else:
            metadata = {}
        metadata.update({"reprojection_error": np.load(str(data_paths.reprojection_error_npy))})

        return cls.from_data(
            body_frame_name_xyz=np.load(str(data_paths.body_npy)) / scale,
            right_hand_frame_name_xyz=np.load(str(data_paths.right_hand_npy)) / scale,
            left_hand_frame_name_xyz=np.load(str(data_paths.left_hand_npy)) / scale,
            face_frame_name_xyz=np.load(str(data_paths.face_npy)) / scale,

            other={"center_of_mass": FreemocapComponentData(name="center_of_mass",
                                                            data=np.load(
                                                                str(data_paths.center_of_mass_npy)) / scale,
                                                            data_source="freemocap",
                                                            trajectory_names=["center_of_mass"])},
            metadata=metadata,            
        )

    @classmethod
    def from_recording_path(cls,
                            recording_path: str,
                            **kwargs):
        data_paths = FreemocapDataPaths.from_recording_folder(recording_path)
        metadata = {"recording_path": recording_path,
                    "data_paths": data_paths}
        logger.info(f"Loading data from paths {data_paths}")
        return cls.from_data_paths(data_paths=data_paths, metadata=metadata, **kwargs)

    def __str__(self):
        return str(FreemocapDataStats.from_freemocap_data(self))

if __name__ == "__main__":
    from freemocap_adapter.core_functions.setup_scene.get_path_to_sample_data import get_path_to_sample_data

    recording_path = get_path_to_sample_data()
    freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path,
                                                       type="original")
    print(str(freemocap_data))
