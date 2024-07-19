import bpy
from bpy.types import Panel

def draw_export_fbx_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle FBX Export Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.export_fbx_properties,
        "show_export_fbx",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.export_fbx_properties.show_export_fbx
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="FBX Export")

    if fmc_adapter_tool.export_fbx_properties.show_export_fbx:

        # FBX Export
        box = layout.box()
        split = box.column().row().split(factor=0.6)
        split.column().label(text='FBX Export Type')
        split.split().column().prop(
            fmc_adapter_tool.export_fbx_properties,
            'fbx_type'
        )

        box.operator(
            'fmc_adapter.export_fbx',
            text='8. Export FBX'
        )
