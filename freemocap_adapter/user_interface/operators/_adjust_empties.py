import math as m
import time

from bpy.types import Operator

from freemocap_adapter.core_functions.empties.adjust_empties import adjust_empties


class FMC_ADAPTER_OT_adjust_empties(Operator):
    bl_idname = 'fmc_adapter.adjust_empties'
    bl_label = 'Freemocap Adapter - Adjust Empties'
    bl_description = "Change the position of the freemocap_origin_axes empty to so it is placed in an imaginary ground plane of the capture between the actor's feet"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Adjust Empties...')

        adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                       z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                       ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                       z_translation_offset=fmc_adapter_tool.vertical_align_position_offset,
                       correct_fingers_empties=fmc_adapter_tool.correct_fingers_empties,
                       add_hand_middle_empty=fmc_adapter_tool.add_hand_middle_empty
                       )

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))
        return {'FINISHED'}
