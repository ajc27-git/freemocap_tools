# from typing import Tuple
from copy import copy
from typing import Tuple

import bpy
import numpy as np

from ajc27_freemocap_blender_addon.core_functions.empties.creation.create_empty_from_trajectory import \
    create_keyframed_empty_from_3d_trajectory_data


def create_trail_empties(trajectory: np.ndarray,
                         parent_object: bpy.types.Object,
                         tail_past_frames: int,
                         trail_future_frames: int):
    """
    Create a trail of empties from a center of mass empty that correspond to the center of mass empty's location on past and future frames.    
    """
    past_com_trail_empties = []
    for frame in range(1, tail_past_frames+1):
        clipped_trajectory = copy(trajectory[:-frame, :])

        past_com_trail_empties.append(create_keyframed_empty_from_3d_trajectory_data(
            trajectory_fr_xyz=clipped_trajectory,
            trajectory_name=f"past_com_trail_empty_{frame}",
            parent_object=parent_object,
            empty_scale=0.01,
            empty_type="SPHERE",
        )
        )


    future_com_trail_empties = []
    for frame in range(trail_future_frames):
        clipped_trajectory = copy(trajectory[frame:, :])
    
        future_com_trail_empties.append(create_keyframed_empty_from_3d_trajectory_data(
            trajectory_fr_xyz=clipped_trajectory,
            trajectory_name=f"future_com_trail_empty_{frame}",
            parent_object=parent_object,
            empty_scale=0.01,
            empty_type="SPHERE",
        )
        )
    return {"past": past_com_trail_empties, "future": future_com_trail_empties}

def create_center_of_mass_trails(center_of_mass_trajectory: np.ndarray,
                                 parent_empty: bpy.types.Object,
                                 tail_past_frames: int,
                                 trail_future_frames: int,
                                 trail_starting_width: float,
                                 trail_minimum_width: float,
                                 trail_size_decay_rate: float,
                                 trail_color: Tuple[float, float, float, float],
                                 ):
    com_trail_empties = create_trail_empties(trajectory=center_of_mass_trajectory,
                                             parent_object=parent_empty,
                                             tail_past_frames=tail_past_frames,
                                             trail_future_frames=trail_future_frames)
    trail_spheres = {}
    for direction, empties in com_trail_empties.items():
        trail_spheres[direction] = []
        for empty_number, empty in enumerate(empties):
            scale = trail_starting_width * (trail_size_decay_rate ** empty_number)
            if scale < trail_minimum_width:
                scale = trail_minimum_width
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8,
                                                 ring_count=8,
                                                 scale=(scale, scale, scale),
                                                 align='WORLD',
                                                 enter_editmode=False,)
            sphere = bpy.context.editable_objects[-1]
            sphere.name = f"{empty.name}_trail_sphere"
            location_constraint = sphere.constraints.new("COPY_LOCATION")
            location_constraint.target = empty
            if empty_number < len(empties) - 1:
                damped_track_constraint = sphere.constraints.new("DAMPED_TRACK")
                damped_track_constraint.target = empties[empty_number+1]
                damped_track_constraint.track_axis = "TRACK_Z"
            trail_spheres[direction].append(sphere)
