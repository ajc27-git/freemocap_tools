import math as m
from typing import Any, Dict

import bpy

from freemocap_adapter.core_functions.mesh.create_mesh.helpers.get_edit_bones import get_edit_bones
import logging
logger = logging.getLogger(__name__)

BASE_CYLINDER_RADIUS = 0.05

MESH_DEFINITIONS = {
    "trunk": {"mesh_type": "cylinder",
              "radius": BASE_CYLINDER_RADIUS,
              "length": {"start": {"name": "spine",
                                   "part": "head",
                                   "dimension": 2,
                                   "offset": 0},
                         "end": {"name": "spine",
                                 "part": "tail",
                                 "dimension": 2,
                                 "offset": 0},
                         "offset": 0.02},
              "location": {"x": {"bone": {"name": "spine",
                                          "part": "head",
                                          "dimension": 0, },
                                 "offset": 0},
                           "y": {"bone": "spine",
                                 "part": "head",
                                 "dimension": 1,
                                 "offset": 0},
                           "z": {"bone": "spine",
                                 "part": "head",
                                 "dimension": 2,
                                 "offset": 0.02}},
              "rotation": {"x": 0,
                           "y": 0,
                           "z": 0}},
    "neck": {"mesh_type": "cylinder",
             "radius": BASE_CYLINDER_RADIUS / 2,
             "length": {"start": {"name": "neck",
                                  "part": "head",
                                  "dimension": 2,
                                  "offset": 0},
                        "end": {"name": "neck",
                                "part": "tail",
                                "dimension": 2,
                                "offset": 0},
                        "offset": 0},
             "location": {"x": {"bone": "neck",
                                "part": "head",
                                "dimension": 0,
                                "offset": 0},
                          "y": {"bone": "neck",
                                "part": "head",
                                "dimension": 1,
                                "offset": 0},
                          "z": {"bone": "neck",
                                "part": "head",
                                "dimension": 2,
                                "offset": 0}},
             "rotation": {"x": 0,
                          "y": 0,
                          "z": 0}},
    "head": {"mesh_type": "sphere",
             "radius": BASE_CYLINDER_RADIUS * 2,
             "location": {"x": {"bone": "neck",
                                "part": "tail",
                                "dimension": 0,
                                "offset": 0},
                          "y": {"bone": "neck",
                                "part": "tail",
                                "dimension": 1,
                                "offset": 0},
                          "z": {"bone": "neck",
                                "part": "tail",
                                "dimension": 2,
                                "offset": 0}},
             "rotation": {"x": 0,
                          "y": 0,
                          "z": 0}},
    "right_eye": {"mesh_type": "sphere",
                  "radius": BASE_CYLINDER_RADIUS / 3,
                  "location": {"x": {"bone": "neck",
                                     "part": "tail",
                                     "dimension": 0,
                                     "offset": -0.04},
                               "y": {"bone": "neck",
                                     "part": "tail",
                                     "dimension": 1,
                                     "offset": -BASE_CYLINDER_RADIUS},
                               "z": {"bone": "neck",
                                     "part": "tail",
                                     "dimension": 2,
                                     "offset": 0.02}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
    "left_eye": {"mesh_type": "sphere",
                 "radius": BASE_CYLINDER_RADIUS / 3,
                 "location": {"x": {"bone": "neck",
                                    "part": "tail",
                                    "dimension": 0,
                                    "offset": 0.04},
                              "y": {"bone": "neck",
                                    "part": "tail",
                                    "dimension": 1,
                                    "offset": -BASE_CYLINDER_RADIUS},
                              "z": {"bone": "neck",
                                    "part": "tail",
                                    "dimension": 2,
                                    "offset": 0.02}},
                 "rotation": {"x": 0,
                              "y": 0,
                              "z": 0}},
    "nose": {"mesh_type": "sphere",
             "radius": BASE_CYLINDER_RADIUS / 3.5,
             "location": {"x": {"bone": "neck",
                                "part": "tail",
                                "dimension": 0,
                                "offset": 0},
                          "y": {"bone": "neck",
                                "part": "tail",
                                "dimension": 1,
                                "offset": -BASE_CYLINDER_RADIUS},
                          "z": {"bone": "neck",
                                "part": "tail",
                                "dimension": 2,
                                "offset": -0.02}},
             "rotation": {"x": 0,
                          "y": 0,
                          "z": 0}},
    "right_arm": {"mesh_type": "cylinder",
                  "radius": BASE_CYLINDER_RADIUS,
                  "length": {"start": {"name": "shoulder_R",
                                       "part": "head",
                                       "dimension": 0,
                                       "offset": 0},
                             "end": {"name": "hand_R",
                                     "part": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                             "offset": 0},
                  "location": {"x": {"bone": "shoulder_R",
                                     "part": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "shoulder_R",
                                     "part": "tail",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "shoulder_R",
                                     "part": "tail",
                                     "dimension": 2,
                                     "offset": -0.02}},
                  "rotation": {"x": 0,
                               "y": m.radians(90),
                               "z": 0}},
    "left_arm": {"mesh_type": "cylinder",
                 "radius": BASE_CYLINDER_RADIUS,
                 "length": {"start": {"name": "shoulder_L",
                                      "part": "head",
                                      "dimension": 0,
                                      "offset": 0},
                            "end": {"name": "hand_L",
                                    "part": "tail",
                                    "dimension": 0,
                                    "offset": 0},
                            "offset": 0},
                 "location": {"x": {"bone": "shoulder_L",
                                    "part": "tail",
                                    "dimension": 0,
                                    "offset": 0},
                              "y": {"bone": "shoulder_L",
                                    "part": "tail",
                                    "dimension": 1,
                                    "offset": 0},
                              "z": {"bone": "shoulder_L",
                                    "part": "tail",
                                    "dimension": 2,
                                    "offset": -0.02}},
                 "rotation": {"x": 0,
                              "y": m.radians(90),
                              "z": 0}},
    "right_hand": {"mesh_type": "sphere",
                   "radius": BASE_CYLINDER_RADIUS,
                   "location": {"x": {"bone": "hand_R",
                                      "part": "tail",
                                      "dimension": 0,
                                      "offset": 0},
                                "y": {"bone": "hand_R",
                                      "part": "tail",
                                      "dimension": 1,
                                      "offset": 0},
                                "z": {"bone": "hand_R",
                                      "part": "tail",
                                      "dimension": 2,
                                      "offset": 0}},
                   "rotation": {"x": 0,
                                "y": 0,
                                "z": 0}},
    "left_hand": {"mesh_type": "sphere",
                  "radius": BASE_CYLINDER_RADIUS,
                  "location": {"x": {"bone": "hand_L",
                                     "part": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "hand_L",
                                     "part": "tail",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "hand_L",
                                     "part": "tail",
                                     "dimension": 2,
                                     "offset": 0}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
    "right_thumb": {"mesh_type": "sphere",
                    "radius": BASE_CYLINDER_RADIUS / 8,
                    "location": {"x": {"bone": "hand_R",
                                       "part": "tail",
                                       "dimension": 0,
                                       "offset": 0},
                                 "y": {"bone": "hand_R",
                                       "part": "tail",
                                       "dimension": 1,
                                       "offset": -BASE_CYLINDER_RADIUS},
                                 "z": {"bone": "hand_R",
                                       "part": "tail",
                                       "dimension": 2,
                                       "offset": 0}},
                    "rotation": {"x": 0,
                                 "y": 0,
                                 "z": 0}},
    "left_thumb": {"mesh_type": "sphere",
                   "radius": BASE_CYLINDER_RADIUS / 8,
                   "location": {"x": {"bone": "hand_L",
                                      "part": "tail",
                                      "dimension": 0,
                                      "offset": 0},
                                "y": {"bone": "hand_L",
                                      "part": "tail",
                                      "dimension": 1,
                                      "offset": -BASE_CYLINDER_RADIUS},
                                "z": {"bone": "hand_L",
                                      "part": "tail",
                                      "dimension": 2,
                                      "offset": 0}},
                   "rotation": {"x": 0,
                                "y": 0,
                                "z": 0}},
    "right_leg": {"mesh_type": "cylinder",
                  "radius": BASE_CYLINDER_RADIUS,
                  "length": {"start": {"name": "thigh_R",
                                       "part": "head",
                                       "dimension": 0,
                                       "offset": 0},
                             "end": {"name": "shin_R",
                                     "part": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                             "offset": 0},
                  "location": {"x": {"bone": "thigh_R",
                                     "part": "head",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "thigh_R",
                                     "part": "head",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "thigh_R",
                                     "part": "head",
                                     "dimension": 2,
                                     "offset": -BASE_CYLINDER_RADIUS / 2}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
    "left_leg": {"mesh_type": "cylinder",
                 "radius": BASE_CYLINDER_RADIUS,
                 "length": {"start": {"name": "thigh_L",
                                        "part": "head",
                                        "dimension": 0,
                                        "offset": 0},
                            "end": {"name": "shin_L",
                                    "part": "tail",
                                    "dimension": 0,
                                    "offset": 0},
                            "offset": 0},
                 "location": {"x": {"bone": "thigh_L",
                                    "part": "head",
                                    "dimension": 0,
                                    "offset": 0},
                              "y": {"bone": "thigh_L",
                                    "part": "head",
                                    "dimension": 1,
                                    "offset": 0},
                              "z": {"bone": "thigh_L",
                                    "part": "head",
                                    "dimension": 2,
                                    "offset": -BASE_CYLINDER_RADIUS / 2}},
                 "rotation": {"x": 0,
                              "y": 0,
                              "z": 0}},
    "right_foot": {"mesh_type": "sphere",
                   "radius": BASE_CYLINDER_RADIUS,
                   "location": {"x": {"bone": "foot_R",
                                      "part": "tail",
                                      "dimension": 0,
                                      "offset": 0},
                                "y": {"bone": "foot_R",
                                      "part": "tail",
                                      "dimension": 1,
                                      "offset": 0},
                                "z": {"bone": "foot_R",
                                      "part": "tail",
                                      "dimension": 2,
                                      "offset": 0}},
                   "rotation": {"x": 0,
                                "y": 0,
                                "z": 0}},
    "left_foot": {"mesh_type": "sphere",
                  "radius": BASE_CYLINDER_RADIUS,
                  "location": {"x": {"bone": "foot_L",
                                     "part": "tail",
                                     "dimension": 0,
                                     "offset": 0},
                               "y": {"bone": "foot_L",
                                     "part": "tail",
                                     "dimension": 1,
                                     "offset": 0},
                               "z": {"bone": "foot_L",
                                     "part": "tail",
                                     "dimension": 2,
                                     "offset": 0}},
                  "rotation": {"x": 0,
                               "y": 0,
                               "z": 0}},
}


def calculate_mesh_rotation(edit_bones, mesh_dict):
    rotation = {"x": None, "y": None, "z": None}
    for dimension in ["x", "y", "z"]:
        rotation[dimension] = mesh_dict["rotation"][dimension]
    return rotation

def calculate_mesh_location(edit_bones, mesh_dict):
    location = {"x": None, "y": None, "z": None}
    for dimension in ["x", "y", "z"]:
        bone_name = mesh_dict["location"][dimension]["bone"]
        part = mesh_dict["location"][dimension]["part"]
        bone_dimension = mesh_dict["location"][dimension]["dimension"]
        offset = mesh_dict["location"][dimension]["offset"]
        if part == "head":
            location[dimension] = edit_bones[bone_name].head[bone_dimension] + offset
        elif part == "tail":
            location[dimension] = edit_bones[bone_name].tail[bone_dimension] + offset
        else:
            raise ValueError(f"start_part must be either 'head' or 'tail', not {part}")
    return location


def calculate_mesh_length(edit_bones,
                          mesh_dict
                          ):
    position = {"start": None, "end": None}
    for place in ["start", "end"]:
        bone_name = mesh_dict["length"][place]["name"]
        part = mesh_dict["length"][place]["part"]
        dimension = mesh_dict["length"][place]["dimension"]
        offset = mesh_dict["length"][place]["offset"]
        if part == "head":
            position[place] = edit_bones[bone_name].head[dimension] + offset
        elif part == "tail":
            position[place] = edit_bones[bone_name].tail[dimension] + offset
        else:
            raise ValueError(f"start_part must be either 'head' or 'tail', not {place}")

    offset = mesh_dict["length"]["offset"]

    length = position["end"] - position["start"] + offset
    return length

def calculate_mesh_definitions(edit_bones:Dict[str,Any]):
    logger.info("Calculating mesh parameters...")
    mesh_defintions = {}
    for mesh_name, mesh_dict in MESH_DEFINITIONS.items():
        mesh_defintions[mesh_name] = {}
        mesh_defintions[mesh_name]["mesh_type"] = mesh_dict["mesh_type"]
        if mesh_dict["mesh_type"] == "cylinder":
            mesh_defintions[mesh_name]["radius"] = mesh_dict["radius"]
            mesh_defintions[mesh_name]["length"] = calculate_mesh_length(edit_bones, mesh_dict)
            mesh_defintions[mesh_name]["location"] = calculate_mesh_location(edit_bones, mesh_dict)
            mesh_defintions[mesh_name]["rotation"] = calculate_mesh_rotation(edit_bones, mesh_dict)
        elif mesh_dict["mesh_type"] == "sphere":
            mesh_defintions[mesh_name]["radius"] = mesh_dict["radius"]
            mesh_defintions[mesh_name]["location"] = calculate_mesh_location(edit_bones, mesh_dict)
            mesh_defintions[mesh_name]["rotation"] = calculate_mesh_rotation(edit_bones, mesh_dict)
        else:
            raise ValueError(f"mesh_type must be either 'cylinder' or 'sphere', not {mesh_dict['mesh_type']}")

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

        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")
    return body_meshes

def parent_mesh_to_rig(body_meshes, rig):
    logger.info("Parenting mesh to rig...")
    body_meshes[0].name = "mesh"
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    # Select all body meshes
    for body_mesh in body_meshes:
        body_mesh.select_set(True)
    # Set fmc_mesh as active
    bpy.context.view_layer.objects.active = body_meshes[0]
    # Join the body meshes
    bpy.ops.object.join()
    ### Parent the fmc_mesh with the rig
    # Select the rig
    rig.select_set(True)
    # Set rig as active
    bpy.context.view_layer.objects.active = rig
    # Parent the mesh and the rig with automatic weights
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')



def create_custom_mesh_altered(rig):
    # Change to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    edit_bones = get_edit_bones(rig)
    mesh_definitions = calculate_mesh_definitions(edit_bones)

    # Create and append the body meshes to the list
    # Define the list that will contain the different meshes of the body
    body_meshes = create_segment_meshes(mesh_definitions)

    parent_mesh_to_rig(body_meshes, rig)


