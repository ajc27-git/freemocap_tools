import time
import math as m
import bpy
from bpy.types import Operator, Panel
from .data_definitions.interface.properties.adjust_empties_properties import (
    AdjustEmptiesProperties
)
from .data_definitions.interface.properties.reduce_bone_length_dispersion_properties import (
    ReduceBoneLengthDispersionProperties
)
from .data_definitions.interface.properties.apply_butterworth_filters_properties import (
    ApplyButterworthFiltersProperties
)
from .data_definitions.interface.properties.add_finger_rotation_limits_properties import (
    AddFingerRotationLimitsProperties
)
from .data_definitions.interface.properties.apply_foot_locking_properties import (
    ApplyFootLockingProperties
)
from .data_definitions.interface.properties.add_armature_properties import (
    AddArmatureProperties
)
from .data_definitions.interface.properties.add_body_mesh_properties import (
    AddBodyMeshProperties
)
from .data_definitions.interface.properties.export_fbx_properties import (
    ExportFBXProperties
)
from .data_definitions.interface.properties.retarget_animation_properties import (
    RetargetAnimationProperties
)
from .data_definitions.interface.panels.adjust_empties_panel import (
    draw_adjust_empties_panel,
)
from .data_definitions.interface.panels.reduce_bone_length_dispersion_panel import (
    draw_reduce_bone_length_dispersion_panel,
)
from .data_definitions.interface.panels.apply_butterworth_filters_panel import (
    draw_apply_butterworth_filters_panel,
)
from .data_definitions.interface.panels.add_finger_rotation_limits_panel import (
    draw_add_finger_rotation_limits_panel,
)
from .data_definitions.interface.panels.apply_foot_locking_panel import (
    draw_apply_foot_locking_panel
)
from .data_definitions.interface.panels.add_armature_panel import (
    draw_add_armature_panel
)
from .data_definitions.interface.panels.add_body_mesh_panel import (
    draw_add_body_mesh_panel
)
from .data_definitions.interface.panels.export_fbx_panel import (
    draw_export_fbx_panel
)
from .data_definitions.interface.panels.retarget_animation_panel import (
    draw_retarget_animation_panel
)
from .core_functions import (
    adjust_empties,
    reduce_bone_length_dispersion,
    add_rig,
    add_mesh_to_rig,
    add_finger_rotation_limits,
    apply_foot_locking,
    apply_butterworth_filters,
    export_fbx,
    retarget_animation,
)
scipy_available = True
try:
    from scipy.signal import butter, filtfilt
except ImportError:
    scipy_available = False
    print("scipy is not installed. Please install scipy to use this addon.")

# Class with the different properties of the methods
class FMC_ADAPTER_PROPERTIES(bpy.types.PropertyGroup):

    adjust_empties_properties: bpy.props.PointerProperty(
        type=AdjustEmptiesProperties
    ) # type: ignore
    reduce_bone_length_dispersion_properties: bpy.props.PointerProperty(
        type=ReduceBoneLengthDispersionProperties
    ) # type: ignore
    apply_butterworth_filters_properties: bpy.props.PointerProperty(
        type=ApplyButterworthFiltersProperties
    ) # type: ignore
    add_finger_rotation_limits_properties: bpy.props.PointerProperty(
        type=AddFingerRotationLimitsProperties
    ) # type: ignore
    apply_foot_locking_properties: bpy.props.PointerProperty(
        type=ApplyFootLockingProperties
    ) # type: ignore
    add_armature_properties: bpy.props.PointerProperty(
        type=AddArmatureProperties
    ) # type: ignore
    add_body_mesh_properties: bpy.props.PointerProperty(
        type=AddBodyMeshProperties
    ) # type: ignore
    export_fbx_properties: bpy.props.PointerProperty(
        type=ExportFBXProperties
    ) # type: ignore
    retarget_animation_properties: bpy.props.PointerProperty(
        type=RetargetAnimationProperties
    ) # type: ignore

# UI Panel Class
class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap Adapter Alt"
    bl_label = "Freemocap Adapter Alt"

    def draw(self, context):
        layout = self.layout

        draw_adjust_empties_panel(context, layout)
        draw_reduce_bone_length_dispersion_panel(context, layout)
        draw_apply_butterworth_filters_panel(context, layout, scipy_available)
        draw_add_finger_rotation_limits_panel(context, layout)
        draw_apply_foot_locking_panel(context, layout)
        draw_add_armature_panel(context, layout)
        draw_add_body_mesh_panel(context, layout)
        draw_export_fbx_panel(context, layout)
        draw_retarget_animation_panel(context, layout)

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

        adjust_empties(
            z_align_ref_empty=fmc_adapter_tool.adjust_empties_properties.vertical_align_reference,
            z_align_angle_offset=fmc_adapter_tool.adjust_empties_properties.vertical_align_angle_offset,
            ground_ref_empty=fmc_adapter_tool.adjust_empties_properties.ground_align_reference,
            z_translation_offset=fmc_adapter_tool.adjust_empties_properties.vertical_align_position_offset,
            correct_fingers_empties=fmc_adapter_tool.adjust_empties_properties.correct_fingers_empties,
            add_hand_middle_empty=fmc_adapter_tool.adjust_empties_properties.add_hand_middle_empty
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

        reduce_bone_length_dispersion(
            interval_variable=fmc_adapter_tool.reduce_bone_length_dispersion_properties.interval_variable,
            interval_factor=fmc_adapter_tool.reduce_bone_length_dispersion_properties.interval_factor,
            body_height=fmc_adapter_tool.reduce_bone_length_dispersion_properties.body_height
        )

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
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_core:
            global_filter_categories.append('core')
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_arms:
            global_filter_categories.append('arms')
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_hands:
            global_filter_categories.append('hands')
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_fingers:
            global_filter_categories.append('fingers')
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_legs:
            global_filter_categories.append('legs')
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_feet:
            global_filter_categories.append('feet')

        local_filter_categories=[]
        if scipy_available:
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_core:
                local_filter_categories.append('core')
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_arms:
                local_filter_categories.append('arms')
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_hands:
                local_filter_categories.append('hands')
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_fingers:
                local_filter_categories.append('fingers')
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_legs:
                local_filter_categories.append('legs')
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_feet:
                local_filter_categories.append('feet')

        if not global_filter_categories and not local_filter_categories:
            print('No category selected')
            return {'FINISHED'}

        # Create the cutoff frequencies dictionary
        global_cutoff_frequencies={}
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_core:
            global_cutoff_frequencies['core'] = fmc_adapter_tool.apply_butterworth_filters_properties.global_filter_core_frequency
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_arms:
            global_cutoff_frequencies['arms'] = fmc_adapter_tool.apply_butterworth_filters_properties.global_filter_arms_frequency
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_hands:
            global_cutoff_frequencies['hands'] = fmc_adapter_tool.apply_butterworth_filters_properties.global_filter_hands_frequency
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_fingers:
            global_cutoff_frequencies['fingers'] = fmc_adapter_tool.apply_butterworth_filters_properties.global_filter_fingers_frequency
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_legs:
            global_cutoff_frequencies['legs'] = fmc_adapter_tool.apply_butterworth_filters_properties.global_filter_legs_frequency
        if fmc_adapter_tool.apply_butterworth_filters_properties.apply_global_filter_feet:
            global_cutoff_frequencies['feet'] = fmc_adapter_tool.apply_butterworth_filters_properties.global_filter_feet_frequency

        local_cutoff_frequencies={}
        if scipy_available:
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_core:
                local_cutoff_frequencies['core'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_core_frequency
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_arms:
                local_cutoff_frequencies['arms'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_arms_frequency
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_hands:
                local_cutoff_frequencies['hands'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_hands_frequency
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_fingers:
                local_cutoff_frequencies['fingers'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_fingers_frequency
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_legs:
                local_cutoff_frequencies['legs'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_legs_frequency
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_feet:
                local_cutoff_frequencies['feet'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_feet_frequency

        local_filter_origins={}
        if scipy_available:
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_core:
                local_filter_origins['core'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_origin_core
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_arms:
                local_filter_origins['arms'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_origin_arms
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_hands:
                local_filter_origins['hands'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_origin_hands
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_fingers:
                local_filter_origins['fingers'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_origin_fingers
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_legs:
                local_filter_origins['legs'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_origin_legs
            if fmc_adapter_tool.apply_butterworth_filters_properties.apply_local_filter_feet:
                local_filter_origins['feet'] = fmc_adapter_tool.apply_butterworth_filters_properties.local_filter_origin_feet

        # Execute export fbx function
        apply_butterworth_filters(
            global_filter_categories=global_filter_categories,
            global_cutoff_frequencies=global_cutoff_frequencies,
            local_filter_categories=local_filter_categories,
            local_cutoff_frequencies=local_cutoff_frequencies,
            local_filter_origins=local_filter_origins,
            interval_variable=fmc_adapter_tool.reduce_bone_length_dispersion_properties.interval_variable,
            interval_factor=fmc_adapter_tool.reduce_bone_length_dispersion_properties.interval_factor,
            body_height=fmc_adapter_tool.reduce_bone_length_dispersion_properties.body_height
        )

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
        if fmc_adapter_tool.apply_foot_locking_properties.target_foot == 'both_feet':
            target_foot_list = ['left_foot', 'right_foot']
        else:
            target_foot_list = [fmc_adapter_tool.foot_locking_target_foot]

        # Prepare the target base markers
        if fmc_adapter_tool.apply_foot_locking_properties.target_base_markers == 'foot_index_and_heel':
            target_base_markers_list = ['foot_index', 'heel']
        else:
            target_base_markers_list = [fmc_adapter_tool.apply_foot_locking_properties.target_base_markers]

        # Execute export fbx function
        apply_foot_locking(
            target_foot=target_foot_list,
            target_base_markers=target_base_markers_list,
            z_threshold=fmc_adapter_tool.apply_foot_locking_properties.z_threshold,
            ground_level=fmc_adapter_tool.apply_foot_locking_properties.ground_level,
            frame_window_min_size=fmc_adapter_tool.apply_foot_locking_properties.frame_window_min_size,
            initial_attenuation_count=fmc_adapter_tool.apply_foot_locking_properties.initial_attenuation_count,
            final_attenuation_count=fmc_adapter_tool.apply_foot_locking_properties.final_attenuation_count,
            lock_xy_at_ground_level=fmc_adapter_tool.apply_foot_locking_properties.lock_xy_at_ground_level,
            knee_hip_compensation_coefficient=fmc_adapter_tool.apply_foot_locking_properties.knee_hip_compensation_coefficient,
            compensate_upper_body=fmc_adapter_tool.apply_foot_locking_properties.compensate_upper_body
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
            add_rig_method=fmc_adapter_tool.add_armature_properties.add_rig_method,
            armature_name=fmc_adapter_tool.add_armature_properties.armature,
            pose_name=fmc_adapter_tool.add_armature_properties.pose,
            keep_symmetry=fmc_adapter_tool.add_armature_properties.keep_symmetry,
            add_fingers_constraints=fmc_adapter_tool.add_armature_properties.add_fingers_constraints,
            add_ik_constraints=fmc_adapter_tool.add_armature_properties.add_ik_constraints,
            ik_transition_threshold=fmc_adapter_tool.add_armature_properties.ik_transition_threshold,
            use_limit_rotation=fmc_adapter_tool.add_armature_properties.use_limit_rotation,
            clear_constraints=fmc_adapter_tool.add_armature_properties.clear_constraints)

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
            add_rig(
                keep_symmetry=fmc_adapter_tool.add_armature_properties.keep_symmetry,
                add_fingers_constraints=fmc_adapter_tool.add_armature_properties.add_fingers_constraints,
                add_ik_constraints=fmc_adapter_tool.add_armature_properties.add_ik_constraints,
                ik_transition_threshold=fmc_adapter_tool.add_armature_properties.ik_transition_threshold,
                use_limit_rotation=fmc_adapter_tool.add_armature_properties.use_limit_rotation,
                clear_constraints=fmc_adapter_tool.add_armature_properties.clear_constraints
            )
        
        print('Executing Add Body Mesh...')
        add_mesh_to_rig(
            body_mesh_mode=fmc_adapter_tool.add_body_mesh_properties.body_mesh_mode,
            armature_name=fmc_adapter_tool.add_armature_properties.armature,
            body_height=fmc_adapter_tool.reduce_bone_length_dispersion_properties.body_height,
            pose_name=fmc_adapter_tool.add_armature_properties.pose
        )

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
                   fbx_type=fmc_adapter_tool.export_fbx_properties.fbx_type)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): '
              + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}
    
class FMC_ADAPTER_OT_retarget_animation(Operator):
    bl_idname = 'fmc_adapter.retarget_animation'
    bl_label = 'Freemocap Adapter - Retarget Animation'
    bl_description = 'Retargets the source armature constraints to the target armature'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Retarget Rig...')

        retarget_animation(
            fmc_adapter_tool.retarget_animation_properties.source_armature,
            fmc_adapter_tool.retarget_animation_properties.target_armature,
            fmc_adapter_tool.retarget_animation_properties.bake_animation,
            fmc_adapter_tool.retarget_animation_properties.clear_constraints
        )

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): '
              + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}
