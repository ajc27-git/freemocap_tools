import logging

import bpy

from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

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


def set_start_end_frame(number_of_frames: int):
    # %% Set start and end frames
    start_frame = 0
    end_frame = number_of_frames
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame


def create_freemocap_parent_empty(name: str = "freemocap_data_parent_empty"):
    logger.info("Creating freemocap parent empty...")
    bpy.ops.object.empty_add(type="ARROWS")
    parent_empty = bpy.context.editable_objects[-1]
    parent_empty.name = name

    return parent_empty


def create_video_parent_empty(name: str = "video_parent_empty"):
    logger.info("Creating video parent empty...")
    bpy.ops.object.empty_add(type="SPHERE")
    parent_empty = bpy.context.editable_objects[-1]
    parent_empty.name = name
    parent_empty.scale = (0.25, 0.25, 0.25)
    return parent_empty
