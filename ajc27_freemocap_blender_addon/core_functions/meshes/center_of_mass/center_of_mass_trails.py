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
                                 trail_size_falloff: float,
                                 trail_color: Tuple[float, float, float, float],
                                 ):
    # Create curve from center of mass trajectory
    curve_object = create_curve_from_trajectory(center_of_mass_trajectory)
    curve_object.parent = parent_empty

    # Create spheres for both past and future trails
    total_spheres = tail_past_frames + trail_future_frames
    sphere_decay = (trail_starting_width - trail_minimum_width) / total_spheres
    create_spheres_on_curve(curve_object, total_spheres, sphere_decay)

    # Set color of the spheres
    for obj in curve_object.children:
        if obj.data:  # to make sure the object is a mesh
            obj.data.materials.append(bpy.data.materials.new(name="Trail_Material"))
            obj.data.materials[0].diffuse_color = trail_color


def create_curve_from_trajectory(trajectory):
    # create a new curve and link it to the scene
    curvedata = bpy.data.curves.new(name="Curve", type='CURVE')
    curve_object = bpy.data.objects.new('Curve_from_trajectory', curvedata)
    bpy.context.collection.objects.link(curve_object)

    # create a new spline in the curve
    polyline = curvedata.splines.new('BEZIER')
    polyline.bezier_points.add(len(trajectory) - 1)

    # iterate over points to set their coordinates
    for i, point in enumerate(trajectory):
        x, y, z = point
        polyline.bezier_points[i].co = (x, y, z)  # (x, y, z) is the format for points

    # set the curve to use AUTO handles, so the handles will be tangent to the curve
    for point in polyline.bezier_points:
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'

    return curve_object

def create_spheres_on_curve(curve_object, total_spheres, sphere_decay):
    spheres = []
    for i in range(total_spheres):
        # Create a new sphere
        bpy.ops.mesh.primitive_uv_sphere_add()
        sphere = bpy.context.object

        # Make the sphere follow the curve
        make_mesh_follow_curve(sphere, curve_object, i * sphere_decay)

        # Add the sphere to the list of spheres
        spheres.append(sphere)

    return spheres
def make_mesh_follow_curve(mesh, curve_object, offset):
    # create a new follow path constraint
    follow_path_constraint = mesh.constraints.new('FOLLOW_PATH')
    follow_path_constraint.offset = offset
    # specify the curve object to follow
    follow_path_constraint.target = curve_object

    # start following the path immediately
    follow_path_constraint.use_fixed_location = False

    # Animate path
    curve_object.data.animation_data_create()
    curve_object.data.animation_data.action = bpy.data.actions.new(name="MyAction")
    curve_object.data.animation_data.action.fcurves.new(data_path="eval_time")
    curve_object.data.animation_data.action.fcurves[0].keyframe_points.insert(frame=0, value=0)
    curve_object.data.animation_data.action.fcurves[0].keyframe_points.insert(frame=100, value=100)




if __name__ == "__main__":
    # Create a 3D Sine Wave
    x_values = np.linspace(0, 10, 100)
    y_values = np.sin(x_values)
    z_values = np.zeros_like(x_values)
    trajectory = np.vstack((x_values, y_values, z_values)).T

    # Create a new empty object to serve as the parent for our trail
    bpy.ops.object.empty_add()
    parent_empty = bpy.context.object

    # Parameters for the trail
    tail_past_frames = 10
    trail_future_frames = 10
    trail_starting_width = 1.0
    trail_minimum_width = 0.1
    trail_size_falloff = 0.1
    trail_color = (1.0, 0.0, 0.0, 1.0)  # Red

    # Create the trail
    create_center_of_mass_trails(trajectory, parent_empty, tail_past_frames, trail_future_frames,
                                 trail_starting_width, trail_minimum_width, trail_size_falloff, trail_color)
