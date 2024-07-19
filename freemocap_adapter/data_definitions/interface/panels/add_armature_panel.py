import bpy
from bpy.types import Panel

def draw_add_armature_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Add Armature Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.add_armature_properties,
        "show_add_rig",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.add_armature_properties.show_add_rig
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Add Armature")

    if fmc_adapter_tool.add_armature_properties.show_add_rig:

        # Add Rig Options
        box = layout.box()

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add Armature Method')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'add_rig_method'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Armature')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'armature'
        )
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Pose')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'pose'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Keep right/left symmetry')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'keep_symmetry'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add finger constraints')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'add_fingers_constraints'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add IK constraints')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'add_ik_constraints'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='IK transition threshold')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'ik_transition_threshold'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add rotation limits')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'use_limit_rotation'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Clear constraints')
        split.split().column().prop(
            fmc_adapter_tool.add_armature_properties,
            'clear_constraints'
        )

        box.operator(
            'fmc_adapter.add_rig',
            text='6. Add Armature'
        )
