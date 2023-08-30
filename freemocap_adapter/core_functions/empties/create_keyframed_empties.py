import logging
from typing import List, Dict

import bpy
import numpy as np

from freemocap_adapter.core_functions.empties.create_virtual_markers import create_virtual_trajectories
from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

logger = logging.getLogger(__name__)

BODY_EMPTY_SCALE = 0.03


def create_keyframed_empty_from_3d_trajectory_data(
        trajectory_fr_xyz: np.ndarray,
        trajectory_name: str,
        parent_origin: List[float] = [0, 0, 0],
        empty_scale: float = 0.1,
        empty_type: str = "PLAIN_AXES",
) -> bpy.types.Object:
    """
    Create a key framed empty from 3d trajectory data
    """
    logger.info(f"Creating keyframed empty from: {trajectory_name}...")
    bpy.ops.object.empty_add(type=empty_type)
    empty_object = bpy.context.editable_objects[-1]
    empty_object.name = trajectory_name

    empty_object.scale = [empty_scale] * 3

    empty_object.parent = parent_origin

    for frame_number in range(trajectory_fr_xyz.shape[0]):
        empty_object.location = [
            trajectory_fr_xyz[frame_number, 0],
            trajectory_fr_xyz[frame_number, 1],
            trajectory_fr_xyz[frame_number, 2],
        ]

        empty_object.keyframe_insert(data_path="location", frame=frame_number)

    return empty_object


def create_keyframed_empties(freemocap_data: FreemocapData,
                             parent_object: bpy.types.Object,
                             names: Dict[str, List[str]],
                             body_empty_scale: float = BODY_EMPTY_SCALE, ):
    hand_empty_scale = body_empty_scale * 0.5
    logger.info(
        "__\n"
        "Loading freemocap trajectory freemocap data as empty markers..."
        "__\n"
    )

    def create_empties(trajectory_frame_marker_xyz: np.ndarray,
                       names_list: List[str],
                       empty_scale: float,
                       empty_type: str) -> Dict[str, bpy.types.Object]:
        empties = {}
        for marker_number in range(trajectory_frame_marker_xyz.shape[1]):
            trajectory_name = names_list[marker_number]
            trajectory_fr_xyz = trajectory_frame_marker_xyz[:, marker_number, :]
            empties[trajectory_name] = create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=parent_object,
                empty_scale=empty_scale,
                empty_type=empty_type,
            )

        return empties

    right_hand_trajectory_names = [f"righthand{empty_name}" for empty_name in names["hand"]]
    left_hand_trajectory_names = [f"lefthand{empty_name}" for empty_name in names["hand"]]

    empties = {}
    try:
        # body trajectories
        empties["body"] = create_empties(trajectory_frame_marker_xyz=freemocap_data.body_fr_mar_xyz,
                                         names_list=names["body"],
                                         empty_scale=body_empty_scale,
                                         empty_type="SPHERE")

        # right hand trajectories
        empties["hands"]["right"] = create_empties(trajectory_frame_marker_xyz=freemocap_data.right_hand_fr_mar_xyz,
                                                   names_list=right_hand_trajectory_names,
                                                   empty_scale=hand_empty_scale,
                                                   empty_type="PLAIN_AXES")

        # left hand trajectories
        empties["hands"]["left"] = create_empties(trajectory_frame_marker_xyz=freemocap_data.left_hand_fr_mar_xyz,
                                                  names_list=left_hand_trajectory_names,
                                                  empty_scale=hand_empty_scale,
                                                  empty_type="PLAIN_AXES")

        # create virtual markers
        virtual_marker_names = create_virtual_trajectories(freemocap_data=freemocap_data,
                                                           parent_object=parent_object,
                                                           names=names,
                                                           body_empty_scale=BODY_EMPTY_SCALE,
                                                           )

        logger.info(f"Adding virtual marker names to body trajectory names  - {virtual_marker_names}")
        logger.info("Done creating virtual markers")

    except Exception as e:
        logger.error(f"Error loading empty markers: {e}!")
        raise
