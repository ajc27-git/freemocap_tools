import bpy
import bpy_extras

from freemocap_adapter.core_functions.load_data.load_freemocap_data import load_and_create_empties


class FMC_ADAPTER_load_freemocap_data(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'fmc_adapter.load_freemocap_data'
    bl_label = "Load FreeMoCap Data"

    def execute(self, context):
        load_and_create_empties(self.filepath)
        return {'FINISHED'}