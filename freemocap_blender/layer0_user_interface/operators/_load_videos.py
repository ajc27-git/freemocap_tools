import logging

import bpy

logger = logging.getLogger(__name__)

from freemocap_blender.layer1_core_functions.load_data.load_videos import load_videos


class FREEMOCAP_ADAPTER_load_videos(bpy.types.Operator):
    bl_idname = 'freemocap_blender._load_videos'
    bl_label = "Load Videos as planes"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        logger.info("Loading videos as planes...")
        scene = context.scene
        freemocap_blender_tool = scene.freemocap_data_properties

        try:
            load_videos(recording_path=freemocap_blender_tool.recording_path)
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            return {'CANCELLED'}
        return {'FINISHED'}
