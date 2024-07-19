import bpy
from .property_types import PropertyTypes

class AddBodyMeshProperties(bpy.types.PropertyGroup):
    show_add_body_mesh: PropertyTypes.Bool(
        description = 'Toggle Add Body Mesh Options'
    ) # type: ignore
    body_mesh_mode: PropertyTypes.Enum(
        default = 'skelly_parts',
        description = 'Mode (source) for adding the mesh to the rig',
        items = [('skelly_parts', 'Skelly Parts', ''),
                 ('skelly', 'Skelly', ''),
                 ('can_man', 'Custom', ''),
                ]
    ) # type: ignore
