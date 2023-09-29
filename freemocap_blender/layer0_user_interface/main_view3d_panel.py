import logging

from bpy.types import Panel

from freemocap_blender import DEBUG_UI

logger = logging.getLogger(__name__)


class VIEW3D_PT_freemocap_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Freemocap"
    bl_label = "Freemocap"

    def draw(self, context):
        if DEBUG_UI:
            logger.trace('Drawing panel...')
        layout = self.layout
        scene = context.scene
        data_properties = scene.freemocap_data_properties
        ui_properties = scene.freemocap_ui_properties

        self._clear_scene_button(layout=layout)

        self._run_all_panel(data_properties=data_properties,
                            ui_properties=ui_properties,
                            layout=layout)

        self._save_data_to_disk_panel(layout=layout)
        #
        # self._load_data_panel(data_properties, layout=layout)
        #
        # self._reduce_bone_dispersion_panel(data_properties, layout=layout)
        #
        # self._add_rig_panel(data_properties, layout=layout)
        #
        # self._add_body_mesh_panel(data_properties, layout=layout)
        #
        # self._fbx_export_panel(layout=layout)

        # ui_column_3 = self.layout.column(align=True)
        # ui_column_3.prop(context.scene, 'frame_current', text='Current Frame#' )
        # ui_column_3.operator('screen.animation_play', icon='PLAY')

    def _clear_scene_button(self, layout):
        # Clear scene button
        clear_scene_box = layout.box()
        clear_scene_box.operator('freemocap_blender._clear_scene', text='Clear Scene')

    def _run_all_panel(self, layout,
                       data_properties,
                       ui_properties
                       ):
        box = layout.box()

        box.row().prop(data_properties,
                       "recording_path",
                       text="FreeMoCap Recording:")

        box.row().prop(data_properties,
                       "data_parent_empty",
                       text="Data Parent Empty")

        run_all_box = box.box()
        run_all_box.operator('freemocap_blender._run_all', text='RUN ALL 💀 ✨')
        self._show_operations_dropdown(ui_properties=ui_properties,
                                       box=run_all_box)

    def _show_operations_dropdown(self,
                                  ui_properties,
                                  box):
        row = box.row()
        row.prop(ui_properties,
                 'show_operations',
                 icon='TRIA_DOWN' if ui_properties.show_operations else 'TRIA_RIGHT',
                 emboss=False)
        if ui_properties.show_operations:
            self._load_freemocap_data_row(box)

            # self._calculate_virtual_trajectories()
            # self._put_data_in_inertial_reference_frame()
            # self._enforce_rigid_bones()
            # self._fix_hand_data()
            # self._save_data_to_disk()
            # self._create_empties()
            # self._add_rig()
            # self._attach_mesh_to_rig()
            # self._add_videos()
            # self._setup_scene()

    def _load_freemocap_data_row(self, box):
        split = box.column().row().split(factor=0.6)
        split.column().label(text='📂')
        split.split().column().operator('freemocap_blender._load_freemocap_data', text='1. Load FreeMoCap Data')

    def _save_data_to_disk_panel(self, layout):
        box = layout.box()
        box.operator('freemocap_blender._save_data_to_disk', text='Save Data to Disk')

    def _fbx_export_panel(self, layout):
        # FBX Export
        fbx_export_box = layout.box()
        fbx_export_box.operator('freemocap_blender._export_fbx', text='5. Export FBX')

    def _add_body_mesh_panel(self, freemocap_blender_tool, layout):
        # Add Body Mesh Options
        body_mesh_box = layout.box()
        body_mesh_box.operator('freemocap_blender._add_body_mesh', text='4. Add Body Mesh')
        # box.label(text='Add Body Mesh Options')
        split = body_mesh_box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(freemocap_blender_tool, 'body_mesh_mode')

    def _add_rig_panel(self, freemocap_blender_tool, layout):
        # Add Rig Options
        add_rig_box = layout.box()
        add_rig_box.operator('freemocap_blender._add_rig', text='3. Add Rig')
        row = add_rig_box.row()
        row.prop(freemocap_blender_tool,
                 'show_add_rig_options',
                 icon='TRIA_DOWN' if freemocap_blender_tool.show_add_rig_options else 'TRIA_RIGHT',
                 emboss=False)
        if freemocap_blender_tool.show_add_rig_options:
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

    def _reduce_bone_dispersion_panel(self, fmc_adapter_tool, layout):
        # Reduce Bone Length Dispersion Options
        bone_length_box = layout.box()
        bone_length_box.operator('fmc_adapter._reduce_bone_length_dispersion', text='2. Reduce Bone Length Dispersion')
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

    def _load_data_panel(self, fmc_adapter_tool, layout):
        # Load empties Options
        load_freemocap_box = layout.box()

        load_freemocap_box.operator('fmc_adapter._freemocap_data_operations', text='0. Load FreeMoCap Data')
        row = load_freemocap_box.row()
        row.label(icon='FILE_MOVIE', )
        row.operator('fmc_adapter._load_videos',
                     text="Load videos as planes",
                     )
        # row = load_freemocap_box.row()
        # row.label(text="Download sample data?")
        # row.operator('fmc_adapter._download_sample_data', text='Download')

        # adjust_empties_box.operator('fmc_adapter._adjust_empties', text='1. Adjust Empties')

    def reorient_empties_panel(self, fmc_adapter_tool, layout):
        # Adjust Empties Options
        reorient_empties_box = layout.box()
        reorient_empties_box.operator('fmc_adapter._reorient_empties', text='1. Re-orient Empties')
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
