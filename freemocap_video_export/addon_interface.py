import bpy
from bpy.types import Operator, Panel
from bpy.props import EnumProperty
from .functions import fmc_export_video
from . import config_variables

# Class with the different properties of the methods
class FMC_VIDEO_EXPORT_PROPERTIES(bpy.types.PropertyGroup):

    export_profile: bpy.props.EnumProperty(
        name        = '',
        description = 'Profile of the export video',
        items       = [('debug', 'Debug', ''),
                       ('showcase', 'Showcase', ''),
                       ('scientific', 'Scientific', ''),
        ],
    )

    scientific_ground_contact_threshold: bpy.props.FloatProperty(
        name        = '',
        default     = 0.05,
        description = 'Ground contact threshold (m)'
    )

# UI Panel Class
class VIEW3D_PT_freemocap_video_export(Panel):
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "UI"
    bl_category     = "Freemocap Video Export"
    bl_label        = "Freemocap Video Export"
    
    def draw(self, context):
        layout                  = self.layout
        scene                   = context.scene
        fmc_video_export_tool   = scene.fmc_video_export_tool
        
        box = layout.box()
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Video Profile')
        split.split().column().prop(fmc_video_export_tool, 'export_profile')

        box.label(text='Scientific Profile Options')
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Ground Contact Threshold (m)')
        split.split().column().prop(fmc_video_export_tool, 'scientific_ground_contact_threshold')

        box.operator('fmc_export_video.export_video', text='Export Video')

# Operator classes that executes the methods
class FMC_ADAPTER_OT_export_video(Operator):
    bl_idname       = 'fmc_export_video.export_video'
    bl_label        = 'Freemocap Export Video'
    bl_description  = "Export the Freemocap Blender output as a video file"
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene                   = context.scene
        fmc_video_export_tool   = scene.fmc_video_export_tool

        print("Exporting video.......")

        config_variables.visual_components['vc_plot_com_bos']['ground_contact_threshold'] = fmc_video_export_tool.scientific_ground_contact_threshold

        fmc_export_video(scene=scene, export_profile=fmc_video_export_tool.export_profile)

        print("Video export completed.")

        return {'FINISHED'}
