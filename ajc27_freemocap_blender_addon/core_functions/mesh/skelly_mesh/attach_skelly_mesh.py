import math
from typing import Dict

import bpy

from ajc27_freemocap_blender_addon.core_functions import PACKAGE_BASE_PATH


def attach_skelly_mesh_to_rig(rig_name: str,
                              body_mesh_name: Dict[str, float],
                              empties: Dict[str, bpy.types.Object], ):
    # Change to object mode
    if bpy.context.selected_objects != []:
        bpy.ops.object.mode_set(mode='OBJECT')

    try:
        # Get the script filepath
        # Import the skelly mesh
        bpy.ops.import_scene.fbx(filepath=str(PACKAGE_BASE_PATH) + '/assets/skelly_lowpoly_mesh.fbx')

    except:
        print("\nCould not find skelly mesh file.")
        return

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # Get reference to armature
    rig = bpy.data.objects[rig_name]

    # Select the rig
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig

    # Change to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Get reference to the neck bone
    neck = rig.data.edit_bones['neck']

    # Get the neck bone tail position and save it as the head position
    head_location = (neck.tail[0], neck.tail[1], neck.tail[2])

    # Change to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get the skelly mesh
    skelly_mesh = bpy.data.objects['Skelly_LowPoly_Mesh']

    # Get the body mesh z dimension
    raw_body_mesh_wingspan_width = skelly_mesh.dimensions.x
    raw_body_mesh_toe_to_toe_depth = skelly_mesh.dimensions.y
    raw_body_mesh_height = skelly_mesh.dimensions.z

    # Set the location of the skelly mesh
    skelly_mesh.location = head_location

    # # Get the height of the body
    # head_center_xyz = empties["body"]["head_center"].location.co
    #
    # left_toe_xyz = empties["body"]["left_foot_index"].location.co
    # right_toe_xyz = empties["body"]["right_foot_index"].location.co
    # left_hand_xyz = empties["body"]["left_heel"].location.co
    # right_heel_xyz = empties["body"]["right_heel"].location.co
    # ground_mean_xyz = (left_toe_xyz + right_toe_xyz + left_hand_xyz + right_heel_xyz) / 4
    #
    # body_height = math.sqrt((head_center_xyz[0] - ground_mean_xyz[0]) ** 2 +
    #                         (head_center_xyz[1] - ground_mean_xyz[1]) ** 2 +
    #                         (head_center_xyz[2] - ground_mean_xyz[2]) ** 2)
    # body_height = body_height * 1.1  # Add 10% to the body height because `head_center_xyz` is not the top of the head
    #
    # # get full wingspan (left-arm length + shoulder-to-shoulder length + right-arm length)
    # left_hand_xyz = empties["left_hand"]["left_hand_index_tip"].location.co
    # left_shoulder_xyz = empties["body"]["left_shoulder"].location.co
    # right_shoulder_xyz = empties["body"]["right_shoulder"].location.co
    # right_hand_xyz = empties["right_hand"]["right_hand_index_tip"].location.co
    #
    # left_arm_length = math.sqrt((left_hand_xyz[0] - left_shoulder_xyz[0]) ** 2 +
    #                             (left_hand_xyz[1] - left_shoulder_xyz[1]) ** 2 +
    #                             (left_hand_xyz[2] - left_shoulder_xyz[2]) ** 2)
    # shoulder_to_shoulder_length = math.sqrt((left_shoulder_xyz[0] - right_shoulder_xyz[0]) ** 2 +
    #                                         (left_shoulder_xyz[1] - right_shoulder_xyz[1]) ** 2 +
    #                                         (left_shoulder_xyz[2] - right_shoulder_xyz[2]) ** 2)
    # right_arm_length = math.sqrt((right_hand_xyz[0] - right_shoulder_xyz[0]) ** 2 +
    #                              (right_hand_xyz[1] - right_shoulder_xyz[1]) ** 2 +
    #                              (right_hand_xyz[2] - right_shoulder_xyz[2]) ** 2)
    #
    # full_wingspan = left_arm_length + shoulder_to_shoulder_length + right_arm_length
    #
    # # get full toe-to-toe length (left-foot length + toe-to-toe length + right-foot length)
    # left_foot_length = math.sqrt((left_toe_xyz[0] - left_hand_xyz[0]) ** 2 +
    #                              (left_toe_xyz[1] - left_hand_xyz[1]) ** 2 +
    #                              (left_toe_xyz[2] - left_hand_xyz[2]) ** 2)
    #
    # right_foot_length = math.sqrt((right_toe_xyz[0] - right_heel_xyz[0]) ** 2 +
    #                               (right_toe_xyz[1] - right_heel_xyz[1]) ** 2 +
    #                               (right_toe_xyz[2] - right_heel_xyz[2]) ** 2)
    #
    # toe_to_toe_length = math.sqrt((left_toe_xyz[0] - right_toe_xyz[0]) ** 2 +
    #                               (left_toe_xyz[1] - right_toe_xyz[1]) ** 2 +
    #                               (left_toe_xyz[2] - right_toe_xyz[2]) ** 2)
    #
    #
    # # Calculate the proportion between the rig and the mesh
    # rig_to_body_mesh_height_ratio = body_height / raw_body_mesh_height
    # rig_to_body_mesh_wingspan_ratio = full_wingspan / raw_body_mesh_wingspan_width
    # rig_to_body_mesh_toe_to_toe_ratio = toe_to_toe_length / raw_body_mesh_toe_to_toe_depth

    # Scale the mesh by the rig and body_mesh proportions multiplied by a scale factor
    skelly_mesh.scale = (rig_to_body_mesh_wingspan_ratio,
                            rig_to_body_mesh_toe_to_toe_ratio,
                            rig_to_body_mesh_height_ratio)


    # Set rig as active
    bpy.context.view_layer.objects.active = skelly_mesh

    # Select the skelly_mesh
    skelly_mesh.select_set(True)

    # Apply transformations to the mesh
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Change skelly mesh origin to (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    ### Parent the skelly_mesh with the rig
    # Select the rig
    rig.select_set(True)
    # Set rig as active
    bpy.context.view_layer.objects.active = rig
    # Parent the body_mesh and the rig with automatic weights
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Rename the skelly mesh to fmc_mesh
    skelly_mesh.name = 'fmc_mesh'
