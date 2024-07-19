import bpy
from bpy.types import Panel

def draw_apply_foot_locking_panel(context, layout):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Apply Foot Locking Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.apply_foot_locking_properties,
        "show_apply_foot_locking",
        text="", icon='TRIA_DOWN' if
        fmc_adapter_tool.apply_foot_locking_properties.show_apply_foot_locking
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Apply Foot Locking")

    if fmc_adapter_tool.apply_foot_locking_properties.show_apply_foot_locking:

        # Apply Foot Locking Options
        box = layout.box()
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Target Foot')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'target_foot'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Target foot base markers')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'target_base_markers'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Z Threshold (m)')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'z_threshold'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Ground Level (m)')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'ground_level'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Frame Window Minimum Size')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'frame_window_min_size'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Initial Attenuation Count')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'initial_attenuation_count'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Final Attenuation Count')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'final_attenuation_count'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Lock XY at Ground Level')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'lock_xy_at_ground_level'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Knee Hip Compensation Coefficient')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'knee_hip_compensation_coefficient'
        )

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Compensate Upper Body Markers')
        split.split().column().prop(
            fmc_adapter_tool.apply_foot_locking_properties,
            'compensate_upper_body'
        )

        box = layout.box()
        box.operator(
            'fmc_adapter.apply_foot_locking',
            text='5. Apply Foot Locking'
        )
