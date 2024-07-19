import bpy
from bpy.types import Panel

def draw_add_finger_rotation_limits_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Add Finger Rotation Limits Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.add_finger_rotation_limits_properties,
        "show_add_finger_rotation_limits",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.add_finger_rotation_limits_properties.show_add_finger_rotation_limits
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Add Finger Rotation Limits")

    if fmc_adapter_tool.add_finger_rotation_limits_properties.show_add_finger_rotation_limits:

        # Add Finger Rotation Limits
        box = layout.box()
        box.operator(
            'fmc_adapter.add_finger_rotation_limits',
            text='4. Add Finger Rotation Limits'
        )
