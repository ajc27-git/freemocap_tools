from pathlib import Path
from typing import Union

import numpy as np


import bpy

import logging

from freemocap_adapter.core_functions.load_data.load_freemocap_data import create_world_origin_axes

logger  = logging.getLogger(__name__)

from freemocap_adapter.core_functions.load_data.load_videos import load_videos



class FMC_ADAPTER_load_videos(bpy.types.Operator):
    bl_idname = 'fmc_adapter.load_videos'
    bl_label = "Load Videos as planes"

    def execute(self, context):
        logger.info("Loading videos as planes...")
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        world_origin_axes = create_world_origin_axes()
        try:
            load_videos(recording_path=fmc_adapter_tool.recording_path,
                        world_origin_axes=world_origin_axes,)
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            return {'CANCELLED'}
        return {'FINISHED'}
