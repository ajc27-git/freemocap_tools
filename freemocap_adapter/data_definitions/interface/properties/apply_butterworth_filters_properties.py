import bpy
from .property_types import PropertyTypes

class ApplyButterworthFiltersProperties(bpy.types.PropertyGroup):
    show_apply_butterworth_filters: PropertyTypes.Bool(
        description = 'Toggle Apply Butterworth Filters Options'
    ) # type: ignore
    position_correction_mode: PropertyTypes.Enum(
        description = 'Position correction mode',
        items = [('overall', 'Overall (Faster)', ''),
                        ('each_children', 'Each Children (Slower)', '')],
    ) # type: ignore
    apply_global_filter_core: PropertyTypes.Bool(
        description = 'Apply global Butterworth filter to core empties '
                        '(hips_center, trunk_center and neck_center)'
    ) # type: ignore
    global_filter_core_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Core empties global Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_core: PropertyTypes.Bool(
        description = 'Apply local Butterworth filter to core empties'
    ) # type: ignore
    local_filter_origin_core: PropertyTypes.Enum(
        description = 'Local filter origin',
        items = [('hips_center', 'Hips', ''),
                        ],
    ) # type: ignore
    local_filter_core_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Core empties local Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_arms: PropertyTypes.Bool(
        name = 'Arms',
        description = 'Apply global Butterworth filter to arms empties '
                        '(shoulde and elbow)'
    ) # type: ignore
    global_filter_arms_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Arms empties global Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_arms: PropertyTypes.Bool(
        description = 'Apply local Butterworth filter to arms empties'
    ) # type: ignore
    local_filter_origin_arms: PropertyTypes.Enum(
        description = 'Local filter origin',
        items = [('neck_center', 'Neck', ''),
                        ],
    ) # type: ignore
    local_filter_arms_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Arms empties local Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_hands: PropertyTypes.Bool(
        name = 'Hands',
        description = 'Apply global Butterworth filter to hands empties '
                        '(wrist and hand)'
    ) # type: ignore
    global_filter_hands_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Hands empties global Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_hands: PropertyTypes.Bool(
        description = 'Apply local Butterworth filter to hands empties'
    ) # type: ignore
    local_filter_origin_hands: PropertyTypes.Enum(
        description = 'Local filter origin',
        items = [('side_elbow', 'Elbow', ''),
                        ],
    ) # type: ignore
    local_filter_hands_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Hands empties local Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_fingers: PropertyTypes.Bool(
        name = 'Fingers',
        description = 'Apply global Butterworth filter to fingers empties '
                        '(_ip, _pip, _dip and _tip)'
    ) # type: ignore
    global_filter_fingers_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Fingers empties global Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_fingers: PropertyTypes.Bool(
        description = 'Apply local Butterworth filter to fingers empties'
    ) # type: ignore
    local_filter_origin_fingers: PropertyTypes.Enum(
        description = 'Local filter origin',
        items = [('side_wrist', 'Wrist', ''),
                        ],
    ) # type: ignore
    local_filter_fingers_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Fingers empties local Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_legs: PropertyTypes.Bool(
        name = 'Legs',
        description = 'Apply global Butterworth filter to legs empties '
                        '(hips and knees)'
    ) # type: ignore
    global_filter_legs_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Legs empties global Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_legs: PropertyTypes.Bool(
        description = 'Apply local Butterworth filter to legs empties'
    ) # type: ignore
    local_filter_origin_legs: PropertyTypes.Enum(
        description = 'Local filter origin',
        items = [('hips_center', 'Hips', ''),
                        ],
    ) # type: ignore
    local_filter_legs_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Legs empties local Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_feet: PropertyTypes.Bool(
        name = 'Feet',
        description = 'Apply global Butterworth filter to feet empties '
                        '(ankle, heel and foot_index)'
    ) # type: ignore
    global_filter_feet_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Feet empties global Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_feet: PropertyTypes.Bool(
        description = 'Apply local Butterworth filter to feet empties'
    ) # type: ignore
    local_filter_origin_feet: PropertyTypes.Enum(
        description = 'Local filter origin',
        items = [('side_knee', 'Knee', ''),
                        ],
    ) # type: ignore
    local_filter_feet_frequency: PropertyTypes.Float(
        default = 7,
        min = 0,
        precision = 2,
        description = 'Feet empties local Butterworth filter cutoff '
                        'frequency (Hz)'
    ) # type: ignore
