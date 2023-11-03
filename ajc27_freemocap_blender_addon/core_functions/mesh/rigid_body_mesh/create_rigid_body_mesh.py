import logging
from typing import Dict

import bpy

from .helpers.put_meshes_on_empties import put_spheres_on_empties, \
    put_bone_meshes_on_empties

logger = logging.getLogger(__name__)


def create_rigid_body_mesh(rig: bpy.types.Object,
                empties: Dict[str, bpy.types.Object], ):
    # Change to edit mode
    bpy.ops.object.empty_add()
    rigid_mesh_parent = bpy.context.editable_objects[-1]
    rigid_mesh_parent.name = "rigid_body_mesh_parent"
    put_spheres_on_empties(empties=empties, parent_empty=rigid_mesh_parent)
    put_bone_meshes_on_empties(empties=empties, parent_empty=rigid_mesh_parent)
    