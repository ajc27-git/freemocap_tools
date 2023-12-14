import math

import bpy
import mathutils

from ajc27_freemocap_blender_addon.data_models.parameter_models.video_config import export_profiles, lens_FOVs


def place_cameras(
        scene: bpy.types.Scene = None,
        export_profile: str = 'debug'
) -> list:
    # Set the horizontal and vertical FOV according to the aspect ratio
    if export_profiles[export_profile]['resolution_x'] / export_profiles[export_profile]['resolution_y'] >= 1:
        camera_horizontal_fov = lens_FOVs['50mm'][
            'horizontal_fov']  # 39.6 # 2 * math.atan((0.5 * render_width) / (0.5 * render_height / math.tan(vFOV / 2)))
        camera_vertical_fov = lens_FOVs['50mm'][
            'vertical_fov']  # 22.8965642148994 # 2 * math.atan((0.5 * render_height) / (0.5 * render_width / math.tan(hFOV / 2)))
    else:
        camera_horizontal_fov = lens_FOVs['50mm']['vertical_fov']
        camera_vertical_fov = lens_FOVs['50mm']['horizontal_fov']

    # Camera angle margin to show more area than the capture movement
    angle_margin = 0.9

    # List of cameras positions
    cameras_positions = []

    # Create the camera
    camera_data = bpy.data.cameras.new(name="Front_Camera")
    camera = bpy.data.objects.new(name="Front_Camera", object_data=camera_data)
    scene.collection.objects.link(camera)

    # Assign the camera to the scene
    scene.camera = camera

    # Set the starting extreme points
    highest_point = mathutils.Vector([0, 0, 0])
    lowest_point = mathutils.Vector([0, 0, 0])
    leftmost_point = mathutils.Vector([0, 0, 0])
    rightmost_point = mathutils.Vector([0, 0, 0])

    # Find the extreme points as the highest, lowest, leftmost, rightmost considering all the frames
    for frame in range(scene.frame_start, scene.frame_end):

        scene.frame_set(frame)

        for object in scene.objects:
            if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin' and object.name != 'center_of_mass_data_parent' and object.name != 'head':
                if object.matrix_world.translation[2] > highest_point[2]:
                    highest_point = object.matrix_world.translation.copy()
                if object.matrix_world.translation[2] < lowest_point[2]:
                    lowest_point = object.matrix_world.translation.copy()
                if object.matrix_world.translation[0] < leftmost_point[0]:
                    leftmost_point = object.matrix_world.translation.copy()
                if object.matrix_world.translation[0] > rightmost_point[0]:
                    rightmost_point = object.matrix_world.translation.copy()

    # Draw the extreme points as mesh spheres
    # bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, enter_editmode=False, align='WORLD', location=highest_point, scale=(1, 1, 1))
    # bpy.data.objects['Sphere'].name = 'highest_point'
    # bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, enter_editmode=False, align='WORLD', location=lowest_point, scale=(1, 1, 1))
    # bpy.data.objects['Sphere'].name = 'lowest_point'
    # bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, enter_editmode=False, align='WORLD', location=leftmost_point, scale=(1, 1, 1))
    # bpy.data.objects['Sphere'].name = 'leftmost_point'
    # bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, enter_editmode=False, align='WORLD', location=rightmost_point, scale=(1, 1, 1))
    # bpy.data.objects['Sphere'].name = 'rightmost_point'

    # Calculate the position of the camera assuming is centered at 0 on the x axis and pointing towards the y axis
    # and covers the extreme points including a margin

    # Camera distances to just cover the leftmost and rightmost points
    camera_y_axis_distance_leftmost = leftmost_point[1] - abs(leftmost_point[0]) / math.atan(
        math.radians(camera_horizontal_fov * angle_margin / 2))
    camera_y_axis_distance_rightmost = rightmost_point[1] - abs(rightmost_point[0]) / math.atan(
        math.radians(camera_horizontal_fov * angle_margin / 2))

    # Camera distances to just cover the highest and lowest points considering its centered between the two points on the z axis
    camera_y_axis_distance_highest = highest_point[1] - ((highest_point[2] - lowest_point[2]) / 2) / math.atan(
        math.radians(camera_vertical_fov * angle_margin / 2))
    camera_y_axis_distance_lowest = lowest_point[1] - ((highest_point[2] - lowest_point[2]) / 2) / math.atan(
        math.radians(camera_vertical_fov * angle_margin / 2))

    # Calculate the final y position of the camera as the minimum distance
    camera_y_axis_distance = min(camera_y_axis_distance_leftmost, camera_y_axis_distance_rightmost,
                                 camera_y_axis_distance_highest, camera_y_axis_distance_lowest)

    camera.location = (0, camera_y_axis_distance, highest_point[2] - (highest_point[2] - lowest_point[2]) / 2)
    camera.rotation_euler = (math.radians(90), 0, 0)

    # Add the camera position to the cameras position list
    cameras_positions.append(camera.location)

    return cameras_positions
