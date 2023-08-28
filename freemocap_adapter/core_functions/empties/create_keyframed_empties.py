from typing import List, Dict

import numpy as np
import bpy

import logging

from freemocap_adapter.core_functions.load_data.load_freemocap_data import logger, create_virtual_trajectories, \
    BODY_EMPTY_SCALE
from freemocap_adapter.data_models.freemocap_data import FreemocapData

logger = logging.getLogger(__name__)

def create_keyframed_empty_from_3d_trajectory_data(
    trajectory_fr_xyz: np.ndarray,
    trajectory_name: str,
    parent_origin: List[float] = [0, 0, 0],
    empty_scale: float = 0.1,
    empty_type: str = "PLAIN_AXES",
):
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


def create_keyframed_empties(freemocap_data: FreemocapData,
                             parent_object: bpy.types.Object,
                             names: Dict[str, List[str]],
                             body_empty_scale: float, ):
    ############################
    ### Load mocap freemocap_data as empty markers

    hand_empty_scale = body_empty_scale * 0.5
    logger.info(
        "__________________________\n"
        "Loading freemocap trajectory freemocap_data as empty markers..."
        "_________________________\n"
    )
    right_hand_trajectory_names = [f"right_hand_{empty_name}" for empty_name in names["hand"]]
    left_hand_trajectory_names = [f"left_hand_{empty_name}" for empty_name in names["hand"]]
    # mediapipe_face_trajectory_names = [f"face_{number}:{empty_name}" for number, empty_name in
    #                                    face_contour_marker_indices]
    try:  # load as much of the freemocap_data as you can, but if there's an error keep going
        # create empty markers for body
        for marker_number in range(freemocap_data.body_fr_mar_xyz.shape[1]):
            trajectory_name = names["body"][marker_number]
            trajectory_fr_xyz = freemocap_data.body_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=parent_object,
                empty_scale=body_empty_scale,
                empty_type="SPHERE",
            )

        for marker_number in range(freemocap_data.right_hand_fr_mar_xyz.shape[1]):
            trajectory_name = right_hand_trajectory_names[marker_number]
            trajectory_fr_xyz = freemocap_data.right_hand_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=parent_object,
                empty_scale=hand_empty_scale,
                empty_type="PLAIN_AXES",
            )

        # create empty markers for left hand
        for marker_number in range(freemocap_data.left_hand_fr_mar_xyz.shape[1]):
            trajectory_name = left_hand_trajectory_names[marker_number]
            trajectory_fr_xyz = freemocap_data.left_hand_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=parent_object,
                empty_scale=hand_empty_scale,
                empty_type="PLAIN_AXES",
            )

        virtual_marker_names = create_virtual_trajectories(freemocap_data=freemocap_data,
                                                           parent_object=parent_object,
                                                           names=names,
                                                           body_empty_scale=BODY_EMPTY_SCALE,
                                                           )

        logger.info(f"Adding virtual marker names to body trajectory names  - {virtual_marker_names}")
        names["body"].extend(virtual_marker_names)
        logger.info("Done creating virtual markers")


    except Exception as e:
        logger.error(f"Error loading empty markers: {e}!")
        raise
