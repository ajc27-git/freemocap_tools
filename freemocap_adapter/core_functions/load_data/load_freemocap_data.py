import logging
from typing import List, Dict

import bpy

from freemocap_adapter.core_functions.empties.create_keyframed_empty import \
    create_keyframed_empty_from_3d_trajectory_data
from freemocap_adapter.core_functions.empties.virtual_markers import test_virtual_marker_definitions, \
    calculate_virtual_marker_trajectory
from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene
from freemocap_adapter.data_models.freemocap_data import FreemocapData
from freemocap_adapter.data_models.mediapipe_names.point_names import MEDIAPIPE_POINT_NAMES
from freemocap_adapter.data_models.mediapipe_names.virtual_markers import MEDIAPIPE_VIRTUAL_MARKER_DEFINITIONS

logger = logging.getLogger(__name__)


def load_freemocap_data(
        recording_path: str,
        mediapipe_names: Dict[str, List[str]] = MEDIAPIPE_POINT_NAMES,
):
    clear_scene()

    logger.info("Loading freemocap_data....")

    try:
        freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)
    except Exception as e:
        logger.info("Failed to load freemocap freemocap_data")
        raise e

    number_of_frames = freemocap_data.body_fr_mar_xyz.shape[0]
    logger.info(f"mediapipe_body_fr_mar_dim.shape: {freemocap_data.body_fr_mar_xyz.shape}\n"
                f"mediapipe_right_hand_fr_mar_dim.shape: {freemocap_data.right_hand_fr_mar_xyz.shape}\n"
                f"mediapipe_left_hand_fr_mar_dim.shape: {freemocap_data.left_hand_fr_mar_xyz.shape}")

    ##############################
    # %% Set start and end frames

    start_frame = 0
    end_frame = number_of_frames

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

    ##############################
    # %% Create Origin Axes
    freemocap_origin_axes = create_freemocap_origin_axes()
    body_empty_scale = 0.03

    load_empties(freemocap_data=freemocap_data,
                 parent=freemocap_origin_axes,
                 names=mediapipe_names,
                 body_empty_scale=body_empty_scale,
                 )

    virtual_marker_names = create_virtual_trajectories(freemocap_data=freemocap_data,
                                                       freemocap_origin_axes=freemocap_origin_axes,
                                                       mediapipe_names=mediapipe_names,
                                                       body_empty_scale=body_empty_scale,
                                                       )

    logger.info(f"Adding virtual marker names to body trajectory names  - {virtual_marker_names}")
    mediapipe_names["body"].extend(virtual_marker_names)
    logger.info("Done creating virtual markers")


def create_virtual_trajectories(body_empty_scale: float,
                                freemocap_data: FreemocapData,
                                freemocap_origin_axes: bpy.types.Object,
                                mediapipe_names: Dict[str, List[str]],
                                ):
    #######################################################################
    # %% create virtual markers
    logger.info("_________________________\n" 
                "-------------------------\n" 
                "Creating virtual markers...")
    # verify that the virtual marker definition dictionary is valid
    test_virtual_marker_definitions(MEDIAPIPE_VIRTUAL_MARKER_DEFINITIONS)
    virtual_marker_names = list(MEDIAPIPE_VIRTUAL_MARKER_DEFINITIONS.keys())
    for virtual_marker_name in virtual_marker_names:
        component_trajectory_names = MEDIAPIPE_VIRTUAL_MARKER_DEFINITIONS[virtual_marker_name]["marker_names"]
        trajectory_weights = MEDIAPIPE_VIRTUAL_MARKER_DEFINITIONS[virtual_marker_name]["marker_weights"]

        logger.info(
            f"Calculating virtual marker trajectory: {virtual_marker_name} \n"
            f"Component trajectories: {component_trajectory_names} \n"
            f" weights: {trajectory_weights}\n"
        )

        virtual_marker_xyz = calculate_virtual_marker_trajectory(
            trajectory_3d_frame_marker_xyz=freemocap_data.body_fr_mar_xyz,
            all_trajectory_names=mediapipe_names["body"],
            component_trajectory_names=component_trajectory_names,
            trajectory_weights=trajectory_weights,
        )
        create_keyframed_empty_from_3d_trajectory_data(
            trajectory_fr_xyz=virtual_marker_xyz,
            trajectory_name=virtual_marker_name,
            parent_origin=freemocap_origin_axes,
            empty_scale=body_empty_scale * 3,
            empty_type="PLAIN_AXES",
        )
    return virtual_marker_names


def load_empties(freemocap_data: FreemocapData,
                 parent: bpy.types.Object,
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
                parent_origin=parent,
                empty_scale=body_empty_scale,
                empty_type="SPHERE",
            )

        for marker_number in range(freemocap_data.right_hand_fr_mar_xyz.shape[1]):
            trajectory_name = right_hand_trajectory_names[marker_number]
            trajectory_fr_xyz = freemocap_data.right_hand_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=parent,
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
                parent_origin=parent,
                empty_scale=hand_empty_scale,
                empty_type="PLAIN_AXES",
            )


    except Exception as e:
        logger.error(f"Error loading empty markers: {e}!")
        raise


def create_freemocap_origin_axes():
    #########################
    ### Create Origin Axes
    bpy.ops.object.empty_add(type="ARROWS")
    freemocap_origin_axes = bpy.context.editable_objects[-1]
    freemocap_origin_axes.name = "freemocap_origin_axes"

    return freemocap_origin_axes
