import logging
from pathlib import Path

from freemocap_blender.layer1_core_functions.empties.creation.create_freemocap_empties import create_freemocap_empties
from freemocap_blender.layer1_core_functions.load_data.load_freemocap_data import load_freemocap_data
from freemocap_blender.layer1_core_functions.setup_scene.make_parent_empties import create_freemocap_parent_empty
from freemocap_blender.layer1_core_functions.setup_scene.set_start_end_frame import set_start_end_frame

logger = logging.getLogger(__name__)

import bpy


class FREEMOCAP_ADAPTER_load_freemocap_data(bpy.types.Operator):  # , bpy_extras.io_utils.ImportHelper):
    bl_idname = 'freemocap_blender._load_freemocap_data'
    bl_label = "Load FreeMoCap Data"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        try:
            scene = context.scene
            data_properties = scene.freemocap_data_properties

            recording_path = data_properties.recording_path
            if recording_path == "":
                logger.error("No recording path specified")
                return {'CANCELLED'}

            recording_name = Path(recording_path).stem
            origin_name = f"{recording_name}_origin"
            freemocap_origin_axes = create_freemocap_parent_empty(name=origin_name)
            data_properties.data_parent_empty = freemocap_origin_axes

            logger.info("Loading freemocap data....")
            handler = load_freemocap_data(recording_path=recording_path)
            handler.mark_processing_stage("original_from_file")
            set_start_end_frame(number_of_frames=handler.number_of_frames)
        except Exception as e:
            logger.error(e)
            return {'CANCELLED'}

        try:
            logger.info("Creating keyframed empties....")
            empties = create_freemocap_empties(handler=handler,
                                               parent_object=freemocap_origin_axes, )
            logger.success(f"Finished creating keyframed empties: {empties.keys()}")
        except Exception as e:
            logger.error(f"Failed to create keyframed empties: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
