from typing import Dict

import bpy

from freemocap_adapter.core_functions.mesh.create_mesh.helpers.create_bone_stick import create_bone_mesh
from freemocap_adapter.core_functions.mesh.create_mesh.helpers.put_sphere_at_location import put_sphere_mesh_at_location
from freemocap_adapter.data_models.mediapipe_names.mediapipe_heirarchy import MEDIAPIPE_HIERARCHY


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

        color, emission_strength, sphere_scale = get_segment_settings(component_name, emission_strength)

        for empty_name, empty in component_dict.items():
            bpy.ops.object.mode_set(mode="OBJECT")
            sphere_mesh = put_sphere_mesh_at_location(name=empty_name,
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

                    stick_mesh = create_bone_mesh(child_name=child_name,
                                                  child_empty=component_dict[child_name],
                                                  parent_empty=empty,
                                                  parent_name=empty_name)

    return meshes


def get_segment_settings(component_name, emission_strength):
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
    return color, emission_strength, sphere_scale
