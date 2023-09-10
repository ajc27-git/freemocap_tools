
import logging

import bpy

logger = logging.getLogger(__name__)
def create_freemocap_parent_empty(name: str = "freemocap_data_parent_empty"):
    logger.info("Creating freemocap parent empty...")
    bpy.ops.object.empty_add(type="ARROWS")
    parent_empty = bpy.context.editable_objects[-1]
    parent_empty.name = name

    return parent_empty


def create_video_parent_empty(name: str = "video_parent_empty"):
    logger.info("Creating video parent empty...")
    bpy.ops.object.empty_add()
    parent_empty = bpy.context.editable_objects[-1]
    parent_empty.name = name
    parent_empty.scale = (1, 1, 1)
    return parent_empty
