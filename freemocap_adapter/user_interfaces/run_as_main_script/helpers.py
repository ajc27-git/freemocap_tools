import logging
import math
import time
from pathlib import Path
from typing import Dict

import bpy

from freemocap_adapter.core_functions.create_mesh.attach_mesh_to_rig import attach_mesh_to_rig
from freemocap_adapter.core_functions.empties.creation.create_freemocap_empties import create_freemocap_empties
from freemocap_adapter.core_functions.empties.reorient_empties import reorient_empties
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler
from freemocap_adapter.core_functions.freemocap_data_operations.load_freemocap_data import load_freemocap_data
from freemocap_adapter.core_functions.freemocap_data_operations.load_videos import load_videos
from freemocap_adapter.core_functions.freemocap_data_operations.save_to_disk.freemocap_data_saver import FreemocapDataSaver
from freemocap_adapter.core_functions.rig.add_rig import add_rig
from freemocap_adapter.core_functions.setup_scene.make_parent_empties import create_video_parent_empty, \
    create_freemocap_parent_empty
from freemocap_adapter.core_functions.setup_scene.set_start_end_frame import set_start_end_frame
from freemocap_adapter.data_models.parameter_models.parameter_models import Config

logger = logging.getLogger(__name__)


def main_add_videos(recording_path: str):
    logger.info("Loading videos as planes...")
    video_parent_empty = create_video_parent_empty(name=f"{Path(recording_path).stem}_video_anchor")
    try:
        load_videos(recording_path=recording_path,
                    parent_empty=video_parent_empty, )
    except Exception as e:
        logger.error(e)
        logger.exception(e)
        raise e


def main_attach_mesh_to_rig(config: Config):
    logger.info("Adding body mesh...")
    attach_mesh_to_rig(body_mesh_mode=config.add_body_mesh.body_mesh_mode)


def main_save_data_to_disk(freemocap_data_handler: FreemocapDataHandler,
                           recording_path: str,
                           empties: Dict[str, bpy.types.Object]):
    try:
        freemocap_data_handler.extract_data_from_empties(empties=empties)
        FreemocapDataSaver(freemocap_data_handler=freemocap_data_handler).save(recording_path=recording_path)
    except Exception as e:
        logger.error(f"Failed to save data to disk: {e}")
        logger.exception(e)
        raise e


def main_add_rig(config: Config,
                 empties: Dict[str, bpy.types.Object]):
    try:
        logger.info("Adding rig...")
        add_rig(empties=empties,
                bone_length_method=config.add_rig.bone_length_method,
                keep_symmetry=config.add_rig.keep_symmetry,
                add_fingers_constraints=config.add_rig.add_fingers_constraints,
                use_limit_rotation=config.add_rig.use_limit_rotation,
                )
    except Exception as e:
        logger.error(f"Failed to add rig: {e}")
        logger.exception(e)
        raise e


def main_reorient_empties(config: Config,
                          empties: Dict[str, bpy.types.Object],
                          freemocap_origin_axes: bpy.types.Object,
                          good_clean_frame: int,
                          ) -> Dict[str, bpy.types.Object]:
    scene = bpy.context.scene
    try:
        start = time.time()
        logger.info('Executing Re-orient Empties...')

        scene.frame_set(good_clean_frame)

        reoriented_empties = reorient_empties(z_align_ref_empty=config.adjust_empties.vertical_align_reference,
                                              z_align_angle_offset=config.adjust_empties.vertical_align_angle_offset,
                                              ground_ref_empty=config.adjust_empties.ground_align_reference,
                                              z_translation_offset=config.adjust_empties.vertical_align_position_offset,
                                              correct_fingers_empties=config.adjust_empties.correct_fingers_empties,
                                              empties=empties,
                                              parent_object=freemocap_origin_axes,
                                              )

        # Get end time and print execution time
        end = time.perf_counter()
        logger.success(
            'Finished reorienting empties! Execution time (s): ' + str(math.trunc((end - start) * 1000) / 1000))
        return reoriented_empties
    except Exception as e:
        logger.exception(f'Error while reorienting empties! {e}')


def main_create_empties(freemocap_data_handler: FreemocapDataHandler,
                        freemocap_origin_axes: bpy.types.Object):
    try:
        # estimate good clean frame (where the body is most still)
        bpy.ops.screen.animation_play()
        bpy.ops.screen.animation_cancel()
        logger.info("Creating keyframed empties....")
        empties = create_freemocap_empties(freemocap_data_handler=freemocap_data_handler,
                                           parent_object=freemocap_origin_axes, )
        logger.success(f"Finished creating keyframed empties: {empties.keys()}")
    except Exception as e:
        logger.error(f"Failed to create keyframed empties: {e}")
    return empties


def main_load_freemocap(recording_path):
    try:
        recording_name = Path(recording_path).stem
        origin_name = f"{recording_name}_origin"
        freemocap_origin_axes = create_freemocap_parent_empty(name=origin_name)

        logger.info("Loading freemocap data....")
        freemocap_data_handler = load_freemocap_data(recording_path=recording_path)
        freemocap_data_handler.mark_processing_stage("original_from_file")
        set_start_end_frame(number_of_frames=freemocap_data_handler.number_of_frames)
    except Exception as e:
        logger.error(f"Failed to load freemocap data: {e}")
        raise e
    return freemocap_data_handler, freemocap_origin_axes


def validate_recording_path(recording_path):
    if recording_path == "":
        logger.error("No recording path specified")
        raise FileNotFoundError("No recording path specified")
    if not Path(recording_path).exists():
        logger.error(f"Recording path {recording_path} does not exist")
        raise FileNotFoundError(f"Recording path {recording_path} does not exist")
