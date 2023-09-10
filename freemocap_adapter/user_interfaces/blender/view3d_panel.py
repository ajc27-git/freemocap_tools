import logging

from bpy.types import Panel

from freemocap_adapter import DEBUG_UI

logger = logging.getLogger(__name__)


class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap Adapter"
    bl_label = "Freemocap Adapter"

    def draw(self, context):
        if DEBUG_UI:
            logger.trace('Drawing panel...')
        layout = self.layout
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Clear scene button
        clear_scene_box = layout.box()
        clear_scene_box.operator('fmc_adapter.clear_scene', text='Clear Scene')

        # Load empties Options
        load_freemocap_box = layout.box()
        row = load_freemocap_box.row()
        row.label(text="FreeMoCap Recording:")
        row.prop(fmc_adapter_tool, "recording_path", text="")
        load_freemocap_box.operator('fmc_adapter.freemocap_data_operations', text='0. Load FreeMoCap Data')

        row = load_freemocap_box.row()
        row.label(icon='FILE_MOVIE', )
        row.operator('fmc_adapter.load_videos',
                     text="Load videos as planes",
                     )

        # row = load_freemocap_box.row()
        # row.label(text="Download sample data?")
        # row.operator('fmc_adapter.download_sample_data', text='Download')

        load_freemocap_box.prop(fmc_adapter_tool,
                                "data_parent_empty",
                                text="Data Parent Empty")

        # adjust_empties_box.operator('fmc_adapter.adjust_empties', text='1. Adjust Empties')

        # Adjust Empties Options
        reorient_empties_box = layout.box()
        reorient_empties_box.operator('fmc_adapter.reorient_empties', text='1. Re-orient Empties')
        row = reorient_empties_box.row()
        row.prop(fmc_adapter_tool,
                 'show_reorient_empties_options',
                 icon='TRIA_DOWN' if fmc_adapter_tool.show_reorient_empties_options else 'TRIA_RIGHT',
                 emboss=False)

        if fmc_adapter_tool.show_reorient_empties_options:
            split = reorient_empties_box.column().row().split(factor=0.6)
            split.column().label(text='Align Reference')
            split.split().column().prop(fmc_adapter_tool, 'vertical_align_reference')

            split = reorient_empties_box.column().row().split(factor=0.6)
            split.column().label(text='Vertical Angle Offset')
            split.split().column().prop(fmc_adapter_tool, 'vertical_align_angle_offset')

            split = reorient_empties_box.column().row().split(factor=0.6)
            split.column().label(text='Ground Reference')
            split.split().column().prop(fmc_adapter_tool, 'ground_align_reference')

            split = reorient_empties_box.column().row().split(factor=0.6)
            split.column().label(text='Vertical Position Offset')
            split.split().column().prop(fmc_adapter_tool, 'vertical_align_position_offset')

            split = reorient_empties_box.column().row().split(factor=0.6)
            split.column().label(text='Correct Fingers Empties')
            split.split().column().prop(fmc_adapter_tool, 'correct_fingers_empties')

            split = reorient_empties_box.column().row().split(factor=0.6)
            split.column().label(text='Add hand middle empty')
            split.split().column().prop(fmc_adapter_tool, 'add_hand_middle_empty')

        # Reduce Bone Length Dispersion Options
        bone_length_box = layout.box()
        bone_length_box.operator('fmc_adapter.reduce_bone_length_dispersion', text='2. Reduce Bone Length Dispersion')
        row = bone_length_box.row()
        row.prop(fmc_adapter_tool,
                 'show_bone_length_options',
                 icon='TRIA_DOWN' if fmc_adapter_tool.show_bone_length_options else 'TRIA_RIGHT',
                 emboss=False)

        if fmc_adapter_tool.show_bone_length_options:
            split = bone_length_box.column().row().split(factor=0.6)
            split.column().label(text='Dispersion Interval Variable')
            split.split().column().prop(fmc_adapter_tool, 'interval_variable')

            split = bone_length_box.column().row().split(factor=0.6)
            split.column().label(text='Dispersion Interval Factor')
            split.split().column().prop(fmc_adapter_tool, 'interval_factor')

        # Reduce Shakiness Options
        # box = layout.box()
        # #box.label(text='Reduce Shakiness Options')

        # split = box.column().row().split(factor=0.6)
        # split.column().label(text='Recording FPS')
        # split.split().column().prop(fmc_adapter_tool, 'recording_fps')

        # box.operator('fmc_adapter.reduce_shakiness', text='Reduce Shakiness')

        # Add Rig Options
        add_rig_box = layout.box()
        add_rig_box.operator('fmc_adapter.add_rig', text='3. Add Rig')
        row = add_rig_box.row()
        row.prop(fmc_adapter_tool,
                 'show_add_rig_options',
                 icon='TRIA_DOWN' if fmc_adapter_tool.show_add_rig_options else 'TRIA_RIGHT',
                 emboss=False)

        if fmc_adapter_tool.show_add_rig_options:
            split = add_rig_box.column().row().split(factor=0.6)
            split.column().label(text='Bone Length Method')
            split.split().column().prop(fmc_adapter_tool, 'bone_length_method')

            split = add_rig_box.column().row().split(factor=0.6)
            split.column().label(text='Keep right/left symmetry')
            split.split().column().prop(fmc_adapter_tool, 'keep_symmetry')

            split = add_rig_box.column().row().split(factor=0.6)
            split.column().label(text='Add finger constraints')
            split.split().column().prop(fmc_adapter_tool, 'add_fingers_constraints')

            split = add_rig_box.column().row().split(factor=0.6)
            split.column().label(text='Add rotation limits')
            split.split().column().prop(fmc_adapter_tool, 'use_limit_rotation')

        # Add Body Mesh Options
        body_mesh_box = layout.box()
        body_mesh_box.operator('fmc_adapter.add_body_mesh', text='4. Add Body Mesh')
        # box.label(text='Add Body Mesh Options')

        split = body_mesh_box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')

        # box.operator('fmc_adapter.actions_op', text='Add Body Mesh').action = 'ADD_BODY_MESH'

        # FBX Export
        fbx_export_box = layout.box()
        fbx_export_box.operator('fmc_adapter.export_fbx', text='5. Export FBX')
