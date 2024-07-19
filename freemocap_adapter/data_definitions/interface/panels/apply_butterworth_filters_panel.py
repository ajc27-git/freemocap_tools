import bpy
from bpy.types import Panel

def draw_apply_butterworth_filters_panel(context, layout, scipy_available):
    fmc_adapter_tool = context.scene.fmc_adapter_tool

    # Create a button to toggle Apply Butterwort Filters Options
    row = layout.row(align=True)
    row.prop(
        fmc_adapter_tool.apply_butterworth_filters_properties,
        "show_apply_butterworth_filters",
        text="",
        icon='TRIA_DOWN' if
        fmc_adapter_tool.apply_butterworth_filters_properties.show_apply_butterworth_filters
        else 'TRIA_RIGHT',
        emboss=False
    )
    row.label(text="Apply Butterworth Filters (Blender 4.0+)")

    if fmc_adapter_tool.apply_butterworth_filters_properties.show_apply_butterworth_filters:

        # Apply Butterworth Filters
        box = layout.box()

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Section')
        split_titles = split.column().split(factor=0.3)
        split_titles.split().column().label(text='Global (Freq)')
        split_titles.split().column().label(text='Local (Freq, Origin)')

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Core')
        split_params = split.column().split(factor=0.3)
        split1 = split_params.column().split(factor=0.15)
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'apply_global_filter_core'
        )
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'global_filter_core_frequency'
        )
        if not scipy_available:
            split_params.column().label(text='Install scipy module')
        else:
            split2 = split_params.column().split(factor=0.07)
            split2.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'apply_local_filter_core'
            )
            split3 = split2.column().split(factor=0.5)
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_core_frequency'
            )
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_origin_core'
            )

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Arms')
        split_params = split.column().split(factor=0.3)
        split1 = split_params.column().split(factor=0.15)
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'apply_global_filter_arms'
        )
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'global_filter_arms_frequency'
        )
        if not scipy_available:
            split_params.column().label(text='Install scipy module')
        else:
            split2 = split_params.column().split(factor=0.07)
            split2.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'apply_local_filter_arms'
            )
            split3 = split2.column().split(factor=0.5)
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_arms_frequency'
            )
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_origin_arms'
            )

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Hands')
        split_params = split.column().split(factor=0.3)
        split1 = split_params.column().split(factor=0.15)
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'apply_global_filter_hands'
        )
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'global_filter_hands_frequency'
        )
        if not scipy_available:
            split_params.column().label(text='Install scipy module')
        else:
            split2 = split_params.column().split(factor=0.07)
            split2.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'apply_local_filter_hands'
            )
            split3 = split2.column().split(factor=0.5)
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_hands_frequency'
            )
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_origin_hands'
            )

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Fingers')
        split_params = split.column().split(factor=0.3)
        split1 = split_params.column().split(factor=0.15)
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'apply_global_filter_fingers'
        )
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'global_filter_fingers_frequency'
        )
        if not scipy_available:
            split_params.column().label(text='Install scipy module')
        else:
            split2 = split_params.column().split(factor=0.07)
            split2.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'apply_local_filter_fingers'
            )
            split3 = split2.column().split(factor=0.5)
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_fingers_frequency'
            )
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_origin_fingers'
            )

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Legs')
        split_params = split.column().split(factor=0.3)
        split1 = split_params.column().split(factor=0.15)
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'apply_global_filter_legs'
        )
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'global_filter_legs_frequency'
        )
        if not scipy_available:
            split_params.column().label(text='Install scipy module')
        else:
            split2 = split_params.column().split(factor=0.07)
            split2.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'apply_local_filter_legs'
            )
            split3 = split2.column().split(factor=0.5)
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_legs_frequency'
            )
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_origin_legs'
            )

        split = box.column().row().split(factor=0.15)
        split.column().label(text='Feet')
        split_params = split.column().split(factor=0.3)
        split1 = split_params.column().split(factor=0.15)
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'apply_global_filter_feet'
        )
        split1.column().prop(
            fmc_adapter_tool.apply_butterworth_filters_properties,
            'global_filter_feet_frequency'
        )
        if not scipy_available:
            split_params.column().label(text='Install scipy module')
        else:
            split2 = split_params.column().split(factor=0.07)
            split2.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'apply_local_filter_feet'
            )
            split3 = split2.column().split(factor=0.5)
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_feet_frequency'
            )
            split3.column().prop(
                fmc_adapter_tool.apply_butterworth_filters_properties,
                'local_filter_origin_feet'
            )

        box.operator(
            'fmc_adapter.apply_butterworth_filters',
            text='3. Apply Butterworth Filters'
        )
