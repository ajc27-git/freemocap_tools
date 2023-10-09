import time
import bpy
import math
import mathutils
import os
import cv2
import numpy as np
from pathlib import Path
from importlib.machinery import SourceFileLoader
import addon_utils
from .config_variables import *
from .classes import *

# Export the Freemocap Blender output as a video file
def fmc_export_video(scene: bpy.types.Scene=None,
                     export_profile: str='debug') -> None:
    
    print("Exporting fmc video...")
    
    # Get start time
    start = time.time()

    # Place the required cameras
    cameras_positions = place_cameras(scene, export_profile)

    # Place the required lights
    place_lights(scene, cameras_positions)

    # Rearrange the background videos
    rearrange_background_videos(scene, videos_x_separation=0.1)

    # Get the Blender file directory
    file_directory = Path(bpy.data.filepath).parent

    # Add the render background for the export profiles that have background
    if export_profile in ('showcase'):
        add_render_background(scene, file_directory)

    # Set the output directory
    video_folder = file_directory / 'video'
    video_folder.mkdir(parents=True, exist_ok=True)

    # Set the output file name
    output_file = os.path.split(bpy.data.filepath)[1][:-6] + "_aux" + ".mp4"

    # Set the rendering properties
    for key, value in render_parameters.items():

        # Split the key into context and property names
        key_parts = key.split(".")

        # Start with the bpy.context object
        context = bpy.context

        # Traverse through the key parts to access the correct context and property
        for part in key_parts[:-1]:
            context = getattr(context, part)

        # Assign the new value to the property
        setattr(context, key_parts[-1], value)

    # Set the render resolution based on the export profile
    bpy.context.scene.render.resolution_x               = export_profiles[export_profile]['resolution_x']
    bpy.context.scene.render.resolution_y               = export_profiles[export_profile]['resolution_y']

    # Set the output file
    render_path = os.path.join(video_folder, output_file)
    bpy.context.scene.render.filepath = render_path

    # Render the animation
    bpy.ops.render.render(animation=True)

    # Add the visual components
    add_visual_components(render_path=render_path,
                          file_directory=file_directory,
                          export_profile=export_profile,
                          scene=scene)

    # Try to remove the auxiliary video file
    try:
        os.remove(render_path)
    except:
        print('Error while removing the auxiliary video file.')    

    # Get end time and print execution time
    end = time.time()
    print('Finished Rendering. Execution time (s): ' + str(math.trunc((end - start)*1000)/1000))


def place_cameras(
    scene: bpy.types.Scene=None,
    export_profile: str='debug'
) -> list:
    
    # Set the horizontal and vertical FOV according to the aspect ratio
    if export_profiles[export_profile]['resolution_x'] / export_profiles[export_profile]['resolution_y'] >= 1:
        camera_horizontal_fov = lens_FOVs['50mm']['horizontal_fov'] # 39.6 # 2 * math.atan((0.5 * render_width) / (0.5 * render_height / math.tan(vFOV / 2)))
        camera_vertical_fov = lens_FOVs['50mm']['vertical_fov'] # 22.8965642148994 # 2 * math.atan((0.5 * render_height) / (0.5 * render_width / math.tan(hFOV / 2)))
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
    highest_point  = mathutils.Vector([0, 0, 0])
    lowest_point    = mathutils.Vector([0, 0, 0])
    leftmost_point  = mathutils.Vector([0, 0, 0])
    rightmost_point = mathutils.Vector([0, 0, 0])

    # Find the extreme points as the highest, lowest, leftmost, rightmost considering all the frames
    for frame in range (scene.frame_start, scene.frame_end):
        
        scene.frame_set(frame)

        for object in scene.objects:
            if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin' and object.name != '_full_body_center_of_mass' and object.name != 'head':
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
    camera_y_axis_distance_leftmost     = leftmost_point[1] - abs(leftmost_point[0]) / math.atan(math.radians(camera_horizontal_fov * angle_margin / 2))
    camera_y_axis_distance_rightmost    = rightmost_point[1] - abs(rightmost_point[0]) / math.atan(math.radians(camera_horizontal_fov * angle_margin / 2))

    # Camera distances to just cover the highest and lowest points considering its centered between the two points on the z axis
    camera_y_axis_distance_highest      = highest_point[1] - ((highest_point[2] - lowest_point[2]) / 2) / math.atan(math.radians(camera_vertical_fov * angle_margin / 2))
    camera_y_axis_distance_lowest       = lowest_point[1] - ((highest_point[2] - lowest_point[2]) / 2) / math.atan(math.radians(camera_vertical_fov * angle_margin / 2))

    # Calculate the final y position of the camera as the minimum distance
    camera_y_axis_distance = min(camera_y_axis_distance_leftmost, camera_y_axis_distance_rightmost, camera_y_axis_distance_highest, camera_y_axis_distance_lowest)

    camera.location = (0, camera_y_axis_distance, highest_point[2] - (highest_point[2] - lowest_point[2]) / 2)
    camera.rotation_euler = (math.radians(90), 0, 0)

    # Add the camera position to the cameras position list
    cameras_positions.append(camera.location)

    return cameras_positions

def place_lights(
    scene: bpy.types.Scene=None,
    cameras_positions: list=None
) -> None:

    # Lights vertical offset in Blender units
    lights_vertical_offset = 2

    # Create the light
    light_data = bpy.data.lights.new(name="Light", type='SPOT')
    light = bpy.data.objects.new(name="Light", object_data=light_data)
    scene.collection.objects.link(light)

    # Set the strength of the light
    light.data.energy = 200 * math.sqrt(lights_vertical_offset**2 + cameras_positions[0][1]**2) 

    # Set the location of the light
    light.location = (cameras_positions[0][0], cameras_positions[0][1], cameras_positions[0][2] + lights_vertical_offset)

    # Set the rotation of the light so it points to the point (0, 0, cameras_positions[0][2])
    light.rotation_euler = (math.atan(abs(cameras_positions[0][1]) / lights_vertical_offset), 0, 0)

def rearrange_background_videos(
    scene: bpy.types.Scene=None,
    videos_x_separation: float=0.1
) -> None:

    # Create a list with the background videos
    background_videos = []

    # Append the background videos to the list
    for object in scene.objects:
        if 'video_' in object.name:
            background_videos.append(object)

    # Get the videos x dimension
    videos_x_dimension = background_videos[0].dimensions.x

    # Calculate the first video x position (from the left to the right)
    first_video_x_position = -(len(background_videos) - 1) / 2 * (videos_x_dimension + videos_x_separation)

    # Iterate through the background videos
    for video_index in range(len(background_videos)):
        
        # Set the location of the video
        background_videos[video_index].location[0] = first_video_x_position + video_index * (videos_x_dimension + videos_x_separation)

def add_visual_components(
    render_path: str,
    file_directory: Path,
    export_profile: str='debug',
    scene: bpy.types.Scene=None,
) -> None:

    # Get a reference to the render
    video = cv2.VideoCapture(render_path)

    # Create a VideoWriter object to write the output frames
    output_writer = cv2.VideoWriter(
        os.path.dirname(render_path) + '/' + os.path.basename(render_path)[:-7] + export_profile + '.mp4',
        cv2.VideoWriter_fourcc(*'mp4v'),
        render_parameters['scene.render.fps'],
        (export_profiles[export_profile]['resolution_x'],
         export_profiles[export_profile]['resolution_y']),
         export_profiles[export_profile]['bitrate'],
    )
    
    # Create new frame_info object
    frame_info  = frame_information(
        file_directory=str(file_directory),
        width=export_profiles[export_profile]['resolution_x'],
        height=export_profiles[export_profile]['resolution_y'],
        total_frames=int(video.get(cv2.CAP_PROP_FRAME_COUNT)),
        total_frames_digits=len(str(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))),
        scene=scene,
    )

    # Creat the visual component objects list
    visual_components = []
    for visual_component in export_profiles[export_profile]['visual_components']:
        visual_component_class = globals()[visual_component]
        visual_components.append(visual_component_class(frame_info))

    index_frame = 0
    # Add the logo to the video
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        # Update the frame number in frame_info
        frame_info.frame_number = index_frame

        # Add each visual component
        for visual_component in visual_components:
            frame = visual_component.add_component(frame, frame_info)

        # Write the frame
        output_writer.write(frame)

        index_frame += 1

    video.release()
    output_writer.release()
    cv2.destroyAllWindows()

def add_render_background(scene: bpy.types.Scene=None,
                          file_directory: Path=None,):
    
    # Set the path to the PNG image
    image_path = str(file_directory) + "/charuco_board.png"
    
    # check if the addon is enabled
    loaded_default, loaded_state = addon_utils.check('io_import_images_as_planes')
    if not loaded_state:
        # enable the addon
        addon_utils.enable('io_import_images_as_planes')

    # Import the image as plane
    bpy.ops.import_image.to_plane(files=[{"name": str(image_path)}],
                                  size_mode='ABSOLUTE',
                                  height=render_background['height'],
    )

    # Change the location of the plane ot be behind the video_0 element
    bpy.data.objects['charuco_board'].location = (bpy.data.objects['charuco_board'].location[0],
                                                  bpy.data.objects['video_0'].location[1] + render_background['y_axis_offset'],
                                                  bpy.data.objects['Front_Camera'].location[2])
