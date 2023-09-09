from pathlib import Path

import bpy

import logging

from freemocap_adapter.core_functions.setup_scene.make_parent_empties import create_video_parent_empty

logger  = logging.getLogger(__name__)

from freemocap_adapter.core_functions.load_freemocap_data.load_videos import load_videos



class FMC_ADAPTER_load_videos(bpy.types.Operator):
    bl_idname = 'fmc_adapter.load_videos'
    bl_label = "Load Videos as planes"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        logger.info("Loading videos as planes...")
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool
        fmc_adapter_tool.recording_path



        video_parent_empty = create_video_parent_empty(name=f"{Path(fmc_adapter_tool.recording_path).stem}_video_anchor")
        try:
            load_videos(recording_path=fmc_adapter_tool.recording_path,
                        parent_empty=video_parent_empty, )
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            return {'CANCELLED'}
        return {'FINISHED'}
