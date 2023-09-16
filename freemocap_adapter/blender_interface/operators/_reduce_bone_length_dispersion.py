import logging
import math as m
import time

from bpy.types import Operator

from freemocap_adapter.core_functions.bones.reduce_bone_length_dispersion import reduce_bone_length_dispersion
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.helpers.freemocap_empties_from_parent_object import \
    freemocap_empties_from_parent_object
from freemocap_adapter.core_functions.freemocap_data_operations.load_freemocap_data import load_freemocap_data
from freemocap_adapter.data_models.bones.bone_definitions import BONE_DEFINITIONS

logger = logging.getLogger(__name__)


class FMC_ADAPTER_OT_reduce_bone_length_dispersion(Operator):
    bl_idname = 'fmc_adapter._reduce_bone_length_dispersion'
    bl_label = 'Freemocap Adapter - Reduce Bone Length Dispersion'
    bl_description = 'Reduce the bone length dispersion by moving the tail empty and its children along the bone projection so the bone new length is within the interval'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        recording_path = fmc_adapter_tool.recording_path
        if recording_path == "":
            logger.error("No recording path specified")
            return {'CANCELLED'}
        freemocap_data_handler = load_freemocap_data(recording_path=recording_path)

        frame_number = scene.frame_current  # grab the current frame number so we can set it back after we're done
        # Get start time
        start = time.time()
        logger.info('Executing Reduce Bone Length Dispersion...')

        reduce_bone_length_dispersion(trajectories=freemocap_data_handler.trajectories,
                                      bones=BONE_DEFINITIONS,
                                      interval_variable=fmc_adapter_tool.interval_variable,
                                      interval_factor=fmc_adapter_tool.interval_factor,
                                      )

        # Get end time and print execution time
        end = time.time()
        logger.success('Finished! Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))
        scene.frame_set(frame_number)  # set the frame back to what it was before we started
        return {'FINISHED'}
