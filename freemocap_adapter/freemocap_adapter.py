import math as m
import time
import logging
import bpy
from bpy.types import Operator, Panel

from freemocap_adapter.core_functions.functions import adjust_empties, reduce_bone_length_dispersion, \
    reduce_shakiness, add_rig, add_mesh_to_rig, export_fbx

logger = logging.getLogger(__name__)

bl_info = {
    'name': 'Freemocap Adapter',
    'author': 'ajc27',
    'version': (1, 1, 7),
    'blender': (3, 0, 0),
    'location': '3D Viewport > Sidebar > Freemocap Adapter',
    'description': 'Add-on to adapt the Freemocap Blender output',
    'category': 'Development',
}

#######################################################################
### Add-on to adapt the Freemocap Blender output. It can adjust the
### empties position, add a rig and a body mesh. The resulting rig 
### and animation can be imported in platforms like Unreal Engine.
### The rig has a TPose as rest pose for easier retargeting.
### For best results, when the script is ran the empties should be
### forming a standing still pose with arms open similar to A or T Pose
### The body_mesh.ply file should be in the same folder as the
### Blender file before manually opening it.
#######################################################################

# Global Variables
# Variable to save if the function Adjust Empties has been already executed
ADJUST_EMPTIES_EXECUTED = False

# Location and rotation vectors of the freemocap_origin_axes in the Adjust Empties method just before resetting its location and rotation to (0, 0, 0)
ORIGIN_LOCATION_PRE_RESET = (0, 0, 0)
ORIGIN_ROTATION_PRE_RESET = (0, 0, 0)

# Dictionary to save the global vector position of all the empties for every animation frame
EMPTY_POSITIONS = {}

# Dictionary to save the speed of all the empties for every animation frame
EMPTY_VELOCITIES = {}


# Class with the different properties of the methods
class FMC_ADAPTER_PROPERTIES(bpy.types.PropertyGroup):
    # Adjust Empties Options
    vertical_align_reference: bpy.props.EnumProperty(
        name='',
        description='Empty that serves as reference to align the z axis',
        items=[('left_knee', 'left_knee', ''),
               ('trunk_center', 'trunk_center', ''),
               ('right_knee', 'right_knee', '')]
    )
    vertical_align_angle_offset: bpy.props.FloatProperty(
        name='',
        default=0,
        description='Angle offset to adjust the vertical alignement of the z axis (in degrees)'
    )
    ground_align_reference: bpy.props.EnumProperty(
        name='',
        description='Empty that serves as ground reference to the axes origin',
        items=[('left_foot_index', 'left_foot_index', ''),
               ('right_foot_index', 'right_foot_index', ''),
               ('left_heel', 'left_heel', ''),
               ('right_heel', 'right_heel', '')]
    )
    vertical_align_position_offset: bpy.props.FloatProperty(
        name='',
        default=0,
        precision=3,
        description='Additional z offset to the axes origin relative to the imaginary ground level'
    )
    correct_fingers_empties: bpy.props.BoolProperty(
        name='',
        default=True,
        description='Correct the fingers empties. Match hand_wrist (axis empty) position to wrist (sphere empty)'
    )
    add_hand_middle_empty: bpy.props.BoolProperty(
        name='',
        default=True,
        description='Add an empty in the middle of the hand between index and pinky empties. This empty is used for a better orientation of the hand (experimental)'
    )

    # Reduce Bone Length Dispersion Options
    interval_variable: bpy.props.EnumProperty(
        name='',
        description='Variable used to define the new length dispersion interval',
        items=[('median', 'Median',
                'Defines the new dispersion interval as [median*(1-interval_factor),median*(1+interval_factor)]'),
               ('stdev', 'Standard Deviation',
                'Defines the new dispersion interval as [median-interval_factor*stdev,median+interval_factor*stdev]')]
    )
    interval_factor: bpy.props.FloatProperty(
        name='',
        default=0,
        min=0,
        precision=3,
        description='Factor to multiply the variable and form the limits of the dispersion interval like [median-factor*variable,median+factor*variable]. ' +
                    'If variable is median, the factor will be limited to values inside [0, 1].' +
                    'If variable is stdev, the factor will be limited to values inside [0, median/stdev]'
    )

    # Reduce Shakiness Options
    recording_fps: bpy.props.FloatProperty(
        name='',
        default=30,
        min=0,
        precision=3,
        description='Frames per second (fps) of the capture recording'
    )

    # Add Rig Options
    bone_length_method: bpy.props.EnumProperty(
        name='',
        description='Method use to calculate length of major bones',
        items=[('median_length', 'Median Length', ''),
               # ('current_frame', 'Current Frame', '')]
               ]
    )
    keep_symmetry: bpy.props.BoolProperty(
        name='',
        default=False,
        description='Keep right/left side symmetry (use average right/left side bone length)'
    )
    add_fingers_constraints: bpy.props.BoolProperty(
        name='',
        default=True,
        description='Add bone constraints for fingers'
    )
    use_limit_rotation: bpy.props.BoolProperty(
        name='',
        default=False,
        description='Add rotation limits (human skeleton) to the bones constraints (experimental)'
    )

    # Add Body Mesh Options
    body_mesh_mode: bpy.props.EnumProperty(
        name='',
        description='Mode (source) for adding the mesh to the rig',
        items=[('custom', 'custom', ''),
               ('file', 'file', '')]
    )


# UI Panel Class
class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap Adapter"
    bl_label = "Freemocap Adapter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Adjust Empties Options
        box = layout.box()
        # box.label(text='Adjust Empties Options')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Align Reference')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_reference')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Angle Offset')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_angle_offset')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Ground Reference')
        split.split().column().prop(fmc_adapter_tool, 'ground_align_reference')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Position Offset')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_position_offset')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Correct Fingers Empties')
        split.split().column().prop(fmc_adapter_tool, 'correct_fingers_empties')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add hand middle empty')
        split.split().column().prop(fmc_adapter_tool, 'add_hand_middle_empty')

        box.operator('fmc_adapter.adjust_empties', text='1. Adjust Empties')

        # Reduce Bone Length Dispersion Options
        box = layout.box()
        # box.label(text='Reduce Bone Length Dispersion Options')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Variable')
        split.split().column().prop(fmc_adapter_tool, 'interval_variable')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Factor')
        split.split().column().prop(fmc_adapter_tool, 'interval_factor')

        box.operator('fmc_adapter.reduce_bone_length_dispersion', text='2. Reduce Bone Length Dispersion')

        # Reduce Shakiness Options
        # box = layout.box()
        # #box.label(text='Reduce Shakiness Options')

        # split = box.column().row().split(factor=0.6)
        # split.column().label(text='Recording FPS')
        # split.split().column().prop(fmc_adapter_tool, 'recording_fps')

        # box.operator('fmc_adapter.reduce_shakiness', text='Reduce Shakiness')

        # Add Rig Options
        box = layout.box()
        # box.label(text='Add Rig Options')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Bone Length Method')
        split.split().column().prop(fmc_adapter_tool, 'bone_length_method')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Keep right/left symmetry')
        split.split().column().prop(fmc_adapter_tool, 'keep_symmetry')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add finger constraints')
        split.split().column().prop(fmc_adapter_tool, 'add_fingers_constraints')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add rotation limits')
        split.split().column().prop(fmc_adapter_tool, 'use_limit_rotation')

        box.operator('fmc_adapter.add_rig', text='3. Add Rig')

        # Add Body Mesh Options
        box = layout.box()
        # box.label(text='Add Body Mesh Options')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')

        # box.operator('fmc_adapter.actions_op', text='Add Body Mesh').action = 'ADD_BODY_MESH'
        box.operator('fmc_adapter.add_body_mesh', text='4. Add Body Mesh')

        # FBX Export
        box = layout.box()
        box.operator('fmc_adapter.export_fbx', text='5. Export FBX')


# Operator classes that executes the methods
class FMC_ADAPTER_OT_adjust_empties(Operator):
    bl_idname = 'fmc_adapter.adjust_empties'
    bl_label = 'Freemocap Adapter - Adjust Empties'
    bl_description = "Change the position of the freemocap_origin_axes empty to so it is placed in an imaginary ground plane of the capture between the actor's feet"
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
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))
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
                                      interval_factor=fmc_adapter_tool.interval_factor)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}


class FMC_ADAPTER_OT_reduce_shakiness(Operator):
    bl_idname = 'fmc_adapter.reduce_shakiness'
    bl_label = 'Freemocap Adapter - Reduce Shakiness'
    bl_description = 'Reduce the shakiness of the capture empties by restricting their acceleration to a defined threshold'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Reduce Shakiness...')

        reduce_shakiness(recording_fps=fmc_adapter_tool.recording_fps)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

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

        if not ADJUST_EMPTIES_EXECUTED:
            print('Executing First Adjust Empties...')

            # Execute Adjust Empties first
            adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                           z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                           ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                           z_translation_offset=fmc_adapter_tool.vertical_align_position_offset,
                           add_hand_middle_empty=fmc_adapter_tool.add_hand_middle_empty,
                           )

        print('Executing Add Rig...')

        add_rig(bone_length_method=fmc_adapter_tool.bone_length_method,
                keep_symmetry=fmc_adapter_tool.keep_symmetry,
                add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
                use_limit_rotation=fmc_adapter_tool.use_limit_rotation)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

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

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

        if not ADJUST_EMPTIES_EXECUTED:
            print('Executing First Adjust Empties...')

            # Execute Adjust Empties first
            adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                           z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                           ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                           z_translation_offset=fmc_adapter_tool.vertical_align_position_offset
                           )

        # Execute Add Rig if there is no rig in the scene
        try:
            root = bpy.data.objects['root']
        except:
            print('Executing Add Rig to have a rig for the mesh...')
            add_rig(use_limit_rotation=fmc_adapter_tool.use_limit_rotation)

        print('Executing Add Body Mesh...')
        add_mesh_to_rig(body_mesh_mode=fmc_adapter_tool.body_mesh_mode)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}


class FMC_ADAPTER_OT_export_fbx(Operator):
    bl_idname = 'fmc_adapter.export_fbx'
    bl_label = 'Freemocap Adapter - Export FBX'
    bl_description = 'Exports a FBX file containing the rig, the mesh and the baked animation'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        # Get start time
        start = time.time()

        print('Executing Export FBX...')

        # Execute export fbx function
        export_fbx(self)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start) * 1000) / 1000))

        return {'FINISHED'}


classes = [FMC_ADAPTER_PROPERTIES,
           VIEW3D_PT_freemocap_adapter,
           FMC_ADAPTER_OT_adjust_empties,
           FMC_ADAPTER_OT_reduce_bone_length_dispersion,
           FMC_ADAPTER_OT_reduce_shakiness,
           FMC_ADAPTER_OT_add_rig,
           FMC_ADAPTER_OT_add_body_mesh,
           FMC_ADAPTER_OT_export_fbx
           ]


def register():
    logger.info(f"Registering {__file__} as add-on")
    for cls in classes:
        logger.info(f"Registering class {cls.__name__}")
        bpy.utils.register_class(cls)

    logger.info(f"Registering property group FMC_ADAPTER_PROPERTIES")
    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type=FMC_ADAPTER_PROPERTIES)

    logger.info(f"Finished registering {__file__} as add-on!")


def unregister():
    logger.info(f"Unregistering {__file__} as add-on")
    for cls in classes:
        logger.info(f"Unregistering class {cls.__name__}")
        bpy.utils.unregister_class(cls)

    logger.info(f"Unregistering property group FMC_ADAPTER_PROPERTIES")
    del bpy.types.Scene.fmc_adapter_tool



# Register the Add-on
if __name__ == "__main__":
    logger.info(f"Running {__file__} as main file ")
    register()
