import logging
from typing import List, Dict

import bpy

from freemocap_adapter.core_functions.empties.create_keyframed_empties import \
    create_keyframed_empty_from_3d_trajectory_data, create_keyframed_empties
from freemocap_adapter.core_functions.empties.virtual_markers import test_virtual_marker_definitions, \
    calculate_virtual_marker_trajectory
from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene
from freemocap_adapter.data_models.freemocap_data import FreemocapData
from freemocap_adapter.data_models.mediapipe_names.point_names import MEDIAPIPE_POINT_NAMES
from freemocap_adapter.data_models.mediapipe_names.virtual_markers import MEDIAPIPE_VIRTUAL_MARKER_DEFINITIONS

logger = logging.getLogger(__name__)

BODY_EMPTY_SCALE = 0.03

def load_freemocap_data(
        recording_path: str,
        mediapipe_names: Dict[str, List[str]] = MEDIAPIPE_POINT_NAMES,
):
    clear_scene()

    logger.info("Loading freemocap_data....")

    try:
        freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)
        return  freemocap_data
    except Exception as e:
        logger.info("Failed to load freemocap freemocap_data")
        raise e



    set_start_end_frame(number_of_frames)

    freemocap_origin_axes = create_freemocap_origin_axes()

    create_keyframed_empties(freemocap_data=freemocap_data,
                             parent_object=freemocap_origin_axes,
                             names=mediapipe_names,
                             body_empty_scale=BODY_EMPTY_SCALE,
                             )




def set_start_end_frame(number_of_frames):
    ##############################
    # %% Set start and end frames
    start_frame = 0
    end_frame = number_of_frames
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame


def create_virtual_trajectories(body_empty_scale: float,
                                freemocap_data: FreemocapData,
                                parent_object: bpy.types.Object,
                                names: Dict[str, List[str]],
                                ):
    #######################################################################
    # %% create virtual markers
    logger.info("_________________________\n" 
                "-------------------------\n" 
                "Creating virtual markers...")


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
            all_trajectory_names=names["body"],
            component_trajectory_names=component_trajectory_names,
            trajectory_weights=trajectory_weights,
        )
        create_keyframed_empty_from_3d_trajectory_data(
            trajectory_fr_xyz=virtual_marker_xyz,
            trajectory_name=virtual_marker_name,
            parent_origin=parent_object,
            empty_scale=body_empty_scale * 3,
            empty_type="PLAIN_AXES",
        )
    return virtual_marker_names


def create_freemocap_origin_axes():
    #########################
    ### Create Origin Axes
    bpy.ops.object.empty_add(type="ARROWS")
    freemocap_origin_axes = bpy.context.editable_objects[-1]
    freemocap_origin_axes.name = "freemocap_origin_axes"

    return freemocap_origin_axes
