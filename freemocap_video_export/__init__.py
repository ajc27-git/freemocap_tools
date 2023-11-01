bl_info = {
    'name'          : 'Freemocap Video Export',
    'author'        : 'ajc27',
    'version'       : (1, 0, 0),
    'blender'       : (3, 0, 0),
    'location'      : '3D Viewport > Sidebar > Freemocap Video Export',
    'description'   : 'Add-on to export the Freemocap Blender output as video',
    'category'      : 'Development',
}

import bpy

def register():
    # Import addon classes
    from freemocap_video_export.addon_interface import FMC_VIDEO_EXPORT_PROPERTIES, VIEW3D_PT_freemocap_video_export, FMC_ADAPTER_OT_export_video

    # Register addon classes
    bpy.utils.register_class(FMC_VIDEO_EXPORT_PROPERTIES)
    bpy.utils.register_class(VIEW3D_PT_freemocap_video_export)
    bpy.utils.register_class(FMC_ADAPTER_OT_export_video)

    bpy.types.Scene.fmc_video_export_tool = bpy.props.PointerProperty(type = FMC_VIDEO_EXPORT_PROPERTIES)

def unregister():
    # Import addon classes
    from .addon_interface import FMC_VIDEO_EXPORT_PROPERTIES, VIEW3D_PT_freemocap_video_export, FMC_ADAPTER_OT_export_video

    # Unregister addon classes
    bpy.utils.unregister_class(FMC_VIDEO_EXPORT_PROPERTIES)
    bpy.utils.unregister_class(VIEW3D_PT_freemocap_video_export)
    bpy.utils.unregister_class(FMC_ADAPTER_OT_export_video)
    
    del bpy.types.Scene.fmc_video_export_tool

if __name__ == "__main__":
    register()