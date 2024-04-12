import time
import math as m
import bpy
from bpy.types import Operator, Panel
from .core_functions import (
    adjust_empties,
    reduce_bone_length_dispersion,
    add_rig,
    add_mesh_to_rig,
    add_finger_rotation_limits,
    apply_foot_locking,
    apply_butterworth_filters,
    export_fbx
)
scipy_available = True
try:
    from scipy.signal import butter, filtfilt
except ImportError:
    scipy_available = False
    print("scipy is not installed. Please install scipy to use this addon.")

def update_menu(self, context, menu_name):
    if menu_name == 'armature':
        self.pose = get_pose_items(self, context)[0][0]

def get_pose_items(self, context):
    if self.armature == 'armature_freemocap':
        items = [('freemocap_tpose', 'FreeMoCap T-Pose', ''),
                ('freemocap_apose', 'FreeMoCap A-Pose', '')]
    elif self.armature == 'armature_ue_metahuman_simple':
        items = [('ue_metahuman_tpose', 'UE Metahuman T-Pose', ''),
                 ('ue_metahuman_default', 'UE Metahuman Default', '')]
        
    return items

# Class with the different properties of the methods
class FMC_ADAPTER_PROPERTIES(bpy.types.PropertyGroup):

    # Adjust Empties Options
    show_adjust_empties: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Adjust Empties Options'
    ) # type: ignore
    vertical_align_reference: bpy.props.EnumProperty(
        name = '',
        description = 'Empty that serves as reference to align the z axis',
        items = [('left_knee', 'left_knee', ''),
                       ('trunk_center', 'trunk_center', ''),
                       ('right_knee', 'right_knee', '')]
    ) # type: ignore
    vertical_align_angle_offset: bpy.props.FloatProperty(
        name = '',
        default = 0,
        description = 'Angle offset to adjust the vertical alignement of the '
                      'z axis (in degrees)'
    ) # type: ignore
    ground_align_reference: bpy.props.EnumProperty(
        name = '',
        description = 'Empty that serves as ground reference to the axes '
                      'origin',
        items = [('left_foot_index', 'left_foot_index', ''),
                       ('right_foot_index', 'right_foot_index', ''),
                       ('left_heel', 'left_heel', ''),
                       ('right_heel', 'right_heel', '')]
    ) # type: ignore
    vertical_align_position_offset: bpy.props.FloatProperty(
        name = '',
        default = 0,
        precision = 3,
        description = 'Additional z offset to the axes origin relative to '
                      'the imaginary ground level'
    ) # type: ignore
    correct_fingers_empties: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Correct the fingers empties. Match hand_wrist '
                      '(axis empty) position to wrist (sphere empty)'
    ) # type: ignore
    add_hand_middle_empty: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Add an empty in the middle of the hand between index '
                      'and pinky empties. This empty is used for a better '
                      'orientation of the hand (experimental)'
    ) # type: ignore

    # Reduce Bone Length Dispersion Options
    show_reduce_bone_length_dispersion: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Reduce Bone Length Dispersion Options'
    ) # type: ignore
    interval_variable: bpy.props.EnumProperty(
        name = '',
        description = 'Variable used to define the new length dispersion '
                      'interval',
        items = [
            ('capture_median',
             'Capture Median',
             'Use the bones median length from the capture. Defines the '
             'new dispersion interval as '
             '[median*(1-interval_factor),median*(1+interval_factor)]'),
            ('standard_length',
             'Standard length',
             'Use the standard lengths based on the total body (rig) '
             'height. Defines the new dispersion interval as '
             '[length*(1-interval_factor),length*(1+interval_factor)]'),
            ('capture_stdev',
             'Capture Std Dev',
             'Use the bones length standard deviation from the capture. '
             'Defines the new dispersion interval as '
             '[median-interval_factor*stdev,median+interval_factor*stdev]')]
    ) # type: ignore
    interval_factor: bpy.props.FloatProperty(
        name = '',
        default = 0,
        min = 0,
        precision = 3,
        description = 'Factor to multiply the variable and form the limits of '
                      'the dispersion interval like '
                      '[median-factor*variable,median+factor*variable]. '
                      'If variable is median, the factor will be limited to '
                      'values inside [0, 1]. '  
                      'If variable is stdev, the factor will be limited to '
                      'values inside [0, median/stdev]'
    ) # type: ignore
    body_height: bpy.props.FloatProperty(
        name = '',
        default = 1.75,
        min = 0,
        precision = 3,
        description = 'Body height in meters. This value is used when the '
                      'interval variable is set to standard length. If a rig '
                      'is added after using Reduce Dispersion with standard '
                      'length, it will have this value as height and the '
                      'bones length will be proporions of this height'
    ) # type: ignore

    # Add Rig Options
    show_add_rig: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Add Rig Options'
    ) # type: ignore
    add_rig_method: bpy.props.EnumProperty(
        name = '',
        description = 'Method used to create the rig',
        items = [('using_rigify', 'Using Rigify', ''),
                 ('bone_by_bone', 'Bone by Bone', '')]
    ) # type: ignore
    armature: bpy.props.EnumProperty(
        name = '',
        description = 'Armature that will be used to create the rig',
        items = [('armature_freemocap', 'FreeMoCap', ''),
                 ('armature_ue_metahuman_simple', 'UE Metahuman Simple', '')],
        update = lambda a,b: update_menu(a,
                                         b,
                                         'armature')
    ) # type: ignore
    pose: bpy.props.EnumProperty(
        name = '',
        description = 'Pose that will be used to create the rig',
        items = get_pose_items,
    ) # type: ignore
    bone_length_method: bpy.props.EnumProperty(
        name = '',
        description = 'Method use to calculate length of major bones',
        items = [('median_length', 'Median Length', '')]
    ) # type: ignore
    keep_symmetry: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Keep right/left side symmetry (use average right/left '
                      'side bone length)'
    ) # type: ignore
    add_fingers_constraints: bpy.props.BoolProperty(
        name = '',
        default = True,
        description = 'Add bone constraints for fingers'
    ) # type: ignore
    add_ik_constraints: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Add IK constraints for arms and legs'
    ) # type: ignore
    ik_transition_threshold: bpy.props.FloatProperty(
        name = '',
        default = 0.9,
        min = 0,
        max = 1,
        precision = 2,
        description = 'Threshold of parallel degree (dot product) between '
                      'base and target ik vectors. It is used to transition '
                      'between vectors to determine the pole bone position'
    ) # type: ignore
    use_limit_rotation: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Add rotation limits (human skeleton) to the bones '
                      'constraints (experimental)'
    ) # type: ignore
    clear_constraints: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Clear added constraints after baking animation'
    ) # type: ignore

    # Add Body Mesh Options
    show_add_body_mesh: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Add Body Mesh Options'
    ) # type: ignore
    body_mesh_mode: bpy.props.EnumProperty(
        name = '',
        default = 'skelly_parts',
        description = 'Mode (source) for adding the mesh to the rig',
        items = [('skelly_parts', 'Skelly Parts', ''),
                 ('skelly', 'Skelly', ''),
                 ('can_man', 'Custom', ''),
                ]
    ) # type: ignore

    # Export FBX Options
    show_export_fbx: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Export FBX Options'
    ) # type: ignore
    fbx_type: bpy.props.EnumProperty(
        name = '',
        description = 'Type of the FBX file',
        items = [('standard', 'Standard', ''),
                 ('unreal_engine', 'Unreal Engine', '')
                ]
    ) # type: ignore

    # Add Finger Rotation Limits Options
    show_add_finger_rotation_limits: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Add Finger Rotation Limits options'
    ) # type: ignore

    # Apply Foot Locking Options
    show_apply_foot_locking: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Apply Foot Locking options'
    ) # type: ignore
    foot_locking_target_foot: bpy.props.EnumProperty(
        name = '',
        description = 'Target foot for applying foot locking',
        items = [('both_feet', 'Both Feet', ''),
                 ('left_foot', 'Left Foot', ''),
                 ('right_foot', 'Right Foot', '')
                ]
    ) # type: ignore
    foot_locking_target_base_markers: bpy.props.EnumProperty(
        name = '',
        description = 'Target foot base markers for applying foot locking',
        items = [('foot_index_and_heel', 'foot_index and heel', ''),
                 ('foot_index', 'foot_index', ''),
                 ('heel', 'heel', '')
                ]
    ) # type: ignore
    foot_locking_z_threshold: bpy.props.FloatProperty(
        name = '',
        default = 0.01,
        precision = 3,
        description = 'Vertical threshold under which foot markers are '
                      'considered for applying foot locking'
    ) # type: ignore
    foot_locking_ground_level: bpy.props.FloatProperty(
        name = '',
        default = 0.0,
        precision = 3,
        description = 'Ground level for applying foot locking. Markers with '
                      'z global coordinate lower than this value will be '
                      'fixed to this level. It must be lower than the '
                      'z threshold'
    ) # type: ignore
    foot_locking_frame_window_min_size: bpy.props.IntProperty(
        name = '',
        default = 10,
        min = 1,
        description = 'Minimum frame window size for applying foot locking. '
                      'A markers z global coordinate has to be lower than the '
                      'z threshold for a consecutive frames count equal or '
                      'bigger than this value.'
                      'It must be equal or greater than '
                      'initial_attenuation_count + final_attenuation_count'
    ) # type: ignore
    foot_locking_initial_attenuation_count: bpy.props.IntProperty(
        name = '',
        default = 5,
        min = 0,
        description = 'This are the first frames of the window which have '
                      'their z coordinate attenuated by the the initial '
                      'quadratic attenuation function'
    ) # type: ignore
    foot_locking_final_attenuation_count: bpy.props.IntProperty(
        name = '',
        default = 5,
        min = 0,
        description = 'This are the last frames of the window which have '
                      'their z coordinate attenuated by the the final '
                      'quadratic attenuation function'
    ) # type: ignore
    foot_locking_lock_xy_at_ground_level: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'When applying foot locking, lock also the x and y '
                      'coordinates at the ground level. This is useful only '
                      'when character is standing still as it might leed to '
                      '"sticky" or "lead" feet effect'
    ) # type: ignore
    foot_locking_knee_hip_compensation_coefficient: bpy.props.FloatProperty(
        name = '',
        default = 1.0,
        precision = 3,
        min = 0.0,
        max = 1.0,
        description = 'After calculating the ankle new z global coordinate, '
                      'the knee and hip markers will be adjusted on the z '
                      'axis by the same delta multiplied by this coefficient.'
                      'A value of 1.0 means knee and hip have the same '
                      'adjustment as the ankle. A value of 0 means knee and '
                      'hip have no adjustment at all. Values lower than 1.0 '
                      'are useful when the rig has IK constraints on the legs.'
                      'This way the ankle adjustment is compensated by the '
                      'knee IK bending'
    ) # type: ignore
    foot_locking_compensate_upper_body: bpy.props.BoolProperty(
        name = '',
        default = True,
        description = 'Compensate the upper body markers by setting the new '
                      'z coordinate of the hips_center marker as the average '
                      'z coordinate of left and right hips markers.'
                      'Then propagate the new z delta to the upper body '
                      'markers starting from the trunk_center.'
    ) # type: ignore

    # Apply Butterworth Filters Options
    show_apply_butterworth_filters: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Toggle Apply Butterworth Filters Options'
    ) # type: ignore
    position_correction_mode: bpy.props.EnumProperty(
        name = '',
        description = 'Position correction mode',
        items = [('overall', 'Overall (Faster)', ''),
                       ('each_children', 'Each Children (Slower)', '')],
    ) # type: ignore
    apply_global_filter_core: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply global Butterworth filter to core empties '
                      '(hips_center, trunk_center and neck_center)'
    ) # type: ignore
    global_filter_core_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Core empties global Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_core: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply local Butterworth filter to core empties'
    ) # type: ignore
    local_filter_origin_core: bpy.props.EnumProperty(
        name = '',
        description = 'Local filter origin',
        items = [('hips_center', 'Hips', ''),
                       ],
    ) # type: ignore
    local_filter_core_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Core empties local Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_arms: bpy.props.BoolProperty(
        name = 'Arms',
        default = False,
        description = 'Apply global Butterworth filter to arms empties '
                      '(shoulde and elbow)'
    ) # type: ignore
    global_filter_arms_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Arms empties global Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_arms: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply local Butterworth filter to arms empties'
    ) # type: ignore
    local_filter_origin_arms: bpy.props.EnumProperty(
        name = '',
        description = 'Local filter origin',
        items = [('neck_center', 'Neck', ''),
                       ],
    ) # type: ignore
    local_filter_arms_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Arms empties local Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_hands: bpy.props.BoolProperty(
        name = 'Hands',
        default = False,
        description = 'Apply global Butterworth filter to hands empties '
                      '(wrist and hand)'
    ) # type: ignore
    global_filter_hands_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Hands empties global Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_hands: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply local Butterworth filter to hands empties'
    ) # type: ignore
    local_filter_origin_hands: bpy.props.EnumProperty(
        name = '',
        description = 'Local filter origin',
        items = [('side_elbow', 'Elbow', ''),
                       ],
    ) # type: ignore
    local_filter_hands_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Hands empties local Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_fingers: bpy.props.BoolProperty(
        name = 'Fingers',
        default = False,
        description = 'Apply global Butterworth filter to fingers empties '
                      '(_ip, _pip, _dip and _tip)'
    ) # type: ignore
    global_filter_fingers_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Fingers empties global Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_fingers: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply local Butterworth filter to fingers empties'
    ) # type: ignore
    local_filter_origin_fingers: bpy.props.EnumProperty(
        name = '',
        description = 'Local filter origin',
        items = [('side_wrist', 'Wrist', ''),
                       ],
    ) # type: ignore
    local_filter_fingers_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Fingers empties local Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_legs: bpy.props.BoolProperty(
        name = 'Legs',
        default = False,
        description = 'Apply global Butterworth filter to legs empties '
                      '(hips and knees)'
    ) # type: ignore
    global_filter_legs_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Legs empties global Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_legs: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply local Butterworth filter to legs empties'
    ) # type: ignore
    local_filter_origin_legs: bpy.props.EnumProperty(
        name = '',
        description = 'Local filter origin',
        items = [('hips_center', 'Hips', ''),
                       ],
    ) # type: ignore
    local_filter_legs_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Legs empties local Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_global_filter_feet: bpy.props.BoolProperty(
        name = 'Feet',
        default = False,
        description = 'Apply global Butterworth filter to feet empties '
                      '(ankle, heel and foot_index)'
    ) # type: ignore
    global_filter_feet_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Feet empties global Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore
    apply_local_filter_feet: bpy.props.BoolProperty(
        name = '',
        default = False,
        description = 'Apply local Butterworth filter to feet empties'
    ) # type: ignore
    local_filter_origin_feet: bpy.props.EnumProperty(
        name = '',
        description = 'Local filter origin',
        items = [('side_knee', 'Knee', ''),
                       ],
    ) # type: ignore
    local_filter_feet_frequency: bpy.props.FloatProperty(
        name = '',
        default = 7,
        min = 0,
        precision = 2,
        description = 'Feet empties local Butterworth filter cutoff '
                      'frequency (Hz)'
    ) # type: ignore

# UI Panel Class
class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap Adapter Alt"
    bl_label = "Freemocap Adapter Alt"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Create a button to toggle Adjust Empties Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_adjust_empties",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_adjust_empties
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Adjust Empties")

        if fmc_adapter_tool.show_adjust_empties:

            # Adjust Empties Options
            box = layout.box()

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Align Reference')
            split.split().column().prop(fmc_adapter_tool,
                                        'vertical_align_reference')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Vertical Angle Offset')
            split.split().column().prop(fmc_adapter_tool,
                                        'vertical_align_angle_offset')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Ground Reference')
            split.split().column().prop(fmc_adapter_tool,
                                        'ground_align_reference')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Vertical Position Offset')
            split.split().column().prop(fmc_adapter_tool,
                                        'vertical_align_position_offset')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Correct Fingers Empties')
            split.split().column().prop(fmc_adapter_tool,
                                        'correct_fingers_empties')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add hand middle empty')
            split.split().column().prop(fmc_adapter_tool,
                                        'add_hand_middle_empty')

            box.operator('fmc_adapter.adjust_empties',
                         text='1. Adjust Empties')

        # Create a button to toggle Reduce Bone Length Dispersion Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_reduce_bone_length_dispersion",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_reduce_bone_length_dispersion
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Reduce Bone Length Dispersion")

        if fmc_adapter_tool.show_reduce_bone_length_dispersion:

            # Reduce Bone Length Dispersion Options
            box = layout.box()

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Dispersion Interval Variable')
            split.split().column().prop(fmc_adapter_tool, 'interval_variable')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Dispersion Interval Factor')
            split.split().column().prop(fmc_adapter_tool, 'interval_factor')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Body (Rig) Height [m]')
            split.split().column().prop(fmc_adapter_tool, 'body_height')

            box.operator('fmc_adapter.reduce_bone_length_dispersion',
                         text='2. Reduce Bone Length Dispersion')

        # Create a button to toggle Apply Butterwort Filters Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_apply_butterworth_filters",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_apply_butterworth_filters
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Apply Butterworth Filters (Blender 4.0+)")

        if fmc_adapter_tool.show_apply_butterworth_filters:

            # Apply Butterwort Filters
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
            split1.column().prop(fmc_adapter_tool,
                                 'apply_global_filter_core')
            split1.column().prop(fmc_adapter_tool,
                                 'global_filter_core_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool,
                                     'apply_local_filter_core')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_core_frequency')
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_origin_core')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Arms')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool,
                                 'apply_global_filter_arms')
            split1.column().prop(fmc_adapter_tool,
                                 'global_filter_arms_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool,
                                     'apply_local_filter_arms')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_arms_frequency')
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_origin_arms')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Hands')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool,
                                 'apply_global_filter_hands')
            split1.column().prop(fmc_adapter_tool,
                                 'global_filter_hands_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool,
                                     'apply_local_filter_hands')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_hands_frequency')
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_origin_hands')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Fingers')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool,
                                 'apply_global_filter_fingers')
            split1.column().prop(fmc_adapter_tool,
                                 'global_filter_fingers_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool,
                                     'apply_local_filter_fingers')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_fingers_frequency')
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_origin_fingers')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Legs')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool,
                                 'apply_global_filter_legs')
            split1.column().prop(fmc_adapter_tool,
                                 'global_filter_legs_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool,
                                     'apply_local_filter_legs')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_legs_frequency')
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_origin_legs')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Feet')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool,
                                 'apply_global_filter_feet')
            split1.column().prop(fmc_adapter_tool,
                                 'global_filter_feet_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool,
                                     'apply_local_filter_feet')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_feet_frequency')
                split3.column().prop(fmc_adapter_tool,
                                     'local_filter_origin_feet')

            box.operator('fmc_adapter.apply_butterworth_filters',
                         text='3. Apply Butterworth Filters')

        # Create a button to toggle Add Finger Rotation Limits Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_add_finger_rotation_limits",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_add_finger_rotation_limits
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Add Finger Rotation Limits")

        if fmc_adapter_tool.show_add_finger_rotation_limits:

            # Add Finger Rotation Limits
            box = layout.box()
            box.operator('fmc_adapter.add_finger_rotation_limits',
                         text='4. Add Finger Rotation Limits')

        # Create a button to toggle Add Finger Rotation Limits Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_apply_foot_locking",
                 text="", icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_apply_foot_locking
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Apply Foot Locking")

        if fmc_adapter_tool.show_apply_foot_locking:

            # Apply Foot Locking Options
            box = layout.box()
            split = box.column().row().split(factor=0.6)
            split.column().label(text='Target Foot')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_target_foot')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Target foot base markers')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_target_base_markers')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Z Threshold (m)')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_z_threshold')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Ground Level (m)')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_ground_level')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Frame Window Minimum Size')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_frame_window_min_size')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Initial Attenuation Count')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_initial_attenuation_count')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Final Attenuation Count')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_final_attenuation_count')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Lock XY at Ground Level')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_lock_xy_at_ground_level')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Knee Hip Compensation Coefficient')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_knee_hip_compensation_coefficient')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Compensate Upper Body Markers')
            split.split().column().prop(fmc_adapter_tool,
                                        'foot_locking_compensate_upper_body')

            box = layout.box()
            box.operator('fmc_adapter.apply_foot_locking',
                         text='4.5. Apply Foot Locking')

        # Create a button to toggle Rig Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_add_rig",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_add_rig
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Add Rig")

        if fmc_adapter_tool.show_add_rig:

            # Add Rig Options
            box = layout.box()

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add Rig Method')
            split.split().column().prop(fmc_adapter_tool,
                                        'add_rig_method')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Armature')
            split.split().column().prop(fmc_adapter_tool,
                                        'armature')
            
            split = box.column().row().split(factor=0.6)
            split.column().label(text='Pose')
            split.split().column().prop(fmc_adapter_tool,
                                        'pose')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Keep right/left symmetry')
            split.split().column().prop(fmc_adapter_tool,
                                        'keep_symmetry')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add finger constraints')
            split.split().column().prop(fmc_adapter_tool,
                                        'add_fingers_constraints')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add IK constraints')
            split.split().column().prop(fmc_adapter_tool,
                                        'add_ik_constraints')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='IK transition threshold')
            split.split().column().prop(fmc_adapter_tool,
                                        'ik_transition_threshold')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add rotation limits')
            split.split().column().prop(fmc_adapter_tool,
                                        'use_limit_rotation')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Clear constraints')
            split.split().column().prop(fmc_adapter_tool,
                                        'clear_constraints')

            box.operator('fmc_adapter.add_rig', text='5. Add Rig')

        # Create a button to toggle Add Body Mesh Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_add_body_mesh",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_add_body_mesh
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="Add Body Mesh")

        if fmc_adapter_tool.show_add_body_mesh:

            # Add Body Mesh Options
            box = layout.box()

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Body Mesh Mode')
            split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')

            box.operator('fmc_adapter.add_body_mesh', text='6. Add Body Mesh')

        # Create a button to toggle FBX Export Options
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool,
                 "show_export_fbx",
                 text="",
                 icon='TRIA_DOWN' if
                    fmc_adapter_tool.show_export_fbx
                    else 'TRIA_RIGHT',
                 emboss=False)
        row.label(text="FBX Export")

        if fmc_adapter_tool.show_export_fbx:

            # FBX Export
            box = layout.box()
            split = box.column().row().split(factor=0.6)
            split.column().label(text='FBX Export Type')
            split.split().column().prop(fmc_adapter_tool,
                                        'fbx_type')

            box.operator('fmc_adapter.export_fbx', text='7. Export FBX')

# Operator classes that executes the methods
class FMC_ADAPTER_OT_adjust_empties(Operator):
    bl_idname = 'fmc_adapter.adjust_empties'
    bl_label = 'Freemocap Adapter - Adjust Empties'
    bl_description = 'Change the position of the empties_parent empty so it is placed in an imaginary ground plane of the capture between the actors feet'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Adjust Empties...')

        adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                       z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                       ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                       z_translation_offset=fmc_adapter_tool.vertical_align_position_offset,
                       correct_fingers_empties=fmc_adapter_tool.correct_fingers_empties,
                       add_hand_middle_empty=fmc_adapter_tool.add_hand_middle_empty
                       )
        
        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))
        return {'FINISHED'}

class FMC_ADAPTER_OT_reduce_bone_length_dispersion(Operator):
    bl_idname = 'fmc_adapter.reduce_bone_length_dispersion'
    bl_label = 'Freemocap Adapter - Reduce Bone Length Dispersion'
    bl_description = 'Reduce the bone length dispersion by moving the tail empty and its children along the bone projection so the bone new length is within the interval'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Reduce Bone Length Dispersion...')

        reduce_bone_length_dispersion(interval_variable=fmc_adapter_tool.interval_variable,
                                      interval_factor=fmc_adapter_tool.interval_factor,
                                      body_height=fmc_adapter_tool.body_height)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_apply_butterworth_filters(Operator):
    bl_idname = 'fmc_adapter.apply_butterworth_filters'
    bl_label = 'Freemocap Adapter - Apply Butterworth Filters'
    bl_description = 'Apply Butterworth filters to the marker empties'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Apply Butterworth Filters...')

        # Create the global and local filter categories lists
        global_filter_categories=[]
        if fmc_adapter_tool.apply_global_filter_core:
            global_filter_categories.append('core')
        if fmc_adapter_tool.apply_global_filter_arms:
            global_filter_categories.append('arms')
        if fmc_adapter_tool.apply_global_filter_hands:
            global_filter_categories.append('hands')
        if fmc_adapter_tool.apply_global_filter_fingers:
            global_filter_categories.append('fingers')
        if fmc_adapter_tool.apply_global_filter_legs:
            global_filter_categories.append('legs')
        if fmc_adapter_tool.apply_global_filter_feet:
            global_filter_categories.append('feet')

        local_filter_categories=[]
        if scipy_available:
            if fmc_adapter_tool.apply_local_filter_core:
                local_filter_categories.append('core')
            if fmc_adapter_tool.apply_local_filter_arms:
                local_filter_categories.append('arms')
            if fmc_adapter_tool.apply_local_filter_hands:
                local_filter_categories.append('hands')
            if fmc_adapter_tool.apply_local_filter_fingers:
                local_filter_categories.append('fingers')
            if fmc_adapter_tool.apply_local_filter_legs:
                local_filter_categories.append('legs')
            if fmc_adapter_tool.apply_local_filter_feet:
                local_filter_categories.append('feet')

        if not global_filter_categories and not local_filter_categories:
            print('No category selected')
            return {'FINISHED'}

        # Create the cutoff frequencies dictionary
        global_cutoff_frequencies={}
        if fmc_adapter_tool.apply_global_filter_core:
            global_cutoff_frequencies['core'] = fmc_adapter_tool.global_filter_core_frequency
        if fmc_adapter_tool.apply_global_filter_arms:
            global_cutoff_frequencies['arms'] = fmc_adapter_tool.global_filter_arms_frequency
        if fmc_adapter_tool.apply_global_filter_hands:
            global_cutoff_frequencies['hands'] = fmc_adapter_tool.global_filter_hands_frequency
        if fmc_adapter_tool.apply_global_filter_fingers:
            global_cutoff_frequencies['fingers'] = fmc_adapter_tool.global_filter_fingers_frequency
        if fmc_adapter_tool.apply_global_filter_legs:
            global_cutoff_frequencies['legs'] = fmc_adapter_tool.global_filter_legs_frequency
        if fmc_adapter_tool.apply_global_filter_feet:
            global_cutoff_frequencies['feet'] = fmc_adapter_tool.global_filter_feet_frequency

        local_cutoff_frequencies={}
        if scipy_available:
            if fmc_adapter_tool.apply_local_filter_core:
                local_cutoff_frequencies['core'] = fmc_adapter_tool.local_filter_core_frequency
            if fmc_adapter_tool.apply_local_filter_arms:
                local_cutoff_frequencies['arms'] = fmc_adapter_tool.local_filter_arms_frequency
            if fmc_adapter_tool.apply_local_filter_hands:
                local_cutoff_frequencies['hands'] = fmc_adapter_tool.local_filter_hands_frequency
            if fmc_adapter_tool.apply_local_filter_fingers:
                local_cutoff_frequencies['fingers'] = fmc_adapter_tool.local_filter_fingers_frequency
            if fmc_adapter_tool.apply_local_filter_legs:
                local_cutoff_frequencies['legs'] = fmc_adapter_tool.local_filter_legs_frequency
            if fmc_adapter_tool.apply_local_filter_feet:
                local_cutoff_frequencies['feet'] = fmc_adapter_tool.local_filter_feet_frequency

        local_filter_origins={}
        if scipy_available:
            if fmc_adapter_tool.apply_local_filter_core:
                local_filter_origins['core'] = fmc_adapter_tool.local_filter_origin_core
            if fmc_adapter_tool.apply_local_filter_arms:
                local_filter_origins['arms'] = fmc_adapter_tool.local_filter_origin_arms
            if fmc_adapter_tool.apply_local_filter_hands:
                local_filter_origins['hands'] = fmc_adapter_tool.local_filter_origin_hands
            if fmc_adapter_tool.apply_local_filter_fingers:
                local_filter_origins['fingers'] = fmc_adapter_tool.local_filter_origin_fingers
            if fmc_adapter_tool.apply_local_filter_legs:
                local_filter_origins['legs'] = fmc_adapter_tool.local_filter_origin_legs
            if fmc_adapter_tool.apply_local_filter_feet:
                local_filter_origins['feet'] = fmc_adapter_tool.local_filter_origin_feet

        # Execute export fbx function
        apply_butterworth_filters(global_filter_categories=global_filter_categories,
                                  global_cutoff_frequencies=global_cutoff_frequencies,
                                  local_filter_categories=local_filter_categories,
                                  local_cutoff_frequencies=local_cutoff_frequencies,
                                  local_filter_origins=local_filter_origins,
                                  interval_variable=fmc_adapter_tool.interval_variable,
                                  interval_factor=fmc_adapter_tool.interval_factor,
                                  body_height=fmc_adapter_tool.body_height)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_add_finger_rotation_limits(Operator):
    bl_idname = 'fmc_adapter.add_finger_rotation_limits'
    bl_label = 'Freemocap Adapter - Add Finger Rotation Limits'
    bl_description = 'Translate the finger marker empties so the bones respect the rotation constraint'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Add Finger Rotation Limits...')

        # Execute export fbx function
        add_finger_rotation_limits()

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_apply_foot_locking(Operator):
    bl_idname = 'fmc_adapter.apply_foot_locking'
    bl_label = 'Freemocap Adapter - Apply Foot Locking'
    bl_description = 'Apply the foot locking constraint'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        if not scipy_available:
            self.report(
                {'ERROR'},
                'Scipy module not available. Please install scipy in '
                + 'your Blender python folder. Example command: \n'
                + 'C:\\Program Files\\Blender Foundation\\Blender 3.6'
                + '\\3.6\python\\bin .\\python.exe -m pip install scipy')
            return {'FINISHED'}

        # Get start time
        start = time.time()

        print('Executing Apply Foot Locking...')

        # Prepare the target foot list
        if fmc_adapter_tool.foot_locking_target_foot == 'both_feet':
            target_foot_list = ['left_foot', 'right_foot']
        else:
            target_foot_list = [fmc_adapter_tool.foot_locking_target_foot]

        # Prepare the target base markers
        if fmc_adapter_tool.foot_locking_target_base_markers == 'foot_index_and_heel':
            target_base_markers_list = ['foot_index', 'heel']
        else:
            target_base_markers_list = [fmc_adapter_tool.foot_locking_target_base_markers]

        # Execute export fbx function
        apply_foot_locking(
            target_foot=target_foot_list,
            target_base_markers=target_base_markers_list,
            z_threshold=fmc_adapter_tool.foot_locking_z_threshold,
            ground_level=fmc_adapter_tool.foot_locking_ground_level,
            frame_window_min_size=fmc_adapter_tool.foot_locking_frame_window_min_size,
            initial_attenuation_count=fmc_adapter_tool.foot_locking_initial_attenuation_count,
            final_attenuation_count=fmc_adapter_tool.foot_locking_final_attenuation_count,
            lock_xy_at_ground_level=fmc_adapter_tool.foot_locking_lock_xy_at_ground_level,
            knee_hip_compensation_coefficient=fmc_adapter_tool.foot_locking_knee_hip_compensation_coefficient,
            compensate_upper_body=fmc_adapter_tool.foot_locking_compensate_upper_body
        )

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_add_rig(Operator):
    bl_idname = 'fmc_adapter.add_rig'
    bl_label = 'Freemocap Adapter - Add Rig'
    bl_description = 'Add a Rig to the capture empties. The method sets the rig rest pose as a TPose'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

        print('Executing Add Rig...')

        add_rig(
            add_rig_method=fmc_adapter_tool.add_rig_method,
            armature_name=fmc_adapter_tool.armature,
            pose_name=fmc_adapter_tool.pose,
            keep_symmetry=fmc_adapter_tool.keep_symmetry,
            add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
            add_ik_constraints=fmc_adapter_tool.add_ik_constraints,
            ik_transition_threshold=fmc_adapter_tool.ik_transition_threshold,
            use_limit_rotation=fmc_adapter_tool.use_limit_rotation,
            clear_constraints=fmc_adapter_tool.clear_constraints)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): '
              + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_add_body_mesh(Operator):
    bl_idname = 'fmc_adapter.add_body_mesh'
    bl_label = 'Freemocap Adapter - Add Body Mesh'
    bl_description = 'Add a body mesh to the rig. The mesh can be a file or a custom mesh made with basic shapes. This method first executes Add Empties and Add Rig(if no rig available)'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        # Execute Add Rig if there is no rig in the scene
        scene_has_rig = False
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                scene_has_rig = True
                break

        if not scene_has_rig:
            print('Executing Add Rig to have a rig for the mesh...')
            add_rig(keep_symmetry=fmc_adapter_tool.keep_symmetry,
                    add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
                    add_ik_constraints=fmc_adapter_tool.add_ik_constraints,
                    ik_transition_threshold=fmc_adapter_tool.ik_transition_threshold,
                    use_limit_rotation=fmc_adapter_tool.use_limit_rotation,
                    clear_constraints=fmc_adapter_tool.clear_constraints)
        
        print('Executing Add Body Mesh...')
        add_mesh_to_rig(body_mesh_mode=fmc_adapter_tool.body_mesh_mode,
                        armature_name=fmc_adapter_tool.armature,
                        body_height=fmc_adapter_tool.body_height,
                        pose_name=fmc_adapter_tool.pose)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_export_fbx(Operator):
    bl_idname = 'fmc_adapter.export_fbx'
    bl_label = 'Freemocap Adapter - Export FBX'
    bl_description = 'Exports a FBX file containing the rig, the mesh and the baked animation'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Export FBX...')

        # Execute export fbx function
        export_fbx(self,
                   fbx_type=fmc_adapter_tool.fbx_type)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): '
              + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}
