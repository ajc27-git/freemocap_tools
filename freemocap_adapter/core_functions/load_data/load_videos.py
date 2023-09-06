from typing import Union
from pathlib import Path
import bpy
import addon_utils

import logging

import numpy as np

logger  = logging.getLogger(__name__)

def get_video_paths(path_to_video_folder: Path) -> list:
    """Search the folder for 'mp4' files (case insensitive) and return them as a list"""
    logger.info(f"Searching for videos in {path_to_video_folder}")
    list_of_video_paths = list(Path(path_to_video_folder).glob("*.mp4")) + list(
        Path(path_to_video_folder).glob("*.MP4")
    )
    unique_list_of_video_paths = list(set(list_of_video_paths))

    return unique_list_of_video_paths

def add_videos_to_scene(videos_path: Union[Path, str],
                        parent_object: bpy.types.Object,
                        video_location_scale: float = 3,
                        video_size_scale: float = 3,
                        ):

    logger.info(f"Adding videos to scene...")

    number_of_videos = len(list(get_video_paths(videos_path)))
    logger.debug(f"Found {number_of_videos} videos in {videos_path}")
    for (
        video_number,
        video_path,
    ) in enumerate(get_video_paths(videos_path)):
        logger.info(f"Adding video: {video_path.name} to scene")

        bpy.ops.import_image.to_plane(
            files=[{"name": video_path.name}],
            directory=str(video_path.parent),
            shader="EMISSION",
        )
        logger.trace(f"Added video: {video_path.name} to scene")
        video_as_plane = bpy.context.editable_objects[-1]
        logger.debug(f"video_as_plane: {video_as_plane}")
        video_as_plane.name = "video_" + str(video_number)
        logger.debug(f"video_as_plane.name: {video_as_plane.name}")
        buffer = 1.1
        vid_x = (video_number * buffer - np.mean(np.arange(0, number_of_videos))) * video_location_scale

        video_as_plane.location = [
            vid_x,
            video_location_scale,
            1,
        ]
        video_as_plane.rotation_euler = [np.pi / 2, 0, 0]
        video_as_plane.scale = [video_size_scale] * 3
        video_as_plane.parent = parent_object


def load_videos(recording_path:str,
                world_origin_axes: bpy.types.Object = None,):
    """
    ############################
    Load videos into scene using `videos_as_planes` addon
    """

    recording_path = Path(recording_path)
    if world_origin_axes is None:
        try :
            world_origin_axes = bpy.context.scene.objects["world_origin_axes"]
        except Exception as e:
            logger.warning(f"Could not find `world_origin_axes` object in scene, creating new one")


    if Path(recording_path / "annotated_videos").is_dir():
        videos_path = Path(recording_path / "annotated_videos")
    elif Path(recording_path / "synchronized_videos").is_dir():
        videos_path = Path(recording_path / "synchronized_videos")
    else:
        logger.warning("Did not find an `annotated_videos` or `synchronized_videos` folder in the recording path")
        videos_path = None

    if videos_path is not None:
        try:
            addon_utils.enable("io_import_images_as_planes")
        except Exception as e:
            logger.error("Error enabling `io_import_images_as_planes` addon: ")
            logger.exception(e)
        try:
            add_videos_to_scene(videos_path=videos_path, parent_object=world_origin_axes)
        except Exception as e:
            logger.error("Error adding videos to scene: ")
            logger.exception(e)
