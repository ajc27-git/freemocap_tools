import math as m
import time

from bpy.types import Operator
from freemocap_adapter.core_functions.empties.reorient_empties import reorient_empties

from freemocap_adapter.core_functions.rig.add_rig import add_rig
from freemocap_adapter.blender_user_interface.operators._add_body_mesh import REORIENT_EMPTIES_EXECUTED
import logging
logger = logging.getLogger(__name__)

class FMC_ADAPTER_OT_add_rig(Operator):
    bl_idname = 'fmc_adapter.add_rig'
    bl_label = 'Freemocap Adapter - Add Rig'
    bl_description = 'Add a Rig to the capture empties. The method sets the rig rest pose as a TPose'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        logger.info(f"Executing {__name__}...")
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

        if not REORIENT_EMPTIES_EXECUTED:
            logger.debug('Executing First Adjust Empties...')

            # Execute Adjust Empties first
            reorient_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                           z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                           ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                           z_translation_offset=fmc_adapter_tool.vertical_align_position_offset,
                           add_hand_middle_empty=fmc_adapter_tool.add_hand_middle_empty,
                           )

        logger.debug('Executing Add Rig...')

        add_rig(bone_length_method=fmc_adapter_tool.bone_length_method,
                keep_symmetry=fmc_adapter_tool.keep_symmetry,
                add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
                use_limit_rotation=fmc_adapter_tool.use_limit_rotation)

        # Get end time and print execution time
        end = time.time()
        logger.debug('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}
