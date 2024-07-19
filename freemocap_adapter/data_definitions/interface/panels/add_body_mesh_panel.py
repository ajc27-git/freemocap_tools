import bpy
from bpy.types import Panel

def draw_add_body_mesh_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Add Body Mesh Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.add_body_mesh_properties,
        "show_add_body_mesh",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.add_body_mesh_properties.show_add_body_mesh
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Add Body Mesh")

    if fmc_adapter_tool.add_body_mesh_properties.show_add_body_mesh:

        # Add Body Mesh Options
        box = layout.box()

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(
            fmc_adapter_tool.add_body_mesh_properties,
            'body_mesh_mode'
        )

        box.operator(
            'fmc_adapter.add_body_mesh',
            text='7. Add Body Mesh'
        )
