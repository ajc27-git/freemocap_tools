import logging
import math as m
import time

from bpy.types import Operator

from freemocap_blender.layer1_core_functions.empties.reorient_empties import reorient_empties
from freemocap_blender.layer1_core_functions.freemocap_data_handler.operations import \
    freemocap_empties_from_parent_object

logger = logging.getLogger(__name__)


class FREEMOCAP_ADAPTER_OT_reorient_empties(Operator):
    bl_idname = 'freemocap_blender._reorient_empties'
    bl_label = 'Freemocap Blender - Re-orient Empties'
    bl_description = "Change the position of the freemocap_origin_axes empty to so it is placed in an imaginary ground plane of the capture between the actor's feet"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        freemocap_blender_tool = scene.freemocap_data_properties
        parent_empty = freemocap_blender_tool.data_parent_empty
        empties = freemocap_empties_from_parent_object(parent_empty)

        frame_number = scene.frame_current  # grab the current frame number so we can set it back after we're done

        # Get start time
        start = time.time()
        logger.info('Executing Re-orient Empties...')
        try:
            reorient_empties(z_align_ref_empty=freemocap_blender_tool.vertical_align_reference,
                             z_align_angle_offset=freemocap_blender_tool.vertical_align_angle_offset,
                             ground_ref_empty=freemocap_blender_tool.ground_align_reference,
                             z_translation_offset=freemocap_blender_tool.vertical_align_position_offset,
                             correct_fingers_empties=freemocap_blender_tool.correct_fingers_empties,
                             empties=empties,
                             parent_object=parent_empty,
                             )

            # Get end time and print execution time
            end = time.time()
            logger.success(
                'Finished reorienting empties! Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))
            scene.frame_set(frame_number)  # set the frame back to what it was before we started
            return {'FINISHED'}
        except Exception as e:
            logger.exception('Error while reorienting empties! {e}')

    def freemocap_empties_from_parent_object(self, parent_empty):
        empties = {empty.name: empty for empty in parent_empty.children}
        return empties
