import logging
from pathlib import Path

import bpy

from freemocap_adapter.core_functions.create_mesh.attach_mesh_to_rig import attach_mesh_to_rig
from freemocap_adapter.core_functions.empties.creation.create_freemocap_empties import create_freemocap_empties
from freemocap_adapter.core_functions.empties.reorient_empties import reorient_empties
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler import freemocap_data_handler
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_saver.freemocap_data_saver import \
    FreemocapDataSaver
from freemocap_adapter.core_functions.freemocap_data_operations.load_freemocap_data import load_freemocap_data
from freemocap_adapter.core_functions.freemocap_data_operations.load_videos import load_videos
from freemocap_adapter.core_functions.rig.add_rig import add_rig
from freemocap_adapter.core_functions.setup_scene.make_parent_empties import create_freemocap_parent_empty, \
    create_video_parent_empty
from freemocap_adapter.core_functions.setup_scene.set_start_end_frame import set_start_end_frame
from freemocap_adapter.data_models.parameter_models.parameter_models import Config

logger = logging.getLogger(__name__)


class MainRunner:
    """
    This class is used to run the program as a main script.
    """

    def __init__(self,
                 recording_path: str,
                 config: Config):
        self.config = config

        self.recording_path = Path(recording_path)
        self.recording_name = self.recording_path.stem
        self.origin_name = f"{self.recording_path.stem}_origin"
        self.data_parent_object = create_freemocap_parent_empty(name=self.origin_name)
        self.freemocap_data_handler = None
        self.empties = None

    def load_freemocap_data(self):
        logger.info("Loading freemocap_data....")
        try:
            logger.info("Loading freemocap data....")
            self.freemocap_data_handler = load_freemocap_data(recording_path=self.recording_path)
            self.freemocap_data_handler.mark_processing_stage("original_from_file")
            set_start_end_frame(number_of_frames=self.freemocap_data_handler.number_of_frames)
        except Exception as e:
            logger.error(f"Failed to load freemocap data: {e}")
            raise e

    def create_empties(self):
        try:
            # estimate good clean frame (where the body is most still)
            bpy.ops.screen.animation_play()
            bpy.ops.screen.animation_cancel()
            logger.info("Creating keyframed empties....")
            self.empties = create_freemocap_empties(freemocap_data_handler=self.freemocap_data_handler,
                                                    parent_object=self.data_parent_object,
                                                    )
            logger.success(f"Finished creating keyframed empties: {self.empties.keys()}")
        except Exception as e:
            logger.error(f"Failed to create keyframed empties: {e}")

    def reorient_empties(self):
        scene = bpy.context.scene
        try:
            logger.info('Executing Re-orient Empties...')

            scene.frame_set(self.freemocap_data_handler.good_clean_frame)

            reoriented_empties = reorient_empties(z_align_ref_empty=self.config.adjust_empties.vertical_align_reference,
                                                  z_align_angle_offset=self.config.adjust_empties.vertical_align_angle_offset,
                                                  ground_ref_empty=self.config.adjust_empties.ground_align_reference,
                                                  z_translation_offset=self.config.adjust_empties.vertical_align_position_offset,
                                                  correct_fingers_empties=self.config.adjust_empties.correct_fingers_empties,
                                                  empties=self.empties,
                                                  parent_object=self.data_parent_object,
                                                  )

            logger.success("Finished reorienting empties!")
            return reoriented_empties
        except Exception as e:
            logger.error(f"Failed to reorient empties: {e}")
            logger.exception(e)
            raise e

    def save_data_to_disk(self):
        try:
            self.freemocap_data_handler.extract_data_from_empties(empties=self.empties)
            FreemocapDataSaver(freemocap_data_handler=self.freemocap_data_handler).save(recording_path=self.recording_path)
        except Exception as e:
            logger.error(f"Failed to save data to disk: {e}")
            logger.exception(e)
            raise e


    def add_rig(self):
        try:
            logger.info("Adding rig...")
            add_rig(empties=self.empties,
                    bone_length_method=self.config.add_rig.bone_length_method,
                    keep_symmetry=self.config.add_rig.keep_symmetry,
                    add_fingers_constraints=self.config.add_rig.add_fingers_constraints,
                    use_limit_rotation=self.config.add_rig.use_limit_rotation,
                    )
        except Exception as e:
            logger.error(f"Failed to add rig: {e}")
            logger.exception(e)
            raise e

    def attach_mesh_to_rig(self):
        logger.info("Adding body mesh...")
        attach_mesh_to_rig(body_mesh_mode=self.config.add_body_mesh.body_mesh_mode)

    def add_videos(self):
        logger.info("Loading videos as planes...")

        try:
            load_videos(recording_path=self.recording_path )
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            raise e

