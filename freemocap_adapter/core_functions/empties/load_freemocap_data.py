from typing import List

import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_keyframed_empty_from_3d_trajectory_data(
    trajectory_fr_xyz: np.ndarray,
    trajectory_name: str,
    parent_origin: List[float, float, float] = (0, 0, 0),
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


def load_and_create_empties(filepath:str):

    if filepath.endswith(".npy"):
        data = np.load(filepath)
    elif filepath.endswith(".csv"):
        data = np.loadtxt(filepath, delimiter=",")

    # Then, you'll create one empty for each trajectory in the data.
    # Again, this is just an example, replace it with your own creation code.
    for i, trajectory in enumerate(data):
        create_keyframed_empty_from_3d_trajectory_data(
            trajectory,
            f"Trajectory {i}"
        )
