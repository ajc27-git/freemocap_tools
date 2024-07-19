import bpy
from .property_types import PropertyTypes

class AddFingerRotationLimitsProperties(bpy.types.PropertyGroup):
    show_add_finger_rotation_limits: bpy.props.BoolProperty(
        description = 'Toggle Add Finger Rotation Limits options'
    ) # type: ignore
