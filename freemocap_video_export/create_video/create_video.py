import math
import os
import time
from pathlib import Path

from freemocap_video_export.config_variables import render_parameters, export_profiles
from freemocap_video_export.create_video.helpers.add_render_background import add_render_background
from freemocap_video_export.create_video.helpers.add_video_overlays import add_visual_components
from freemocap_video_export.create_video.helpers.place_lights import place_lights
from freemocap_video_export.create_video.helpers.place_cameras import place_cameras
from freemocap_video_export.create_video.helpers.rearrange_background_videos import rearrange_background_videos

import bpy

def create_export_video(scene: bpy.types.Scene,
                        export_profile: str = 'debug') -> None:
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
        add_render_background(scene, 'showcase')

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
    bpy.context.scene.render.resolution_x = export_profiles[export_profile]['resolution_x']
    bpy.context.scene.render.resolution_y = export_profiles[export_profile]['resolution_y']

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
    print('Finished Rendering. Execution time (s): ' + str(math.trunc((end - start) * 1000) / 1000))
