import bpy
from bpy.types import Panel

def draw_adjust_empties_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Adjust Empties Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.adjust_empties_properties,
        "show_adjust_empties",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.adjust_empties_properties.show_adjust_empties
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Adjust Empties")

    if fmc_adapter_tool.adjust_empties_properties.show_adjust_empties:

        # Adjust Empties Options
        box = layout.box()

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Align Reference')
        split.split().column().prop(
            fmc_adapter_tool.adjust_empties_properties,
            'vertical_align_reference'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Angle Offset')
        split.split().column().prop(
            fmc_adapter_tool.adjust_empties_properties,
            'vertical_align_angle_offset'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Ground Reference')
        split.split().column().prop(
            fmc_adapter_tool.adjust_empties_properties,
            'ground_align_reference'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Position Offset')
        split.split().column().prop(
            fmc_adapter_tool.adjust_empties_properties,
            'vertical_align_position_offset'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Correct Fingers Empties')
        split.split().column().prop(
            fmc_adapter_tool.adjust_empties_properties,
            'correct_fingers_empties'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add hand middle empty')
        split.split().column().prop(
            fmc_adapter_tool.adjust_empties_properties,
            'add_hand_middle_empty'
        )

        box.operator(
            'fmc_adapter.adjust_empties',
            text='1. Adjust Empties'
        )
        