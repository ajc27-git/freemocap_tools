from typing import List
import bpy
import numpy as np

import logging
logger = logging.getLogger(__name__)

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
