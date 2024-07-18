import bpy
from bpy.types import Operator
import math as m
import statistics
import mathutils
import numpy as np
import os
from pathlib import Path
from importlib.machinery import SourceFileLoader
import addon_utils

scipy_available = True
try:
    from scipy.signal import butter, filtfilt
    from scipy.optimize import minimize
except ImportError:
    scipy_available = False
    print("scipy is not installed. Please install scipy to use this addon.")

from .data_definitions.anthropomorphic_dimensions import (
    anthropomorphic_dimensions)
from .data_definitions.virtual_bones import virtual_bones
from .data_definitions.empties_dict import empties_dict
from .data_definitions.ik_control_bones import ik_control_bones
from .data_definitions.ik_pole_bones import ik_pole_bones
from .data_definitions.skelly_parts import skelly_parts
from .data_definitions.foot_locking_markers import foot_locking_markers
from .data_definitions.bone_constraints import bone_constraints

from .data_definitions.armatures.freemocap import armature_freemocap
from .data_definitions.armatures.ue_metahuman_simple import (
    armature_ue_metahuman_simple
)
from .data_definitions.armatures.bone_name_map import bone_name_map

from .data_definitions.poses.freemocap_tpose import freemocap_tpose
from .data_definitions.poses.freemocap_apose import freemocap_apose
from .data_definitions.poses.ue_metahuman_default import ue_metahuman_default
from .data_definitions.poses.ue_metahuman_tpose import ue_metahuman_tpose
from .data_definitions.poses.ue_metahuman_realtime import ue_metahuman_realtime

if bpy.app.version_string[0] < '4':
    from .io_scene_fbx_functions_blender3 import (
        fbx_animations_do_blender3,
        fbx_data_armature_elements_blender3,
        fbx_data_object_elements_blender3,
        fbx_data_bindpose_element_blender3)

if bpy.app.version_string[0] >= '4':
    from .io_scene_fbx_functions_blender4 import (
        fbx_animations_do_blender4,
        fbx_data_armature_elements_blender4,
        fbx_data_object_elements_blender4,
        fbx_data_bindpose_element_blender4)

# Global Variables
# Variable to save if the function Adjust Empties has been already executed
adjust_empties_executed = False

# Location and rotation vectors of the empties_parent in the Adjust Empties method just before resetting its location and rotation to (0, 0, 0)
origin_location_pre_reset = (0, 0, 0)
origin_rotation_pre_reset = (0, 0, 0)

# Dictionary to save the global vector position of all the empties for every animation frame
empty_positions = {}

# Dictionary to save the speed of all the empties for every animation frame
empty_speeds = {}

# Function to update all the empties positions in the dictionary
def update_empty_positions(target_empty: str='',
                           position_reference: str='local') -> None:

    print('Updating Empty Positions Dictionary...')

    # Get the scene context
    scene = bpy.context.scene

    # Change to Object Mode if there is one or more objects selected
    if len(bpy.context.selected_objects) != 0:
        bpy.ops.object.mode_set(mode="OBJECT")

    # Check if the target_empty is defined to avoid iterating through all the empties
    if target_empty != '':
        # Check if the target_empty variable is a list instead of a single value (a list will mean a bone head and tail pair)
        if isinstance(target_empty, list):
            #  Reset the empty positions
            empty_positions[target_empty[0]] = {'x': [], 'y': [], 'z': []}
            empty_positions[target_empty[1]] = {'x': [], 'y': [], 'z': []}

            # Iterate through each scene frame and save the coordinates of the
            # empties in the dictionary. Separate between local and global
            # position reference
            if position_reference == 'local':
                for frame in range (scene.frame_start, scene.frame_end):
                    # Set scene frame
                    scene.frame_set(frame)
                    # Save the x, y, z position of the empties
                    empty_positions[target_empty[0]]['x'].append(bpy.data.objects[target_empty[0]].location[0])
                    empty_positions[target_empty[0]]['y'].append(bpy.data.objects[target_empty[0]].location[1])
                    empty_positions[target_empty[0]]['z'].append(bpy.data.objects[target_empty[0]].location[2])
                    empty_positions[target_empty[1]]['x'].append(bpy.data.objects[target_empty[1]].location[0])
                    empty_positions[target_empty[1]]['y'].append(bpy.data.objects[target_empty[1]].location[1])
                    empty_positions[target_empty[1]]['z'].append(bpy.data.objects[target_empty[1]].location[2])

            elif position_reference == 'global':
                for frame in range (scene.frame_start, scene.frame_end):
                    # Set scene frame
                    scene.frame_set(frame)
                    # Save the x, y, z position of the empties
                    empty_positions[target_empty[0]]['x'].append(bpy.data.objects[target_empty[0]].matrix_world.to_translation()[0])
                    empty_positions[target_empty[0]]['y'].append(bpy.data.objects[target_empty[0]].matrix_world.to_translation()[1])
                    empty_positions[target_empty[0]]['z'].append(bpy.data.objects[target_empty[0]].matrix_world.to_translation()[2])
                    empty_positions[target_empty[1]]['x'].append(bpy.data.objects[target_empty[1]].matrix_world.to_translation()[0])
                    empty_positions[target_empty[1]]['y'].append(bpy.data.objects[target_empty[1]].matrix_world.to_translation()[1])
                    empty_positions[target_empty[1]]['z'].append(bpy.data.objects[target_empty[1]].matrix_world.to_translation()[2])

        else:
            #  Reset the empty positions
            empty_positions[target_empty] = {'x': [], 'y': [], 'z': []}

            # Iterate through each scene frame and save the coordinates of the empty in the dictionary.
            for frame in range (scene.frame_start, scene.frame_end):
                # Set scene frame
                scene.frame_set(frame)
                # Save the x, y, z position of the empty
                empty_positions[target_empty]['x'].append(bpy.data.objects[target_empty].location[0])
                empty_positions[target_empty]['y'].append(bpy.data.objects[target_empty].location[1])
                empty_positions[target_empty]['z'].append(bpy.data.objects[target_empty].location[2])

    else:
        # Create a list with only the names of the marker empties
        marker_empties = [object.name for object in bpy.data.objects if object.type == 'EMPTY' and
                                                                        '_origin' not in object.name and
                                                                        object.name not in ('empties_parent', 'center_of_mass_data_parent', 'center_of_mass', 'rigid_body_meshes_parent', 'videos_parent')]

        # Reset the empty positions dictionary with empty arrays for each empty
        for empty in marker_empties:
            empty_positions[empty] = {'x': [], 'y': [], 'z': []}

        # Iterate through each scene frame and save the coordinates of each
        # empty in the dictionary. Separate between local and global
        # position reference
        if position_reference == 'local':
            for frame in range (scene.frame_start, scene.frame_end):
                # Set scene frame
                scene.frame_set(frame)
                # Iterate through each empty
                for empty in marker_empties:
                    # Save the x, y, z position of the empty
                    empty_positions[empty]['x'].append(bpy.data.objects[empty].location[0])
                    empty_positions[empty]['y'].append(bpy.data.objects[empty].location[1])
                    empty_positions[empty]['z'].append(bpy.data.objects[empty].location[2])
        
        elif position_reference == 'global':
            for frame in range (scene.frame_start, scene.frame_end):
                # Set scene frame
                scene.frame_set(frame)
                # Iterate through each empty
                for empty in marker_empties:
                    # Save the x, y, z position of the empty
                    empty_positions[empty]['x'].append(bpy.data.objects[empty].matrix_world.to_translation()[0])
                    empty_positions[empty]['y'].append(bpy.data.objects[empty].matrix_world.to_translation()[1])
                    empty_positions[empty]['z'].append(bpy.data.objects[empty].matrix_world.to_translation()[2])

    # Reset the scene frame to the start
    scene.frame_set(scene.frame_start)

    print('Empty Positions Dictionary update completed.')

# Function to update all the information of the virtual bones dictionary (lengths, median and stdev)
def update_virtual_bones_info(target_bone: str=''):

    # Check if the target bone is defined to only update and print what it is necessary
    if target_bone != '':
        print('Updating Virtual Bone: ' + target_bone)
        # Reset the lengths list of the target virtual bone
        virtual_bones[target_bone]['lengths'] = []

        # Iterate through the empty_positions dictionary and calculate the distance between the head and tail and append it to the lengths list
        for frame in range (0, len(empty_positions[virtual_bones[target_bone]['tail']]['x'])):
            # Calculate the length of the bone for this frame
            head        = virtual_bones[target_bone]['head']
            tail        = virtual_bones[target_bone]['tail']
            head_pos    = (empty_positions[head]['x'][frame], empty_positions[head]['y'][frame], empty_positions[head]['z'][frame])
            tail_pos    = (empty_positions[tail]['x'][frame], empty_positions[tail]['y'][frame], empty_positions[tail]['z'][frame])

            virtual_bones[target_bone]['lengths'].append(m.dist(head_pos, tail_pos))

        # Update the length median and stdev values of the target bone
        # Exclude posible length NaN (produced by an empty with NaN values as position) values from the median and standard deviation
        try:
            virtual_bones[target_bone]['median'] = statistics.median([length for length in virtual_bones[target_bone]['lengths'] if not m.isnan(length)])
        except:
            virtual_bones[target_bone]['median'] = m.nan

        # If the median is nan (every length values was nan) then directly set the stdev as nan to avoid a calculus error
        if m.isnan(virtual_bones[target_bone]['median']):
            virtual_bones[target_bone]['stdev'] = m.nan
        else:
            try:
                virtual_bones[target_bone]['stdev'] = statistics.stdev([length for length in virtual_bones[target_bone]['lengths'] if not m.isnan(length)])
            except:
                virtual_bones[target_bone]['stdev'] = m.nan

    else:
        print('Updating Virtual Bones Information...')

        # Reset the lengths list for every virtual bone
        for bone in virtual_bones:
            virtual_bones[bone]['lengths'] = []

        # Adjust tail empty of hand bones depending if hand_middle empties exist or not
        try:
            right_hand_middle_name = bpy.data.objects['right_hand_middle'].name
            virtual_bones['hand.R']['tail'] = 'right_hand_middle'
            virtual_bones['hand.L']['tail'] = 'left_hand_middle'
        except:
            virtual_bones['hand.R']['tail'] = 'right_index'
            virtual_bones['hand.L']['tail'] = 'left_index'

        # Iterate through the empty_positions dictionary and calculate the distance between the head and tail and append it to the lengths list
        # for frame in range (0, len(empty_positions['hips_center']['x'])):
        for frame in range (0, len(empty_positions[list(empty_positions.keys())[0]]['x'])):

            # Iterate through each bone
            for bone in virtual_bones:
                # Calculate the length of the bone for this frame
                head        = virtual_bones[bone]['head']
                tail        = virtual_bones[bone]['tail']
                head_pos    = (empty_positions[head]['x'][frame], empty_positions[head]['y'][frame], empty_positions[head]['z'][frame])
                tail_pos    = (empty_positions[tail]['x'][frame], empty_positions[tail]['y'][frame], empty_positions[tail]['z'][frame])

                virtual_bones[bone]['lengths'].append(m.dist(head_pos, tail_pos))

        # Update the length median and stdev values for each bone
        for bone in virtual_bones:
            # Exclude posible length NaN (produced by an empty with NaN values as position) values from the median and standard deviation
            try:
                virtual_bones[bone]['median'] = statistics.median([length for length in virtual_bones[bone]['lengths'] if not m.isnan(length)])
            except:
                virtual_bones[bone]['median'] = m.nan

            # If the median is nan (every length values was nan) then directly set the stdev as nan to avoid a calculus error
            if m.isnan(virtual_bones[bone]['median']):
                virtual_bones[bone]['stdev'] = m.nan
            else:
                try:
                    virtual_bones[bone]['stdev'] = statistics.stdev([length for length in virtual_bones[bone]['lengths'] if not m.isnan(length)])
                except:
                    virtual_bones[bone]['stdev'] = m.nan

        print('Virtual Bones Information update completed.')

def add_hands_middle_empties():

    # Try checking if the hand middle empties have been already added
    try:
        right_hand_middle_name = bpy.data.objects['right_hand_middle'].name
        # Right Hand Middle Empty exists. Nothing is done
        print('Hand Middle Empties already added.')

    except:
        # Hand Middle Empties do not exist
        print('Adding Hand Middle Empties...')

        # Define the empties that serve as reference to locate the middle empties
        # middle_references = ['index', 'pinky']
        middle_references = ['hand_middle_finger_mcp', 'hand_ring_finger_mcp']

        # Add the empties
        bpy.ops.object.empty_add(type='ARROWS', align='WORLD', location=(0, 0, 0), scale=(0.1, 0.1, 0.1))
        right_hand_middle        = bpy.context.active_object
        right_hand_middle.name   = 'right_hand_middle'
        right_hand_middle.scale  = (0.02, 0.02, 0.02)

        bpy.ops.object.empty_add(type='ARROWS', align='WORLD', location=(0, 0, 0), scale=(0.1, 0.1, 0.1))
        left_hand_middle        = bpy.context.active_object
        left_hand_middle.name   = 'left_hand_middle'
        left_hand_middle.scale  = (0.02, 0.02, 0.02)

        # Copy the action data from the index fingers to have the base
        right_hand_middle.animation_data_create()
        right_hand_middle.animation_data.action = bpy.data.actions["right_" + middle_references[0] + "Action"].copy()
        right_hand_middle.animation_data.action.name = 'right_hand_middleAction'

        left_hand_middle.animation_data_create()
        left_hand_middle.animation_data.action = bpy.data.actions["left_" + middle_references[0] + "Action"].copy()
        left_hand_middle.animation_data.action.name = 'left_hand_middleAction'

        # Move the empties_parent empty to the position and rotation previous to the Adjust Empties method ending
        origin = bpy.data.objects['empties_parent']
        origin.location         = origin_location_pre_reset
        origin.rotation_euler   = origin_rotation_pre_reset

        # Select the new empties
        right_hand_middle.select_set(True)
        left_hand_middle.select_set(True)

        # Set the origin active in 3Dview
        bpy.context.view_layer.objects.active = bpy.data.objects['empties_parent']
        # Parent selected empties to empties_parent keeping transforms
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Reset the position and rotation of the origin
        origin.location         = mathutils.Vector([0, 0, 0])
        origin.rotation_euler   = mathutils.Vector([0, 0, 0])

        # Create a list with the new hand middle empties
        hand_middle_empties = [right_hand_middle, left_hand_middle]

        # Create a list of the hand sides
        hand_side = ['right', 'left']

        # Iterate through each frame and calculate the middle point between the index and pinky empty markers for each hand
        # Update the new hand middle empties position with that point
        for frame_index in range (0, len(empty_positions['right_index']['x']) - 1):

            for side_index in range (0, 2):
                # Get the positions of the middle references
                ref0_position    = mathutils.Vector([empty_positions[hand_side[side_index] + '_' + middle_references[0]]['x'][frame_index],
                                                     empty_positions[hand_side[side_index] + '_' + middle_references[0]]['y'][frame_index],
                                                     empty_positions[hand_side[side_index] + '_' + middle_references[0]]['z'][frame_index]])
                ref1_position    = mathutils.Vector([empty_positions[hand_side[side_index] + '_' + middle_references[1]]['x'][frame_index],
                                                     empty_positions[hand_side[side_index] + '_' + middle_references[1]]['y'][frame_index],
                                                     empty_positions[hand_side[side_index] + '_' + middle_references[1]]['z'][frame_index]])
                
                # Get the new position of the middle empties
                hand_middle_position  = ref0_position + (ref1_position - ref0_position) / 2

                # Update the action property of the middle empty
                hand_middle_empties[side_index].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1] = hand_middle_position[0]
                hand_middle_empties[side_index].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1] = hand_middle_position[1]
                hand_middle_empties[side_index].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1] = hand_middle_position[2]

        print('Adding Hand Middle completed.')

# Function to draw a vector for debbuging purposes
def draw_vector(origin, angle, name):
    
    bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=origin, rotation=mathutils.Vector([0,0,1]).rotation_difference(angle).to_euler(), scale=(0.002, 0.002, 0.002))
    bpy.data.objects["Empty"].name = name
    
    # bpy.ops.object.empty_add(type='SPHERE', align='WORLD', location=(origin+angle*5), scale=(0.001, 0.001, 0.001))
    # bpy.data.objects["Empty"].scale = (0.01, 0.01, 0.01)
    # bpy.data.objects["Empty"].name = 'Sphere_' + name

    return

#  Function to define a quadratic function for the ik pole bone position calculus transition
def quadratic_function(x1, x2, x3, y1, y2, y3):
    A = np.array([
        [x1**2, x1, 1],
        [x2**2, x2, 1],
        [x3**2, x3, 1]
    ])
    b = np.array([y1, y2, y3])
    
    # Solve for the coefficients
    a, b, c = np.linalg.solve(A, b)
    
    # Define the quadratic function
    def quadratic_function(t):
        return a*t**2 + b*t + c
    
    return quadratic_function

# Function to calculate the position of a an ik pole bone based on the position of the limb markers
def calculate_ik_pole_position(base_marker_name: str,
                               pole_marker_name: str,
                               target_marker_name: str,
                               aux_markers: list,
                               dot_product_threshold: float,
                               transition_function,):

    # Get the marker objects
    base_marker    = bpy.data.objects[base_marker_name]
    pole_marker    = bpy.data.objects[pole_marker_name]
    target_marker  = bpy.data.objects[target_marker_name]

    # Get the base vector (vector from base marker to pole marker)
    base_vector     = pole_marker.matrix_world.translation - base_marker.matrix_world.translation

    # Get the target vector (vector from target marker to pole marker)
    target_vector   = pole_marker.matrix_world.translation - target_marker.matrix_world.translation

    # Normalize the vectors
    base_vector_normalized = base_vector.normalized()
    target_vector_normalized = target_vector.normalized()

    #  Calculate the pole projection vector as the sum of the base vector and the target vector
    pole_projection = (base_vector_normalized + target_vector_normalized).normalized()

    # Get the dot product of the base vector and the target vector
    dot_product = base_vector_normalized.dot(target_vector_normalized)

    # If the vectors are almost parallel (dot product near minus one), use the auxiliary markers to determine approximate direction
    if dot_product < (dot_product_threshold * -1):
        # Get auxiliary markers
        aux_0 = bpy.data.objects[aux_markers[0]]
        aux_1 = bpy.data.objects[aux_markers[1]]
        
        # Get the auxiliary vector
        aux_vector = (aux_0.matrix_world.translation - aux_1.matrix_world.translation).normalized()
        
        # Get the perpendicular projection of the aux_vector onto the base vector
        perpendicular_aux = (aux_vector - base_vector_normalized * (base_vector_normalized.dot(aux_vector) / base_vector_normalized.length_squared)).normalized()

        # Get the pondered coefficient from the transition function
        pondered_coefficient = transition_function(abs(dot_product))

        # Get the final pole projection vector as pondered sum of the base vector and the perpendicular aux vector
        final_pole_projection = mathutils.Vector((1 - pondered_coefficient) * pole_projection + pondered_coefficient * perpendicular_aux).normalized()
    
    else:
        final_pole_projection = pole_projection

    # Debug
    # bpy.ops.object.mode_set(mode='OBJECT')
    # draw_vector(pole_marker.matrix_world.translation, base_vector_normalized, 'base_vector')
    # draw_vector(pole_marker.matrix_world.translation, target_vector_normalized, 'target_vector')    
    # draw_vector(pole_marker.matrix_world.translation, pole_projection, 'pole_projection_' + str(dot_product))
    # if perpendicular_aux is not None:
    #     draw_vector(pole_marker.matrix_world.translation, perpendicular_aux, 'perpendicular_aux_' + str(dot_product))
    # draw_vector(pole_marker.matrix_world.translation, final_pole_projection, 'final_pole_projection_' + str(dot_product))
    # bpy.context.view_layer.objects.active = bpy.data.objects['root']
    # bpy.ops.object.mode_set(mode='POSE')

    # Get the pole bone position as the projection vector multiplied by the sum of the length of the base vector and the length of the target vector
    pole_bone_position = mathutils.Vector(pole_marker.matrix_world.translation + final_pole_projection * (base_vector.length + target_vector.length))

    return pole_bone_position

# Function to translate the empties recursively
def translate_empty(empties_dict, empty, frame_index, delta, recursivity: bool=True):

    try:
        # Translate the empty in the animation location curve
        actual_x = bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1] = actual_x + delta[0]
        actual_y = bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1] = actual_y + delta[1]
        actual_z = bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1] = actual_z + delta[2]
    except:
        # Empty does not exist or does not have animation data
        #print('Empty ' + empty + ' does not have animation data on frame ' + str(frame_index))
        pass

    # If recursivity is set to True then call this function to the children of the empty
    if recursivity:

        # If empty has children then call this function for every child
        if empty in empties_dict:
            for child in empties_dict[empty]['children']:
                translate_empty(empties_dict, child, frame_index, delta, recursivity)

# Function to rotate the virtual bones by its tail empty using a rotation matrix. Do it recursively for its children
def rotate_virtual_bone(empty, origin, rot_matrix: mathutils.Matrix):
    # Get the scene current frame
    frame_index = bpy.context.scene.frame_current

    # Get the current location of the empty
    empty_current_location = bpy.data.objects[empty].matrix_world.translation

    # Get local vector from origin to the virtual bone tail empty
    empty_local_vector = empty_current_location - origin

    # Rotate the local vector using the rotation matrix
    rotated_empty_vector = rot_matrix @ empty_local_vector

    # Get the world space rotated empty vector
    new_empty_vector = origin + rotated_empty_vector

    # Change the position of the empty in the world space
    bpy.data.objects[empty].matrix_world.translation = new_empty_vector

    # Translate the empty in the animation location curve
    try:
        bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1] = new_empty_vector[0]
        bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1] = new_empty_vector[1]
        bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1] = new_empty_vector[2]
    except:
        # Empty does not exist or does not have animation data
        print('Empty ' + empty + ' does not have animation data on frame ' + str(frame_index))

    # If empty has children then call this function for every child
    if empty in empties_dict:
        for child in empties_dict[empty]['children']:
            rotate_virtual_bone(child, origin, rot_matrix)

def adjust_empties(z_align_ref_empty: str='left_knee',
                   z_align_angle_offset: float=0,
                   ground_ref_empty: str='left_foot_index',
                   z_translation_offset: float=-0.01,
                   correct_fingers_empties: bool=True,
                   add_hand_middle_empty: bool=True,
                   ):
    
    # Reference to the global adjust_empties_executed variable
    global adjust_empties_executed
    # Reference to the global origin location and rotation pre reset variables
    global origin_location_pre_reset
    global origin_rotation_pre_reset

    # Get the scene context
    scene = bpy.context.scene

    # Play and stop the animation in case the first frame empties are in a strange position
    bpy.ops.screen.animation_play()
    bpy.ops.screen.animation_cancel()

    ### Unparent empties from empties_parent ###
    for object in bpy.data.objects:
        if object.type == "EMPTY" and object.name != 'empties_parent' and '_origin' not in object.name and 'center_of_mass' not in object.name and object.name != 'rigid_body_meshes_parent':
            object.parent = None

    ### Move empties_parent to the hips_center empty and rotate it so the ###
    ### z axis intersects the trunk_center empty and the x axis intersects the left_hip empty ###
    origin = bpy.data.objects['empties_parent']
    hips_center = bpy.data.objects['hips_center']

    left_hip = bpy.data.objects['left_hip']

    # Move origin to hips_center
    origin.location = hips_center.location
    
    # Rotate origin in the xy plane so its x axis crosses the vertical projection of left_hip
    # Obtain left_hip location
    left_hip_location = left_hip.location
    # Calculate left_hip xy coordinates from origin location
    left_hip_x_from_origin  = left_hip_location[0] - origin.location[0]
    left_hip_y_from_origin  = left_hip_location[1] - origin.location[1]
    # Calculate angle from origin x axis to projection of left_hip on xy plane. It will depend if left_hip_x_from_origin is positive or negative
    left_hip_xy_angle_prev  = m.atan(left_hip_y_from_origin / left_hip_x_from_origin)
    left_hip_xy_angle       = left_hip_xy_angle_prev if left_hip_x_from_origin >= 0 else m.radians(180) + left_hip_xy_angle_prev
    # Rotate origin around the z axis to point at left_hip
    origin.rotation_euler[2] = left_hip_xy_angle
    
    # Calculate left_hip z position from origin
    left_hip_z_from_origin = left_hip_location[2] - origin.location[2]
    #left_hip_z_from_origin = abs(left_hip_location[2]) - abs(origin.location[2])
    # Calculate angle from origin local x axis to the position of left_hip on origin xz plane
    left_hip_xz_angle = m.atan(left_hip_z_from_origin / m.sqrt(m.pow(left_hip_x_from_origin,2) + m.pow(left_hip_y_from_origin,2)))

    # Rotate origin around the local y axis to point at left_hip. The angle is multiplied by -1 because is the origin that is rotating
    origin.rotation_euler.rotate_axis("Y", left_hip_xz_angle * -1)
    
    ### Calculate angle in the local yz plane to rotate origin so its z axis crosses the z_align_empty ###
    ### Preferably the trunk_center or left_knee ###
    # Get the z_align_empty object
    z_align_empty = bpy.data.objects[z_align_ref_empty]
    # Get z_align_empty location from origin
    z_align_empty_loc_from_origin = z_align_empty.location - origin.location
    # Get the vector distance
    z_align_empty_from_origin_dist = z_align_empty_loc_from_origin.length
    # Get the location vector normalized
    z_align_empty_loc_from_origin_norm = z_align_empty_loc_from_origin.normalized()
    # Rotate the normalized vector with the current origin rotation
    # Get the matrix of origin euler rotation
    origin_rot_matrix = origin.rotation_euler.to_matrix()
    # Rotate the trunk center location normalized vector by the origin rotation matrix
    z_align_empty_loc_from_origin_norm_rot = z_align_empty_loc_from_origin_norm @ origin_rot_matrix
    # Calculate rotation angle of the trunk center on the origin local yz plane using the rotated normalized vector
    z_align_empty_yz_rot_angle = m.atan(z_align_empty_loc_from_origin_norm_rot[1] / z_align_empty_loc_from_origin_norm_rot[2])

    # Rotate the origin on its local yz plane. The angle is multiply by -1 because its the origin that is rotating
    origin.rotation_euler.rotate_axis("X", (z_align_empty_yz_rot_angle + m.radians(z_align_angle_offset)) * -1)
        
    ### Move the origin along its local z axis to place it at an imaginary "capture ground plane" ###
    ### Preferable be placed at a heel or foot_index level ###
    # Get the ground reference empty object
    ground_empty = bpy.data.objects[ground_ref_empty]
    # Get ground_empty location from origin
    ground_empty_loc_from_origin = ground_empty.location - origin.location
    # Get the vector distance
    ground_empty_from_origin_dist = ground_empty_loc_from_origin.length

    # Get the location vector normalized
    ground_empty_loc_from_origin_norm = ground_empty_loc_from_origin.normalized()
    # Rotate the normalized vector with the current origin rotation
    # Get the matrix of origin euler rotation
    origin_rot_matrix = origin.rotation_euler.to_matrix()
    # Rotate the ground empty location normalized vector by the origin rotation matrix
    ground_empty_loc_from_origin_norm_rot = ground_empty_loc_from_origin_norm @ origin_rot_matrix

    # Calculate the ground empty z position in the origin local axis
    ground_empty_z_in_local_origin = ground_empty_from_origin_dist * ground_empty_loc_from_origin_norm_rot[2]

    ### Move the origin along its local z axis to align it to the ground_empty empty ###

    # Create the translation vector in the origin local axis
    origin_translation_vector = mathutils.Vector([0, 0, (ground_empty_z_in_local_origin + z_translation_offset)])
    # Invert the origin rotation matrix so it converts from local to global space
    origin_rot_matrix.invert()
    # Rotate the origin translation vector with the inversed rotation matrix
    origin_translation_vector_global = origin_translation_vector @ origin_rot_matrix

    # Translate the origin using the translation_vector_global
    origin.location += origin_translation_vector_global

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT') 

    ### Reparent all the capture empties to the origin (empties_parent) ###
    for object in bpy.data.objects:
        if object.type == "EMPTY" and object.name != 'empties_parent' and '_origin' not in object.name and 'center_of_mass' not in object.name and object.name != 'rigid_body_meshes_parent':
            # Select empty
            object.select_set(True)

    # Save the origin world matrix
    origin_location_pre_reset = (origin.location[0], origin.location[1], origin.location[2])
    origin_rotation_pre_reset = (origin.rotation_euler[0], origin.rotation_euler[1], origin.rotation_euler[2])

    # Set the origin active in 3Dview
    bpy.context.view_layer.objects.active = origin
    # Parent selected empties to origin keeping transforms
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    # Reset origin transformation to world origin
    origin.location = mathutils.Vector([0, 0, 0])
    origin.rotation_euler = mathutils.Vector([0, 0, 0])

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # Adjust the position of the finger tracking empties. Move right_hand_wrist (and all its child empties) to match the right_wrist position
    if correct_fingers_empties:
        hand_side = ['right', 'left']

        # Iterate through each scene frame and calculate the position delta from x_hand_wrist to x_wrist and move all the fingers empties by that delta
        for frame in range (scene.frame_start, scene.frame_end):
            # Set scene frame
            scene.frame_set(frame)

            for side in hand_side:
                # Get the position delta
                position_delta      = bpy.data.objects[side + '_wrist'].location - bpy.data.objects[side + '_hand_wrist'].location

                # Translate the hand_wrist empty and its children by the position delta
                translate_empty(empties_dict, side + '_hand_wrist', frame, position_delta)

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

    # Add the hand middle empties if the option is enabled
    if add_hand_middle_empty:

        # Update the empty positions dictionary
        update_empty_positions()

        add_hands_middle_empties()

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['empties_parent'].select_set(True)

    # Change the adjust_empties_executed variable
    adjust_empties_executed = True

def reduce_bone_length_dispersion(interval_variable: str='capture_median', interval_factor: float=0.01, body_height: float=1.75, target_bone: str=''):

    # Get the scene context
    scene = bpy.context.scene

    # Check if the target bone is defined to only update and print what it is necessary
    if target_bone != '':
        # Set the recursivity mode to False to only adjust the target bone
        recursivity = False
        # Update only the target bone head and tail empties positions
        update_empty_positions([virtual_bones[target_bone]['head'], virtual_bones[target_bone]['tail']])
        # Update the information of the target bone
        update_virtual_bones_info(target_bone=target_bone)

    else:
        # Set the recursivity mode to True to adjust the children bones
        recursivity = True
        # Update the empty positions dictionary
        update_empty_positions()
        # Update the information of the virtual bones
        update_virtual_bones_info()

        # Print the current bones length median, standard deviation and coefficient of variation
        print('Current Virtual Bone Information:')
        print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))

        for bone in virtual_bones:

            # Get the statistic values
            current_median  = virtual_bones[bone]['median']
            current_stdev   = virtual_bones[bone]['stdev']
            current_cv      = virtual_bones[bone]['stdev']/virtual_bones[bone]['median']

            print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(current_median*100*10000000)/10000000), str(m.trunc(current_stdev*100*10000000)/10000000), str(m.trunc(current_cv*100*10000)/10000)))

    # Iterate through the lengths array of each bone and check if the length is outside the interval defined by x*stdev with x as a factor
    # If the bone length is outside the interval, adjust the coordinates of the tail empty and its children so the new bone length is at the border of the interval
    empties_positions_corrected = 0

    for bone in virtual_bones:

        # If the target bone is defined, only adjust the length of the target bone
        if target_bone != '':
            if bone != target_bone:
                continue
        
        frame_index = 0

        for length in virtual_bones[bone]['lengths']:
        
            # If the length is equal to nan (bone head or/and tail is nan) then continue with the next length
            if m.isnan(length):
                frame_index += 1
                continue

            # Get the bone median and stdev values
            median  = virtual_bones[bone]['median']
            stdev   = virtual_bones[bone]['stdev']

            # Calculate inferior and superior interval limit depending on interval variable
            if interval_variable == 'capture_median':
                # Fix interval_factor to 1 in case is greater than 1
                if interval_factor > 1:
                    interval_factor = 1
                # Calculate limits
                inferior_limit  = median * (1 - interval_factor)
                superior_limit  = median * (1 + interval_factor)
            elif interval_variable == 'capture_stdev':
                # Fix interval_factor to median/stdev in case is greater than median/stdev
                if interval_factor > (median/stdev):
                    interval_factor = median / stdev
                # Calculate limits
                inferior_limit  = median - interval_factor * stdev
                superior_limit  = median + interval_factor * stdev
            elif interval_variable == 'standard_length':
                # Use the bone standard anthropomorphic dimension relative to the body height
                inferior_limit  = anthropomorphic_dimensions[bone]['dimension'] * body_height * (1 - interval_factor)
                superior_limit  = anthropomorphic_dimensions[bone]['dimension'] * body_height * (1 + interval_factor)

            # Check if bone length is outside the interval
            if length < inferior_limit or length > superior_limit:

                head        = virtual_bones[bone]['head']
                tail        = virtual_bones[bone]['tail']
                # Get vector between the bone's tail and head empties
                head_position   = mathutils.Vector([empty_positions[head]['x'][frame_index], empty_positions[head]['y'][frame_index], empty_positions[head]['z'][frame_index]])
                tail_position   = mathutils.Vector([empty_positions[tail]['x'][frame_index], empty_positions[tail]['y'][frame_index], empty_positions[tail]['z'][frame_index]])
                bone_vector     = tail_position - head_position
                # Get the new bone length depending of the actual length value (interval inferior or superior limit)
                new_length      = inferior_limit if length < inferior_limit else superior_limit
                # Get the normalized bone vector by dividing the bone_vector by its length
                bone_vector_norm = bone_vector / length
                # Get the tail position delta by multiplying the normalized bone vector by the substraction of new_length and length
                position_delta  = bone_vector_norm * (new_length - length)
                # Translate the tail empty and its children by the position delta.
                translate_empty(empties_dict, tail, frame_index, position_delta, recursivity)

                empties_positions_corrected += 1
            
            frame_index += 1
    
    # Only update empty positions and virtual bones info and show statistics if the target bone is not defined
    if target_bone == '':
        # Update the empty positions dictionary
        update_empty_positions()
        # Update the information of the virtual bones
        update_virtual_bones_info()

        # Print the new bones length median, standard deviation and coefficient of variation
        print('New Virtual Bone Information:')
        print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
        for bone in virtual_bones:

            # If the target bone is defined, only print the information of the target bone
            if target_bone != '':
                if bone != target_bone:
                    continue

            # Get the statistic values
            new_median  = virtual_bones[bone]['median']
            new_stdev   = virtual_bones[bone]['stdev']
            new_cv      = virtual_bones[bone]['stdev']/virtual_bones[bone]['median']

            print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(new_median*100*10000000)/10000000), str(m.trunc(new_stdev*100*10000000)/10000000), str(m.trunc(new_cv*100*10000)/10000)))

        print('Total empties positions corrected: ' + str(empties_positions_corrected))
    

# Function to add fingers rotation limits constraints. Starting from the fingers mcp, each hand virtual bone rotation will be
# analysed. If the rotation is outside the limits, the bone tail empty will be translated around the bone head empty.
# The resulting rotation will be just on the border of the limits interval. The rotation analysis will be done separately
# on the local x and z axes of the virtual bone. When an empty is rotated, all of its children empties will be rotated equally recursevily
def add_finger_rotation_limits():
    
    def calculate_bone_axes_from_parent(bone):
        # Calculate the bone's y axis
        bone_y_axis = mathutils.Vector(bpy.data.objects[virtual_bones[bone]['tail']].matrix_world.translation - bpy.data.objects[virtual_bones[bone]['head']].matrix_world.translation)

        # Calculate the difference between the bone's y axis and its parent bone's y axis
        rotation_quat = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_y_axis'].rotation_difference(bone_y_axis)

        # Rotate the parent x and z axes to get the bones local x and z axes
        bone_x_axis = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_x_axis'].copy()
        bone_x_axis.rotate(rotation_quat)
        bone_z_axis = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_z_axis'].copy()
        bone_z_axis.rotate(rotation_quat)

        # Save the vectors in the virtual_bones dictionary
        virtual_bones[bone]['bone_x_axis'] = mathutils.Vector(bone_x_axis)
        virtual_bones[bone]['bone_y_axis'] = mathutils.Vector(bone_y_axis)
        virtual_bones[bone]['bone_z_axis'] = mathutils.Vector(bone_z_axis)

        return
    
    def get_rot_delta(bone, axis):

        # Get the ortogonal axis
        ort_axis = 'z' if axis == 'x' else 'x'

        # Set the bone axis
        bone_axis = virtual_bones[bone]['bone_' + axis + '_axis']
        # Set the parent bone axis
        parent_bone_axis = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_' + axis + '_axis']
        # Set the parent bone ortogonal axis
        parent_bone_ort_axis = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_' + ort_axis + '_axis']

        # Calculate the dot product between the x axes of the bone and its parent bone
        dot_product = bone_axis.dot(parent_bone_axis)

        # Based on the dot product calculate the rotation angle cosine between the axis of the bone and its parent bone
        angle_cosine = dot_product / (bone_axis.magnitude * parent_bone_axis.magnitude)

        # Calculate the angle between the perpendicular vectors in radians
        if angle_cosine > 1:
            angle = m.acos(1)
        elif angle_cosine < -1:
            angle = m.acos(-1)
        else:
            angle = m.acos(angle_cosine)

        # Calculate the cross product between the axis of the bone and its parent bone axis
        cross_product = mathutils.Vector(parent_bone_axis.cross(bone_axis))

        # Calculate the dot product between the cross product and the parent ortogonal axis
        cross_dot_product = cross_product.dot(parent_bone_ort_axis)

        # If the dot product is negative then the rotation angle is negative
        if cross_dot_product < 0:
            angle = -angle

        # Check if the angle is within the rotation limit values.
        # If it is outside, rotate the bone tail empty around the cross product
        # so the angle is on the closest rotation limit.
        # Rotate the bone tail children by the same delta recursively.
        rot_delta = 0

        # Calculate the angle difference between the rotation limit and the x_angle
        if angle < m.radians(virtual_bones[bone]['rot_limit_min_' + axis]):
            rot_delta = m.radians(virtual_bones[bone]['rot_limit_min_' + axis]) - angle
        elif angle > m.radians(virtual_bones[bone]['rot_limit_max_' + axis]):
            rot_delta = m.radians(virtual_bones[bone]['rot_limit_max_' + axis]) - angle

        # Adjust the rotation delta according to the dot product
        if cross_dot_product < 0:
            rot_delta = -rot_delta

        return rot_delta

    # Get the scene context
    scene = bpy.context.scene

    for frame in range (scene.frame_start, scene.frame_end):

        # Set scene frame
        scene.frame_set(frame)

        # Calculate the hand bones origin axes
        for side in ['left', 'right']:
            # y_axis
            hand_y_axis = bpy.data.objects[side + '_hand_middle'].matrix_world.translation - bpy.data.objects[side + '_wrist'].matrix_world.translation
            
            # z_axis
            hand_to_thumb_cmc = bpy.data.objects[side + '_hand_thumb_cmc'].matrix_world.translation - bpy.data.objects[side + '_wrist'].matrix_world.translation
            hand_z_axis = hand_to_thumb_cmc - hand_y_axis * (hand_y_axis.dot(hand_to_thumb_cmc) / hand_y_axis.length_squared)

            # x_axis as the orthogonal vector of the y_axis and z_axis
            hand_x_axis = mathutils.Vector(hand_y_axis.cross(hand_z_axis))

            # Save the vectors in the virtual_bones dictionary
            virtual_bones['hand.' + side[0].upper()]['bone_x_axis'] = mathutils.Vector(hand_x_axis)
            virtual_bones['hand.' + side[0].upper()]['bone_y_axis'] = mathutils.Vector(hand_y_axis)
            virtual_bones['hand.' + side[0].upper()]['bone_z_axis'] = mathutils.Vector(hand_z_axis)

        # Iterate through the virtual bones dictionary and add constraints if the bone has the finger category
        for bone in virtual_bones:

            # If the bone has the hands or fingers category then calculate its origin axes based on its parent bone's axes
            if virtual_bones[bone]['category'] in ['hands', 'fingers']:
                
                calculate_bone_axes_from_parent(bone)

                # If the bone has the fingers category then calculate its origin axes based on its parent bone's axes and rotate the tail empty (and its children) to meet the constraints
                if virtual_bones[bone]['category'] == 'fingers':

                    parent_bone = virtual_bones[bone]['parent_bone']

                    for axis in ['x', 'z']:

                        # Get the rotation delta
                        rot_delta = get_rot_delta(bone, axis)
                        
                        # If the rot_delta is different than 0 then rotate the bone tail empty
                        if rot_delta != 0:
                            
                            # Calculate the rotation matrix axis as the cross products of the bone and parent axes
                            matrix_axis = mathutils.Vector(virtual_bones[parent_bone]['bone_' + axis + '_axis'].cross(virtual_bones[bone]['bone_' + axis + '_axis']))
                            matrix_axis.normalize()
                            
                            # Get the rotation matrix
                            rot_matrix = mathutils.Matrix.Rotation(rot_delta, 4, matrix_axis)

                            # Rotate the virtual bone tail empty
                            rotate_virtual_bone(virtual_bones[bone]['tail'], bpy.data.objects[virtual_bones[bone]['head']].matrix_world.translation, rot_matrix)

                            # Recalculate the bone's y axis
                            bone_y_axis = mathutils.Vector(bpy.data.objects[virtual_bones[bone]['tail']].matrix_world.translation - bpy.data.objects[virtual_bones[bone]['head']].matrix_world.translation)

                            # Calculate the difference between the bone's y axis and its parent bone's y axis
                            rotation_quat = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_y_axis'].rotation_difference(bone_y_axis)

                            # Rotate the parent x and z axes to get the bones local x and z axes
                            bone_x_axis = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_x_axis'].copy()
                            bone_x_axis.rotate(rotation_quat)
                            bone_z_axis = virtual_bones[virtual_bones[bone]['parent_bone']]['bone_z_axis'].copy()
                            bone_z_axis.rotate(rotation_quat)

                            # Save the vectors in the virtual_bones dictionary
                            virtual_bones[bone]['bone_x_axis'] = mathutils.Vector(bone_x_axis)
                            virtual_bones[bone]['bone_y_axis'] = mathutils.Vector(bone_y_axis)
                            virtual_bones[bone]['bone_z_axis'] = mathutils.Vector(bone_z_axis)

    # Reset the scene frame
    scene.frame_set(scene.frame_start)


# Function to apply different butterworth filters to the empty positions
def apply_butterworth_filters(global_filter_categories: list=[],
                              global_cutoff_frequencies: dict={},
                              local_filter_categories: list=[],
                              local_cutoff_frequencies: dict={},
                              local_filter_origins: dict={},
                              interval_variable: str='standard_length',
                              interval_factor: float=0,
                              body_height: float=1.75,):

    # Get the scene context
    scene = bpy.context.scene
    
    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # Apply global filters
    if len(global_filter_categories) > 0:
        
        # Check if all the categories have the same cutoff frequency
        if all(value == list(global_cutoff_frequencies.values())[0] for value in global_cutoff_frequencies.values()):
            # Select all the empties that are in the categories
            for empty in empties_dict:
                if empties_dict[empty]['category'] in global_filter_categories:
                    # Select the empty
                    bpy.data.objects[empty].select_set(True)

            # Save the current area
            current_area = bpy.context.area.type

            # Change the current area to the graph editor
            bpy.context.area.type = "GRAPH_EDITOR"

            # Apply the butterworth filter
            bpy.ops.graph.butterworth_smooth(cutoff_frequency=list(global_cutoff_frequencies.values())[0],
                                            filter_order=4,
                                            samples_per_frame=1,
                                            blend=1.0,
                                            blend_in_out=1)
            
            # Restore the area
            bpy.context.area.type = current_area

            # Deselect all objects
            for object in bpy.data.objects:
                object.select_set(False)

        else:
            #  Iterate through the categories dictionary
            for category in global_filter_categories:
                # Iterate through the empties_dict
                for empty in empties_dict:
                    # If the empty is in the category
                    if empties_dict[empty]['category'] == category:
                        # Select the empty
                        bpy.data.objects[empty].select_set(True)

                # Save the current area
                current_area = bpy.context.area.type

                # Change the current area to the graph editor
                bpy.context.area.type = "GRAPH_EDITOR"

                # Apply the butterworth filter
                bpy.ops.graph.butterworth_smooth(cutoff_frequency=global_cutoff_frequencies[category],
                                                filter_order=4,
                                                samples_per_frame=1,
                                                blend=1.0,
                                                blend_in_out=1)
                
                # Restore the area
                bpy.context.area.type = current_area

                # Deselect all objects
                for object in bpy.data.objects:
                    object.select_set(False)

    # Apply local filters
    if len(local_filter_categories) > 0:

        # Iterate through the local filter categories
        for category in local_filter_categories:

            # Update the empties position dictionary
            update_empty_positions()

            # Prepare the butterworth filter parameters
            normalized_cutoff = local_cutoff_frequencies[category] / (0.5 * 60)

            # Create Butterworth filter coefficients
            b, a = butter(4, normalized_cutoff, btype='low', analog=False, output='ba')

            # Iterate through the empties_dict
            for empty in empties_dict:
                # If the empty is in the category
                if empties_dict[empty]['category'] == category:
                    #  Get the origin of the filter. Replace the side prefix with the empty's side
                    filter_origin = local_filter_origins[category]
                    if 'side' in filter_origin:
                        if 'right' in empty:
                            filter_origin = filter_origin.replace('side', 'right')
                        elif 'left' in empty:
                            filter_origin = filter_origin.replace('side', 'left')

                    # Get the local position lists as the difference between the empty and filter origin for each frame
                    local_x = [empty_pos_x - filter_origin_pos_x for empty_pos_x, filter_origin_pos_x in zip(empty_positions[empty]['x'], empty_positions[filter_origin]['x'])]
                    local_y = [empty_pos_y - filter_origin_pos_y for empty_pos_y, filter_origin_pos_y in zip(empty_positions[empty]['y'], empty_positions[filter_origin]['y'])]
                    local_z = [empty_pos_z - filter_origin_pos_z for empty_pos_z, filter_origin_pos_z in zip(empty_positions[empty]['z'], empty_positions[filter_origin]['z'])]

                    # Filter each position delta list
                    filtered_local_x = filtfilt(b, a, local_x)
                    filtered_local_y = filtfilt(b, a, local_y)
                    filtered_local_z = filtfilt(b, a, local_z)

                    # Translate the empty in the animation location curve
                    for frame_index in range(scene.frame_start, len(filtered_local_x)):
                        # Get the delta vector between the unfiltered and filtered local position
                        delta_pos = [filtered_local_x[frame_index] - local_x[frame_index],
                                     filtered_local_y[frame_index] - local_y[frame_index],
                                     filtered_local_z[frame_index] - local_z[frame_index]]
                        # Check if the filtered delta is not equal to the [0, 0, 0] vector
                        if delta_pos != [0, 0, 0]:
                            # Translate the empty
                            translate_empty(empties_dict, empty, frame_index, delta_pos, recursivity=False)

    # Reduce the bone length dispersion
    reduce_bone_length_dispersion(interval_variable=interval_variable, interval_factor=interval_factor, body_height=body_height, target_bone='')

def add_rig(add_rig_method: str='using_rigify',
            armature_name: str='armature_freemocap',
            pose_name: str='freemocap_tpose',
            keep_symmetry: bool=False,
            add_fingers_constraints: bool=False,
            add_ik_constraints: bool=False,
            ik_transition_threshold: float=0.5,
            use_limit_rotation: bool=False,
            clear_constraints: bool=False):

    # Get the scene context
    scene = bpy.context.scene

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # If there is an existing metarig, delete it
    try:
        print('Deleting previous metarigs...')
        for object in bpy.data.objects:
            if object.type == "ARMATURE":
                # pass
                bpy.data.objects.remove(object, do_unlink=True)
    except AttributeError:
        print('No existing metarigs to delete')

    if add_rig_method == 'bone_by_bone':
        print('Adding rig with bone by bone method...')

        # Get the armature and pose types
        armature = globals()[armature_name]
        pose = globals()[pose_name]

        # Update the empty positions dictionary
        update_empty_positions()

        # Update the information of the virtual bones
        update_virtual_bones_info()

        # Get rig height as the sum of the major bones length in a standing position. Assume foot declination angle of 23º
        avg_ankle_projection_length = (m.sin(m.radians(23)) * virtual_bones['foot.R']['median'] + m.sin(m.radians(23)) * virtual_bones['foot.L']['median']) / 2
        avg_shin_length = (virtual_bones['shin.R']['median'] + virtual_bones['shin.L']['median']) / 2
        avg_thigh_length = (virtual_bones['thigh.R']['median'] + virtual_bones['thigh.L']['median']) / 2

        # Add the armature
        bpy.ops.object.armature_add(
            enter_editmode=False,
            align='WORLD',
            location=(0, 0, 0),
        )

        # Rename the armature
        bpy.data.armatures[0].name = 'root'
        # Get reference to armature
        rig = bpy.data.objects['Armature']
        # Rename the rig object to pelvis
        rig.name = 'root'
        # Get reference to the renamed armature
        rig = bpy.data.objects['root']

        # Change to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Remove the default bone
        rig.data.edit_bones.remove(rig.data.edit_bones['Bone'])

        # Get the inverse bone_map_dict
        inv_bone_name_map = {value: key for key, value in bone_name_map[armature_name].items()}

        # Iterate over the armature dictionary
        for bone in armature:

            # Get the reference to the parent of the bone if its not root
            parent_name = armature[bone]['parent_bone']
            if parent_name != 'root':
                parent_bone = rig.data.edit_bones[parent_name]

            # Add the new bone
            rig_bone = rig.data.edit_bones.new(bone)

            # Set the bone head position
            if bone in ('pelvis'):
                rig_bone.head = mathutils.Vector(
                    [
                        0,
                        0,
                        avg_ankle_projection_length
                        + avg_shin_length
                        + avg_thigh_length,
                    ]
                )
            else:
                # Set the bone position relative to its parent
                if armature[bone]['parent_position'] == 'head':
                    rig_bone.head = parent_bone.head
                elif armature[bone]['parent_position'] == 'tail':
                    rig_bone.head = parent_bone.tail

            # Get the bone vector
            if inv_bone_name_map[bone] not in virtual_bones:
                bone_vector = mathutils.Vector(
                    [0, 0, armature[bone]['default_length']]
                )
            else:
                bone_vector = mathutils.Vector(
                    [0, 0, virtual_bones[inv_bone_name_map[bone]]['median']]
                )

            # Get rot_vector
            # rot_vector = mathutils.Vector(pose[bone]['rotation'])
            # Get the rotation matrix
            rotation_matrix = mathutils.Euler(
                mathutils.Vector(pose[bone]['rotation']),
                'XYZ',
            ).to_matrix()

            # Rotate the bone vector
            # rotated_bone_vector = rotation_matrix @ bone_vector

            rig_bone.tail = (
                    rig_bone.head
                    + rotation_matrix @ bone_vector
                    )

            # Set the bone tail using its orientation and length.
            # Rotate the bone vector in each axis separately
            # for axis in (0, 1, 2):
            #     rot_vector = mathutils.Vector([
            #         pose[bone]['rotation'][0] if axis == 0 else 0,
            #         pose[bone]['rotation'][1] if axis == 1 else 0,
            #         pose[bone]['rotation'][2] if axis == 2 else 0
            #         ])

            #     rotation_matrix = mathutils.Matrix.Rotation(
            #         rot_vector.length,
            #         4,
            #         rot_vector.normalized()
            #         )

            #     rig_bone.tail = (
            #         rig_bone.head
            #         + rotation_matrix @ bone_vector
            #         )

            #     # Update the bone vector
            #     bone_vector = rig_bone.tail - rig_bone.head

            # Assign the roll to the bone
            rig_bone.roll = pose[bone]['roll']

            # Parent the bone if its parent exists
            if parent_name != 'root':
                rig_bone.parent = parent_bone
                rig_bone.use_connect = armature[bone]['connected']

        # Special armature conditions
        if armature_name == 'armature_ue_metahuman_simple':
            # Change parents of thigh bones
            rig.data.edit_bones['thigh_r'].use_connect = False
            rig.data.edit_bones['thigh_l'].use_connect = False
            rig.data.edit_bones['thigh_r'].parent = rig.data.edit_bones['pelvis']
            rig.data.edit_bones['thigh_l'].parent = rig.data.edit_bones['pelvis']


        # Add the ik bones if specified
        if add_ik_constraints:
            for ik_control in ik_control_bones:
                ik_bone = rig.data.edit_bones.new(ik_control)
                ik_bone.head = rig.data.edit_bones[bone_name_map[armature_name][ik_control_bones[ik_control]['controlled_bone']]].head
                ik_bone.tail = ik_bone.head + mathutils.Vector(
                    ik_control_bones[ik_control]['tail_relative_position'])
            for ik_pole in ik_pole_bones:
                ik_bone = rig.data.edit_bones.new(ik_pole)
                ik_bone.head = ik_pole_bones[ik_pole]['head_position']
                ik_bone.tail = ik_pole_bones[ik_pole]['tail_position']



    elif add_rig_method == 'using_rigify':
        # Add normal human armature
        bpy.ops.object.armature_human_metarig_add()
        # Rename metarig armature to "root"
        bpy.data.armatures[0].name = "root"
        # Get reference to armature
        rig = bpy.data.objects['metarig']
        # Rename the rig object to root
        rig.name = "root"
        # Get reference to the renamed armature
        rig = bpy.data.objects['root']

        # Add the rig setting the bones length as the median length across all the frames
        print('Adding rig with median length method...')

        # Update the empty positions dictionary
        update_empty_positions()

        # Update the information of the virtual bones
        update_virtual_bones_info()

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        # Select the only the rig
        rig.select_set(True)

        # Get rig height as the sum of the major bones length in a standing position. Assume foot declination angle of 23º
        avg_ankle_projection_length     = (m.sin(m.radians(23)) * virtual_bones['foot.R']['median'] + m.sin(m.radians(23)) * virtual_bones['foot.L']['median']) / 2
        avg_shin_length                 = (virtual_bones['shin.R']['median'] + virtual_bones['shin.L']['median']) / 2
        avg_thigh_length                = (virtual_bones['thigh.R']['median'] + virtual_bones['thigh.L']['median']) / 2

        rig_height = avg_ankle_projection_length + avg_shin_length + avg_thigh_length + virtual_bones['spine']['median'] + virtual_bones['spine.001']['median'] + virtual_bones['neck']['median']
        
        # Calculate new rig proportion
        rig_new_proportion = rig_height / rig.dimensions.z
        # Scale the rig by the new proportion
        rig.scale = (rig_new_proportion, rig_new_proportion, rig_new_proportion)

        # Apply transformations to rig (scale must be (1, 1, 1) so it doesn't export badly
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Get references to the different rig bones
        bpy.ops.object.mode_set(mode='EDIT')

        spine           = rig.data.edit_bones['spine']
        spine_003       = rig.data.edit_bones['spine.003']
        spine_004       = rig.data.edit_bones['spine.004']
        spine_005       = rig.data.edit_bones['spine.005']
        spine_006       = rig.data.edit_bones['spine.006']
        face            = rig.data.edit_bones['face']
        nose            = rig.data.edit_bones['nose']
        breast_R        = rig.data.edit_bones['breast.R']
        breast_L        = rig.data.edit_bones['breast.L']
        shoulder_R      = rig.data.edit_bones['shoulder.R']
        shoulder_L      = rig.data.edit_bones['shoulder.L']
        upper_arm_R     = rig.data.edit_bones['upper_arm.R']
        upper_arm_L     = rig.data.edit_bones['upper_arm.L']
        forearm_R       = rig.data.edit_bones['forearm.R']
        forearm_L       = rig.data.edit_bones['forearm.L']
        hand_R          = rig.data.edit_bones['hand.R']
        hand_L          = rig.data.edit_bones['hand.L']
        pelvis_R        = rig.data.edit_bones['pelvis.R']
        pelvis_L        = rig.data.edit_bones['pelvis.L']
        thigh_R         = rig.data.edit_bones['thigh.R']
        thigh_L         = rig.data.edit_bones['thigh.L']
        shin_R          = rig.data.edit_bones['shin.R']
        shin_L          = rig.data.edit_bones['shin.L']
        foot_R          = rig.data.edit_bones['foot.R']
        foot_L          = rig.data.edit_bones['foot.L']
        toe_R           = rig.data.edit_bones['toe.R']
        toe_L           = rig.data.edit_bones['toe.L']
        heel_02_R       = rig.data.edit_bones['heel.02.R']
        heel_02_L       = rig.data.edit_bones['heel.02.L']

        # Get the hips_center z position as the sum of heel, shin and thigh lengths
        hips_center_z_pos = avg_ankle_projection_length + avg_shin_length + avg_thigh_length

        # Move the spine and pelvis bone heads to the point (0, 0, hips_center_z_pos)
        spine.head      = (0, 0, hips_center_z_pos)
        pelvis_R.head   = (0, 0, hips_center_z_pos)
        pelvis_L.head   = (0, 0, hips_center_z_pos)

        # Calculate the average length of the pelvis bones
        avg_pelvis_length = (virtual_bones['pelvis.R']['median'] + virtual_bones['pelvis.L']['median']) / 2

        # Set the pelvis bones length based on the keep symmetry parameter
        pelvis_R_length  = avg_pelvis_length if keep_symmetry else virtual_bones['pelvis.R']['median']
        pelvis_L_length  = avg_pelvis_length if keep_symmetry else virtual_bones['pelvis.L']['median']

        # Align the pelvis bone tails to the hips center
        pelvis_R.tail   = (-pelvis_R_length, 0, hips_center_z_pos)
        pelvis_L.tail   = (pelvis_L_length, 0, hips_center_z_pos)
        # Reset pelvis bones rotations
        pelvis_R.roll   = 0
        pelvis_L.roll   = 0

        # Move thighs bone head to the position of corresponding pelvis bone tail
        thigh_R.head    = (-pelvis_R_length, 0, hips_center_z_pos)
        thigh_L.head    = (pelvis_L_length, 0, hips_center_z_pos)

        # Set the thigh bones length based on the keep symmetry parameter
        thigh_R_length  = avg_thigh_length if keep_symmetry else virtual_bones['thigh.R']['median']
        thigh_L_length  = avg_thigh_length if keep_symmetry else virtual_bones['thigh.L']['median']

        # Align the thighs bone tail to the bone head
        thigh_R.tail    = (-pelvis_R_length, 0, hips_center_z_pos - thigh_R_length)
        thigh_L.tail    = (pelvis_L_length, 0, hips_center_z_pos - thigh_L_length)

        # Set the shin bones length based on the keep symmetry parameter
        shin_R_length   = avg_shin_length if keep_symmetry else virtual_bones['shin.R']['median']
        shin_L_length   = avg_shin_length if keep_symmetry else virtual_bones['shin.L']['median']

        # Align the shin bones to the thigh bones
        shin_R.tail     = (-pelvis_R_length, 0, hips_center_z_pos - thigh_R_length - shin_R_length)
        shin_L.tail     = (pelvis_L_length, 0, hips_center_z_pos - thigh_L_length - shin_L_length)

        # Remove the toe bones
        rig.data.edit_bones.remove(rig.data.edit_bones['toe.R'])
        rig.data.edit_bones.remove(rig.data.edit_bones['toe.L'])

        # Move the foot bones tail to adjust their length depending on keep symmetry and also form a 23º degree with the horizontal plane
        avg_foot_length = (virtual_bones['foot.R']['median'] + virtual_bones['foot.L']['median']) / 2

        # Set the foot bones length based on the keep symmetry parameter
        foot_R_length   = avg_foot_length if keep_symmetry else virtual_bones['foot.R']['median']
        foot_L_length   = avg_foot_length if keep_symmetry else virtual_bones['foot.L']['median']

        foot_R.tail     = (-pelvis_R_length, -foot_R_length * m.cos(m.radians(23)), foot_R.head[2] - foot_R_length * m.sin(m.radians(23)))
        foot_L.tail     = (pelvis_L_length, -foot_L_length * m.cos(m.radians(23)), foot_L.head[2] - foot_L_length * m.sin(m.radians(23)))

        # Move the heel bones so their head is aligned with the ankle on the x axis
        avg_heel_length    = (virtual_bones['heel.02.R']['median'] + virtual_bones['heel.02.L']['median']) / 2

        # Set the heel bones length based on the keep symmetry parameter
        heel_02_R_length   = avg_heel_length if keep_symmetry else virtual_bones['heel.02.R']['median']
        heel_02_L_length   = avg_heel_length if keep_symmetry else virtual_bones['heel.02.L']['median']

        heel_02_R.head      = (-pelvis_R_length, heel_02_R.head[1], heel_02_R.head[2])
        heel_02_R.tail      = (-pelvis_R_length - heel_02_R_length, heel_02_R.tail[1], heel_02_R.tail[2])
        heel_02_L.head      = (pelvis_L_length, heel_02_L.head[1], heel_02_L.head[2])
        heel_02_L.tail      = (pelvis_L_length + heel_02_L_length, heel_02_L.tail[1], heel_02_L.tail[2])

        # Make the heel bones be connected with the shin bones
        heel_02_R.parent        = shin_R
        heel_02_R.use_connect   = True
        heel_02_L.parent        = shin_L
        heel_02_L.use_connect   = True

        # Add a pelvis bone to the root and then make it the parent of spine, pelvis.R and pelvis.L bones
        pelvis = rig.data.edit_bones.new('pelvis')
        pelvis.head = spine.head
        pelvis.tail = spine.head + mathutils.Vector([0, 0.1, 0])

        # Change the spine, pelvis.R, pelvis.L, thigh.R and thigh.L bones parents
        pelvis_R.parent         = pelvis
        pelvis_R.use_connect    = False
        pelvis_L.parent         = pelvis
        pelvis_L.use_connect    = False
        thigh_R.parent          = pelvis
        thigh_R.use_connect     = False
        thigh_L.parent          = pelvis
        thigh_L.use_connect     = False
        spine.parent            = pelvis
        spine.use_connect       = False

        # Change parent of spine.003 bone to spine to erase bones spine.001 and spine.002
        spine_003.parent        = spine
        spine_003.use_connect   = True
        # Remove spine.001 and spine.002 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.001'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.002'])

        # Rename spine.003 to spine.001
        rig.data.edit_bones['spine.003'].name = "spine.001"
        spine_001 = rig.data.edit_bones['spine.001']

        # Adjust the spine bone length and align it vertically
        spine.tail = (spine.head[0], spine.head[1], spine.head[2] + virtual_bones['spine']['median'])

        # Adjust the spine.001 bone length and align it vertically
        spine_001.tail = (spine_001.head[0], spine_001.head[1], spine_001.head[2] + virtual_bones['spine.001']['median'])

        # Calculate the shoulders head z offset from the spine.001 tail. This to raise the shoulders and breasts by that offset
        shoulder_z_offset = spine_001.tail[2] - shoulder_R.head[2]

        # Raise breasts and shoulders by the z offset
        breast_R.head[2]    += shoulder_z_offset
        breast_R.tail[2]    += shoulder_z_offset
        breast_L.head[2]    += shoulder_z_offset
        breast_L.tail[2]    += shoulder_z_offset
        shoulder_R.head[2]  += shoulder_z_offset
        shoulder_R.tail[2]  += shoulder_z_offset
        shoulder_L.head[2]  += shoulder_z_offset
        shoulder_L.tail[2]  += shoulder_z_offset

        # Get average shoulder length
        avg_shoulder_length = (virtual_bones['shoulder.R']['median'] + virtual_bones['shoulder.L']['median']) / 2

        # Set the shoulder bones length based on the keep symmetry parameter
        shoulder_R_length   = avg_shoulder_length if keep_symmetry else virtual_bones['shoulder.R']['median']
        shoulder_L_length   = avg_shoulder_length if keep_symmetry else virtual_bones['shoulder.L']['median']

        # Move the shoulder tail in the x axis
        shoulder_R.tail[0] = spine_001.tail[0] - shoulder_R_length
        shoulder_L.tail[0] = spine_001.tail[0] + shoulder_L_length

        # Calculate the upper_arms head x and z offset from the shoulder_R tail. This to raise and adjust the arms and hands by that offset
        upper_arm_R_x_offset = shoulder_R.tail[0] - upper_arm_R.head[0]
        upper_arm_R_z_offset = spine_001.tail[2] - upper_arm_R.head[2]
        upper_arm_L_x_offset = shoulder_L.tail[0] - upper_arm_L.head[0]
        upper_arm_L_z_offset = spine_001.tail[2] - upper_arm_L.head[2]
        
        upper_arm_R.head[2] += upper_arm_R_z_offset
        upper_arm_R.tail[2] += upper_arm_R_z_offset
        upper_arm_R.head[0] += upper_arm_R_x_offset
        upper_arm_R.tail[0] += upper_arm_R_x_offset
        for bone in upper_arm_R.children_recursive:
            if not bone.use_connect:
                bone.head[2] += upper_arm_R_z_offset
                bone.tail[2] += upper_arm_R_z_offset
                bone.head[0] += upper_arm_R_x_offset
                bone.tail[0] += upper_arm_R_x_offset
            else:
                bone.tail[2] += upper_arm_R_z_offset
                bone.tail[0] += upper_arm_R_x_offset
                
        upper_arm_L.head[2] += upper_arm_L_z_offset
        upper_arm_L.tail[2] += upper_arm_L_z_offset
        upper_arm_L.head[0] += upper_arm_L_x_offset
        upper_arm_L.tail[0] += upper_arm_L_x_offset
        for bone in upper_arm_L.children_recursive:
            if not bone.use_connect:
                bone.head[2] += upper_arm_L_z_offset
                bone.tail[2] += upper_arm_L_z_offset
                bone.head[0] += upper_arm_L_x_offset
                bone.tail[0] += upper_arm_L_x_offset
            else:
                bone.tail[2] += upper_arm_L_z_offset
                bone.tail[0] += upper_arm_L_x_offset

        # Align the y position of breasts, shoulders, arms and hands to the y position of the spine.001 tail
        # Calculate the breasts head y offset from the spine.001 tail
        breast_y_offset = spine_001.tail[1] - breast_R.head[1]
        # Move breast by the y offset
        breast_R.head[1] += breast_y_offset
        breast_R.tail[1] += breast_y_offset
        breast_L.head[1] += breast_y_offset
        breast_L.tail[1] += breast_y_offset

        # Temporarily remove breast bones. (Comment these lines if breast bones are needed)
        rig.data.edit_bones.remove(rig.data.edit_bones[breast_R.name])
        rig.data.edit_bones.remove(rig.data.edit_bones[breast_L.name])

        # Set the y position to which the arms bones will be aligned
        arms_bones_y_pos = spine_001.tail[1]
        # Move shoulders on y axis and also move shoulders head to the center at x=0 , 
        shoulder_R.head[1] = arms_bones_y_pos
        shoulder_R.head[0] = 0
        shoulder_R.tail[1] = arms_bones_y_pos
        shoulder_L.head[1] = arms_bones_y_pos
        shoulder_L.head[0] = 0
        shoulder_L.tail[1] = arms_bones_y_pos

        # Move upper_arm and forearm
        upper_arm_R.head[1] = arms_bones_y_pos
        upper_arm_R.tail[1] = arms_bones_y_pos
        upper_arm_L.head[1] = arms_bones_y_pos
        upper_arm_L.tail[1] = arms_bones_y_pos

        # Calculate hand head y offset to arms_bones_y_pos to move the whole hand
        hand_R_y_offset = arms_bones_y_pos - hand_R.head[1]
        hand_L_y_offset = arms_bones_y_pos - hand_L.head[1]

        # Move hands and its children by the y offset (forearm tail is moved by hand head)
        hand_R.head[1] += hand_R_y_offset
        hand_R.tail[1] += hand_R_y_offset
        for bone in hand_R.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_R_y_offset
                bone.tail[1] += hand_R_y_offset
            else:
                bone.tail[1] += hand_R_y_offset
                
        hand_L.head[1] += hand_L_y_offset
        hand_L.tail[1] += hand_L_y_offset
        for bone in hand_L.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_L_y_offset
                bone.tail[1] += hand_L_y_offset
            else:
                bone.tail[1] += hand_L_y_offset

        # Connect the unparented bones
        shoulder_R.use_connect = True
        shoulder_L.use_connect = True
        upper_arm_R.use_connect = True
        upper_arm_L.use_connect = True

        # Change to Pose Mode to rotate the arms and make a T Pose for posterior retargeting
        bpy.ops.object.mode_set(mode='POSE')
        pose_upper_arm_R = rig.pose.bones['upper_arm.R']
        pose_upper_arm_R.rotation_mode  = 'XYZ'
        pose_upper_arm_R.rotation_euler = (0,m.radians(-7),m.radians(-29))
        pose_upper_arm_R.rotation_mode  = 'QUATERNION'
        pose_upper_arm_L = rig.pose.bones['upper_arm.L']
        pose_upper_arm_L.rotation_mode  = 'XYZ'
        pose_upper_arm_L.rotation_euler = (0,m.radians(7),m.radians(29))
        pose_upper_arm_L.rotation_mode  = 'QUATERNION'
        pose_forearm_R = rig.pose.bones['forearm.R']
        pose_forearm_R.rotation_mode    = 'XYZ'
        pose_forearm_R.rotation_euler   = (0,0,m.radians(-4))
        pose_forearm_R.rotation_mode    = 'QUATERNION'
        pose_forearm_L = rig.pose.bones['forearm.L']
        pose_forearm_L.rotation_mode    = 'XYZ'
        pose_forearm_L.rotation_euler   = (0,0,m.radians(4))
        pose_forearm_L.rotation_mode    = 'QUATERNION'
        pose_hand_R = rig.pose.bones['hand.R']
        pose_hand_R.rotation_mode    = 'XYZ'
        pose_hand_R.rotation_euler   = (m.radians(-5.7),0,m.radians(-3.7))
        pose_hand_R.rotation_mode    = 'QUATERNION'
        pose_hand_L = rig.pose.bones['hand.L']
        pose_hand_L.rotation_mode    = 'XYZ'
        pose_hand_L.rotation_euler   = (m.radians(-5.7),0,m.radians(3.7))
        pose_hand_L.rotation_mode    = 'QUATERNION'
        pose_thigh_R = rig.pose.bones['thigh.R']
        pose_thigh_R.rotation_mode    = 'XYZ'
        pose_thigh_R.rotation_euler   = (0,0,m.radians(3))
        pose_thigh_R.rotation_mode    = 'QUATERNION'
        pose_foot_R = rig.pose.bones['foot.R']
        pose_foot_R.rotation_mode    = 'XYZ'
        pose_foot_R.rotation_euler   = (0,0,m.radians(4))
        pose_foot_R.rotation_mode    = 'QUATERNION'
        pose_thigh_L = rig.pose.bones['thigh.L']
        pose_thigh_L.rotation_mode    = 'XYZ'
        pose_thigh_L.rotation_euler   = (0,0,m.radians(-3))
        pose_thigh_L.rotation_mode    = 'QUATERNION'
        pose_foot_L = rig.pose.bones['foot.L']
        pose_foot_L.rotation_mode    = 'XYZ'
        pose_foot_L.rotation_euler   = (0,0,m.radians(-4))
        pose_foot_L.rotation_mode    = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Get new bone references
        upper_arm_R     = rig.data.edit_bones['upper_arm.R']
        upper_arm_L     = rig.data.edit_bones['upper_arm.L']
        forearm_R       = rig.data.edit_bones['forearm.R']
        forearm_L       = rig.data.edit_bones['forearm.L']
        hand_R          = rig.data.edit_bones['hand.R']
        hand_L          = rig.data.edit_bones['hand.L']        

        # Get average upperarm length
        avg_upper_arm_length = (virtual_bones['upper_arm.R']['median'] + virtual_bones['upper_arm.L']['median']) / 2

        # Set the upperarm bones length based on the keep symmetry parameter
        upper_arm_R_length   = avg_upper_arm_length if keep_symmetry else virtual_bones['upper_arm.R']['median']
        upper_arm_L_length   = avg_upper_arm_length if keep_symmetry else virtual_bones['upper_arm.L']['median']

        # Move the upper_arm tail in the x axis
        upper_arm_R.tail[0] = upper_arm_R.head[0] - upper_arm_R_length
        upper_arm_L.tail[0] = upper_arm_L.head[0] + upper_arm_L_length

        # Get average forearm length
        avg_forearm_length = (virtual_bones['forearm.R']['median'] + virtual_bones['forearm.L']['median']) / 2

        # Set the forearm bones length based on the keep symmetry parameter
        forearm_R_length   = avg_forearm_length if keep_symmetry else virtual_bones['forearm.R']['median']
        forearm_L_length   = avg_forearm_length if keep_symmetry else virtual_bones['forearm.L']['median']

        # Calculate the x axis offset of the current forearm tail x position and the forearm head x position plus the calculated forearm length
        # This is to move the forearm tail and all the hand bones
        forearm_R_tail_x_offset = (forearm_R.head[0] - forearm_R_length) - forearm_R.tail[0]
        forearm_L_tail_x_offset = (forearm_L.head[0] + forearm_L_length) - forearm_L.tail[0]

        # Move forearms tail and its children by the x offset
        forearm_R.tail[0] += forearm_R_tail_x_offset
        for bone in forearm_R.children_recursive:
            if not bone.use_connect:
                bone.head[0] += forearm_R_tail_x_offset
                bone.tail[0] += forearm_R_tail_x_offset
            else:
                bone.tail[0] += forearm_R_tail_x_offset
                
        forearm_L.tail[0] += forearm_L_tail_x_offset
        for bone in forearm_L.children_recursive:
            if not bone.use_connect:
                bone.head[0] += forearm_L_tail_x_offset
                bone.tail[0] += forearm_L_tail_x_offset
            else:
                bone.tail[0] += forearm_L_tail_x_offset

        # Get average hand length
        avg_hand_length = (virtual_bones['hand.R']['median'] + virtual_bones['hand.L']['median']) / 2

        # Set the forearm bones length based on the keep symmetry parameter
        hand_R_length   = avg_hand_length if keep_symmetry else virtual_bones['hand.R']['median']
        hand_L_length   = avg_hand_length if keep_symmetry else virtual_bones['hand.L']['median']

        # Move hands tail to match the average length
        hand_R.tail[0] = hand_R.head[0] - hand_R_length
        hand_L.tail[0] = hand_L.head[0] + hand_L_length

        ### Adjust the position of the neck, head and face bones ###
        spine_001   = rig.data.edit_bones['spine.001']
        spine_004   = rig.data.edit_bones['spine.004']
        nose        = rig.data.edit_bones['nose']
        nose_001    = rig.data.edit_bones['nose.001']

        # Set spine.004 bone head position equal to the spine.001 tail
        spine_004.head = (spine_001.tail[0], spine_001.tail[1], spine_001.tail[2])

        # Change spine.004 tail position values
        spine_004.tail = (spine_004.head[0], spine_004.head[1], spine_004.head[2] + virtual_bones['neck']['median'])

        # Change the parent of the face bone for the spine.004 bone
        face = rig.data.edit_bones['face']
        face.parent = spine_004
        face.use_connect = False

        # Remove spine.005 and spine.006 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.005'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.006'])

        # Calculate the y and z offset of the nose.001 bone tail using the imaginary face bone. Assume a 18º of declination angle
        nose_y_offset = -virtual_bones['face']['median'] * m.cos(m.radians(18)) - nose_001.tail[1]
        nose_z_offset = (spine_004.tail[2] - virtual_bones['face']['median'] * m.sin(m.radians(18))) - nose_001.tail[2]
        
        # Move the face bone on the z axis using the calculated offset
        face.head[2] += nose_z_offset
        face.tail[2] += nose_z_offset

        # Move on the y and z axis the children bones from the face bone using the calculated offsets
        for bone in face.children_recursive:
            if not bone.use_connect:
                bone.head[1] += nose_y_offset
                bone.tail[1] += nose_y_offset
                bone.head[2] += nose_z_offset
                bone.tail[2] += nose_z_offset
            else:
                bone.tail[1] += nose_y_offset
                bone.tail[2] += nose_z_offset
                
        # Move the face bone head to the spine.004 tail
        face.head[1] = spine_004.tail[1]
        face.head[2] = spine_004.tail[2]
        # Move the face bone tail to point 18º down (towards nose bone tip)
        face.tail[1] = face.head[1] - (virtual_bones['face']['median'] * m.cos(m.radians(18)) / 2)
        face.tail[2] = face.head[2] - (virtual_bones['face']['median'] * m.sin(m.radians(18)) / 2)

        # Connect the spine.004 bone to the spine.001 bone
        spine_004.use_connect = True
        # Rename spine.004 to neck
        rig.data.edit_bones['spine.004'].name = "neck"

        # Rotate the spine and neck bones to complete the TPOSE
        bpy.ops.object.mode_set(mode='POSE')

        pose_spine = rig.pose.bones['spine']
        pose_spine.rotation_mode    = 'XYZ'
        pose_spine.rotation_euler   = (m.radians(3), 0, 0)
        pose_spine.rotation_mode    = 'QUATERNION'
        pose_spine_001 = rig.pose.bones['spine.001']
        pose_spine_001.rotation_mode    = 'XYZ'
        pose_spine_001.rotation_euler   = (m.radians(-10), 0, 0)
        pose_spine_001.rotation_mode    = 'QUATERNION'
        pose_neck = rig.pose.bones['neck']
        pose_neck.rotation_mode    = 'XYZ'
        pose_neck.rotation_euler   = (m.radians(6), 0, 0)
        pose_neck.rotation_mode    = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Adjust the fingers

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Get new bone references
        hand_R          = rig.data.edit_bones['hand.R']
        hand_L          = rig.data.edit_bones['hand.L']
        palm_01_R       = rig.data.edit_bones['palm.01.R']
        palm_01_L       = rig.data.edit_bones['palm.01.L']
        palm_02_R       = rig.data.edit_bones['palm.02.R']
        palm_02_L       = rig.data.edit_bones['palm.02.L']
        palm_03_R       = rig.data.edit_bones['palm.03.R']
        palm_03_L       = rig.data.edit_bones['palm.03.L']
        palm_04_R       = rig.data.edit_bones['palm.04.R']
        palm_04_L       = rig.data.edit_bones['palm.04.L']
        thumb_01_R      = rig.data.edit_bones['thumb.01.R']
        thumb_01_L      = rig.data.edit_bones['thumb.01.L']
        thumb_02_R      = rig.data.edit_bones['thumb.02.R']
        thumb_02_L      = rig.data.edit_bones['thumb.02.L']
        thumb_03_R      = rig.data.edit_bones['thumb.03.R']
        thumb_03_L      = rig.data.edit_bones['thumb.03.L']
        f_index_01_R    = rig.data.edit_bones['f_index.01.R']
        f_index_01_L    = rig.data.edit_bones['f_index.01.L']
        f_index_02_R    = rig.data.edit_bones['f_index.02.R']
        f_index_02_L    = rig.data.edit_bones['f_index.02.L']
        f_index_03_R    = rig.data.edit_bones['f_index.03.R']
        f_index_03_L    = rig.data.edit_bones['f_index.03.L']
        f_middle_01_R    = rig.data.edit_bones['f_middle.01.R']
        f_middle_01_L    = rig.data.edit_bones['f_middle.01.L']
        f_middle_02_R    = rig.data.edit_bones['f_middle.02.R']
        f_middle_02_L    = rig.data.edit_bones['f_middle.02.L']
        f_middle_03_R    = rig.data.edit_bones['f_middle.03.R']
        f_middle_03_L    = rig.data.edit_bones['f_middle.03.L']
        f_ring_01_R    = rig.data.edit_bones['f_ring.01.R']
        f_ring_01_L    = rig.data.edit_bones['f_ring.01.L']
        f_ring_02_R    = rig.data.edit_bones['f_ring.02.R']
        f_ring_02_L    = rig.data.edit_bones['f_ring.02.L']
        f_ring_03_R    = rig.data.edit_bones['f_ring.03.R']
        f_ring_03_L    = rig.data.edit_bones['f_ring.03.L']
        f_pinky_01_R    = rig.data.edit_bones['f_pinky.01.R']
        f_pinky_01_L    = rig.data.edit_bones['f_pinky.01.L']
        f_pinky_02_R    = rig.data.edit_bones['f_pinky.02.R']
        f_pinky_02_L    = rig.data.edit_bones['f_pinky.02.L']
        f_pinky_03_R    = rig.data.edit_bones['f_pinky.03.R']
        f_pinky_03_L    = rig.data.edit_bones['f_pinky.03.L']
        foot_R          = rig.data.edit_bones['foot.R']
        foot_L          = rig.data.edit_bones['foot.L']

        # IK controlling bones
        if add_ik_constraints:
            # Add hand and foot IK controller bones to the rig for the forearms IK constraints
            hand_IK_R = rig.data.edit_bones.new('hand.IK.R')
            hand_IK_L = rig.data.edit_bones.new('hand.IK.L')
            foot_IK_R = rig.data.edit_bones.new('foot.IK.R')
            foot_IK_L = rig.data.edit_bones.new('foot.IK.L')

            # Place the hand IK controller bones head at the same location as the hand bones head
            hand_IK_R.head = hand_R.head
            hand_IK_L.head = hand_L.head

            # Place the hand IK controller bones tail 10 cm above the hand bones tail
            hand_IK_R.tail = hand_IK_R.head + mathutils.Vector([0, 0, 0.1])
            hand_IK_L.tail = hand_IK_L.head + mathutils.Vector([0, 0, 0.1])

            # Place the foot IK controller bones head at the same location as the foot bones head
            foot_IK_R.head = foot_R.head
            foot_IK_L.head = foot_L.head

            # Place the foot IK controller bones tail 15 cm to the outside from the bone head
            foot_IK_R.tail = foot_IK_R.head + mathutils.Vector([-0.15, 0, 0])
            foot_IK_L.tail = foot_IK_L.head + mathutils.Vector([0.15, 0, 0])

            # Add the IK pole target bones
            arm_pole_target_R = rig.data.edit_bones.new('arm_pole_target.R')
            arm_pole_target_L = rig.data.edit_bones.new('arm_pole_target.L')
            leg_pole_target_R = rig.data.edit_bones.new('leg_pole_target.R')
            leg_pole_target_L = rig.data.edit_bones.new('leg_pole_target.L')

            # Place the pole target bones at z = 0 level, separated from the rig by 0.25 on the y axis
            arm_pole_target_R.head = mathutils.Vector([0, 0, 0])
            arm_pole_target_R.tail = mathutils.Vector([0, 0.25, 0])
            arm_pole_target_L.head = mathutils.Vector([0, 0, 0])
            arm_pole_target_L.tail = mathutils.Vector([0, 0.25, 0])
            leg_pole_target_R.head = mathutils.Vector([0, 0, 0])
            leg_pole_target_R.tail = mathutils.Vector([0, 0.25, 0])
            leg_pole_target_L.head = mathutils.Vector([0, 0, 0])
            leg_pole_target_L.tail = mathutils.Vector([0, 0.25, 0])

        # Add the thumb carpals
        thumb_carpal_R = rig.data.edit_bones.new('thumb.carpal.R')
        thumb_carpal_R.head = hand_R.head
        thumb_carpal_R.tail = thumb_carpal_R.head + mathutils.Vector([0, -virtual_bones['thumb.carpal.R']['median'], 0])
        thumb_carpal_L = rig.data.edit_bones.new('thumb.carpal.L')
        thumb_carpal_L.head = hand_L.head
        thumb_carpal_L.tail = thumb_carpal_L.head + mathutils.Vector([0, -virtual_bones['thumb.carpal.L']['median'], 0])
        
        # Asign the parent to thumb carpals
        thumb_carpal_R.parent       = hand_R
        thumb_carpal_R.use_connect  = False
        thumb_carpal_L.parent       = hand_L
        thumb_carpal_L.use_connect  = False

        # Change the parent of thumb.01 to thumb.carpal
        thumb_01_R.parent   = thumb_carpal_R
        thumb_01_L.parent   = thumb_carpal_L

        # Create a palm bones list and phalanges dictionary to continue the finger adjustment
        palm_bones  = [thumb_carpal_R, thumb_carpal_L, palm_01_R, palm_01_L, palm_02_R, palm_02_L, palm_03_R, palm_03_L, palm_04_R, palm_04_L]
        phalanges   = {
            'thumb.carpal.R'    : [thumb_01_R, thumb_02_R, thumb_03_R],
            'thumb.carpal.L'    : [thumb_01_L, thumb_02_L, thumb_03_L],
            'palm.01.R'         : [f_index_01_R, f_index_02_R, f_index_03_R],
            'palm.01.L'         : [f_index_01_L, f_index_02_L, f_index_03_L],
            'palm.02.R'         : [f_middle_01_R, f_middle_02_R, f_middle_03_R],
            'palm.02.L'         : [f_middle_01_L, f_middle_02_L, f_middle_03_L],
            'palm.03.R'         : [f_ring_01_R, f_ring_02_R, f_ring_03_R],
            'palm.03.L'         : [f_ring_01_L, f_ring_02_L, f_ring_03_L],
            'palm.04.R'         : [f_pinky_01_R, f_pinky_02_R, f_pinky_03_R],
            'palm.04.L'         : [f_pinky_01_L, f_pinky_02_L, f_pinky_03_L],
        }

        # Iterate through the palm bones to adjust several properties
        for palm_bone in palm_bones:
            # Change the first phalange connect setting to True
            phalanges[palm_bone.name][0].use_connect  = True
            # Move the head of the metacarpal bones to match the hand bone head
            palm_bone.head = palm_bone.parent.head
            # Move the tail of the metacarpal bones so they are aligned horizontally
            palm_bone.tail[2] = palm_bone.head[2]
            # Change metacarpal bones lengths
            palm_bone.length = virtual_bones[palm_bone.name]['median']
        
        # Align the phalanges to the x axis (set bones head and tail y position equal to yz position of metacarpals bone tail)
        for palm_bone in palm_bones:
            for phalange in phalanges[palm_bone.name]:
                phalange.head = phalange.parent.tail
                # Calculate the sign to multiply the length of the phalange
                length_sign = -1 if ".R" in phalange.name else 1
                # Set the length by moving the bone tail along the x axis. Using this instead of just setting bone.length because that causes some bone inversions
                phalange.tail = (phalange.head[0] + length_sign * virtual_bones[phalange.name]['median'], phalange.head[1], phalange.head[2])
                # Reset the phalange bone roll to 0
                phalange.roll = 0


        # Rotate the thumb bones to form a natural pose
        bpy.ops.object.mode_set(mode='POSE')

        pose_thumb_carpal_R                 = rig.pose.bones['thumb.carpal.R']
        pose_thumb_carpal_R.rotation_mode   = 'XYZ'
        pose_thumb_carpal_R.rotation_euler  = (m.radians(-28.048091), m.radians(7.536737), m.radians(-40.142189))
        pose_thumb_carpal_R.rotation_mode   = 'QUATERNION'
        pose_thumb_01_R                     = rig.pose.bones['thumb.01.R']
        pose_thumb_01_R.rotation_mode       = 'XYZ'
        # pose_thumb_01_R.rotation_euler      = (m.radians(20), m.radians(0), m.radians(80))
        pose_thumb_01_R.rotation_euler      = (m.radians(0), m.radians(0), m.radians(90))
        pose_thumb_01_R.rotation_mode       = 'QUATERNION'
        # pose_thumb_02_R                     = rig.pose.bones['thumb.02.R']
        # pose_thumb_02_R.rotation_mode       = 'XYZ'
        # pose_thumb_02_R.rotation_euler      = (m.radians(0), m.radians(0), m.radians(-25))
        # pose_thumb_02_R.rotation_mode       = 'QUATERNION'
        # pose_thumb_03_R                     = rig.pose.bones['thumb.03.R']
        # pose_thumb_03_R.rotation_mode       = 'XYZ'
        # pose_thumb_03_R.rotation_euler      = (m.radians(0), m.radians(0), m.radians(-10))
        # pose_thumb_03_R.rotation_mode       = 'QUATERNION'
        pose_thumb_carpal_L                 = rig.pose.bones['thumb.carpal.L']
        pose_thumb_carpal_L.rotation_mode   = 'XYZ'
        pose_thumb_carpal_L.rotation_euler  = (m.radians(-28.048091), m.radians(-7.536737), m.radians(40.142189))
        pose_thumb_carpal_L.rotation_mode   = 'QUATERNION'
        pose_thumb_01_L                     = rig.pose.bones['thumb.01.L']
        pose_thumb_01_L.rotation_mode       = 'XYZ'
        # pose_thumb_01_L.rotation_euler      = (m.radians(20), m.radians(0), m.radians(-80))
        pose_thumb_01_L.rotation_euler      = (m.radians(0), m.radians(0), m.radians(-90))
        pose_thumb_01_L.rotation_mode       = 'QUATERNION'
        # pose_thumb_02_L                     = rig.pose.bones['thumb.02.L']
        # pose_thumb_02_L.rotation_mode       = 'XYZ'
        # pose_thumb_02_L.rotation_euler      = (m.radians(0), m.radians(0), m.radians(25))
        # pose_thumb_02_L.rotation_mode       = 'QUATERNION'
        # pose_thumb_03_L                     = rig.pose.bones['thumb.03.L']
        # pose_thumb_03_L.rotation_mode       = 'XYZ'
        # pose_thumb_03_L.rotation_euler      = (m.radians(0), m.radians(0), m.radians(10))
        # pose_thumb_03_L.rotation_mode       = 'QUATERNION'

        # Rotate the forearm and shin bones to bend the elbows and knees a little bit and avoid incorrect rotations
        pose_forearm_R                  = rig.pose.bones['forearm.R']
        pose_forearm_R.rotation_mode    = 'XYZ'
        pose_forearm_R.rotation_euler   = (m.radians(2), m.radians(0), m.radians(0))
        pose_forearm_R.rotation_mode    = 'QUATERNION'
        pose_forearm_L                  = rig.pose.bones['forearm.L']
        pose_forearm_L.rotation_mode    = 'XYZ'
        pose_forearm_L.rotation_euler   = (m.radians(2), m.radians(0), m.radians(0))
        pose_forearm_L.rotation_mode    = 'QUATERNION'
        pose_thigh_R                    = rig.pose.bones['thigh.R']
        pose_thigh_R.rotation_mode      = 'XYZ'
        pose_thigh_R.rotation_euler     = (m.radians(-2), m.radians(0), m.radians(0))
        pose_thigh_R.rotation_mode      = 'QUATERNION'
        pose_thigh_L                    = rig.pose.bones['thigh.L']
        pose_thigh_L.rotation_mode      = 'XYZ'
        pose_thigh_L.rotation_euler     = (m.radians(-2), m.radians(0), m.radians(0))
        pose_thigh_L.rotation_mode      = 'QUATERNION'
        pose_shin_R                     = rig.pose.bones['shin.R']
        pose_shin_R.rotation_mode       = 'XYZ'
        pose_shin_R.rotation_euler      = (m.radians(2), m.radians(0), m.radians(0))
        pose_shin_R.rotation_mode       = 'QUATERNION'
        pose_shin_L                     = rig.pose.bones['shin.L']
        pose_shin_L.rotation_mode       = 'XYZ'
        pose_shin_L.rotation_euler      = (m.radians(2), m.radians(0), m.radians(0))
        pose_shin_L.rotation_mode       = 'QUATERNION'


        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

    # Change mode to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    ### Add bone constrains ###
    print('Adding bone constraints...')

    # Change to pose mode
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')

    # Create each constraint
    for bone in bone_constraints:

        # If it is a finger bone amd add_fingers_constraints is False continue with the next bone
        if not add_fingers_constraints and len([finger_part for finger_part in ['palm', 'thumb', 'index', 'middle', 'ring', 'pinky'] if finger_part in bone]) > 0:
            continue

        for cons in bone_constraints[bone]:
            # Add new constraint determined by type

            # Exclude unwanted combinations of options, bones and constraints
            if not use_limit_rotation and cons['type'] == 'LIMIT_ROTATION':
                continue
            elif not add_ik_constraints and (cons['type'] == 'IK' or (bone in ['forearm.R', 'forearm.L'] and cons['type'] in ['COPY_ROTATION'])):
                continue
            elif add_ik_constraints and bone in ['forearm.R', 'forearm.L', 'shin.R', 'shin.L'] and cons['type'] in ['COPY_ROTATION', 'DAMPED_TRACK', 'LOCKED_TRACK']:
                continue
            elif not add_ik_constraints and bone in ['hand.IK.R', 'hand.IK.L', 'foot.IK.R', 'foot.IK.L', 'arm_pole_target.R', 'arm_pole_target.L', 'leg_pole_target.R', 'leg_pole_target.L']:
                continue
            else:
                # bone_cons = rig.pose.bones[bone].constraints.new(cons['type'])
                bone_cons = rig.pose.bones[bone_name_map[armature_name][bone]].constraints.new(cons['type'])
            
            # Define aditional parameters based on the type of constraint
            if cons['type'] == 'LIMIT_ROTATION':
                bone_cons.use_limit_x   = cons['use_limit_x']
                bone_cons.min_x         = m.radians(cons['min_x'])
                bone_cons.max_x         = m.radians(cons['max_x'])
                bone_cons.use_limit_y   = cons['use_limit_y']
                bone_cons.min_y         = m.radians(cons['min_y'])
                bone_cons.max_y         = m.radians(cons['max_y'])
                bone_cons.use_limit_z   = cons['use_limit_z']
                bone_cons.min_z         = m.radians(cons['min_z'])
                bone_cons.max_z         = m.radians(cons['max_z'])
                bone_cons.owner_space   = cons['owner_space']
            elif cons['type'] == 'COPY_LOCATION':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.use_offset    = cons['use_offset']
            elif cons['type'] == 'LOCKED_TRACK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.track_axis    = cons['track_axis'][pose_name]
                bone_cons.lock_axis     = cons['lock_axis'][pose_name]
                bone_cons.influence     = cons['influence']
            elif cons['type'] == 'DAMPED_TRACK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.track_axis    = cons['track_axis']
            elif cons['type'] == 'IK':
                bone_cons.target = bpy.data.objects[cons['target']]
                bone_cons.subtarget = rig.pose.bones[bone_name_map[armature_name][cons['subtarget']]].name
                bone_cons.pole_target = bpy.data.objects[cons['pole_target']]
                bone_cons.pole_subtarget = rig.pose.bones[bone_name_map[armature_name][cons['pole_subtarget']]].name
                bone_cons.chain_count = cons['chain_count']
                bone_cons.pole_angle = cons['pole_angle'][pose_name]
                # bone_cons.pole_angle = cons['pole_angle']
                rig.pose.bones[bone_name_map[armature_name][bone]].lock_ik_x = cons['lock_ik_x']
                rig.pose.bones[bone_name_map[armature_name][bone]].lock_ik_y = cons['lock_ik_y']
                rig.pose.bones[bone_name_map[armature_name][bone]].lock_ik_z = cons['lock_ik_z']
                rig.pose.bones[bone_name_map[armature_name][bone]].use_ik_limit_x = cons['use_ik_limit_x']
                rig.pose.bones[bone_name_map[armature_name][bone]].use_ik_limit_y = cons['use_ik_limit_y']
                rig.pose.bones[bone_name_map[armature_name][bone]].use_ik_limit_z = cons['use_ik_limit_z']
                rig.pose.bones[bone_name_map[armature_name][bone]].ik_min_x = cons['ik_min_x']
                rig.pose.bones[bone_name_map[armature_name][bone]].ik_max_x = cons['ik_max_x']
                rig.pose.bones[bone_name_map[armature_name][bone]].ik_min_y = cons['ik_min_y']
                rig.pose.bones[bone_name_map[armature_name][bone]].ik_max_y = cons['ik_max_y']
                rig.pose.bones[bone_name_map[armature_name][bone]].ik_min_z = cons['ik_min_z']
                rig.pose.bones[bone_name_map[armature_name][bone]].ik_max_z = cons['ik_max_z']
            elif cons['type'] == 'COPY_ROTATION':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.subtarget     = rig.pose.bones[bone_name_map[armature_name][cons['subtarget']]].name
                bone_cons.use_x         = cons['use_x']
                bone_cons.use_y         = cons['use_y']
                bone_cons.use_z         = cons['use_z']
                bone_cons.target_space  = cons['target_space']
                bone_cons.owner_space   = cons['owner_space']
                bone_cons.influence     = cons['influence']

    if add_ik_constraints:

        # Get the transition quadratic function
        ik_quadratic_function = quadratic_function(x1=ik_transition_threshold,
                                                x2=((ik_transition_threshold + 1)/2),
                                                x3=1,
                                                y1=0.0,
                                                y2=0.25,
                                                y3=1)

        # Loop through the scene frames and calculate the pole angle for each IK constraint to animate the pole_angle variable
        for frame in range(scene.frame_start, scene.frame_end + 1):
            bpy.context.scene.frame_set(frame)

            for bone in ik_pole_bones:
                #  Calculate the pole bone position
                pole_bone_position = calculate_ik_pole_position(ik_pole_bones[bone]['base_marker'],
                                                                ik_pole_bones[bone]['pole_marker'],
                                                                ik_pole_bones[bone]['target_marker'],
                                                                ik_pole_bones[bone]['aux_markers'],
                                                                ik_transition_threshold,
                                                                ik_quadratic_function)

                rig.pose.bones[bone].location = pole_bone_position
                rig.pose.bones[bone].keyframe_insert(data_path="location")

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

    ### Bake animation to the rig ###
    # Get the empties ending frame
    ending_frame = int(bpy.data.actions[0].frame_range[1])
    # Bake animation
    # bpy.ops.nla.bake(frame_start=0, frame_end=ending_frame, bake_types={'POSE'})
    bpy.ops.nla.bake(frame_start=0, frame_end=ending_frame, only_selected=False, visual_keying=True, clear_constraints=clear_constraints, bake_types={'POSE'})

    # Change back to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
def add_mesh_to_rig(body_mesh_mode: str="custom",
                    armature_name: str="armature_freemocap",
                    body_height: float=1.75,
                    pose_name: str="freemocap_tpose"):

    if body_mesh_mode == "file":
        
        try:
            bpy.ops.import_mesh.ply(filepath="body_mesh.ply")
            
        except:
            print("\nCould not find body_mesh file.")
            return

        # Get reference to the rig
        rig = bpy.data.objects['root']
    
        # Get the rig z dimension
        rig_z_dimension = rig.dimensions.z
        
        # Get the body_mesh z dimension
        body_mesh = bpy.data.objects['body_mesh']
        body_mesh_z_dimension = body_mesh.dimensions.z

        # Calculate the proportion between the rig and the body_mesh
        rig_to_body_mesh = rig_z_dimension / body_mesh_z_dimension

        # Scale the mesh by the rig and body_mesh proportion multiplied by a scale factor
        body_mesh.scale = (rig_to_body_mesh * 1.04, rig_to_body_mesh * 1.04, rig_to_body_mesh * 1.04)
    
        # Apply transformations to body_mesh (scale must be (1, 1, 1) so it doesn't export badly
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = body_mesh
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        ### Parent the body_mesh with the rig
        # Select the body_mesh
        body_mesh.select_set(True)
        # Select the rig
        rig.select_set(True)
        # Set rig as active
        bpy.context.view_layer.objects.active = rig
        # Parent the body_mesh and the rig with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    elif body_mesh_mode == "skelly":
        
        # Change to object mode
        if bpy.context.selected_objects != []:
            bpy.ops.object.mode_set(mode='OBJECT')

        try:
            # Get the script filepath
            script_file = os.path.realpath(__file__)
            # Get the script folder
            directory = os.path.dirname(script_file)
            # Import the skelly mesh
            bpy.ops.import_scene.fbx(filepath=directory+'/assets/skelly_lowpoly_mesh.fbx')
            
        except:
            print("\nCould not find skelly mesh file.")
            return
        
        # Deselect all objects
        for object in bpy.data.objects:
            object.select_set(False)

        # Get reference to armature
        for capture_object in bpy.data.objects:
            if capture_object.type == "ARMATURE" and ("_rig" in capture_object.name or capture_object.name == "root"):
                rig = capture_object

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
        body_mesh_z_dimension = skelly_mesh.dimensions.z
        
        # Set the location of the skelly mesh
        skelly_mesh.location = head_location

        # Calculate the proportion between the rig and the mesh
        rig_to_body_mesh = body_height / body_mesh_z_dimension

        # Scale the mesh by the rig and body_mesh proportions multiplied by a scale factor
        skelly_mesh.scale = (rig_to_body_mesh * 1.0, rig_to_body_mesh * 1.0, rig_to_body_mesh * 1.0)

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

        # Rename the skelly mesh to skelly_mesh
        skelly_mesh.name = 'skelly_mesh'

    elif body_mesh_mode == "skelly_parts_old":

        # Change to object mode
        if bpy.context.selected_objects != []:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Get reference to the rig
        for capture_object in bpy.data.objects:
            if capture_object.type == "ARMATURE" and ("_rig" in capture_object.name or capture_object.name == "root"):
                rig = capture_object

        # Deselect all objects
        for object in bpy.data.objects:
            object.select_set(False)

        #  Set the rig as active object
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig

        #  Get the scene render fps
        scene_render_fps = bpy.context.scene.render.fps

        # Change to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        #  Iterate through the skelly parts dictionary and update the default origin, length and normalized direction
        for part in skelly_parts:
            skelly_parts[part]['bones_origin']  = mathutils.Vector(rig.data.edit_bones[bone_name_map[armature_name][skelly_parts[part]['bones'][0]]].head)
            skelly_parts[part]['bones_end']     = mathutils.Vector(rig.data.edit_bones[bone_name_map[armature_name][skelly_parts[part]['bones'][-1]]].tail)
            skelly_parts[part]['bones_length']  = (skelly_parts[part]['bones_end'] - skelly_parts[part]['bones_origin']).length

        # Change to object mode
        bpy.ops.object.mode_set(mode='OBJECT')        

        # Get the script filepath
        script_file = os.path.realpath(__file__)
        # Get the script folder
        directory = os.path.dirname(script_file)

        # Define the list that will contain the different Skelly meshes
        skelly_meshes = []

        # Iterate through the skelly parts dictionary and add the correspondent skelly part
        for part in skelly_parts:
            try:
                # Import the skelly mesh
                bpy.ops.import_scene.fbx(filepath=directory+'/assets/skelly_parts/Skelly_' + part + '.fbx')

            except:
                print("\nCould not find Skelly_" + part + " mesh file.")
                continue

            skelly_meshes.append(bpy.data.objects['Skelly_' + part])

            # Get reference to the imported mesh
            skelly_part = bpy.data.objects['Skelly_' + part]

            # Move the Skelly part to the equivalent bone's head location
            skelly_part.location = skelly_parts[part]['bones_origin'] + mathutils.Vector(skelly_parts[part]['position_offset'])

            # Adjust rotation if necessary
            if skelly_parts[part]['adjust_rotation']:
                # Get the direction vector
                bone_vector = skelly_parts[part]['bones_end'] - skelly_parts[part]['bones_origin']
                # Get new bone vector after applying the position offset
                new_bone_vector = skelly_parts[part]['bones_end'] - skelly_parts[part]['bones_origin'] + mathutils.Vector(skelly_parts[part]['position_offset'])
                # Get the angle between the two vectors
                rotation_quaternion = new_bone_vector.rotation_difference(bone_vector)
                # Change the rotation mode
                skelly_part.rotation_mode = 'QUATERNION'
                # Rotate the Skelly part
                skelly_part.rotation_quaternion = rotation_quaternion

            # Get the bone length
            if skelly_parts[part]['adjust_rotation']:
                bone_length = (skelly_parts[part]['bones_end'] - (skelly_parts[part]['bones_origin'] + mathutils.Vector(skelly_parts[part]['position_offset']))).length
            else:
                bone_length = skelly_parts[part]['bones_length']

            # Get the mesh length
            mesh_length = skelly_parts[part]['mesh_length']

            # Resize the Skelly part to match the bone length
            skelly_part.scale = (bone_length / mesh_length, bone_length / mesh_length, bone_length / mesh_length)

        # Rename the first mesh to skelly_mesh
        skelly_meshes[0].name = "skelly_mesh"

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # Select all body meshes
        for skelly_mesh in skelly_meshes:
            skelly_mesh.select_set(True)

        # Set skelly_mesh as active
        bpy.context.view_layer.objects.active = skelly_meshes[0]
        
        # Join the body meshes
        bpy.ops.object.join()

        # Select the rig
        rig.select_set(True)
        # Set rig as active
        bpy.context.view_layer.objects.active = rig
        # Parent the mesh and the rig with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        # Restore the scene render fps in case it was changed
        bpy.context.scene.render.fps = scene_render_fps

    elif body_mesh_mode == "skelly_parts":
        
        # Get references to the armature pose
        pose = globals()[pose_name]

        # Change to object mode
        if bpy.context.selected_objects != []:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Get reference to the rig
        for capture_object in bpy.data.objects:
            if capture_object.type == "ARMATURE" and (
                "_rig" in capture_object.name or
                capture_object.name == "root"
                ):
                rig = capture_object

        # Deselect all objects
        for object in bpy.data.objects:
            object.select_set(False)

        #  Set the rig as active object
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig

        # Change to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        #  Iterate through the skelly parts dictionary and update the
        #  default origin, length and normalized direction
        for part in skelly_parts:
            skelly_parts[part]['bones_origin'] = mathutils.Vector(rig.data.edit_bones[bone_name_map[armature_name][skelly_parts[part]['bones'][0]]].head)
            skelly_parts[part]['bones_end'] = mathutils.Vector(rig.data.edit_bones[bone_name_map[armature_name][skelly_parts[part]['bones'][-1]]].tail)
            skelly_parts[part]['bones_length'] = (skelly_parts[part]['bones_end'] - skelly_parts[part]['bones_origin']).length

        # Change to object mode
        bpy.ops.object.mode_set(mode='OBJECT')        

        # Get the script filepath
        script_file = os.path.realpath(__file__)
        # Get the script folder
        directory = os.path.dirname(script_file)

        # Define the list that will contain the different Skelly meshes
        skelly_meshes = []

        # Iterate through the skelly parts dictionary and add the correspondent skelly part
        for part in skelly_parts:
            # if part != 'upper_arm.R':
            #     continue
            try:
                # Import the skelly mesh
                bpy.ops.import_scene.fbx(
                    filepath=directory
                    + '/assets/skelly_parts_meshes/Skelly_' + part + '.fbx')

            except:
                print("\nCould not find Skelly_" + part + " mesh file.")
                continue

            skelly_meshes.append(bpy.data.objects['Skelly_' + part])

            # Get reference to the imported mesh
            skelly_part = bpy.data.objects['Skelly_' + part]

            # Get the rotation matrix
            if part == 'head':
                rotation_matrix = mathutils.Matrix.Identity(4)
            else:
                rotation_matrix = mathutils.Euler(
                    mathutils.Vector(pose[bone_name_map[armature_name][part]]['rotation']),
                    'XYZ',
                ).to_matrix()

            # Move the Skelly part to the equivalent bone's head location
            skelly_part.location = (skelly_parts[part]['bones_origin']
                + rotation_matrix @ mathutils.Vector(skelly_parts[part]['position_offset'])
                # + mathutils.Vector(skelly_parts[part]['position_offset'])
            )

            # Rotate the part mesh with the rotation matrix
            skelly_part.rotation_euler = rotation_matrix.to_euler('XYZ')

            # Get the bone length
            if skelly_parts[part]['adjust_rotation']:
                bone_length = (skelly_parts[part]['bones_end'] - (skelly_parts[part]['bones_origin'] + (rotation_matrix @ mathutils.Vector(skelly_parts[part]['position_offset'])))).length
            else:
                bone_length = skelly_parts[part]['bones_length']

            # Get the mesh length
            mesh_length = skelly_parts[part]['mesh_length']

            # Resize the Skelly part to match the bone length
            skelly_part.scale = (bone_length / mesh_length, bone_length / mesh_length, bone_length / mesh_length)

            # Adjust rotation if necessary
            if skelly_parts[part]['adjust_rotation']:
                # Save the Skelly part's original location
                part_location = mathutils.Vector(skelly_part.location)

                # Get the direction vector
                bone_vector = skelly_parts[part]['bones_end'] - skelly_parts[part]['bones_origin']
                # Get new bone vector after applying the position offset
                new_bone_vector = skelly_parts[part]['bones_end'] - part_location
               
                # Apply the rotations to the Skelly part
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

                # Get the angle between the two vectors
                rotation_quaternion = bone_vector.rotation_difference(new_bone_vector)
                # Change the rotation mode
                skelly_part.rotation_mode = 'QUATERNION'
                # Rotate the Skelly part
                skelly_part.rotation_quaternion = rotation_quaternion

            # Apply the transformations to the Skelly part
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        # Rename the first mesh to skelly_mesh
        skelly_meshes[0].name = "skelly_mesh"

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # Select all body meshes
        for skelly_mesh in skelly_meshes:
            skelly_mesh.select_set(True)

        # Set skelly_mesh as active
        bpy.context.view_layer.objects.active = skelly_meshes[0]
        
        # Join the body meshes
        bpy.ops.object.join()

        # Select the rig
        rig.select_set(True)
        # Set rig as active
        bpy.context.view_layer.objects.active = rig
        # Parent the mesh and the rig with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            

    elif body_mesh_mode == "can_man":
    
        # Change to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all objects
        for object in bpy.data.objects:
            object.select_set(False)

        # Get reference to armature
        rig = bpy.data.objects['root']

        # Select the rig
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig

        # Change to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        ### Add cylinders and spheres for the major bones

        # Get the bone references to calculate the meshes locations and proportions
        spine       = rig.data.edit_bones['spine']
        spine_001   = rig.data.edit_bones['spine.001']
        shoulder_R  = rig.data.edit_bones['shoulder.R']
        shoulder_L  = rig.data.edit_bones['shoulder.L']
        neck        = rig.data.edit_bones['neck']
        hand_R      = rig.data.edit_bones['hand.R']
        hand_L      = rig.data.edit_bones['hand.L']
        pelvis_R    = rig.data.edit_bones['pelvis.R']
        pelvis_L    = rig.data.edit_bones['pelvis.L']
        thigh_R     = rig.data.edit_bones['thigh.R']
        thigh_L     = rig.data.edit_bones['thigh.L']
        shin_R      = rig.data.edit_bones['shin.R']
        shin_L      = rig.data.edit_bones['shin.L']
        foot_R      = rig.data.edit_bones['foot.R']
        foot_L      = rig.data.edit_bones['foot.L']

        # Calculate parameters of the different body meshes
        trunk_mesh_radius           = shoulder_R.length / 3
        trunk_mesh_depth            = spine_001.tail[2] - spine.head[2] + 0.05 * body_height
        trunk_mesh_location         = (spine.head[0], spine.head[1], spine.head[2] + trunk_mesh_depth / 2 - 0.025 * body_height)
        neck_mesh_depth             = neck.length
        neck_mesh_location          = (neck.head[0], neck.head[1], neck.head[2] + neck.length / 2)
        shoulders_mesh_depth        = shoulder_R.length + shoulder_L.length + 0.05
        shoulders_mesh_location     = (neck.head[0], neck.head[1], neck.head[2])
        head_mesh_location          = (neck.tail[0], neck.tail[1], neck.tail[2])
        head_mesh_radius            = neck.length / 2
        right_eye_mesh_location     = (neck.tail[0] - 0.04, neck.tail[1] - head_mesh_radius, neck.tail[2] + 0.02)
        right_eye_mesh_radius       = head_mesh_radius / 3
        left_eye_mesh_location      = (neck.tail[0] + 0.04, neck.tail[1] - head_mesh_radius, neck.tail[2] + 0.02)
        left_eye_mesh_radius        = head_mesh_radius / 3
        nose_mesh_location          = (neck.tail[0], neck.tail[1] - head_mesh_radius, neck.tail[2] - 0.02)
        nose_mesh_radius            = head_mesh_radius / 3.5
        right_arm_mesh_depth        = shoulder_R.tail[0] - hand_R.head[0]
        right_arm_mesh_location     = (shoulder_R.tail[0] - right_arm_mesh_depth / 2, shoulder_R.tail[1], shoulder_R.tail[2] - 0.02)
        right_arm_mesh_radius       = right_arm_mesh_depth / 10
        left_arm_mesh_depth         = hand_L.head[0] - shoulder_L.tail[0] 
        left_arm_mesh_location      = (shoulder_L.tail[0] + left_arm_mesh_depth / 2, shoulder_L.tail[1], shoulder_L.tail[2] - 0.02)
        left_arm_mesh_radius        = left_arm_mesh_depth / 10
        right_hand_mesh_location    = (hand_R.tail[0], hand_R.tail[1], hand_R.tail[2])
        right_hand_mesh_radius      = right_arm_mesh_depth / 8
        right_thumb_mesh_location   = (hand_R.tail[0], hand_R.tail[1] - right_hand_mesh_radius, hand_R.tail[2])
        right_thumb_mesh_radius     = right_hand_mesh_radius / 3
        left_hand_mesh_location     = (hand_L.tail[0], hand_L.tail[1], hand_L.tail[2])
        left_hand_mesh_radius       = left_arm_mesh_depth / 8
        left_thumb_mesh_location    = (hand_L.tail[0], hand_L.tail[1] - left_hand_mesh_radius, hand_L.tail[2])
        left_thumb_mesh_radius      = left_hand_mesh_radius / 3
        hips_mesh_depth             = pelvis_R.length + pelvis_L.length + 0.05
        hips_mesh_location          = (pelvis_R.head[0], pelvis_R.head[1], pelvis_R.head[2])
        right_leg_mesh_depth        = thigh_R.head[2] - shin_R.tail[2]
        right_leg_mesh_location     = (thigh_R.head[0], thigh_R.head[1], thigh_R.head[2] - right_leg_mesh_depth / 2)
        left_leg_mesh_depth         = thigh_L.head[2] - shin_L.tail[2]
        left_leg_mesh_location      = (thigh_L.head[0], thigh_L.head[1], thigh_L.head[2] - left_leg_mesh_depth / 2)
        right_foot_mesh_location    = (foot_R.head[0], (foot_R.head[1] + foot_R.tail[1]) / 2, (foot_R.head[2] + foot_R.tail[2]) / 2)
        left_foot_mesh_location     = (foot_L.head[0], (foot_L.head[1] + foot_L.tail[1]) / 2, (foot_L.head[2] + foot_L.tail[2]) / 2)

        # Create and append the body meshes to the list
        # Define the list that will contain the different meshes of the body
        body_meshes = []
        # Set basic cylinder properties
        cylinder_cuts   = 20
        vertices        = 16
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = trunk_mesh_radius,
            depth           = trunk_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = trunk_mesh_location,
            rotation        = (0.0, 0.0, 0.0),
            scale           = (1, 0.5, 1)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Neck
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.02,
            depth           = neck_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = neck_mesh_location,
            rotation        = (0.0, 0.0, 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Shoulders
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.05,
            depth           = shoulders_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = shoulders_mesh_location,
            rotation        = (0.0, m.pi/2, 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Head
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = head_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = head_mesh_location,
            scale           = (1, 1.2, 1.2)
        )
        body_meshes.append(bpy.context.active_object)

        # Right Eye
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = right_eye_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = right_eye_mesh_location,
            scale           = (1, 1, 1)
        )
        body_meshes.append(bpy.context.active_object)

        # Left Eye
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = left_eye_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_eye_mesh_location,
            scale           = (1, 1, 1)
        )
        body_meshes.append(bpy.context.active_object)

        # Nose
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = nose_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = nose_mesh_location,
            scale           = (1, 1, 1)
        )
        body_meshes.append(bpy.context.active_object)
        
        # Right Arm
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = right_arm_mesh_radius,
            depth           = right_arm_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = right_arm_mesh_location,
            rotation        = (0.0, m.radians(90), 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Left Arm
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = left_arm_mesh_radius,
            depth           = left_arm_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_arm_mesh_location,
            rotation        = (0.0, m.radians(90), 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Right Hand
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = right_hand_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = right_hand_mesh_location,
            scale           = (1.4, 0.8, 0.5)
        )
        body_meshes.append(bpy.context.active_object)

        # Right Thumb
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = right_thumb_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = right_thumb_mesh_location,
            scale           = (1.0, 1.4, 1.0)
        )
        body_meshes.append(bpy.context.active_object)

        # Left Hand
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = left_hand_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_hand_mesh_location,
            scale           = (1.4, 0.8, 0.5)
        )
        body_meshes.append(bpy.context.active_object)

        # Left Thumb
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = left_thumb_mesh_radius,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_thumb_mesh_location,
            scale           = (1.0, 1.4, 1.0)
        )
        body_meshes.append(bpy.context.active_object)

        # Hips
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.05,
            depth           = hips_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = hips_mesh_location,
            rotation        = (0.0, m.pi/2, 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")
        
        # Right Leg
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.08,
            depth           = right_leg_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = right_leg_mesh_location,
            rotation        = (0.0, 0.0, 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Left Leg
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.08,
            depth           = left_leg_mesh_depth,
            end_fill_type   = 'NGON',
            calc_uvs        = True,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_leg_mesh_location,
            rotation        = (0.0, 0.0, 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Right Foot
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = 0.05,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = right_foot_mesh_location,
            scale           = (1.5, 5.0, 1.7)
        )
        body_meshes.append(bpy.context.active_object)

        # Left Foot
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = 0.05,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_foot_mesh_location,
            scale           = (1.5, 5.0, 1.7)
        )
        body_meshes.append(bpy.context.active_object)

        ### Join all the body_meshes with the trunk mesh
        # Rename the trunk mesh to fmc_mesh
        body_meshes[0].name = "fmc_mesh"
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

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
    
    else:
        print("Unknown add mesh mode")

def export_fbx(self: Operator,
               fbx_type: str='standard'):

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    # Variable to check if the original rig name has been saved
    rig_original_name_saved = False

    # Select only the rig and the body_mesh.
    for capture_object in bpy.data.objects:
        if capture_object.type == "ARMATURE":
            # Save the original rig name
            if not rig_original_name_saved:
                rig_original_name       = capture_object.name
                rig_original_name_saved = True

            # Rename the rig if its name is different from root
            if capture_object.name != "root":
                capture_object.name = "root"

            # Select the rig                
            capture_object.select_set(True)

    bpy.data.objects['skelly_mesh'].select_set(True)

    # Get the Blender file directory
    file_directory = Path(bpy.data.filepath).parent

    fbx_folder = file_directory / 'FBX'
    fbx_folder.mkdir(parents=True, exist_ok=True)

    # Define the export parameters dictionary
    export_parameters = {
        'filepath':fbx_folder / 'fmc_export.fbx',
        'use_selection':True,
        'use_visible':False,
        'use_active_collection':False,
        'global_scale':1.0,
        'apply_unit_scale':True,
        'apply_scale_options':'FBX_SCALE_NONE',
        'use_space_transform':True,
        'bake_space_transform':False,
        'object_types':{'ARMATURE', 'MESH', 'EMPTY'},
        'use_mesh_modifiers':True,
        'use_mesh_modifiers_render':True,
        'mesh_smooth_type':'FACE',
        'colors_type':'SRGB',
        'prioritize_active_color':False,
        'use_subsurf':False,
        'use_mesh_edges':False,
        'use_tspace':False,
        'use_triangles':False,
        'use_custom_props':False,
        'add_leaf_bones':False,
        'primary_bone_axis':'Y',
        'secondary_bone_axis':'X',
        'use_armature_deform_only':False,
        'armature_nodetype':'NULL',
        'bake_anim':True,
        'bake_anim_use_all_bones':True,
        'bake_anim_use_nla_strips':False,
        'bake_anim_use_all_actions':False,
        'bake_anim_force_startend_keying':True,
        'bake_anim_step':1.0,
        'bake_anim_simplify_factor':0.0,
        'path_mode':'AUTO',
        'embed_textures':False,
        'batch_mode':'OFF',
        'use_batch_own_dir':True,
        'use_metadata':True,
        'axis_forward':'Y',
        'axis_up':'Z'
    }

    ################# Use of Blender io_scene_fbx addon #############################

    # Load the io_scene_fbx addon
    addons = {os.path.basename(os.path.dirname(module.__file__)): module.__file__ for module in addon_utils.modules()}
    addon_folder_path = os.path.dirname(addons.get('io_scene_fbx'))
    print(addon_folder_path)
    try:
        SourceFileLoader('io_scene_fbx', os.path.join(addon_folder_path, '__init__.py')).load_module()
    except RuntimeError as error:
        print(error)

    # Import the export_fbx_bin module and necessary utilities
    import io_scene_fbx.export_fbx_bin as export_fbx_bin

    from io_scene_fbx.export_fbx_bin import (
        fbx_data_bindpose_element,
        AnimationCurveNodeWrapper
    )
    from bpy_extras.io_utils import axis_conversion
    from io_scene_fbx.fbx_utils import (
        FBX_MODELS_VERSION,
        FBX_POSE_BIND_VERSION,
        FBX_DEFORMER_SKIN_VERSION,
        FBX_DEFORMER_CLUSTER_VERSION,
        BLENDER_OBJECT_TYPES_MESHLIKE,
        units_convertor_iter,
        matrix4_to_array,
        get_fbx_uuid_from_key,
        get_blenderID_name,
        get_blender_bindpose_key,
        get_blender_anim_stack_key,
        get_blender_anim_layer_key,
        elem_empty,
        elem_data_single_bool,
        elem_data_single_int32,
        elem_data_single_int64,
        elem_data_single_float64,
        elem_data_single_string,
        elem_data_single_int32_array,
        elem_data_single_float64_array,
        elem_properties,
        elem_props_template_init,
        elem_props_template_set,
        elem_props_template_finalize,
        fbx_name_class
    )

    if bpy.app.version_string[0] >= '4':
        from io_scene_fbx.fbx_utils import (
        FBX_KTIME,
        elem_data_single_char,
        ObjectWrapper
    )

    convert_rad_to_deg_iter = units_convertor_iter("radian", "degree")

    from io_scene_fbx.export_fbx_bin import fbx_data_element_custom_properties

    # Backup the method original_fbx_data_armature_elements of export_fbx_bin before it is modified
    backup_fbx_animations_do            = export_fbx_bin.fbx_animations_do
    backup_fbx_data_armature_elements   = export_fbx_bin.fbx_data_armature_elements
    backup_fbx_data_object_elements     = export_fbx_bin.fbx_data_object_elements
    backup_fbx_data_bindpose_element    = export_fbx_bin.fbx_data_bindpose_element


    # Modified the functions to adapt the fbx output to UE

    SCALE_FACTOR = 100


    SCALE_FACTOR_Blender4 = 100

    export_parameters["global_matrix"] = (
        axis_conversion(
            to_forward=export_parameters['axis_forward'],
            to_up=export_parameters['axis_up'],
        ).to_4x4()
    )

    # Replace the modified functions temporarily in the FBX type is unreal engine
    if fbx_type == 'unreal_engine':

        if bpy.app.version_string[0] < '4':
            print('Exporting with Blender older than 4.0')
            export_fbx_bin.fbx_animations_do            = fbx_animations_do_blender3
            export_fbx_bin.fbx_data_armature_elements   = fbx_data_armature_elements_blender3
            export_fbx_bin.fbx_data_object_elements     = fbx_data_object_elements_blender3
            export_fbx_bin.fbx_data_bindpose_element    = fbx_data_bindpose_element_blender3

        if bpy.app.version_string[0] >= '4':
            print('Exporting with Blender 4.0+')
            export_fbx_bin.fbx_animations_do            = fbx_animations_do_blender4
            export_fbx_bin.fbx_data_armature_elements   = fbx_data_armature_elements_blender4
            export_fbx_bin.fbx_data_object_elements     = fbx_data_object_elements_blender4
            export_fbx_bin.fbx_data_bindpose_element    = fbx_data_bindpose_element_blender4
    
    # Simulate the FBX Export Operator Class
    self = type(
        'FMCExportFBX',
        (object,),
        {'report': print("error")}
    )

    # Export the FBX file
    export_fbx_bin.save(self, bpy.context, **export_parameters)

    # Restore the modified functions with the saved backups if the FBX type is unreal engine
    if fbx_type == 'unreal_engine':
        export_fbx_bin.fbx_animations_do            = backup_fbx_animations_do
        export_fbx_bin.fbx_data_armature_elements   = backup_fbx_data_armature_elements
        export_fbx_bin.fbx_data_object_elements     = backup_fbx_data_object_elements
        export_fbx_bin.fbx_data_bindpose_element    = backup_fbx_data_bindpose_element

    # Restore the name of the rig object
    for capture_object in bpy.data.objects:
        if capture_object.type == "ARMATURE":
            # Restore the original rig name
            capture_object.name = rig_original_name

def apply_foot_locking(
        target_foot: list=['left_foot', 'right_foot'],
        target_base_markers: list=['foot_index', 'heel'],
        z_threshold: float=0.01,
        ground_level: float=0.0,
        frame_window_min_size: int=10,
        initial_attenuation_count: int=5,
        final_attenuation_count: int=5,
        lock_xy_at_ground_level: bool=False,
        knee_hip_compensation_coefficient: float=1.0,
        compensate_upper_body: bool=True)->None:
    
    # Get the scene context
    scene = bpy.context.scene

    # Get current frame
    current_frame = scene.frame_current

    # Update the empties position dictionary with the global positions
    update_empty_positions(position_reference='global')

    # Get the scene start and end frames
    start_frame = scene.frame_start
    end_frame = scene.frame_end

    # Get the relative last frame
    last_frame = end_frame - start_frame

    # Get the transformation matrix of the empties parent object
    empty_parent_matrix = bpy.data.objects['empties_parent'].matrix_world

    # Define the attenuation functions
    initial_attenuation = quadratic_function(
        x1=0,
        x2=(initial_attenuation_count / 2),
        x3=(initial_attenuation_count - 1),
        y1=z_threshold,
        y2=z_threshold - (z_threshold - ground_level) * 3 / 4,
        y3=ground_level)
    
    final_attenuation = quadratic_function(
        x1=0,
        x2=(final_attenuation_count / 2),
        x3=(final_attenuation_count - 1),
        y1=ground_level,
        y2=ground_level + (z_threshold - ground_level) * 3 / 4,
        y3=z_threshold)
    
    # Define the error function to be optimized when adjusting the
    # ankle position
    def error_function(z_C, x_C, y_C, x_A, y_A, z_A, x_B, y_B, z_B, length_A_to_C, length_B_to_C):
        error1 = (x_A - x_C)**2 + (y_A - y_C)**2 + (z_A - z_C)**2 - length_A_to_C**2
        error2 = (x_B - x_C)**2 + (y_B - y_C)**2 + (z_B - z_C)**2 - length_B_to_C**2
        return error1**2 + error2**2
    
    # Set the overall_changed_frames variable to save all the frames
    # that were changed for posterior upper body adjustment
    overall_changed_frames = []

    # Iterate through the foot_locking_markers dictionary
    for foot in foot_locking_markers:
        if foot not in target_foot:
            continue

        # Variable to save the changed frames for later ankle adjustment
        changed_frames = []
        # Update the correspondent virtual bones info
        update_virtual_bones_info(
            target_bone=foot_locking_markers[foot]['bones'][0])
        update_virtual_bones_info(
            target_bone=foot_locking_markers[foot]['bones'][1])

        # Iterate through the base markers
        for base_marker in foot_locking_markers[foot]['base']:
            if base_marker not in [foot.split('_')[0] + '_' + marker
                                   for marker in target_base_markers]:
                continue

            # Set the initial variables
            frame = 0
            window = 0
            final_attenuation_aux = final_attenuation_count

            # Iterate through the animation frames
            while frame < last_frame:
                if empty_positions[base_marker]['z'][frame] < z_threshold:
                    # Marker is under threshold the next frames are checked to conform the window
                    window += 1

                    for following_frame in range(frame + 1, last_frame):
                        if empty_positions[base_marker]['z'][following_frame] < z_threshold:
                            # Following marker is under threshold, the window is increased
                            window += 1
                        if following_frame == last_frame - 1 or empty_positions[base_marker]['z'][following_frame] >= z_threshold:
                            # Following marker is the last one or is not under threshold, the window size is checked
                            if window < frame_window_min_size:
                                # Window is not big enough. Break the cycle and continue from the frame that was over threshold
                                # Before continuing, make sure that no marker is below the ground level
                                for window_frame in range(frame, frame + window):
                                    if empty_positions[base_marker]['z'][window_frame] < ground_level:
                                        # Marker's z position is forced to the ground level
                                        # Get the delta vector on the global z axis
                                        delta_vector = mathutils.Vector([0, 0, ground_level - empty_positions[base_marker]['z'][window_frame]])
                                        # Adjust the delta vector to the empty parent axis
                                        delta_vector_adjusted = delta_vector @ empty_parent_matrix
                                        try:
                                            # Change the marker's local position with the adjusted delta vector
                                            bpy.data.objects[base_marker].animation_data.action.fcurves[0].keyframe_points[start_frame + window_frame].co[1] += delta_vector_adjusted[0]
                                            bpy.data.objects[base_marker].animation_data.action.fcurves[1].keyframe_points[start_frame + window_frame].co[1] += delta_vector_adjusted[1]
                                            bpy.data.objects[base_marker].animation_data.action.fcurves[2].keyframe_points[start_frame + window_frame].co[1] += delta_vector_adjusted[2]
                                            changed_frames.append(start_frame + window_frame)
                                        except AttributeError as e:
                                            print('error:' + str(e))

                                frame = following_frame
                                window = 0
                                break
                            else:
                                # Window is big enough so the locking logic is applied
                                # Initial attenuation is applied
                                for locking_frame in range(frame, frame + initial_attenuation_count):
                                    # Get the z position from the initial attenuation function
                                    new_z_position = round(initial_attenuation(locking_frame - frame), 5)
                                    # Get the delta vector on the global z axis
                                    delta_vector = mathutils.Vector([0, 0, new_z_position - empty_positions[base_marker]['z'][locking_frame]])
                                    # Adjust the delta vector to the empty parent axis
                                    delta_vector_adjusted = delta_vector @ empty_parent_matrix
                                    try:
                                        # Change the marker's local position with the adjusted delta vector
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[0].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[0]
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[1].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[1]
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[2].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[2]
                                        changed_frames.append(start_frame + locking_frame)
                                    except Exception as e:
                                        # Empty does not exist or does not have animation data
                                        print('error:' + str(e))

                                # Check if the window ends at the last frame. If so the final attenuation aux variable is set to zero
                                if following_frame == last_frame - 1:
                                    final_attenuation_aux = 0

                                # If the lock_xy_at_ground_level is True, save the x and y position of the first frame of the next loop
                                if lock_xy_at_ground_level:
                                    ground_level_x = bpy.data.objects[base_marker].animation_data.action.fcurves[0].keyframe_points[start_frame + frame + initial_attenuation_count].co[1]
                                    ground_level_y = bpy.data.objects[base_marker].animation_data.action.fcurves[1].keyframe_points[start_frame + frame + initial_attenuation_count].co[1]
                                
                                # For the frames between the initial attenuation and the final attenuation the z position is set to the ground level
                                for locking_frame in range(frame + initial_attenuation_count, frame + (window - final_attenuation_aux)):
                                    # Get the delta vector on the global z axis consider x and y position if lock_xy_at_ground_level is True
                                    if lock_xy_at_ground_level:
                                        delta_vector = mathutils.Vector([ground_level_x - empty_positions[base_marker]['x'][locking_frame],
                                                                        ground_level_y - empty_positions[base_marker]['y'][locking_frame],
                                                                        ground_level - empty_positions[base_marker]['z'][locking_frame]])
                                    else:
                                        delta_vector = mathutils.Vector([0, 0, ground_level - empty_positions[base_marker]['z'][locking_frame]])

                                    # Adjust the delta vector to the empty parent axis
                                    delta_vector_adjusted = delta_vector @ empty_parent_matrix

                                    try:
                                    # Change the marker's local position with the adjusted delta vector
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[0].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[0]
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[1].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[1]
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[2].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[2]
                                        changed_frames.append(start_frame + locking_frame)
                                    except AttributeError as e:
                                        # Empty does not exist or does not have animation data
                                        print('error:' + str(e))

                                # Final attenuation is applied if final_attenuation_count is greater than zero
                                for locking_frame in range(frame + (window - final_attenuation_aux), frame + window):
                                    # Get the z position from the final attenuation function
                                    new_z_position = round(final_attenuation(locking_frame - (frame + window - final_attenuation_aux)), 5)
                                    # Get the delta vector on the global z axis
                                    delta_vector = mathutils.Vector([0, 0, new_z_position - empty_positions[base_marker]['z'][locking_frame]])
                                    # Adjust the delta vector to the empty parent axis
                                    delta_vector_adjusted = delta_vector @ empty_parent_matrix

                                    try:
                                        # Change the marker's local position with the adjusted delta vector
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[0].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[0]
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[1].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[1]
                                        bpy.data.objects[base_marker].animation_data.action.fcurves[2].keyframe_points[start_frame + locking_frame].co[1] += delta_vector_adjusted[2]
                                        changed_frames.append(start_frame + locking_frame)
                                    except Exception as e:
                                        # Empty does not exist or does not have animation data
                                        print('error:' + str(e))
                                    
                                frame = following_frame
                                window = 0
                                break

                frame += 1

        # Update the empties position dictionary with the global positions
        # for the two base markers
        update_empty_positions(
            target_empty=[foot_locking_markers[foot]['base'][0], foot_locking_markers[foot]['base'][1]],
            position_reference='global'
        )

        # Adjust the ankle marker position in the previous modified frames so the median
        # ankle-foot_index and ankle-heel distances are equal to the median lengths before the change
        for changed_frame in list(set(changed_frames)):
            # Get the initial position variables of the ankle z position's optimization problem
            base_marker_0_x = empty_positions[foot_locking_markers[foot]['base'][0]]['x'][changed_frame - start_frame]
            base_marker_0_y = empty_positions[foot_locking_markers[foot]['base'][0]]['y'][changed_frame - start_frame]
            base_marker_0_z = empty_positions[foot_locking_markers[foot]['base'][0]]['z'][changed_frame - start_frame]
            base_marker_1_x = empty_positions[foot_locking_markers[foot]['base'][1]]['x'][changed_frame - start_frame]
            base_marker_1_y = empty_positions[foot_locking_markers[foot]['base'][1]]['y'][changed_frame - start_frame]
            base_marker_1_z = empty_positions[foot_locking_markers[foot]['base'][1]]['z'][changed_frame - start_frame]

            ankle_marker_x = empty_positions[foot_locking_markers[foot]['ankle'][0]]['x'][changed_frame - start_frame]
            ankle_marker_y = empty_positions[foot_locking_markers[foot]['ankle'][0]]['y'][changed_frame - start_frame]

            base_bone_0_distance = virtual_bones[foot_locking_markers[foot]['bones'][0]]['median']
            base_bone_1_distance = virtual_bones[foot_locking_markers[foot]['bones'][1]]['median']

            #  Get the current ankle z position
            current_ankle_pos = empty_positions[foot_locking_markers[foot]['ankle'][0]]['z'][changed_frame - start_frame]

            # Set the initial ankle z guess as the actual ankle z
            # position. If the initial ankle z guess is not higher than
            # both of the base markers z positions then set the initial
            # ankle z guess to the highest base marker z position plus
            # a margin
            initial_ankle_z_guess = max(current_ankle_pos,
                                        max([base_marker_0_z,
                                             base_marker_1_z]) + 0.1)
                
            # Use scipy.optimize.minimize to minimize the error function
            # and find the optimal z coordinate of C
            result = minimize(error_function,
                              initial_ankle_z_guess,
                              args=(ankle_marker_x,
                                    ankle_marker_y,
                                    base_marker_0_x,
                                    base_marker_0_y,
                                    base_marker_0_z,
                                    base_marker_1_x,
                                    base_marker_1_y,
                                    base_marker_1_z,
                                    base_bone_0_distance,
                                    base_bone_1_distance)
            )

            # Set the new ankle z position
            # Get the delta vector on the global z axis
            delta_vector = mathutils.Vector([0, 0, result.x[0] - empty_positions[foot_locking_markers[foot]['ankle'][0]]['z'][changed_frame - start_frame]])
            # Adjust the delta vector to the empty parent axis
            delta_vector_adjusted = delta_vector @ empty_parent_matrix
            try:
                # Change the marker's local position with the adjusted delta vector
                bpy.data.objects[foot_locking_markers[foot]['ankle'][0]].animation_data.action.fcurves[0].keyframe_points[changed_frame].co[1] += delta_vector_adjusted[0]
                bpy.data.objects[foot_locking_markers[foot]['ankle'][0]].animation_data.action.fcurves[1].keyframe_points[changed_frame].co[1] += delta_vector_adjusted[1]
                bpy.data.objects[foot_locking_markers[foot]['ankle'][0]].animation_data.action.fcurves[2].keyframe_points[changed_frame].co[1] += delta_vector_adjusted[2]
            except AttributeError as e:
                # Empty does not exist or does not have animation data
                print('error:' + str(e))

            # Compensate the knee and the hip markers if knee_hip_compensation_coefficient is not zero
            if knee_hip_compensation_coefficient != 0:
                # Get the delta vector on the global z axis
                ankle_z_delta = mathutils.Vector([0, 0, result.x[0] - current_ankle_pos])
                # Adjust the ankle z delta to the empty parent axis
                ankle_z_delta_adjusted = ankle_z_delta @ empty_parent_matrix
                # Change the compensation markers' z position
                for compensation_marker in foot_locking_markers[foot]['compensation_markers']:
                    try:
                        marker_x_position = bpy.data.objects[compensation_marker].animation_data.action.fcurves[0].keyframe_points[changed_frame].co[1]
                        marker_y_position = bpy.data.objects[compensation_marker].animation_data.action.fcurves[1].keyframe_points[changed_frame].co[1]
                        marker_z_position = bpy.data.objects[compensation_marker].animation_data.action.fcurves[2].keyframe_points[changed_frame].co[1]

                        bpy.data.objects[compensation_marker].animation_data.action.fcurves[0].keyframe_points[changed_frame].co[1] = marker_x_position + ankle_z_delta_adjusted[0] * knee_hip_compensation_coefficient
                        bpy.data.objects[compensation_marker].animation_data.action.fcurves[1].keyframe_points[changed_frame].co[1] = marker_y_position + ankle_z_delta_adjusted[1] * knee_hip_compensation_coefficient
                        bpy.data.objects[compensation_marker].animation_data.action.fcurves[2].keyframe_points[changed_frame].co[1] = marker_z_position + ankle_z_delta_adjusted[2] * knee_hip_compensation_coefficient
                    except Exception as e:
                        # Empty does not exist or does not have animation data
                        print('error:' + str(e))

        # Update the overall_changed_frames list
        overall_changed_frames += list(set(changed_frames))

    if compensate_upper_body:
        # Compensate the upper body markers starting from the hips_center
                    
        # Update the empties position dictionary with the global positions
        # for the two hip markers
        update_empty_positions(
            target_empty=['left_hip', 'right_hip'],
            position_reference='global'
        )

        # Iterate through the overall_changed_frames list
        for changed_frame in list(set(overall_changed_frames)):
            # Get the new hips_center z coordinate as the average of the
            # left and right hip z coordinates
            new_hips_center_z = (empty_positions['left_hip']['z'][changed_frame - start_frame] + empty_positions['right_hip']['z'][changed_frame - start_frame]) / 2
            # Get the delta vector on the global z axis
            hips_center_z_delta = mathutils.Vector([0, 0, new_hips_center_z - empty_positions['hips_center']['z'][changed_frame - start_frame]])
            # Adjust the delta vector to the empty parent axis
            hips_center_z_delta_adjusted = hips_center_z_delta @ empty_parent_matrix

            try:
                # Change the marker's local position with the adjusted delta vector
                bpy.data.objects['hips_center'].animation_data.action.fcurves[0].keyframe_points[changed_frame].co[1] += hips_center_z_delta_adjusted[0]
                bpy.data.objects['hips_center'].animation_data.action.fcurves[1].keyframe_points[changed_frame].co[1] += hips_center_z_delta_adjusted[1]
                bpy.data.objects['hips_center'].animation_data.action.fcurves[2].keyframe_points[changed_frame].co[1] += hips_center_z_delta_adjusted[2]
            except Exception as e:
                # Empty does not exist or does not have animation data
                print('error:' + str(e))

            # Recursevely translate the empties from trunk_center
            translate_empty(
                empties_dict=empties_dict,
                empty='trunk_center',
                frame_index=changed_frame,
                delta=hips_center_z_delta_adjusted,
                recursivity=True)


    # Restore the current frame
    scene.frame_current = current_frame

def retarget_animation(
    source_armature: str,
    target_armature: str,
    bake_animation: bool,
    clear_constraints: bool,
)->None:
    print('Retargeting ' + source_armature + ' to ' + target_armature)

    # Get the scene context
    scene = bpy.context.scene

    # Get a list with the target armature pose bones
    target_armature_pose_bones = [bone.name for bone in bpy.data.objects[target_armature].pose.bones]

    max_bone_count = 0
    target_map_armature = ''

    # Loop through the bone_name_map and check which armature has the most bones
    # of the target armature.
    for armature in bone_name_map:
        count = sum(bone in bone_name_map[armature].values() for bone in target_armature_pose_bones)
        if count > max_bone_count:
            max_bone_count = count
            target_map_armature = armature
        print('armature: ' + armature + ' count: ' + str(count))

    # Print the name of the selected target armature
    print('Selected target armature: ' + target_map_armature)

    # Get the inverse bone_map_dict
    inv_bone_name_map = {value: key for key, value in bone_name_map[target_map_armature].items()}

    # Create a dictionary to store the target bone rolls
    target_bone_rolls = {}

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # Select the target armature
    bpy.data.objects[target_armature].select_set(True)

    # Change to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Loop through the target armature edit bones and save the bone roll
    for bone in bpy.data.objects[target_armature].data.edit_bones:
        target_bone_rolls[bone.name] = bone.roll

    # Change to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Loop through the target armature pose bones and add bone constraints
    # based on the inv_bone_name_map
    for bone in bpy.data.objects[target_armature].pose.bones:
        if bone.name in inv_bone_name_map:
            if inv_bone_name_map[bone.name] == 'pelvis':
                bone_constraint = bone.constraints.new('COPY_LOCATION')
                bone_constraint.target = bpy.data.objects[source_armature]
                bone_constraint.subtarget = 'pelvis'
                bone_constraint.use_offset = True
                bone_constraint.target_space = 'LOCAL'

                bone_constraint = bone.constraints.new('COPY_ROTATION')
                bone_constraint.target = bpy.data.objects[source_armature]
                bone_constraint.subtarget = 'pelvis'
                bone_constraint.mix_mode = 'ADD'
            else:
                bone_constraint = bone.constraints.new('COPY_ROTATION')
                bone_constraint.target = bpy.data.objects[source_armature]
                bone_constraint.subtarget = inv_bone_name_map[bone.name]
                bone_constraint.mix_mode = 'REPLACE'

    # Change the roll of the source armature bones to match the roll of the target armature bones
    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)
    # Select the source armature
    bpy.data.objects[source_armature].select_set(True)
    # Change to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Change source armature bones
    for bone in inv_bone_name_map:
        if bone != 'null' and bone in target_bone_rolls:
            bpy.data.objects[source_armature].data.edit_bones[inv_bone_name_map[bone]].roll = target_bone_rolls[bone]

    # Change to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Adjust source armature hand constraints in target armature special cases
    if 'mixamo' in target_map_armature:
        bpy.data.objects[source_armature].pose.bones['hand.R'].constraints['Locked Track'].track_axis = 'TRACK_X'
        bpy.data.objects[source_armature].pose.bones['hand.L'].constraints['Locked Track'].track_axis = 'TRACK_NEGATIVE_X'

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)
    # Select the target armature
    bpy.data.objects[target_armature].select_set(True)
    # Change to pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Bake the animation on the target armature
    if bake_animation:
        bpy.ops.nla.bake(
            frame_start=scene.frame_start,
            frame_end=scene.frame_end,
            only_selected=False,
            visual_keying=True,
            clear_constraints=clear_constraints,
            bake_types={'POSE'}
        )

    # Change to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
