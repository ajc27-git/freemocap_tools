import logging
import math as m
import time

from bpy.types import Operator

from freemocap_blender.layer1_core_functions.export.fbx import export_fbx

logger = logging.getLogger(__name__)


class FREEMOCAP_ADAPTER_OT_export_fbx(Operator):
    bl_idname = 'freemocap_adapter._export_fbx'
    bl_label = 'Freemocap Adapter - Export FBX'
    bl_description = 'Exports a FBX file containing the rig, the mesh and the baked animation'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        logger.info('Executing Export FBX...')
        scene = context.scene
        freemocap_adapter_tool = scene.freemocap_data_properties

        recording_path = freemocap_adapter_tool.recording_path
        if recording_path == "":
            logger.error("No recording path specified")
            return {'CANCELLED'}

        # Get start time
        start = time.time()

        # Execute export fbx function
        export_fbx(recording_path=recording_path, )

        # Get end time and print execution time
        end = time.time()
        logger.debug('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}
