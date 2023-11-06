# from typing import Tuple

from typing import Tuple

import bpy
import numpy as np


def create_center_of_mass_trails(center_of_mass_trajectory: np.ndarray,
                                 parent_empty: bpy.types.Object,
                                 tail_past_frames: int,
                                 trail_future_frames: int,
                                 trail_starting_width: float,
                                 trail_minimum_width: float,
                                 trail_size_decay_rate: float,
                                 trail_color: Tuple[float, float, float, float],
                                 ):
    # Create curve from center of mass trajectory
    curve_object = create_curve_from_trajectory(trajectory=center_of_mass_trajectory,
                                                trajectory_name="center_of_mass")
    curve_object.parent = parent_empty

    # Create spheres for both past and future trails

    create_spheres_on_curve(curve_object=curve_object,
                            parent_empty=parent_empty,
                            starting_radius=trail_starting_width,
                            minimum_radius=trail_minimum_width,
                            future_sphere_count=trail_future_frames,
                            past_sphere_count=tail_past_frames,
                            sphere_size_decay_rate=trail_size_decay_rate,
                            color=trail_color)


def create_curve_from_trajectory(trajectory: np.ndarray,
                                 trajectory_name: str):
    # create a new curve and link it to the scene
    curvedata = bpy.data.curves.new(name=f"{trajectory_name}_curve_data", type='CURVE')
    curve_object = bpy.data.objects.new(f"{trajectory_name}_trajectory", curvedata)
    bpy.context.collection.objects.link(curve_object)

    # create a new spline in the curve
    polyline = curvedata.splines.new('BEZIER')
    polyline.bezier_points.add(len(trajectory) - 1)

    # iterate over points to set their coordinates
    for frame_number in range(trajectory.shape[0]):
        
        polyline.bezier_points[frame_number].co = tuple(*trajectory[frame_number, :])  # (x, y, z) is the format for points

    # set the curve to use AUTO handles, so the handles will be tangent to the curve
    for point in polyline.bezier_points:
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'

    return curve_object


def create_spheres_on_curve(curve_object: bpy.types.Object,
                            parent_empty: bpy.types.Object,
                            future_sphere_count: int,
                            past_sphere_count: int,
                            starting_radius: float,
                            minimum_radius: float,
                            sphere_size_decay_rate: float,
                            color: Tuple[float, float, float, float]):
    spheres = []

    for direction in ["future", "past"]:
        if direction == "future":
            sphere_count = future_sphere_count
            offset_sign = -1
        elif direction == "past":
            sphere_count = past_sphere_count
            offset_sign = 1
        else:
            raise ValueError(f"Direction must be 'future' or 'past', not {direction}")

        for sphere_number in range(sphere_count):
            # Create a new sphere
            bpy.ops.mesh.primitive_uv_sphere_add()
            sphere = bpy.context.object
            scale = starting_radius * np.exp(-sphere_size_decay_rate * sphere_number)
            if scale < minimum_radius:
                scale = minimum_radius
            sphere.scale = (scale, scale, scale)
            bpy.ops.object.transform_apply(scale=True)
            sphere.parent = parent_empty
            sphere.name = f"{direction}_sphere_{sphere_number}"
            # Make the sphere follow the curve
            make_mesh_follow_curve(mesh=sphere,
                                   curve_object=curve_object,
                                   offset=sphere_number*offset_sign)

            # Add the sphere to the list of spheres
            spheres.append(sphere)
            # Set color of the spheres
            sphere.data.materials.append(bpy.data.materials.new(name="Trail_Material"))
            sphere.data.materials[0].diffuse_color = color

    return spheres


def make_mesh_follow_curve(mesh: bpy.types.Object,
                           curve_object: bpy.types.Object,
                           offset: int):
    # create a new follow path constraint
    follow_path_constraint = mesh.constraints.new('FOLLOW_PATH')
    follow_path_constraint.offset = offset
    # specify the curve object to follow
    follow_path_constraint.target = curve_object

    # start following the path immediately
    follow_path_constraint.use_fixed_location = False

    # Animate path
    curve_object.data.animation_data_create()
    action_name = f"MyAction_{mesh.name}"  # Generate unique action name
    curve_object.data.animation_data.action = bpy.data.actions.new(name=action_name)
    curve_object.data.animation_data.action.fcurves.new(data_path="eval_time")
    curve_object.data.animation_data.action.fcurves[0].keyframe_points.insert(frame=bpy.context.scene.frame_start, value=bpy.context.scene.frame_start)
    curve_object.data.animation_data.action.fcurves[0].keyframe_points.insert(frame=bpy.context.scene.frame_end, value=bpy.context.scene.frame_end)


if __name__ == "__main__":
    # set start end frame
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 100
    number_of_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start
    # Create a 3D Sine Wave
    x_values = np.linspace(-3 * np.pi, 3 * np.pi, number_of_frames)
    y_values = np.sin(x_values)
    z_values = np.cos(x_values)
    trajectory_in = np.vstack((x_values, y_values, z_values)).T

    # Create a new empty object to serve as the parent for our trail
    bpy.ops.object.empty_add()
    parent_empty_in = bpy.context.object

    # Parameters for the trail
    tail_past_frames_in = int(number_of_frames * .1)
    trail_future_frames_in = int(number_of_frames * .1)
    trail_starting_width_in = 1.0
    trail_minimum_width_in = 0.1
    trail_size_falloff_in = 0.1
    # random color
    trail_color_in = (np.random.rand(), np.random.rand(), np.random.rand(), 1.0)

    # Create the trail
    create_center_of_mass_trails(trajectory_in,
                                 parent_empty_in,
                                 tail_past_frames_in,
                                 trail_future_frames_in,
                                 trail_starting_width_in,
                                 trail_minimum_width_in,
                                 trail_size_falloff_in,
                                 trail_color_in)
