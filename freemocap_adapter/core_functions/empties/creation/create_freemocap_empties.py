import logging

import bpy

from freemocap_adapter.core_functions.empties.creation.create_empty_from_trajectory import \
    create_empties
from freemocap_adapter.core_functions.empties.creation.create_virtual_trajectories import calculate_virtual_trajectories
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler

logger = logging.getLogger(__name__)

BODY_EMPTY_SCALE = 0.03


def create_freemocap_empties(freemocap_data_handler: FreemocapDataHandler,
                             parent_object: bpy.types.Object,
                             body_empty_scale: float = BODY_EMPTY_SCALE,
                             ):
    hand_empty_scale = body_empty_scale * 0.5
    logger.info(
        "__\n"
        "Loading freemocap trajectory freemocap data as empty markers..."
        "__\n"
    )

    empties = {}
    try:
        # body trajectories
        empties["body"] = create_empties(trajectory_frame_marker_xyz=freemocap_data_handler.body_frame_name_xyz,
                                         names_list=freemocap_data_handler.body_names,
                                         empty_scale=body_empty_scale,
                                         empty_type="SPHERE",
                                         parent_object=parent_object, )

        empties["hands"] = {}
        # right hand trajectories
        empties["hands"]["right"] = create_empties(
            trajectory_frame_marker_xyz=freemocap_data_handler.right_hand_frame_name_xyz,
            names_list=freemocap_data_handler.right_hand_names,
            empty_scale=hand_empty_scale,
            empty_type="PLAIN_AXES",
            parent_object=parent_object,
        )
        # left hand trajectories
        empties["hands"]["left"] = create_empties(
            trajectory_frame_marker_xyz=freemocap_data_handler.left_hand_frame_name_xyz,
            names_list=freemocap_data_handler.left_hand_names,
            empty_scale=hand_empty_scale,
            empty_type="PLAIN_AXES",
            parent_object=parent_object,
        )
        return empties

    except Exception as e:
        logger.exception(f"Error loading empty markers: {e}!")
        raise
