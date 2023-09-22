import json
import logging
import math as m
from typing import Any, Dict

import bpy

from freemocap_adapter.core_functions.mesh.create_mesh.helpers.put_sphere_at_location import put_sphere_mesh_at_location

logger = logging.getLogger(__name__)

BASE_CYLINDER_RADIUS = 0.05

MESH_DEFINITIONS = {
    "trunk": {"mesh_type": "cylinder",
              "radius": BASE_CYLINDER_RADIUS,
              "length": {"start": {"name": "spine",
                                   "head_tail": "head",
                                   "dimension": 2,
                                   "offset": 0},
                         "end": {"name": "spine",
                                 "head_tail": "tail",
                                 "dimension": 2,
                                 "offset": 0},
                         "offset": 0.02},
              "location": {"x": {"bone": "spine",
                                 "head_tail": "head",
                                 "dimension": 0,
                                 "offset": 0},
                           "y": {"bone": "spine",
                                 "head_tail": "head",
                                 "dimension": 1,
                                 "offset": 0},
                           "z": {"bone": "spine",
                                 "head_tail": "head",
                                 "dimension": 2,
                                 "offset": 0.02}},
              "rotation": {"x": 0,
                           "y": 0,
                           "z": 0}},
    "neck": {"mesh_type": "cylinder",
             "radius": BASE_CYLINDER_RADIUS / 2,
             "length": {"start": {"name": "neck",
                                  "head_tail": "head",
                                  "dimension": 2,
                                  "offset": 0},
                        "end": {"name": "neck",
                                "head_tail": "tail",
                                "dimension": 2,
                                "offset": 0},
                        "offset": 0},
             "location": {"x": {"bone": "neck",
                                "head_tail": "head",
                                "dimension": 0,
                                "offset": 0},
                          "y": {"bone": "neck",
                                "head_tail": "head",
                                "dimension": 1,
                                "offset": 0},
                          "z": {"bone": "neck",
                                "head_tail": "head",
                                "dimension": 2,
                                "offset": 0}},
             "rotation": {"x": 0,
                          "y": 0,
                          "z": 0}},
    "head": {"mesh_type": "sphere",
             "radius": BASE_CYLINDER_RADIUS * 2,
             "location": {"x": {"bone": "neck",
                                "head_tail": "tail",
                                "dimension": 0,
                                "offset": 0},
                          "y": {"bone": "neck",
                                "head_tail": "tail",
                                "dimension": 1,
                                "offset": 0},
                          "z": {"bone": "neck",
                                "head_tail": "tail",
                                "dimension": 2,
                                "offset": 0}},
             "rotation": {"x": 0,
                          "y": 0,
                          "z": 0}},
    "right_eye": {"mesh_type": "sphere",
                  "radius": BASE_CYLINDER_RADIUS / 3,
                  "location": {"x": {"bone": "neck",
                                     "head_tail": "tail",
                                     "dimension": 0,
                                     "offset": -0.04},
                               "y": {"bone": "neck",
                                     "head_tail": "tail",
                                     "dimension": 1,
                                     "offset": -BASE_CYLINDER_RADIUS},
                               "z": {"bone": "neck",
                                     "head_tail": "tail",
                                     "dimension": 2,
                                     "offset": 0.02}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
    "left_eye": {"mesh_type": "sphere",
                 "radius": BASE_CYLINDER_RADIUS / 3,
                 "location": {"x": {"bone": "neck",
                                    "head_tail": "tail",
                                    "dimension": 0,
                                    "offset": 0.04},
                              "y": {"bone": "neck",
                                    "head_tail": "tail",
                                    "dimension": 1,
                                    "offset": -BASE_CYLINDER_RADIUS},
                              "z": {"bone": "neck",
                                    "head_tail": "tail",
                                    "dimension": 2,
                                    "offset": 0.02}},
                 "rotation": {"x": 0,
                              "y": 0,
                              "z": 0}},
    "nose": {"mesh_type": "sphere",
             "radius": BASE_CYLINDER_RADIUS / 3.5,
             "location": {"x": {"bone": "neck",
                                "head_tail": "tail",
                                "dimension": 0,
                                "offset": 0},
                          "y": {"bone": "neck",
                                "head_tail": "tail",
                                "dimension": 1,
                                "offset": -BASE_CYLINDER_RADIUS},
                          "z": {"bone": "neck",
                                "head_tail": "tail",
                                "dimension": 2,
                                "offset": -0.02}},
             "rotation": {"x": 0,
                          "y": 0,
                          "z": 0}},
    "right_arm": {"mesh_type": "cylinder",
                  "radius": BASE_CYLINDER_RADIUS,
                  "length": {"start": {"name": "shoulder_R",
                                       "head_tail": "head",
                                       "dimension": 0,
                                       "offset": 0},
                             "end": {"name": "hand_R",
                                     "head_tail": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                             "offset": 0},
                  "location": {"x": {"bone": "shoulder_R",
                                     "head_tail": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "shoulder_R",
                                     "head_tail": "tail",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "shoulder_R",
                                     "head_tail": "tail",
                                     "dimension": 2,
                                     "offset": -0.02}},
                  "rotation": {"x": 0,
                               "y": m.radians(90),
                               "z": 0}},
    "left_arm": {"mesh_type": "cylinder",
                 "radius": BASE_CYLINDER_RADIUS,
                 "length": {"start": {"name": "shoulder_L",
                                      "head_tail": "head",
                                      "dimension": 0,
                                      "offset": 0},
                            "end": {"name": "hand_L",
                                    "head_tail": "tail",
                                    "dimension": 0,
                                    "offset": 0},
                            "offset": 0},
                 "location": {"x": {"bone": "shoulder_L",
                                    "head_tail": "tail",
                                    "dimension": 0,
                                    "offset": 0},
                              "y": {"bone": "shoulder_L",
                                    "head_tail": "tail",
                                    "dimension": 1,
                                    "offset": 0},
                              "z": {"bone": "shoulder_L",
                                    "head_tail": "tail",
                                    "dimension": 2,
                                    "offset": -0.02}},
                 "rotation": {"x": 0,
                              "y": m.radians(90),
                              "z": 0}},
    "right_hand": {"mesh_type": "sphere",
                   "radius": BASE_CYLINDER_RADIUS,
                   "location": {"x": {"bone": "hand_R",
                                      "head_tail": "tail",
                                      "dimension": 0,
                                      "offset": 0},
                                "y": {"bone": "hand_R",
                                      "head_tail": "tail",
                                      "dimension": 1,
                                      "offset": 0},
                                "z": {"bone": "hand_R",
                                      "head_tail": "tail",
                                      "dimension": 2,
                                      "offset": 0}},
                   "rotation": {"x": 0,
                                "y": 0,
                                "z": 0}},
    "left_hand": {"mesh_type": "sphere",
                  "radius": BASE_CYLINDER_RADIUS,
                  "location": {"x": {"bone": "hand_L",
                                     "head_tail": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "hand_L",
                                     "head_tail": "tail",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "hand_L",
                                     "head_tail": "tail",
                                     "dimension": 2,
                                     "offset": 0}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
    "right_thumb": {"mesh_type": "sphere",
                    "radius": BASE_CYLINDER_RADIUS / 8,
                    "location": {"x": {"bone": "hand_R",
                                       "head_tail": "tail",
                                       "dimension": 0,
                                       "offset": 0},
                                 "y": {"bone": "hand_R",
                                       "head_tail": "tail",
                                       "dimension": 1,
                                       "offset": -BASE_CYLINDER_RADIUS},
                                 "z": {"bone": "hand_R",
                                       "head_tail": "tail",
                                       "dimension": 2,
                                       "offset": 0}},
                    "rotation": {"x": 0,
                                 "y": 0,
                                 "z": 0}},
    "left_thumb": {"mesh_type": "sphere",
                   "radius": BASE_CYLINDER_RADIUS / 8,
                   "location": {"x": {"bone": "hand_L",
                                      "head_tail": "tail",
                                      "dimension": 0,
                                      "offset": 0},
                                "y": {"bone": "hand_L",
                                      "head_tail": "tail",
                                      "dimension": 1,
                                      "offset": -BASE_CYLINDER_RADIUS},
                                "z": {"bone": "hand_L",
                                      "head_tail": "tail",
                                      "dimension": 2,
                                      "offset": 0}},
                   "rotation": {"x": 0,
                                "y": 0,
                                "z": 0}},
    "right_leg": {"mesh_type": "cylinder",
                  "radius": BASE_CYLINDER_RADIUS,
                  "length": {"start": {"name": "thigh_R",
                                       "head_tail": "head",
                                       "dimension": 0,
                                       "offset": 0},
                             "end": {"name": "shin_R",
                                     "head_tail": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                             "offset": 0},
                  "location": {"x": {"bone": "thigh_R",
                                     "head_tail": "head",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "thigh_R",
                                     "head_tail": "head",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "thigh_R",
                                     "head_tail": "head",
                                     "dimension": 2,
                                     "offset": -BASE_CYLINDER_RADIUS / 2}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
    "left_leg": {"mesh_type": "cylinder",
                 "radius": BASE_CYLINDER_RADIUS,
                 "length": {"start": {"name": "thigh_L",
                                      "head_tail": "head",
                                      "dimension": 0,
                                      "offset": 0},
                            "end": {"name": "shin_L",
                                    "head_tail": "tail",
                                    "dimension": 0,
                                    "offset": 0},
                            "offset": 0},
                 "location": {"x": {"bone": "thigh_L",
                                    "head_tail": "head",
                                    "dimension": 0,
                                    "offset": 0},
                              "y": {"bone": "thigh_L",
                                    "head_tail": "head",
                                    "dimension": 1,
                                    "offset": 0},
                              "z": {"bone": "thigh_L",
                                    "head_tail": "head",
                                    "dimension": 2,
                                    "offset": -BASE_CYLINDER_RADIUS / 2}},
                 "rotation": {"x": 0,
                              "y": 0,
                              "z": 0}},
    "right_foot": {"mesh_type": "sphere",
                   "radius": BASE_CYLINDER_RADIUS,
                   "location": {"x": {"bone": "foot_R",
                                      "head_tail": "tail",
                                      "dimension": 0,
                                      "offset": 0},
                                "y": {"bone": "foot_R",
                                      "head_tail": "tail",
                                      "dimension": 1,
                                      "offset": 0},
                                "z": {"bone": "foot_R",
                                      "head_tail": "tail",
                                      "dimension": 2,
                                      "offset": 0}},
                   "rotation": {"x": 0,
                                "y": 0,
                                "z": 0}},
    "left_foot": {"mesh_type": "sphere",
                  "radius": BASE_CYLINDER_RADIUS,
                  "location": {"x": {"bone": "foot_L",
                                     "head_tail": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "foot_L",
                                     "head_tail": "tail",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "foot_L",
                                     "head_tail": "tail",
                                     "dimension": 2,
                                     "offset": 0}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
}


def calculate_mesh_rotation(mesh_dict):
    dimension_string_map = {0: "x", 1: "y", 2: "z"}
    rotation = []
    for dimension in [0, 1, 2]:
        dimension_string = dimension_string_map[dimension]
        rotation.append(mesh_dict["rotation"][dimension_string])
    return rotation


def calculate_mesh_location(edit_bones, mesh_dict):
    dimension_string_map = {0: "x", 1: "y", 2: "z"}
    location = []
    for dimension in [0, 1, 2]:
        dimension_string = dimension_string_map[dimension]
        bone_name = mesh_dict["location"][dimension_string]["bone"]
        head_tail = mesh_dict["location"][dimension_string]["head_tail"]
        bone_dimension = mesh_dict["location"][dimension_string]["dimension"]
        offset = mesh_dict["location"][dimension_string]["offset"]
        if head_tail == "head":
            location.append(edit_bones[bone_name].head[bone_dimension] + offset)
        elif head_tail == "tail":
            location.append(edit_bones[bone_name].tail[bone_dimension] + offset)
        else:
            raise ValueError(f"start_part must be either 'head' or 'tail', not {head_tail}")
    return location


def calculate_mesh_length(edit_bones,
                          mesh_dict
                          ):
    position = {"start": None, "end": None}
    for start_end in ["start", "end"]:
        bone_name = mesh_dict["length"][start_end]["name"]
        head_tail = mesh_dict["length"][start_end]["head_tail"]
        dimension = mesh_dict["length"][start_end]["dimension"]
        offset = mesh_dict["length"][start_end]["offset"]
        if head_tail == "head":
            position[start_end] = edit_bones[bone_name].head[dimension] + offset
        elif head_tail == "tail":
            position[start_end] = edit_bones[bone_name].tail[dimension] + offset
        else:
            raise ValueError(f"start_part must be either 'head' or 'tail', not {start_end}")

    offset = mesh_dict["length"]["offset"]

    length = position["end"] - position["start"] + offset
    return length


def calculate_mesh_definitions(edit_bones: Dict[str, Any]):
    logger.info("Calculating mesh definitions...")
    mesh_defintions = {}
    for mesh_name, mesh_dict in MESH_DEFINITIONS.items():
        mesh_defintions[mesh_name] = {}
        mesh_defintions[mesh_name]["mesh_type"] = mesh_dict["mesh_type"]
        if mesh_dict["mesh_type"] == "cylinder":
            mesh_defintions[mesh_name]["radius"] = mesh_dict["radius"]
            mesh_defintions[mesh_name]["length"] = calculate_mesh_length(edit_bones, mesh_dict)
            mesh_defintions[mesh_name]["location"] = calculate_mesh_location(edit_bones, mesh_dict)
            mesh_defintions[mesh_name]["rotation"] = calculate_mesh_rotation(mesh_dict)
        elif mesh_dict["mesh_type"] == "sphere":
            mesh_defintions[mesh_name]["radius"] = mesh_dict["radius"]
            mesh_defintions[mesh_name]["location"] = calculate_mesh_location(edit_bones, mesh_dict)
            mesh_defintions[mesh_name]["rotation"] = calculate_mesh_rotation(mesh_dict)
        else:
            raise ValueError(f"mesh_type must be either 'cylinder' or 'sphere', not {mesh_dict['mesh_type']}")
        logger.debug(f"mesh_defintions[{mesh_name}]:|n {json.dumps(mesh_defintions[mesh_name])}")

    logger.success("Done calculating mesh definitions")
    return mesh_defintions


def create_segment_meshes(mesh_definitions):
    body_meshes = []
    # Set basic cylinder properties
    cylinder_cuts = 20
    vertices = 16
    for mesh_name, mesh_dict in mesh_definitions.items():
        logger.info(f"Creating mesh: {mesh_name}")
        if mesh_dict["mesh_type"] == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=vertices,
                radius=mesh_dict["radius"],
                depth=mesh_dict["length"],
                end_fill_type='NGON',
                calc_uvs=True,
                enter_editmode=False,
                align='WORLD',
                location=mesh_dict["location"],
                rotation=mesh_dict["rotation"]
            )
        elif mesh_dict["mesh_type"] == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=mesh_dict["radius"],
                enter_editmode=False,
                align='WORLD',
                location=mesh_dict["location"],
                scale=(1, 1, 1)
            )
        else:
            raise ValueError(f"mesh_type must be either 'cylinder' or 'sphere', not {mesh_dict['mesh_type']}")
        mesh = bpy.context.active_object
        mesh.name = mesh_name
        body_meshes.append(mesh)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")
    return body_meshes


def parent_mesh_to_rig(meshes, rig):
    logger.info("Parenting mesh to rig...")
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


def put_spheres_on_joint_centers(rig: bpy.types.Object):
    try:
        edit_bones = rig.data.edit_bones
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for edit_bone in edit_bones:
            logger.info(f"Creating sphere for {edit_bone.name}")
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=1,
                enter_editmode=False,
                align='WORLD',
                location=edit_bone.head,
                scale=(1, 1, 1)
            )
            sphere = bpy.context.active_object
            sphere.name = f"{edit_bone.name}_sphere"
            bpy.ops.object.select_all(action='DESELECT')
            sphere.select_set(True)
            rig.select_set(True)  # Select the rig
            bpy.context.view_layer.objects.active = rig  # Set the rig as the active object
            bpy.context.view_layer.objects.active = sphere
            bpy.ops.object.parent_set(type='BONE', keep_transform=True)
            sphere.select_set(False)
    except Exception as e:
        logger.error(f"Failed to create spheres on joint centers: {e}")
        logger.exception(e)
        raise e


def put_spheres_on_empties(empties: Dict[str, bpy.types.Object]):
    meshes = []
    components = {}

    components["body"] = empties["body"]
    components["right_hand"] = empties["hands"]["right"]
    components["left_hand"] = empties["hands"]["left"]

    for component_name, empties in components.items():
        if component_name == "body":
            color = "#00FF00"
            sphere_scale = .02
        elif component_name == "left_hand":
            color = "#FF0000"
            sphere_scale = .01
        elif component_name == "right_hand":
            color = "#0000FF"
            sphere_scale = .01
        else:
            color = "#FF00FF"
            sphere_scale = .01

        for empty_name, empty in empties.items():
            bpy.ops.object.mode_set(mode="OBJECT")
            put_sphere_mesh_at_location(name=empty_name,
                                        location=empty.location,
                                        sphere_scale=sphere_scale,
                                        color=color,
                                        )
            mesh = bpy.context.active_object
            constraint = mesh.constraints.new(type="COPY_LOCATION")
            constraint.target = empty
            meshes.append(mesh)

    return meshes


def create_custom_mesh_altered(rig: bpy.types.Object,
                               empties: Dict[str, bpy.types.Object], ):
    # Change to edit mode

    meshes = put_spheres_on_empties(empties=empties)
    # parent_mesh_to_rig(meshes, rig)
    ### Join all the body_meshes into one mesh
    # Rename the first body_mesh to "mesh"


    # edit_bones = get_edit_bones(rig)
    # mesh_definitions = calculate_mesh_definitions(edit_bones)
    #
    # # Create and append the body meshes to the list
    # # Define the list that will contain the different meshes of the body
    # body_meshes = create_segment_meshes(mesh_definitions)

