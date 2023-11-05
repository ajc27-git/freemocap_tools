# from typing import Tuple

# import bpy
# import numpy as np


# def create_center_of_mass_trails(center_of_mass_empty: bpy.types.Object,
#                                  parent_empty: bpy.types.Object,
#                                  tail_past_frames: int,
#                                  trail_future_frames: int,
#                                  trail_starting_width: float,
#                                  trail_minimum_width: float,
#                                  trail_size_falloff: float,
#                                  trail_color: Tuple[float, float, float, float],
#                                  ):
#     """
#     Create a trail of that shows the previous and upcoming positions of the center of mass trajecotry in a blender curve

#     The meshes fall off in size as they get further from the current frame down to a minimum size
#     """

#     start_frame = bpy.context.scene.frame_start
#     end_frame = bpy.context.scene.frame_end
#     number_of_frames = end_frame - start_frame

#     for frame_number in range(start_frame, end_frame):
#         bpy.context.scene.frame_set(frame_number)
#         current_center_of_mass_location = center_of_mass_empty.location.copy()




# def create_mesh_from_trajectory(trajectory:np.ndarray):

#     # convert your array to a list of tuples
#     vertices = [tuple(point) for point in trajectory.T]

#     # create polyline
#     polyline = bpy.data.curves.new('polyline', 'CURVE')
#     polyline.dimensions = '3D'
#     polyline_line = polyline.splines.new('POLY')

#     # add points to polyline
#     polyline_line.points.add(len(vertices)-1)
#     for index, vertex in enumerate(vertices):
#         x, y, z = vertex
#         polyline_line.points[index].co = (x, y, z, 1) # 4th element is weight

#     # create object
#     object_data_add = bpy.data.objects.new('ObjectName', polyline)

#     # link object to collection
#     bpy.context.collection.objects.link(object_data_add)

if __name__ == "__main__":
    print('hi')
    import bpy
    import math
    import numpy as np

    past_trail_length = 20
    future_trail_length = 10
    # Define the trajectory length
    frames = 100
    bpy.context.scene.frame_end = frames
    t = np.linspace(-2 * np.pi, 2 * np.pi, frames)

    # 3D sine wave trajectory
    x = t
    y = np.sin(t)
    z = np.cos(t)

    trajectory_points = list(zip(x, y, z))
    trail_length = 20  # including the frame in the middle
    bpy.ops.mesh.primitive_uv_sphere_add(scale=(0.1, 0.1, 0.1))
    current_trail_mesh = bpy.context.active_object
    past_trail_meshes = []
    for past_point in range(past_trail_length):
        bpy.ops.mesh.primitive_uv_sphere_add(scale=(0.1, 0.1, 0.1))
        past_trail_meshes.append(bpy.context.active_object)

    for frame_number in range(frames):
        current_trail_mesh.location = trajectory_points[frame_number]
        current_trail_mesh.keyframe_insert(data_path="location", frame=frame_number)
        # Update the trail_meshes' locations and sizes
        for past_frame_number, past_mesh in enumerate(past_trail_meshes):
            if past_frame_number == frame_number:
                past_frame_number = 0
            else:
                past_frame_number = frame_number - past_frame_number
            frame_difference = (np.abs(frame_number - past_frame_number))+1

            scale = 1/frame_difference

            print(f"frame_difference: {frame_difference}, scale: {scale}")
            past_mesh.location = trajectory_points[past_frame_number]
            past_mesh.scale = (scale, scale, scale)

            past_mesh.keyframe_insert(data_path="location",
                                      frame=frame_number)
        


    print('bye')