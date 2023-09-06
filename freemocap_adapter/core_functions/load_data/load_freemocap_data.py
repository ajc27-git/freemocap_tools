import logging
from typing import List, Dict

import bpy

from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene
from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData
from freemocap_adapter.data_models.mediapipe_names.trajectory_names import MEDIAPIPE_TRAJECTORY_NAMES

logger = logging.getLogger(__name__)


def load_freemocap_data(
        recording_path: str,
):

    logger.info("Loading freemocap_data....")

    try:
        freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)
        freemocap_data.mark_processing_stage("original_from_file")
        logger.info(f"Loaded freemocap_data from {recording_path} successfully: \n{freemocap_data}")
        logger.debug(str(freemocap_data))
        return freemocap_data
    except Exception as e:
        logger.info("Failed to load freemocap freemocap_data")
        raise e



    set_start_end_frame(number_of_frames)






def set_start_end_frame(number_of_frames:int):
    # %% Set start and end frames
    start_frame = 0
    end_frame = number_of_frames
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame


def create_freemocap_origin_axes():
    logger.info("Creating freemocap origin axes...")
    bpy.ops.object.empty_add(type="ARROWS")
    freemocap_origin_axes = bpy.context.editable_objects[-1]
    freemocap_origin_axes.name = "freemocap_origin_axes"

    return freemocap_origin_axes

def create_world_origin_axes():
    logger.info("Creating world origin axes...")
    bpy.ops.object.empty_add()
    world_origin_axes = bpy.context.editable_objects[-1]
    world_origin_axes.name = "world_origin_axes"

    return world_origin_axes
