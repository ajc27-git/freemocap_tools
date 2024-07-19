import bpy
from .property_types import PropertyTypes

def get_available_armatures(self, context):
    available_rigs = []

    for scene_object in bpy.data.objects:
        if scene_object.type == 'ARMATURE':
            available_rigs.append((scene_object.name, scene_object.name, ''))

    return available_rigs

class RetargetAnimationProperties(bpy.types.PropertyGroup):
    # Retarget Animation options
    show_retarget_animation: PropertyTypes.Bool(
        description = 'Toggle Retarget Animation Options'
    ) # type: ignore
    retarget_source_armature: PropertyTypes.Enum(
        description = 'Source armature which constraints will be copied from',
        items = get_available_armatures,
    ) # type: ignore
    retarget_target_armature: PropertyTypes.Enum(
        description = 'Target armature which constraints will be copied to',
        items = get_available_armatures,
    ) # type: ignore
    retarget_bake_animation: PropertyTypes.Bool(
        default = True,
        description = 'Bake Animation'
    ) # type: ignore
    retarget_clear_constraints: PropertyTypes.Bool(
        default = True,
        description = 'Clear Constraints'
    ) # type: ignore
