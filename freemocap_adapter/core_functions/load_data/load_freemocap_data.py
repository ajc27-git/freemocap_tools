import logging
from typing import List, Dict

import bpy

from freemocap_adapter.core_functions.empties.create_keyframed_empty import \
    create_keyframed_empty_from_3d_trajectory_data
from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene
from freemocap_adapter.data_models.freemocap_data import DataPaths, FreeMoCapData
from freemocap_adapter.data_models.mediapipe_names.mediapipe_point_names import MEDIAPIPE_EMPTY_NAMES

logger = logging.getLogger(__name__)


def load_freemocap_data(
        data_paths: DataPaths,
        mediapipe_empty_names: Dict[str, List[str]] = MEDIAPIPE_EMPTY_NAMES,
):
    clear_scene()

    logger.info("Loading data....")


    try:
        data = FreeMoCapData.from_paths(data_paths=data_paths)
    except Exception as e:
        logger.info("Failed to load freemocap data")
        raise e

    number_of_frames = mediapipe_body_fr_mar_xyz.shape[0]
    logger.info(f"mediapipe_body_fr_mar_dim.shape: {mediapipe_body_fr_mar_xyz.shape}\n"
                f"mediapipe_right_hand_fr_mar_dim.shape: {mediapipe_right_hand_fr_mar_xyz.shape}\n"
                f"mediapipe_left_hand_fr_mar_dim.shape: {mediapipe_left_hand_fr_mar_xyz.shape}")

    freemocap_origin_axes = create_scene_origin_axes()

    ##############################
    # %% Set start and end frames

    start_frame = 0
    end_frame = number_of_frames

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

    ############################
    ### Load mocap data as empty markers

    logger.info(
        "_________________________\n"
        "__________________________\n"
        "Loading freemocap trajectory data as empty markers..."
        "_________________________\n"
    )

    mediapipe_body_trajectory_names = [empty_name for empty_name in mediapipe_empty_names["body"]]

    mediapipe_right_hand_trajectory_names = [f"right_hand_{empty_name}" for empty_name in mediapipe_empty_names["hand"]]
    mediapipe_left_hand_trajectory_names = [f"left_hand_{empty_name}" for empty_name in mediapipe_empty_names["hand"]]
    # mediapipe_face_trajectory_names = [f"face_{number}:{empty_name}" for number, empty_name in
    #                                    face_contour_marker_indices]

    try:  # load as much of the data as you can, but if there's an error keep going
        # create empty markers for body
        body_empty_scale = 0.03
        for marker_number in range(mediapipe_body_fr_mar_xyz.shape[1]):
            trajectory_name = mediapipe_body_trajectory_names[marker_number]
            trajectory_fr_xyz = mediapipe_body_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=freemocap_origin_axes,
                empty_scale=body_empty_scale,
                empty_type="SPHERE",
            )

        # create empty markers for right hand
        hand_empty_scale = body_empty_scale * 0.5
        for marker_number in range(mediapipe_right_hand_fr_mar_xyz.shape[1]):
            trajectory_name = mediapipe_right_hand_trajectory_names[marker_number]
            trajectory_fr_xyz = mediapipe_right_hand_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=freemocap_origin_axes,
                empty_scale=hand_empty_scale,
                empty_type="PLAIN_AXES",
            )

        # create empty markers for left hand
        for marker_number in range(mediapipe_left_hand_fr_mar_xyz.shape[1]):
            trajectory_name = mediapipe_left_hand_trajectory_names[marker_number]
            trajectory_fr_xyz = mediapipe_left_hand_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=freemocap_origin_axes,
                empty_scale=hand_empty_scale,
                empty_type="PLAIN_AXES",
            )

        # create empty markers for body segment centers
        body_segment_center_empty_scale = body_empty_scale * 0.7
        for marker_number in range(body_segment_centers_fr_mar_xyz.shape[1]):
            trajectory_name = BODY_SEGMENT_NAMES[marker_number]
            trajectory_fr_xyz = body_segment_centers_fr_mar_xyz[:, marker_number, :]
            create_keyframed_empty_from_3d_trajectory_data(
                trajectory_fr_xyz=trajectory_fr_xyz,
                trajectory_name=trajectory_name,
                parent_origin=freemocap_origin_axes,
                empty_scale=body_segment_center_empty_scale,
                empty_type="PLAIN_AXES",
            )

        # create empty markers for full body center of mass
        full_body_center_of_mass_empty_scale = body_empty_scale * 1.5
        create_keyframed_empty_from_3d_trajectory_data(
            trajectory_fr_xyz=center_of_mass_fr_xyz,
            trajectory_name=FULL_BODY_CENTER_OF_MASS_NAME,
            parent_origin=freemocap_origin_axes,
            empty_scale=full_body_center_of_mass_empty_scale,
            empty_type="SPHERE",
        )

        # # create empty markers for face
        # face_empty_scale = 0.005
        # for marker_number in face_contour_marker_indices:
        #
        #     if marker_number < len(mediapipe_face_trajectory_names):
        #         trajectory_name = mediapipe_face_trajectory_names[marker_number]
        #     else:
        #         trajectory_name = f"face_{marker_number}"
        #
        #     trajectory_fr_xyz = mediapipe_face_fr_mar_xyz[:, marker_number, :]
        #     create_keyframed_empty_from_3d_trajectory_data(
        #         trajectory_fr_xyz=trajectory_fr_xyz,
        #         trajectory_name=trajectory_name,
        #         parent_origin=freemocap_origin_axes,
        #         empty_scale=face_empty_scale,
        #         empty_type="PLAIN_AXES",
        #     )
    except Exception as e:
        logger.info(f"Error loading empty markers: {e}!")

    #######################################################################
    # %% create virtual markers
    logger.info("_________________________\n" "-------------------------\n" "Creating virtual markers...")

    # verify that the virtual marker definition dictionary is valid
    test_virtual_marker_definitions(mediapipe_virtual_marker_definitions_dict)

    virtual_marker_names = list(mediapipe_virtual_marker_definitions_dict.keys())
    for virtual_marker_name in virtual_marker_names:
        component_trajectory_names = mediapipe_virtual_marker_definitions_dict[virtual_marker_name]["marker_names"]
        trajectory_weights = mediapipe_virtual_marker_definitions_dict[virtual_marker_name]["marker_weights"]

        logger.info(
            f"Calculating virtual marker trajectory: {virtual_marker_name} \n"
            f"Component trajectories: {component_trajectory_names} \n"
            f" weights: {trajectory_weights}\n"
        )

        virtual_marker_xyz = calculate_virtual_marker_trajectory(
            trajectory_3d_frame_marker_xyz=mediapipe_body_fr_mar_xyz,
            all_trajectory_names=mediapipe_body_trajectory_names,
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

    logger.info(f"Adding virtual marker names to body trajectory names  - {virtual_marker_names}")
    mediapipe_body_trajectory_names.extend(virtual_marker_names)
    logger.info("Done creating virtual markers")


def create_scene_origin_axes():
    #########################
    ### Create Origin Axes
    bpy.ops.object.empty_add(type="SPHERE", scale=(.3, .3, .3))
    world_origin_axes = bpy.context.editable_objects[-1]
    world_origin_axes.name = "world_origin"  # will stay at origin
    bpy.ops.object.empty_add(type="ARROWS")
    freemocap_origin_axes = bpy.context.editable_objects[-1]
    freemocap_origin_axes.name = "freemocap_origin_axes"

    return freemocap_origin_axes
