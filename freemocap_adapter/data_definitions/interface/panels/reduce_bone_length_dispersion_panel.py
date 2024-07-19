import bpy
from bpy.types import Panel

def draw_reduce_bone_length_dispersion_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Reduce Bone Length Dispersion Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.reduce_bone_length_dispersion_properties,
        "show_reduce_bone_length_dispersion",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.reduce_bone_length_dispersion_properties.show_reduce_bone_length_dispersion
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Reduce Bone Length Dispersion")

    if fmc_adapter_tool.reduce_bone_length_dispersion_properties.show_reduce_bone_length_dispersion:

        # Reduce Bone Length Dispersion Options
        box = layout.box()

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Variable')
        split.split().column().prop(
            fmc_adapter_tool.reduce_bone_length_dispersion_properties,
            'interval_variable'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Factor')
        split.split().column().prop(
            fmc_adapter_tool.reduce_bone_length_dispersion_properties,
            'interval_factor'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Body (Rig) Height [m]')
        split.split().column().prop(
            fmc_adapter_tool.reduce_bone_length_dispersion_properties,
            'body_height'
        )

        box.operator(
            'fmc_adapter.reduce_bone_length_dispersion',
            text='2. Reduce Bone Length Dispersion'
        )
