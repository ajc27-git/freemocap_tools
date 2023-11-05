from typing import Tuple

import bpy

def create_center_of_mass_trails(center_of_mass_empty: bpy.types.Object,
                                 parent_empty: bpy.types.Object,
                                 tail_past_frames: int,
                                 trail_future_frames: int,
                                 trail_starting_width: float = 0.1,
                                 trail_minimum_width: float = 0.01,
                                 trail_size_falloff: float = 0.5,
                                 trail_color: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0),
                                 ):
    """
    Create a trail of that shows the previous and upcoming positions of the center of mass trajecotry in a blender curve

    The meshes fall off in size as they get further from the current frame down to a minimum size
    """
    pass

# import bpy
# import numpy as np

# # Generate trajectory along a 3D sine wave
# t = np.linspace(0, 10, 100)
# x = np.sin(t)
# y = np.cos(t)
# z = t
# trajectory = np.column_stack((x, y, z))

# # Define middle index of trajectory
# middle_index = len(trajectory) // 2

# # Create a sphere at each point along the trajectory
# for index, position in enumerate(trajectory):
#     # Calculate index distance from the middle point
#     index_distance = abs(index - middle_index)

#     # Scale the radius based on the index distance, adjust the scaling factor as needed
#     raw_radius =  (1 / (index_distance + 0.01))
#     radius = min(raw_radius, 0.2)  # limiting the radius to a maximum of 0.2

#     bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=position)