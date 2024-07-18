import bpy
from bpy.types import Panel

class VIEW3D_PT_reduce_bone_length_dispersion_interface(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap Adapter Alt"
    bl_label = "Reduce Bone Length Dispersion"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Adjust Empties Options
        box = layout.box()

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Variable')
        split.split().column().prop(fmc_adapter_tool, 'interval_variable')

