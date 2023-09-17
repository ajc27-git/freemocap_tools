import logging
from typing import Dict, Any

import bpy

from freemocap_adapter.core_functions.mesh.create_mesh.helpers.put_sphere_at_location import put_sphere_mesh_at_location
from freemocap_adapter.data_models.bones.bone_definitions import BONE_DEFINITIONS

logger = logging.getLogger(__name__)


def create_mesh(rig: bpy.types.Object,
                bones: Dict[str, Any] = BONE_DEFINITIONS):
    edit_bones = {}
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig.data.edit_bones:
        edit_bones[bone.name] = bone

    meshes = []
    for bone_name, bone_dict in bones.items():
        bpy.ops.object.mode_set(mode="OBJECT")

        color = get_mesh_color(bone_dict)
        scale = get_sphere_scale(bone_dict)

        if not bone_name in edit_bones.keys():
            logger.warning(f"Bone {bone_name} not found in rig")
            continue

        head_location = list(edit_bones[bone_name].head)
        tail_location = list(edit_bones[bone_name].tail)

        meshes.append(put_sphere_mesh_at_location(name=bone_name + "_head",
                                                  location=head_location,
                                                  sphere_scale=scale,
                                                  color=color,
                                                  )
                      )
        meshes.append(put_sphere_mesh_at_location(name=bone_name + "_tail",
                                                  location=tail_location,
                                                  sphere_scale=scale*.5,
                                                  )
                      )

    ### Join all the body_meshes into one mesh
    # Rename the first body_mesh to "mesh"
    meshes[0].name = "mesh"
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    # Select all body meshes
    for mesh in meshes:
        mesh.select_set(True)
    # Set fmc_mesh as active
    bpy.context.view_layer.objects.active = meshes[0]
    # Join the body meshes
    bpy.ops.object.join()
    ### Parent the mesh with the rig
    # Select the rig
    rig.select_set(True)
    # Set rig as active
    bpy.context.view_layer.objects.active = rig
    # Parent the mesh and the rig with automatic weights
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def get_mesh_color(bone_dict) -> str:
    if "right" in bone_dict["head"]:
        if "hand" in bone_dict["head"]:
            color = "#FF00FF"  # right hand is magenta
        else:
            color = "#FF0000"  # right side is red
    elif "left" in bone_dict["head"]:
        if "hand" in bone_dict["head"]:
            color = "#00FFFF"  # left hand is cyan
        else:
            color = "#0000FF"  # left side is blue
    else:
        color = "#FFFF00"  # center is yellow
    return color


def get_sphere_scale(bone_dict) -> float:
    scale = 0.04
    if "hand" in bone_dict["head"]:
        scale *= .5  # hands are smaller

    return scale
