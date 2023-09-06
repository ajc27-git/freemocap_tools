import logging
from typing import List, Dict

import bpy
import numpy as np

from freemocap_adapter.core_functions.empties.creation.create_empy_from_trajectory import \
    create_keyframed_empty_from_3d_trajectory_data
from freemocap_adapter.core_functions.empties.creation.create_virtual_markers import calculate_virtual_trajectories
from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

logger = logging.getLogger(__name__)

BODY_EMPTY_SCALE = 0.03


def create_freemocap_empties(freemocap_data: FreemocapData,
                             parent_object: bpy.types.Object,
                             body_empty_scale: float = BODY_EMPTY_SCALE,
                             ):
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

    if parent_object is None:
        parent_object = bpy.context.scene.objects["freemocap_origin_axes"]

    empties = {}
    try:
        # body trajectories
        empties["body"] = create_empties(trajectory_frame_marker_xyz=freemocap_data.body_fr_mar_xyz,
                                         names_list=freemocap_data.body_names,
                                         empty_scale=body_empty_scale,
                                         empty_type="SPHERE")

        empties["hands"] = {}
        # right hand trajectories
        empties["hands"]["right"] = create_empties(trajectory_frame_marker_xyz=freemocap_data.right_hand_fr_mar_xyz,
                                                   names_list=freemocap_data.right_hand_names,
                                                   empty_scale=hand_empty_scale,
                                                   empty_type="PLAIN_AXES")

        # left hand trajectories
        empties["hands"]["left"] = create_empties(trajectory_frame_marker_xyz=freemocap_data.left_hand_fr_mar_xyz,
                                                  names_list=freemocap_data.left_hand_names,
                                                  empty_scale=hand_empty_scale,
                                                  empty_type="PLAIN_AXES")

        # creation virtual markers
        calculate_virtual_trajectories(freemocap_data=freemocap_data,
                                       parent_object=parent_object,
                                       body_empty_scale=BODY_EMPTY_SCALE,
                                       )

        logger.info(f"Adding virtual marker names to body trajectory names")
        logger.info("Done creating virtual markers")
        return empties

    except Exception as e:
        logger.exception(f"Error loading empty markers: {e}!")
        raise
