bl_info = {
    'name'          : 'Freemocap Adapter Alt',
    'author'        : 'ajc27',
    'version'       : (1, 6, 1),
    'blender'       : (3, 0, 0),
    'location'      : '3D Viewport > Sidebar > Freemocap Adapter Alt',
    'description'   : 'Add-on to adapt the Freemocap Blender output',
    'category'      : 'Development',
}

import bpy

from .data_definitions.interface.properties.adjust_empties_properties import AdjustEmptiesProperties
from .data_definitions.interface.properties.reduce_bone_length_dispersion_properties import ReduceBoneLengthDispersionProperties
from .data_definitions.interface.properties.apply_butterworth_filters_properties import ApplyButterworthFiltersProperties
from .data_definitions.interface.properties.add_finger_rotation_limits_properties import AddFingerRotationLimitsProperties
from .data_definitions.interface.properties.apply_foot_locking_properties import ApplyFootLockingProperties
from .data_definitions.interface.properties.add_armature_properties import AddArmatureProperties
from .data_definitions.interface.properties.add_body_mesh_properties import AddBodyMeshProperties
from .data_definitions.interface.properties.export_fbx_properties import ExportFBXProperties
from .data_definitions.interface.properties.retarget_animation_properties import RetargetAnimationProperties

from .addon_interface import (FMC_ADAPTER_PROPERTIES,
                              VIEW3D_PT_freemocap_adapter,
                              FMC_ADAPTER_OT_adjust_empties,
                              FMC_ADAPTER_OT_reduce_bone_length_dispersion,
                              FMC_ADAPTER_OT_apply_butterworth_filters,
                              FMC_ADAPTER_OT_add_finger_rotation_limits,
                              FMC_ADAPTER_OT_apply_foot_locking,
                              FMC_ADAPTER_OT_add_rig,
                              FMC_ADAPTER_OT_add_body_mesh,
                              FMC_ADAPTER_OT_export_fbx,
                              FMC_ADAPTER_OT_retarget_animation,
)

classes = [AdjustEmptiesProperties,
           ReduceBoneLengthDispersionProperties,
           ApplyButterworthFiltersProperties,
           AddFingerRotationLimitsProperties,
           ApplyFootLockingProperties,
           AddArmatureProperties,
           AddBodyMeshProperties,
           ExportFBXProperties,
           RetargetAnimationProperties,
           FMC_ADAPTER_PROPERTIES,
           VIEW3D_PT_freemocap_adapter,
           FMC_ADAPTER_OT_adjust_empties,
           FMC_ADAPTER_OT_reduce_bone_length_dispersion,
           FMC_ADAPTER_OT_apply_butterworth_filters,
           FMC_ADAPTER_OT_add_finger_rotation_limits,
           FMC_ADAPTER_OT_apply_foot_locking,
           FMC_ADAPTER_OT_add_rig,
           FMC_ADAPTER_OT_add_body_mesh,
           FMC_ADAPTER_OT_export_fbx,
           FMC_ADAPTER_OT_retarget_animation,
]

def register():
    """
    A function to register classes and assign a pointer property to
    bpy.types.Scene.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type = FMC_ADAPTER_PROPERTIES)

def unregister():
    """
    Function to unregister classes and delete an attribute
    from bpy.types.Scene.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.fmc_adapter_tool

# Register the Add-on
if __name__ == "__main__":
    register()
