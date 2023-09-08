import math as m
import time

from bpy.types import Operator

from freemocap_adapter.core_functions.export.fbx import export_fbx
import logging
logger = logging.getLogger(__name__)


class FMC_ADAPTER_OT_export_fbx(Operator):
    bl_idname = 'fmc_adapter.export_fbx'
    bl_label = 'Freemocap Adapter - Export FBX'
    bl_description = 'Exports a FBX file containing the rig, the mesh and the baked animation'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        # Get start time
        start = time.time()

        logger.info('Executing Export FBX...')

        # Execute export fbx function
        export_fbx(self, 
                   recording_path=context.scene.fmc_adapter.recording_path,)

        # Get end time and print execution time
        end = time.time()
        logger.debug('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}
