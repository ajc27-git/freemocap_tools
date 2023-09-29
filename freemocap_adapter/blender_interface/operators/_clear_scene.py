import bpy

from freemocap_adapter.core_functions.setup_scene.clear_scene import clear_scene


class FMC_ADAPTER_clear_scene(bpy.types.Operator):
    bl_idname = 'fmc_adapter._clear_scene'
    bl_label = "Clear Scene"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        clear_scene()
        return {'FINISHED'}