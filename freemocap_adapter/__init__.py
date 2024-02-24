bl_info = {
    'name'          : 'Freemocap Adapter Alt',
    'author'        : 'ajc27',
    'version'       : (1, 3, 2),
    'blender'       : (3, 0, 0),
    'location'      : '3D Viewport > Sidebar > Freemocap Adapter Alt',
    'description'   : 'Add-on to adapt the Freemocap Blender output',
    'category'      : 'Development',
}

import bpy

from .addon_interface import (FMC_ADAPTER_PROPERTIES,
                              VIEW3D_PT_freemocap_adapter,
                              FMC_ADAPTER_OT_adjust_empties,
                              FMC_ADAPTER_OT_reduce_bone_length_dispersion,
                              FMC_ADAPTER_OT_add_rig,
                              FMC_ADAPTER_OT_add_body_mesh,
                              FMC_ADAPTER_OT_export_fbx,
                              FMC_ADAPTER_OT_add_finger_rotation_limits,
                              FMC_ADAPTER_OT_apply_butterworth_filters
)

classes = [FMC_ADAPTER_PROPERTIES,
           VIEW3D_PT_freemocap_adapter,
           FMC_ADAPTER_OT_adjust_empties,
           FMC_ADAPTER_OT_reduce_bone_length_dispersion,
           FMC_ADAPTER_OT_add_rig,
           FMC_ADAPTER_OT_add_body_mesh,
           FMC_ADAPTER_OT_export_fbx,
           FMC_ADAPTER_OT_add_finger_rotation_limits,
           FMC_ADAPTER_OT_apply_butterworth_filters,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type = FMC_ADAPTER_PROPERTIES)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.fmc_adapter_tool

# Register the Add-on
if __name__ == "__main__":
    register()
