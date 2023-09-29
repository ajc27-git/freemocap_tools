import logging
import math as m
import time

from bpy.types import Operator

from freemocap_blender.layer1_core_functions.empties.reduce_shakiness import reduce_shakiness

logger = logging.getLogger(__name__)


class FREEMOCAP_ADAPTER_OT_reduce_shakiness(Operator):
    bl_idname = 'freemocap_adapter._reduce_shakiness'
    bl_label = 'Freemocap Adapter - Reduce Shakiness'
    bl_description = 'Reduce the shakiness of the capture empties by restricting their acceleration to a defined threshold'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        freemocap_adapter_tool = scene.freemocap_data_properties

        # Get start time
        start = time.time()
        logger.info('Executing Reduce Shakiness...')

        reduce_shakiness(recording_fps=freemocap_adapter_tool.recording_fps)

        # Get end time and print execution time
        end = time.time()
        logger.debug('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}
