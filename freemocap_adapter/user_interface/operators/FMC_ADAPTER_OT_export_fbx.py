import math as m
import time

from bpy.types import Operator

from freemocap_adapter.core_functions.export.fbx import export_fbx


class FMC_ADAPTER_OT_export_fbx(Operator):
    bl_idname = 'fmc_adapter.export_fbx'
    bl_label = 'Freemocap Adapter - Export FBX'
    bl_description = 'Exports a FBX file containing the rig, the mesh and the baked animation'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        # Get start time
        start = time.time()

        print('Executing Export FBX...')

        # Execute export fbx function
        export_fbx(self)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}
