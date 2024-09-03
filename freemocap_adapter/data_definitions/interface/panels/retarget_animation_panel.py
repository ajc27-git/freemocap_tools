import bpy
from bpy.types import Panel

def draw_retarget_animation_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Retarget Animation Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.retarget_animation_properties,
        "show_retarget_animation",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.retarget_animation_properties.show_retarget_animation
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Retarget Animation")

    if fmc_adapter_tool.retarget_animation_properties.show_retarget_animation:

        # Retarget Animation Options
        box = layout.box()
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Source FreeMoCap Armature')
        split.split().column().prop(
            fmc_adapter_tool.retarget_animation_properties,
            'source_armature'
        )
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Target Armature')
        split.split().column().prop(
            fmc_adapter_tool.retarget_animation_properties,
            'target_armature'
        )

        # split = box.column().row().split(factor=0.6)
        # split.column().label(text='Target Armature Type')
        # split.split().column().prop(
        #     fmc_adapter_tool.retarget_animation_properties,
        #     'target_armature_type'
        # )
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Bake Animation')
        split.split().column().prop(
            fmc_adapter_tool.retarget_animation_properties,
            'bake_animation'
        )
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Clear Constraints')
        split.split().column().prop(
            fmc_adapter_tool.retarget_animation_properties,
            'clear_constraints'
        )

        box.operator(
            'fmc_adapter.retarget_animation',
            text='9. Retarget Animation'
        )
