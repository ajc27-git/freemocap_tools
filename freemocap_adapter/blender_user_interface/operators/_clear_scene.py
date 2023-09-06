from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene

import bpy
class FMC_ADAPTER_clear_scene(bpy.types.Operator):
    bl_idname = 'fmc_adapter.clear_scene'
    bl_label = "Clear Scene"

    def execute(self, context):
        clear_scene()
        return {'FINISHED'}
