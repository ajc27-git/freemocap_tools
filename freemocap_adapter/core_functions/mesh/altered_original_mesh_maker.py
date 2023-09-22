import logging
from typing import Dict

import bmesh
import bpy

from freemocap_adapter.core_functions.mesh.create_mesh.helpers.put_sphere_at_location import put_sphere_mesh_at_location
from freemocap_adapter.data_models.mediapipe_names.mediapipe_heirarchy import MEDIAPIPE_HIERARCHY

logger = logging.getLogger(__name__)


def parent_mesh_to_rig(meshes, rig):
    logger.info("Parenting mesh to rig...")
    try:
        meshes[0].name = "mesh"
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        # Select all body meshes
        for body_mesh in meshes:
            body_mesh.select_set(True)
        # Set fmc_mesh as active
        bpy.context.view_layer.objects.active = meshes[0]
        # Join the body meshes
        bpy.ops.object.join()
        ### Parent the fmc_mesh with the rig
        # Select the rig
        rig.select_set(True)
        # Set rig as active
        bpy.context.view_layer.objects.active = rig
        # Parent the mesh and the rig with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    except Exception as e:
        logger.error(f"Failed to parent mesh to rig: {e}")
        raise e


def put_spheres_on_empties(empties: Dict[str, bpy.types.Object]):
    meshes = []

    components = {}
    components["body"] = empties["body"]
    components["right_hand"] = empties["hands"]["right"]
    components["left_hand"] = empties["hands"]["left"]
    components["other"] = {}
    for other_name, other_component_dict in empties["other"].items():
        for name, empty in other_component_dict.items():
            components["other"][name] = empty

    for component_name, component_dict in components.items():
        emission_strength = 1.0

        if component_name == "body":
            if "right" in component_name:
                color = "#FF0000"
            elif "left" in component_name:
                color = "#0000FF"
            else:
                color = "#002244"
            sphere_scale = .025
        elif component_name == "left_hand":
            color = "#00FF44"
            sphere_scale = .01
        elif component_name == "right_hand":
            color = "#aa0000"
            sphere_scale = .01
        elif component_name == "other":
            color = "#FF00FF"
            sphere_scale = .04
            emission_strength = 100

        for empty_name, empty in component_dict.items():
            bpy.ops.object.mode_set(mode="OBJECT")
            put_sphere_mesh_at_location(name=empty_name,
                                        location=empty.location,
                                        sphere_scale=sphere_scale,
                                        color=color,
                                        emission_strength=emission_strength)

            bpy.ops.object.mode_set(mode="OBJECT")
            sphere_mesh = bpy.context.active_object
            constraint = sphere_mesh.constraints.new(type="COPY_LOCATION")
            constraint.target = empty


            if empty_name in MEDIAPIPE_HIERARCHY.keys():
                bpy.ops.object.mode_set(mode="EDIT")
                for child_name in MEDIAPIPE_HIERARCHY[empty_name]["children"]:
                    if "hand_wrist" in child_name:
                        continue

                    stick_mesh = create_bone_stick(child_name=child_name,
                                                   child_empty=component_dict[child_name],
                                                   parent_empty=empty,
                                                   parent_name=empty_name)



    return meshes


def create_bone_stick(child_name: str,
                      child_empty: bpy.types.Object,
                      parent_name: str,
                      parent_empty: bpy.types.Object,
                      skin_radius: float = .005,
                      ):
    bone_name = f"{parent_name}_{child_name}_bone"
    stick_mesh = bpy.data.meshes.new(name=bone_name)
    mesh_obj = bpy.data.objects.new(bone_name, stick_mesh)
    bpy.context.collection.objects.link(mesh_obj)

    bm = bmesh.new()

    parent_vertex = bm.verts.new(parent_empty.location)
    child_vertex = bm.verts.new(child_empty.location)

    bm.edges.new([parent_vertex, child_vertex])

    bm.to_mesh(stick_mesh)
    bm.free()

    modifier = mesh_obj.modifiers.new(name="Skin", type='SKIN')
    modifier.use_smooth_shade = True

    for vertex in stick_mesh.skin_vertices[0].data:
        vertex.radius = skin_radius, skin_radius

    return mesh_obj


def create_custom_mesh_altered(rig: bpy.types.Object,
                               empties: Dict[str, bpy.types.Object], ):
    return
    # Change to edit mode
    meshes = put_spheres_on_empties(empties=empties)

    parent_mesh_to_rig(meshes, rig)
