import logging
from pathlib import Path

from freemocap_adapter.core_functions.empties.creation.create_freemocap_empties import create_freemocap_empties
from freemocap_adapter.core_functions.freemocap_data_operations.load_freemocap_data import load_freemocap_data
from freemocap_adapter.core_functions.setup_scene.make_parent_empties import create_freemocap_parent_empty
from freemocap_adapter.core_functions.setup_scene.set_start_end_frame import set_start_end_frame

logger = logging.getLogger(__name__)

import bpy


class FMC_ADAPTER_load_freemocap_data(bpy.types.Operator):  # , bpy_extras.io_utils.ImportHelper):
    bl_idname = 'fmc_adapter.freemocap_data_operations'
    bl_label = "Load FreeMoCap Data"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        try:
            scene = context.scene
            fmc_adapter_tool = scene.fmc_adapter_tool

            recording_path = fmc_adapter_tool.recording_path
            if recording_path == "":
                logger.error("No recording path specified")
                return {'CANCELLED'}

            recording_name = Path(recording_path).stem
            origin_name = f"{recording_name}_origin"
            freemocap_origin_axes = create_freemocap_parent_empty(name=origin_name)
            fmc_adapter_tool.data_parent_empty = freemocap_origin_axes

            logger.info("Loading freemocap data....")
            freemocap_data_handler = load_freemocap_data(recording_path=recording_path)
            freemocap_data_handler.mark_processing_stage("original_from_file")
            set_start_end_frame(number_of_frames=freemocap_data_handler.number_of_frames)
        except Exception as e:
            logger.error(e)
            return {'CANCELLED'}


        scene.frame_set(freemocap_data_handler.good_clean_frame)
        bpy.ops.screen.animation_play()
        bpy.ops.screen.animation_cancel()
       

        try:
            logger.info("Creating keyframed empties....")
            empties = create_freemocap_empties(freemocap_data_handler=freemocap_data_handler,
                                               parent_object=freemocap_origin_axes, )
            logger.success(f"Finished creating keyframed empties: {empties.keys()}")
        except Exception as e:
            logger.error(f"Failed to create keyframed empties: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
