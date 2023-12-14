import os
from pathlib import Path

from freemocap_video_export.config_variables import render_parameters, export_profiles

import bpy
import cv2

from freemocap_video_export.create_video.visual_overlays import VIDEO_OVERLAY_CLASSES
from freemocap_video_export.create_video.visual_overlays.frame_information_dataclass import FrameInformation


def add_visual_components(
        render_path: str,
        file_directory: Path,
        export_profile: str = 'debug',
        scene: bpy.types.Scene = None,
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
    frame_info = FrameInformation(
        file_directory=str(file_directory),
        width=export_profiles[export_profile]['resolution_x'],
        height=export_profiles[export_profile]['resolution_y'],
        total_frames=int(video.get(cv2.CAP_PROP_FRAME_COUNT)),
        total_frames_digits=len(str(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))),
        scene=scene,
    )

    # Creat the visual component objects list
    visual_components_list = []
    for visual_component in export_profiles[export_profile]['visual_components']:
        visual_component_class = VIDEO_OVERLAY_CLASSES[visual_component]
        try:
            visual_components_list.append(visual_component_class(frame_info))
        except Exception as e:
            print(f"Error instantiating {visual_component_class}: {e}, skipping...")


    index_frame = 0
    # Add the logo to the video
    while video.isOpened():
        success, image = video.read()
        if not success:
            break

        # Update the frame number in frame_info
        frame_info.frame_number = index_frame

        # Add each visual component
        for visual_component in visual_components_list:
            image = visual_component.add_component(image, frame_info)

        # Write the frame
        output_writer.write(image)

        index_frame += 1

    # Delete the "plot_aux.png" file if it exists
    try:
        os.remove(str(frame_info.file_directory) + '/video/' + 'plot_aux.png')
    except FileNotFoundError:
        pass

    video.release()
    output_writer.release()
    cv2.destroyAllWindows()
