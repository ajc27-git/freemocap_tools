import logging
import math as m
import time

from bpy.types import Operator

from freemocap_adapter.core_functions.bones.reduce_bone_length_dispersion import reduce_bone_length_dispersion
from freemocap_adapter.data_models.bones.bone_definitions import BONE_DEFINITIONS

logger = logging.getLogger(__name__)


class FMC_ADAPTER_OT_reduce_bone_length_dispersion(Operator):
    bl_idname = 'fmc_adapter.reduce_bone_length_dispersion'
    bl_label = 'Freemocap Adapter - Reduce Bone Length Dispersion'
    bl_description = 'Reduce the bone length dispersion by moving the tail empty and its children along the bone projection so the bone new length is within the interval'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool
        parent_empty = fmc_adapter_tool.data_parent_empty
        empties = {empty.name: empty for empty in parent_empty.children}
        # Get start time
        start = time.time()
        logger.info('Executing Reduce Bone Length Dispersion...')

        reduce_bone_length_dispersion(empties=empties,
                                      bones=BONE_DEFINITIONS,
                                      interval_variable=fmc_adapter_tool.interval_variable,
                                      interval_factor=fmc_adapter_tool.interval_factor,
                                      )

        # Get end time and print execution time
        end = time.time()
        logger.success('Finished! Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}
