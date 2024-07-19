import bpy
from .property_types import PropertyTypes

class ExportFBXProperties(bpy.types.PropertyGroup):
    show_export_fbx: PropertyTypes.Bool(
        description = 'Toggle Export FBX Options'
    ) # type: ignore
    fbx_type: PropertyTypes.Enum(
        description = 'Type of the FBX file',
        items = [('standard', 'Standard', ''),
                 ('unreal_engine', 'Unreal Engine', '')
                ]
    ) # type: ignore
