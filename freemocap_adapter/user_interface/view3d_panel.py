from bpy.types import Panel


class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap Adapter"
    bl_label = "Freemocap Adapter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # Load empties Options
        load_freemocap_box = layout.box()
        load_freemocap_box.operator('fmc_adapter.load_freemocap_data', text='0. Load FreeMoCap Data')

        # adjust_empties_box.operator('fmc_adapter.adjust_empties', text='1. Adjust Empties')

        # Adjust Empties Options
        adjust_empties_box = layout.box()

        split = adjust_empties_box.column().row().split(factor=0.6)
        split.column().label(text='Align Reference')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_reference')

        split = adjust_empties_box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Angle Offset')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_angle_offset')

        split = adjust_empties_box.column().row().split(factor=0.6)
        split.column().label(text='Ground Reference')
        split.split().column().prop(fmc_adapter_tool, 'ground_align_reference')

        split = adjust_empties_box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Position Offset')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_position_offset')

        split = adjust_empties_box.column().row().split(factor=0.6)
        split.column().label(text='Correct Fingers Empties')
        split.split().column().prop(fmc_adapter_tool, 'correct_fingers_empties')

        split = adjust_empties_box.column().row().split(factor=0.6)
        split.column().label(text='Add hand middle empty')
        split.split().column().prop(fmc_adapter_tool, 'add_hand_middle_empty')

        adjust_empties_box.operator('fmc_adapter.adjust_empties', text='1. Adjust Empties')

        # Reduce Bone Length Dispersion Options
        bone_length_box = layout.box()
        # box.label(text='Reduce Bone Length Dispersion Options')

        split = bone_length_box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Variable')
        split.split().column().prop(fmc_adapter_tool, 'interval_variable')

        split = bone_length_box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Factor')
        split.split().column().prop(fmc_adapter_tool, 'interval_factor')

        bone_length_box.operator('fmc_adapter.reduce_bone_length_dispersion', text='2. Reduce Bone Length Dispersion')

        # Reduce Shakiness Options
        # box = layout.box()
        # #box.label(text='Reduce Shakiness Options')

        # split = box.column().row().split(factor=0.6)
        # split.column().label(text='Recording FPS')
        # split.split().column().prop(fmc_adapter_tool, 'recording_fps')

        # box.operator('fmc_adapter.reduce_shakiness', text='Reduce Shakiness')

        # Add Rig Options
        add_rig_box = layout.box()
        # box.label(text='Add Rig Options')

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

        add_rig_box.operator('fmc_adapter.add_rig', text='3. Add Rig')

        # Add Body Mesh Options
        body_mesh_box = layout.box()
        # box.label(text='Add Body Mesh Options')

        split = body_mesh_box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')

        # box.operator('fmc_adapter.actions_op', text='Add Body Mesh').action = 'ADD_BODY_MESH'
        body_mesh_box.operator('fmc_adapter.add_body_mesh', text='4. Add Body Mesh')

        # FBX Export
        fbx_export_box = layout.box()
        fbx_export_box.operator('fmc_adapter.export_fbx', text='5. Export FBX')
