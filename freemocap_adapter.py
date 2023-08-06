bl_info = {
    'name'          : 'Freemocap Adapter',
    'author'        : 'ajc27',
    'version'       : (1, 1, 3),
    'blender'       : (3, 0, 0),
    'location'      : '3D Viewport > Sidebar > Freemocap Adapter',
    'description'   : 'Add-on to adapt the Freemocap Blender output',
    'category'      : 'Development',
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import EnumProperty
import math as m
import mathutils
import time
import statistics

#######################################################################
### Add-on to adapt the Freemocap Blender output. It can adjust the
### empties position, add a rig and a body mesh. The resulting rig 
### and animation can be imported in platforms like Unreal Engine.
### The rig has a TPose as rest pose for easier retargeting.
### For best results, when the script is ran the empties should be
### forming a standing still pose with arms open similar to A or T Pose
### The body_mesh.ply file should be in the same folder as the
### Blender file before manually opening it.
#######################################################################

# Global Variables
# Variable to save if the function Adjust Empties has been already executed
adjust_empties_executed = False

# Dictionary to save the global vector position of all the empties for every animation frame
empty_positions = {}

# Create a dictionary with all the major bones with their head and tail empties.
# Also add variables to store each frame bone lengths, the median and the stdev.
virtual_bones = {
    'pelvis.R': {
        'head'      : 'hips_center',
        'tail'      : 'right_hip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'pelvis.L': {
        'head'      : 'hips_center',
        'tail'      : 'left_hip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'spine': {
        'head'      : 'hips_center',
        'tail'      : 'trunk_center',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'spine.001': {
        'head'      : 'trunk_center',
        'tail'      : 'neck_center',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'neck': {
        'head'      : 'neck_center',
        'tail'      : 'head_center',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'head_nose': { # Imaginary bone from head center to nose tip to align the face bones 
        'head'      : 'head_center',
        'tail'      : 'nose',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'shoulder.R': {
        'head'      : 'neck_center',
        'tail'      : 'right_shoulder',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'shoulder.L': {
        'head'      : 'neck_center',
        'tail'      : 'left_shoulder',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'upper_arm.R': {
        'head'      : 'right_shoulder',
        'tail'      : 'right_elbow',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'upper_arm.L': {
        'head'      : 'left_shoulder',
        'tail'      : 'left_elbow',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'forearm.R': {
        'head'      : 'right_elbow',
        'tail'      : 'right_wrist',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'forearm.L': {
        'head'      : 'left_elbow',
        'tail'      : 'left_wrist',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'hand.R': {
        'head'      : 'right_wrist',
        'tail'      : 'right_index',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'hand.L': {
        'head'      : 'left_wrist',
        'tail'      : 'left_index',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.01.R': {
        'head'      : 'right_wrist',
        'tail'      : 'right_thumb',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.01.L': {
        'head'      : 'left_wrist',
        'tail'      : 'left_thumb',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.04.R': {
        'head'      : 'right_wrist',
        'tail'      : 'right_pinky',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.04.L': {
        'head'      : 'left_wrist',
        'tail'      : 'left_pinky',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thigh.R': {
        'head'      : 'right_hip',
        'tail'      : 'right_knee',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thigh.L': {
        'head'      : 'left_hip',
        'tail'      : 'left_knee',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'shin.R': {
        'head'      : 'right_knee',
        'tail'      : 'right_ankle',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'shin.L': {
        'head'      : 'left_knee',
        'tail'      : 'left_ankle',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'foot.R': {
        'head'      : 'right_ankle',
        'tail'      : 'right_foot_index',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'foot.L': {
        'head'      : 'left_ankle',
        'tail'      : 'left_foot_index',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'heel.02.R': {
        'head'      : 'right_ankle',
        'tail'      : 'right_heel',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'heel.02.L': {
        'head'      : 'left_ankle',
        'tail'      : 'left_heel',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
}

# Dictionary containing the empty children for each of the capture empties.
# This will be used to correct the position of the empties (and its children) that are outside the bone length interval defined by x*stdev
empties_dict = {
    'hips_center': {
        'children'    : ['right_hip', 'left_hip', 'trunk_center']},
    'trunk_center': {
        'children'    : ['neck_center']},
    'neck_center': {
        'children'    : ['right_shoulder', 'left_shoulder', 'head_center']},
    'head_center': {
        'children'    : ['nose', 'mouth_right', 'mouth_left', 'right_eye', 'right_eye_inner', 'right_eye_outer', 'left_eye', 'left_eye_inner', 'left_eye_outer', 'right_ear', 'left_ear']},
    'right_shoulder': {
        'children'    : ['right_elbow']},
    'left_shoulder': {
        'children'    : ['left_elbow']},
    'right_elbow': {
        'children'    : ['right_wrist']},
    'left_elbow': {
        'children'    : ['left_wrist']},
    'right_wrist': {
        'children'    : ['right_thumb', 'right_index', 'right_pinky', 'right_hand_wrist', 'right_hand_thumb_cmc', 'right_hand_thumb_mcp',
                        'right_hand_thumb_ip', 'right_hand_thumb_tip', 'right_hand_index_finger_mcp', 'right_hand_index_finger_pip', 'right_hand_index_finger_dip',
                        'right_hand_index_finger_tip', 'right_hand_middle_finger_mcp', 'right_hand_middle_finger_pip', 'right_hand_middle_finger_dip',
                        'right_hand_middle_finger_tip', 'right_hand_ring_finger_mcp', 'right_hand_ring_finger_pip', 'right_hand_ring_finger_dip',
                        'right_hand_ring_finger_tip', 'right_hand_pinky_mcp', 'right_hand_pinky_pip', 'right_hand_pinky_dip', 'right_hand_pinky_tip']},
    'left_wrist': {
        'children'    : ['left_thumb', 'left_index', 'left_pinky', 'left_hand_wrist', 'left_hand_thumb_cmc', 'left_hand_thumb_mcp',
                        'left_hand_thumb_ip', 'left_hand_thumb_tip', 'left_hand_index_finger_mcp', 'left_hand_index_finger_pip', 'left_hand_index_finger_dip',
                        'left_hand_index_finger_tip', 'left_hand_middle_finger_mcp', 'left_hand_middle_finger_pip', 'left_hand_middle_finger_dip',
                        'left_hand_middle_finger_tip', 'left_hand_ring_finger_mcp', 'left_hand_ring_finger_pip', 'left_hand_ring_finger_dip',
                        'left_hand_ring_finger_tip', 'left_hand_pinky_mcp', 'left_hand_pinky_pip', 'left_hand_pinky_dip', 'left_hand_pinky_tip']},
    'right_hip': {
        'children'    : ['right_knee']},
    'left_hip': {
        'children'    : ['left_knee']},
    'right_knee': {
        'children'    : ['right_ankle']},
    'left_knee': {
        'children'    : ['left_ankle']},
    'right_ankle': {
        'children'    : ['right_foot_index', 'right_heel']},
    'left_ankle': {
        'children'    : ['left_foot_index', 'left_heel']}
}

# Function to update all the empties positions in the dictionary
def update_empty_positions():

    print('Updating Empty Positions Dictionary...')

    # Get the scene context
    scene = bpy.context.scene

    # Change to Object Mode
    bpy.ops.object.mode_set(mode="OBJECT")

    # Reset the empty positions dictionary with empty arrays for each empty
    for object in bpy.data.objects:
        if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin':
            empty_positions[object.name] = {'x': [], 'y': [], 'z': []}

    # Iterate through each scene frame and save the coordinates of each empty in the dictionary
    for frame in range (scene.frame_start, scene.frame_end + 1):
        # Set scene frame
        scene.frame_set(frame)
        # Iterate through each object
        for object in bpy.data.objects:
            if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin':
                # Save the x, y, z position of the empty
                empty_positions[object.name]['x'].append(bpy.data.objects[object.name].location[0])
                empty_positions[object.name]['y'].append(bpy.data.objects[object.name].location[1])
                empty_positions[object.name]['z'].append(bpy.data.objects[object.name].location[2])

    # Reset the scene frame to the start
    scene.frame_set(scene.frame_start)

    print('Empty Positions Dictionary update completed.')

# Function to update all the information of the virtual bones dictionary (lengths, median and stdev)
def update_virtual_bones_info():

    print('Updating Virtual Bones Information...')

    # Reset the lengths list for every virtual bone
    for bone in virtual_bones:
        virtual_bones[bone]['lengths'] = []

    # Iterate through the empty_positions dictionary and calculate the distance between the head and tail and append it to the lengths list
    for frame in range (0, len(empty_positions['hips_center']['x'])):

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
        virtual_bones[bone]['median'] = statistics.median(virtual_bones[bone]['lengths'])
        virtual_bones[bone]['stdev'] = statistics.stdev(virtual_bones[bone]['lengths'])

    print('Virtual Bones Information update completed.')

######################################################################
######################### ADJUST EMPTIES #############################
######################################################################

def adjust_empties(z_align_ref_empty: str='left_knee',
                   z_align_angle_offset: float=0,
                   ground_ref_empty: str='left_foot_index',
                   z_translation_offset: float=-0.01,
                   ):
    
    # Reference to the global adjust_empties_executed variable
    global adjust_empties_executed

    # Play and stop the animation in case the first frame empties are in a strange position
    bpy.ops.screen.animation_play()
    bpy.ops.screen.animation_cancel()

    ### Delete sphere meshes ###
    for object in bpy.data.objects:
        if "sphere" in object.name:
            bpy.data.objects.remove(object, do_unlink=True)

    ### Unparent empties from freemocap_origin_axes ###
    for object in bpy.data.objects:
        if object.type == "EMPTY" and object.name != "freemocap_origin_axes" and object.name != "world_origin":
            object.parent = None

    ### Move freemocap_origin_axes to the hips_center empty and rotate it so the ###
    ### z axis intersects the trunk_center empty and the x axis intersects the left_hip empty ###
    origin = bpy.data.objects['freemocap_origin_axes']
    hips_center = bpy.data.objects['hips_center']

    left_hip = bpy.data.objects['left_hip']

    # Move origin to hips_center
    origin.location = hips_center.location
    # Rotate origin in the xy plane so its x axis crosses the vertical projection of left_hip
    # Obtain left_hip location
    left_hip_location = left_hip.location
    # Calculate left_hip xy coordinates from origin location
    left_hip_x_from_origin = left_hip_location[0] - origin.location[0]
    left_hip_y_from_origin = left_hip_location[1] - origin.location[1]
    # Calculate angle from origin x axis to projection of left_hip on xy plane. It will depend if left_hip_x_from_origin is positive or negative
    left_hip_xy_angle_prev  = m.atan(left_hip_y_from_origin / left_hip_x_from_origin)
    left_hip_xy_angle       = left_hip_xy_angle_prev if left_hip_x_from_origin >= 0 else m.radians(180) + left_hip_xy_angle_prev
    # Rotate origin around the z axis to point at left_hip
    origin.rotation_euler[2] = left_hip_xy_angle

    # Calculate left_hip z position from origin
    left_hip_z_from_origin = left_hip_location[2] - origin.location[2]
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

    ### Reparent all the capture empties to the origin (freemocap_origin_axes) ###
    for object in bpy.data.objects:
        if object.type == "EMPTY" and object.name != "freemocap_origin_axes" and object.name != "world_origin":
            # Select empty
            object.select_set(True)

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

    # Change the adjust_empties_executed variable
    adjust_empties_executed = True

######################################################################
#################### REDUCE BONE LENGTH DISPERSION ###################
######################################################################

def reduce_bone_length_dispersion(interval_variable: str='median', interval_factor: float=0.01):

    # Update the empty positions dictionary
    update_empty_positions()

    # Update the information of the virtual bones
    update_virtual_bones_info()

    # Print the current bones length median, standard deviation and coefficient of variation
    print('Current Virtual Bone Information:')
    print('{:<12} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
    for bone in virtual_bones:
        print('{:<12} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(virtual_bones[bone]['median']*100*10000000)/10000000), str(m.trunc(virtual_bones[bone]['stdev']*100*10000000)/10000000), str(m.trunc(virtual_bones[bone]['stdev']/virtual_bones[bone]['median']*100*10000)/10000)))

    # Iterate through the lengths array of each bone and check if the length is outside the interval defined by x*stdev with x as a factor
    # If the bone length is outside the interval, adjust the coordinates of the tail empty and its children so the new bone length is at the border of the interval
    empties_positions_corrected = 0

    for bone in virtual_bones:
        
        frame_index = 0

        for length in virtual_bones[bone]['lengths']:
        
            # Check if bone length is outside interval
            median          = virtual_bones[bone]['median']
            stdev           = virtual_bones[bone]['stdev']
            # Calculate inferior and superior interval limit depending on interval variable
            if interval_variable == 'median':
                # Fix interval_factor to 1 in case is greater than 1
                if interval_factor > 1:
                    interval_factor = 1
                # Calculate limits
                inferior_limit  = median * (1 - interval_factor)
                superior_limit  = median * (1 + interval_factor)
            elif interval_variable == 'stdev':
                # Fix interval_factor to median/stdev in case is greater than median/stdev
                if interval_factor > (median/stdev):
                    interval_factor = median / stdev
                # Calculate limits
                inferior_limit  = median - interval_factor * stdev
                superior_limit  = median + interval_factor * stdev

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
                # Translate the tail empty and its children by the position delta
                translate_empty(empties_dict, tail, frame_index, position_delta)

                empties_positions_corrected += 1
            
            frame_index += 1
    
    # Update the empty positions dictionary
    update_empty_positions()

    # Update the information of the virtual bones
    update_virtual_bones_info()

    # Print the new bones length median, standard deviation and coefficient of variation
    print('New Virtual Bone Information:')
    print('{:<12} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
    for bone in virtual_bones:
        print('{:<12} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(virtual_bones[bone]['median']*100*10000000)/10000000), str(m.trunc(virtual_bones[bone]['stdev']*100*10000000)/10000000), str(m.trunc(virtual_bones[bone]['stdev']/virtual_bones[bone]['median']*100*10000)/10000)))

    print('Total empties positions corrected: ' + str(empties_positions_corrected))

# Function to translate the empties recursively
def translate_empty(empties_dict, empty, frame_index, delta):

    # Translate the empty in the animation location curve
    actual_x = bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1]
    bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1] = actual_x + delta[0]
    actual_y = bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1]
    bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1] = actual_y + delta[1]
    actual_z = bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1]
    bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1] = actual_z + delta[2]

    # If empty has children then call this function for every child
    if empty in empties_dict:
        for child in empties_dict[empty]['children']:
            translate_empty(empties_dict, child, frame_index, delta)

######################################################################
############################# ADD RIG ################################
######################################################################

def add_rig(bone_length_method: str='median_length', keep_symmetry: bool=False, use_limit_rotation: bool=False):

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # If there is an existing metarig, delete it
    try:
        print('Deleting previous metarigs...')
        for object in bpy.data.objects:
            if object.type == "ARMATURE" :
                bpy.data.objects.remove(object, do_unlink=True)
    except:
        print('No existing metarigs to delete')

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

    if bone_length_method == 'median_length':

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

        # Apply transformations to rig (scale must be (1, 1, 1) so it doesn't fail on send2ue export
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
        heel_02_R.length    = heel_02_R_length
        heel_02_L.head      = (pelvis_L_length, heel_02_L.head[1], heel_02_L.head[2])
        heel_02_L.length    = heel_02_L_length

        # Make the heel bones be connected with the shin bones
        heel_02_R.parent        = shin_R
        heel_02_R.use_connect   = True
        heel_02_L.parent        = shin_L
        heel_02_L.use_connect   = True

        # Add a pelvis bone to the root and then make it the parent of spine, pelvis.R and pelvis.L bones
        pelvis = rig.data.edit_bones.new('pelvis')
        pelvis.head = spine.head
        pelvis.tail = spine.head + mathutils.Vector([0, 0.1, 0])

        # Change the pelvis.R, pelvis.L, thigh.R, thigh.L and spine parent to the new pelvis bone
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

        # Change to Pose Mode to rotate the arms and make a T Pose for posterior retargeting
        bpy.ops.object.mode_set(mode='POSE')
        pose_upper_arm_R = rig.pose.bones['upper_arm.R']
        pose_upper_arm_R.rotation_mode  = 'XYZ'
        pose_upper_arm_R.rotation_euler = (0,0,m.radians(-29))
        pose_upper_arm_R.rotation_mode  = 'QUATERNION'
        pose_upper_arm_L = rig.pose.bones['upper_arm.L']
        pose_upper_arm_L.rotation_mode  = 'XYZ'
        pose_upper_arm_L.rotation_euler = (0,0,m.radians(29))
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

        # Calculate the y and z offset of the nose.001 bone tail using the imaginary head_nose bone. Assume a 18º of declination angle
        nose_y_offset = -virtual_bones['head_nose']['median'] * m.cos(m.radians(18)) - nose_001.tail[1]
        nose_z_offset = (spine_004.tail[2] - virtual_bones['head_nose']['median'] * m.sin(m.radians(18))) - nose_001.tail[2]
        
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
                
        # Move the face bone head to align it horizontally
        face.head[1] = spine_004.tail[1]
        face.head[2] = face.tail[2]
        face.tail[1] = face.head[1] - (virtual_bones['head_nose']['median'] * m.cos(m.radians(18)) / 2)

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

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='OBJECT')

    elif bone_length_method == 'current_frame':

        print('Adding rig with current frame length method...')

        # Scale armature so it fits the capture empties height in a standing position. The reference point will be hips_center
        # Get the rig z dimension
        rig_z_dimension = rig.dimensions.z
        # Get hips_center global position
        hips_center_glob_pos = bpy.data.objects['hips_center'].matrix_world.translation
        # Get the rig thigh.R bone head z position (this will be aligned with the hips_center empty
        thigh_r_z_pos = (rig.matrix_world @ rig.pose.bones['thigh.R'].head)[2]
        # Calculate the proportion between the hips_center z pos and the thigh_r_z_pos
        hips_center_to_thigh_R = hips_center_glob_pos[2] / thigh_r_z_pos

        # Scale the rig by the hips_center_z and the thigh_r_z_pos proportion
        rig.scale = (hips_center_to_thigh_R, hips_center_to_thigh_R, hips_center_to_thigh_R)
        # Apply transformations to rig (scale must be (1, 1, 1) so it doesn't fail on send2ue export
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

        # Move spine and pelvis bones head to hips_center location
        spine.head      = hips_center_glob_pos
        pelvis_R.head   = hips_center_glob_pos
        pelvis_L.head   = hips_center_glob_pos
        # Align each pelvis bone tail to its corresponding hip empty
        right_hip_glob_pos = bpy.data.objects['right_hip'].matrix_world.translation
        left_hip_glob_pos = bpy.data.objects['left_hip'].matrix_world.translation
        pelvis_R.tail = right_hip_glob_pos
        pelvis_L.tail = left_hip_glob_pos
        
        # Calculate the length of the thighs as the average distance between the hips and knees empties
        # Get global position of knee empties
        right_knee_glob_pos = bpy.data.objects['right_knee'].matrix_world.translation
        left_knee_glob_pos  = bpy.data.objects['left_knee'].matrix_world.translation
        # Get average distance
        thigh_length = (m.dist(right_hip_glob_pos, right_knee_glob_pos) + m.dist(left_hip_glob_pos, left_knee_glob_pos)) / 2
        # Move the thighs tail in the z axis
        thigh_R.tail[2] = right_hip_glob_pos[2] - thigh_length
        thigh_L.tail[2] = left_hip_glob_pos[2] - thigh_length
        
        # Calculate the length of the shins as the average distance between the knees and ankle empties
        # Get global position of ankle empties
        right_ankle_glob_pos = bpy.data.objects['right_ankle'].matrix_world.translation
        left_ankle_glob_pos  = bpy.data.objects['left_ankle'].matrix_world.translation
        # Get average distance
        shin_length = (m.dist(right_knee_glob_pos, right_ankle_glob_pos) + m.dist(left_knee_glob_pos, left_ankle_glob_pos)) / 2
        # Move the shins tail in the z axis
        shin_R.tail[2] = shin_R.head[2] - shin_length
        shin_L.tail[2] = shin_L.head[2] - shin_length
        
        # Calculate the distance between thighs bone heads and the corresponding hip empty in the x and y axes
        thigh_R_head_x_offset = right_hip_glob_pos[0] - thigh_R.head[0]
        thigh_R_head_y_offset = right_hip_glob_pos[1] - thigh_R.head[1]
        thigh_L_head_x_offset = left_hip_glob_pos[0] - thigh_L.head[0]
        thigh_L_head_y_offset = left_hip_glob_pos[1] - thigh_L.head[1]

        # Translate the entire legs using the previous offsets
        
        # Right leg
        thigh_R.head[0]     += thigh_R_head_x_offset
        thigh_R.head[1]     += thigh_R_head_y_offset
        thigh_R.tail[0]     += thigh_R_head_x_offset
        # Align the thigh vertically
        thigh_R.tail[1]     = thigh_R.head[1]
        shin_R.tail[0]      += thigh_R_head_x_offset
        shin_R.tail[1]      += thigh_R_head_y_offset
        foot_R.tail[0]      += thigh_R_head_x_offset
        toe_R.tail[0]       += thigh_R_head_x_offset
        heel_02_R.head[0]   += thigh_R_head_x_offset
        heel_02_R.head[1]   += thigh_R_head_y_offset
        heel_02_R.tail[0]   += thigh_R_head_x_offset
        heel_02_R.tail[1]   += thigh_R_head_y_offset
        
        # Move the right heel so its bone head aligns with the right ankle in the x axis
        heel_02_R_head_x_offset = shin_R.tail[0] - heel_02_R.head[0]
        heel_02_R.head[0] += heel_02_R_head_x_offset
        heel_02_R.tail[0] += heel_02_R_head_x_offset
        # Make the heel bone be connected with the shin bone
        heel_02_R.use_connect    = True
            
        # Left leg
        thigh_L.head[0]     += thigh_L_head_x_offset
        thigh_L.head[1]     += thigh_L_head_y_offset
        thigh_L.tail[0]     += thigh_L_head_x_offset
        # Align the thigh vertically
        thigh_L.tail[1]     = thigh_L.head[1]
        shin_L.tail[0]      += thigh_L_head_x_offset
        shin_L.tail[1]      += thigh_L_head_y_offset
        foot_L.tail[0]      += thigh_L_head_x_offset
        toe_L.tail[0]       += thigh_L_head_x_offset
        heel_02_L.head[0]   += thigh_L_head_x_offset
        heel_02_L.head[1]   += thigh_L_head_y_offset
        heel_02_L.tail[0]   += thigh_L_head_x_offset
        heel_02_L.tail[1]   += thigh_L_head_y_offset

        # Move the left heel so its bone head aligns with the left ankle in the x axis
        heel_02_L_head_x_offset = shin_L.tail[0] - heel_02_L.head[0]
        heel_02_L.head[0] += heel_02_L_head_x_offset
        heel_02_L.tail[0] += heel_02_L_head_x_offset
        # Make the heel bone be connected with the shin bone
        heel_02_L.use_connect    = True

        # Add a pelvis bone to the root and then make it the parent of spine, pelvis.R and pelvis.L bones
        pelvis = rig.data.edit_bones.new('pelvis')
        pelvis.head = hips_center_glob_pos
        pelvis.tail = hips_center_glob_pos + mathutils.Vector([0, 0.1, 0])

        # Change the pelvis.R, pelvis.L, thigh.R, thigh.L and spine parent to the new pelvis bone
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
        spine_003.parent = spine
        spine_003.use_connect = True
        # Remove spine.001 and spine.002 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.001'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.002'])

        # Rename spine.003 to spine.001
        rig.data.edit_bones['spine.003'].name = "spine.001"
        spine_001 = rig.data.edit_bones['spine.001']

        # Calculate the distance between the hips_center empty and the trunk_center empty
        # This distance will be the length of the spine bone
        # Get trunk_center global position
        trunk_center_glob_pos = bpy.data.objects['trunk_center'].matrix_world.translation
        # Get distance to hips_center empty
        spine_length = m.dist(trunk_center_glob_pos, hips_center_glob_pos)
        
        # Change spine tail position values
        spine.tail[1] = spine.head[1]
        spine.tail[2] = spine.head[2] + spine_length

        # Calculate the distance between the trunk_center empty and the neck_center empty
        # This distance will be the length of the spine.001 bone
        # Get neck_center global position
        neck_center_glob_pos = bpy.data.objects['neck_center'].matrix_world.translation
        # Get distance to trunk_center empty
        spine_001_length = m.dist(neck_center_glob_pos, trunk_center_glob_pos)

        # Change spine.001 tail position values
        spine_001.tail[1] = spine_001.head[1]
        spine_001.tail[2] = spine_001.head[2] + spine_001_length

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
        
        # Calculate the shoulders length as the average of the distance between neck_center empty and shoulder empties
        # Get global position of shoulder empties
        right_shoulder_glob_pos = bpy.data.objects['right_shoulder'].matrix_world.translation
        left_shoulder_glob_pos  = bpy.data.objects['left_shoulder'].matrix_world.translation
        # Get average distance
        shoulder_length = (m.dist(neck_center_glob_pos, right_shoulder_glob_pos) + m.dist(neck_center_glob_pos, left_shoulder_glob_pos)) / 2
        # Move the shoulder tail in the x axis
        shoulder_R.tail[0] = spine_001.tail[0] - shoulder_length
        shoulder_L.tail[0] = spine_001.tail[0] + shoulder_length
        
        # Calculate the upper_arms head x and z offset from the shoulder_R tail. This to raise and adjust the arms and hands by that offset
        upper_arm_R_x_offset = shoulder_R.tail[0] - upper_arm_R.head[0]
        upper_arm_R_z_offset = spine_001.tail[2] - upper_arm_R.head[2]
        
        upper_arm_R.head[2] += upper_arm_R_z_offset
        upper_arm_R.tail[2] += upper_arm_R_z_offset
        upper_arm_R.head[0] += upper_arm_R_x_offset
        upper_arm_R.tail[0] += upper_arm_R_x_offset
        for bone in upper_arm_R.children_recursive:
            if not bone.use_connect:
                bone.head[0] += upper_arm_R_x_offset
                bone.tail[0] += upper_arm_R_x_offset
                bone.head[2] += upper_arm_R_z_offset
                bone.tail[2] += upper_arm_R_z_offset
            else:
                bone.tail[0] += upper_arm_R_x_offset
                bone.tail[2] += upper_arm_R_z_offset
                
        upper_arm_L.head[2] += upper_arm_R_z_offset
        upper_arm_L.tail[2] += upper_arm_R_z_offset
        upper_arm_L.head[0] -= upper_arm_R_x_offset
        upper_arm_L.tail[0] -= upper_arm_R_x_offset
        for bone in upper_arm_L.children_recursive:
            if not bone.use_connect:
                bone.head[0] -= upper_arm_R_x_offset
                bone.tail[0] -= upper_arm_R_x_offset
                bone.head[2] += upper_arm_R_z_offset
                bone.tail[2] += upper_arm_R_z_offset
            else:
                bone.tail[0] -= upper_arm_R_x_offset
                bone.tail[2] += upper_arm_R_z_offset

        # Align the y position of breasts, shoulders, arms and hands to the y position of the spine.001 tail
        # Calculate the breasts head y offset from the spine.001 tail
        breast_y_offset = spine_001.tail[1] - breast_R.head[1]
        # Move breast by the y offset
        breast_R.head[1] += breast_y_offset
        breast_R.tail[1] += breast_y_offset
        breast_L.head[1] += breast_y_offset
        breast_L.tail[1] += breast_y_offset

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
        hand_y_offset = arms_bones_y_pos - hand_R.head[1]

        # Move hands and its children by the y offset (forearm tail is moved by hand head)
        hand_R.head[1] += hand_y_offset
        hand_R.tail[1] += hand_y_offset
        for bone in hand_R.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_y_offset
                bone.tail[1] += hand_y_offset
            else:
                bone.tail[1] += hand_y_offset
                
        hand_L.head[1] += hand_y_offset
        hand_L.tail[1] += hand_y_offset
        for bone in hand_L.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_y_offset
                bone.tail[1] += hand_y_offset
            else:
                bone.tail[1] += hand_y_offset

        # Change to Pose Mode to rotate the arms and make a T Pose for posterior retargeting
        bpy.ops.object.mode_set(mode='POSE')
        pose_upper_arm_R = rig.pose.bones['upper_arm.R']
        pose_upper_arm_R.rotation_mode  = 'XYZ'
        pose_upper_arm_R.rotation_euler = (0,0,m.radians(-29))
        pose_upper_arm_R.rotation_mode  = 'QUATERNION'
        pose_upper_arm_L = rig.pose.bones['upper_arm.L']
        pose_upper_arm_L.rotation_mode  = 'XYZ'
        pose_upper_arm_L.rotation_euler = (0,0,m.radians(29))
        pose_upper_arm_L.rotation_mode  = 'QUATERNION'
        pose_forearm_R = rig.pose.bones['forearm.R']
        pose_forearm_R.rotation_mode    = 'XYZ'
        pose_forearm_R.rotation_euler   = (0,0,m.radians(-4))
        pose_forearm_R.rotation_mode    = 'QUATERNION'
        pose_forearm_L = rig.pose.bones['forearm.L']
        pose_forearm_L.rotation_mode    = 'XYZ'
        pose_forearm_L.rotation_euler   = (0,0,m.radians(4))
        pose_forearm_L.rotation_mode    = 'QUATERNION'
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
        
        upper_arm_R     = rig.data.edit_bones['upper_arm.R']
        upper_arm_L     = rig.data.edit_bones['upper_arm.L']
        forearm_R       = rig.data.edit_bones['forearm.R']
        forearm_L       = rig.data.edit_bones['forearm.L']
        
        # Calculate the length of the upper_arms as the average distance between the shoulder and elbow empties
        # Get global position of elbow empties
        right_elbow_glob_pos = bpy.data.objects['right_elbow'].matrix_world.translation
        left_elbow_glob_pos  = bpy.data.objects['left_elbow'].matrix_world.translation
        # Get average distance
        upper_arm_length = (m.dist(right_shoulder_glob_pos, right_elbow_glob_pos) + m.dist(left_shoulder_glob_pos, left_elbow_glob_pos)) / 2
        # Move the upper_arm tail in the x axis
        upper_arm_R.tail[0] = upper_arm_R.head[0] - upper_arm_length
        upper_arm_L.tail[0] = upper_arm_L.head[0] + upper_arm_length
        
        # Calculate the length of the forearms as the average distance between the elbow and wrist empties
        # Get global position of wrist empties
        right_wrist_glob_pos = bpy.data.objects['right_wrist'].matrix_world.translation
        left_wrist_glob_pos  = bpy.data.objects['left_wrist'].matrix_world.translation
        # Get average distance
        forearm_length = (m.dist(right_elbow_glob_pos, right_wrist_glob_pos) + m.dist(left_elbow_glob_pos, left_wrist_glob_pos)) / 2
        
        # Calculate the x axis offset of the current forearm tail x position and the forearm head x position plus the calculated forearm length
        # This is to move the forearm tail and all the hand bones
        forearm_tail_x_offset = (forearm_R.head[0] - forearm_length) - forearm_R.tail[0]
        
        # Move forearms tail and its children by the x offset
        forearm_R.tail[0] += forearm_tail_x_offset
        for bone in forearm_R.children_recursive:
            if not bone.use_connect:
                bone.head[0] += forearm_tail_x_offset
                bone.tail[0] += forearm_tail_x_offset
            else:
                bone.tail[0] += forearm_tail_x_offset
                
        forearm_L.tail[0] -= forearm_tail_x_offset
        for bone in forearm_L.children_recursive:
            if not bone.use_connect:
                bone.head[0] -= forearm_tail_x_offset
                bone.tail[0] -= forearm_tail_x_offset
            else:
                bone.tail[0] -= forearm_tail_x_offset

        ### Adjust the position of the neck, head and face bones ###
        spine_001   = rig.data.edit_bones['spine.001']
        spine_004   = rig.data.edit_bones['spine.004']
        nose        = rig.data.edit_bones['nose']

        # Set spine.004 bone head position equal to the spine.001 tail
        spine_004.head = (spine_001.tail[0], spine_001.tail[1], spine_001.tail[2])
        
        # Calculate the distance between the neck_center empty and the head_center empty
        # This distance will be the length of the spine.004 (neck) bone
        # Get head_center global position
        head_center_glob_pos = bpy.data.objects['head_center'].matrix_world.translation
        # Get distance to trunk_center empty
        spine_004_length = m.dist(head_center_glob_pos, neck_center_glob_pos)
        
        # Change spine.004 tail position values
        spine_004.tail[1] = spine_004.head[1]
        spine_004.tail[2] = spine_004.head[2] + spine_004_length

        # Change the parent of the face bone for the spine.004 bone
        face = rig.data.edit_bones['face']
        face.parent = spine_004
        face.use_connect = False

        # Remove spine.005 and spine.006 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.005'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.006'])

        # Calculate the y and z offset of the nose bone tail to the spine.004 bone tail
        # Get nose empty global position
        nose_glob_pos = bpy.data.objects['nose'].matrix_world.translation
        # Get the distance between nose empty and head_center empty
        nose_to_head_center = m.dist(nose_glob_pos, head_center_glob_pos)

        nose_y_offset = (spine_004.tail[1] - nose_to_head_center) - nose.tail[1]
        nose_z_offset = nose_glob_pos[2] - nose.tail[2]

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
                
        # Move the face bone head to align it horizontally
        face.head[1] = spine_004.tail[1]
        face.head[2] = face.tail[2]
        face.tail[1] = face.head[1] - nose_to_head_center / 2

        # Rename spine.004 to neck
        rig.data.edit_bones['spine.004'].name = "neck"

        # Rotate the spine and neck bones to complete the TPOSE
        bpy.ops.object.mode_set(mode='POSE')

        pose_spine = rig.pose.bones['spine']
        pose_spine.rotation_mode    = 'XYZ'
        pose_spine.rotation_euler   = (m.radians(4), 0, 0)
        pose_spine.rotation_mode    = 'QUATERNION'
        pose_spine_001 = rig.pose.bones['spine.001']
        pose_spine_001.rotation_mode    = 'XYZ'
        pose_spine_001.rotation_euler   = (m.radians(-12), 0, 0)
        pose_spine_001.rotation_mode    = 'QUATERNION'
        pose_neck = rig.pose.bones['neck']
        pose_neck.rotation_mode    = 'XYZ'
        pose_neck.rotation_euler   = (m.radians(7), 0, 0)
        pose_neck.rotation_mode    = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='OBJECT')

    ### Add bone constrains ###
    print('Adding bone constraints...')
    # Change to pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Create a dictionary with the different bone constraints
    constraints = {
        "pelvis": [
            {'type':'COPY_LOCATION','target':'hips_center'},
            {'type':'LOCKED_TRACK','target':'right_hip','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Z','influence':1.0}],
        "pelvis.R": [
            {'type':'DAMPED_TRACK','target':'right_hip','track_axis':'TRACK_Y'}],
        "pelvis.L": [
            {'type':'DAMPED_TRACK','target':'left_hip','track_axis':'TRACK_Y'}],
        "spine": [
            {'type':'COPY_LOCATION','target':'hips_center'},
            {'type':'DAMPED_TRACK','target':'trunk_center','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':68,'use_limit_y':True,'min_y':-45,'max_y':45,'use_limit_z':True,'min_z':-30,'max_z':30,'owner_space':'LOCAL'}],
        "spine.001": [
            {'type':'DAMPED_TRACK','target':'neck_center','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_shoulder','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':22,'use_limit_y':True,'min_y':-45,'max_y':45,'use_limit_z':True,'min_z':-30,'max_z':30,'owner_space':'LOCAL'}],
        "neck": [
            {'type':'DAMPED_TRACK','target':'head_center','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'nose','track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-37,'max_x':22,'use_limit_y':True,'min_y':-45,'max_y':45,'use_limit_z':True,'min_z':-30,'max_z':30,'owner_space':'LOCAL'}],
        "face": [
            {'type':'DAMPED_TRACK','target':'nose','track_axis':'TRACK_Y'}],
        "shoulder.R": [
            {'type':'COPY_LOCATION','target':'neck_center'},
            {'type':'DAMPED_TRACK','target':'right_shoulder','track_axis':'TRACK_Y'}],
        "shoulder.L": [
            {'type':'COPY_LOCATION','target':'neck_center'},
            {'type':'DAMPED_TRACK','target':'left_shoulder','track_axis':'TRACK_Y'}],
        "upper_arm.R": [
            {'type':'DAMPED_TRACK','target':'right_elbow','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-135,'max_x':90,'use_limit_y':True,'min_y':-98,'max_y':180,'use_limit_z':True,'min_z':-97,'max_z':91,'owner_space':'LOCAL'}],
        "upper_arm.L": [
            {'type':'DAMPED_TRACK','target':'left_elbow','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-135,'max_x':90,'use_limit_y':True,'min_y':-180,'max_y':98,'use_limit_z':True,'min_z':-91,'max_z':97,'owner_space':'LOCAL'}],
        "forearm.R": [
            {'type':'DAMPED_TRACK','target':'right_wrist','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':0,'max_y':146,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "forearm.L": [
            {'type':'DAMPED_TRACK','target':'left_wrist','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':-146,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "hand.R": [
            {'type':'DAMPED_TRACK','target':'right_index','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_thumb','track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':0.8},
            {'type':'LOCKED_TRACK','target':'right_thumb','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Y','influence':0.2},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-36,'max_y':25,'use_limit_z':True,'min_z':-86,'max_z':90,'owner_space':'LOCAL'}],
        "hand.L": [
            {'type':'DAMPED_TRACK','target':'left_index','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'left_thumb','track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':0.8},
            {'type':'LOCKED_TRACK','target':'left_thumb','track_axis':'TRACK_X','lock_axis':'LOCK_Y','influence':0.2},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-25,'max_y':36,'use_limit_z':True,'min_z':-90,'max_z':86,'owner_space':'LOCAL'}],
        "thigh.R": [
            {'type':'COPY_LOCATION','target':'right_hip'},
            {'type':'DAMPED_TRACK','target':'right_knee','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-155,'max_x':45,'use_limit_y':True,'min_y':-105,'max_y':85,'use_limit_z':True,'min_z':-88,'max_z':17,'owner_space':'LOCAL'}],
        "thigh.L": [
            {'type':'COPY_LOCATION','target':'left_hip'},
            {'type':'DAMPED_TRACK','target':'left_knee','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-155,'max_x':45,'use_limit_y':True,'min_y':-85,'max_y':105,'use_limit_z':True,'min_z':-17,'max_z':88,'owner_space':'LOCAL'}],
        "shin.R": [
            {'type':'DAMPED_TRACK','target':'right_ankle','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "shin.L": [
            {'type':'DAMPED_TRACK','target':'left_ankle','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "foot.R": [
            {'type':'DAMPED_TRACK','target':'right_foot_index','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-31,'max_x':63,'use_limit_y':True,'min_y':-26,'max_y':26,'use_limit_z':True,'min_z':-15,'max_z':74,'owner_space':'LOCAL'}],
        "foot.L": [
            {'type':'DAMPED_TRACK','target':'left_foot_index','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-31,'max_x':63,'use_limit_y':True,'min_y':-26,'max_y':26,'use_limit_z':True,'min_z':-74,'max_z':15,'owner_space':'LOCAL'}],
        "heel.02.R": [
            {'type':'DAMPED_TRACK','target':'right_heel','track_axis':'TRACK_Y'}],
        "heel.02.L": [
            {'type':'DAMPED_TRACK','target':'left_heel','track_axis':'TRACK_Y'}],
    }

    # Create each constraint
    for bone in constraints:
        for cons in constraints[bone]:
            # Add new constraint determined by type
            if not use_limit_rotation and cons['type'] == 'LIMIT_ROTATION':
                continue
            else:
                bone_cons = rig.pose.bones[bone].constraints.new(cons['type'])            
            
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
                pass
            elif cons['type'] == 'COPY_LOCATION':
                bone_cons.target        = bpy.data.objects[cons['target']]
            elif cons['type'] == 'LOCKED_TRACK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.track_axis    = cons['track_axis']
                bone_cons.lock_axis     = cons['lock_axis']
                bone_cons.influence     = cons['influence']
            elif cons['type'] == 'DAMPED_TRACK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.track_axis    = cons['track_axis']

    ### Bake animation to the rig ###
    # Get the empties ending frame
    ending_frame = int(bpy.data.actions[0].frame_range[1])
    # Bake animation
    bpy.ops.nla.bake(frame_start=1, frame_end=ending_frame, bake_types={'POSE'})

    # Change back to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
######################################################################
######################## ADD MESH TO ARMATURE ########################
######################################################################

def add_mesh_to_rig(body_mesh_mode: str="file"):
    
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
    
        # Apply transformations to body_mesh (scale must be (1, 1, 1) so it doesn't fail on send2ue export
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
        
    elif body_mesh_mode == "custom":
    
        # Get reference to armature
        rig = bpy.data.objects['root']

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
        thigh_R     = rig.data.edit_bones['thigh.R']
        thigh_L     = rig.data.edit_bones['thigh.L']
        shin_R      = rig.data.edit_bones['shin.R']
        shin_L      = rig.data.edit_bones['shin.L']
        foot_R      = rig.data.edit_bones['foot.R']
        foot_L      = rig.data.edit_bones['foot.L']

        # Calculate parameters of the different body meshes
        trunk_mesh_radius           = shoulder_R.length
        trunk_mesh_depth            = spine_001.tail[2] - spine.head[2] + 0.02
        trunk_mesh_location         = (spine.head[0], spine.head[1], spine.head[2] + trunk_mesh_depth / 2)
        neck_mesh_depth             = neck.length
        neck_mesh_location          = (neck.head[0], neck.head[1], neck.head[2] + neck.length / 2)
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
        right_leg_mesh_depth        = thigh_R.head[2] - shin_R.tail[2]
        right_leg_mesh_location     = (thigh_R.head[0], thigh_R.head[1], thigh_R.head[2] - right_leg_mesh_depth / 2)
        left_leg_mesh_depth         = thigh_L.head[2] - shin_L.tail[2]
        left_leg_mesh_location      = (thigh_L.head[0], thigh_L.head[1], thigh_L.head[2] - left_leg_mesh_depth / 2)
        right_foot_mesh_location    = (foot_R.tail[0], foot_R.tail[1], foot_R.tail[2])
        left_foot_mesh_location     = (foot_L.tail[0], foot_L.tail[1], foot_L.tail[2])

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
            rotation        = (0.0, 0.0, 0.0)
        )
        body_meshes.append(bpy.context.active_object)
        # Add subdivisions to the mesh so it bends properly
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cylinder_cuts)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Neck
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.05,
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

        # Right Leg
        bpy.ops.mesh.primitive_cylinder_add(
            vertices        = vertices,
            radius          = 0.05,
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
            radius          = 0.05,
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
            scale           = (1.0, 2.3, 1.2)
        )
        body_meshes.append(bpy.context.active_object)

        # Left Foot
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius          = 0.05,
            enter_editmode  = False,
            align           = 'WORLD',
            location        = left_foot_mesh_location,
            scale           = (1.0, 2.3, 1.2)
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
        print("Unknown add rig mode")

# Class with the different properties of the methods
class FMC_ADAPTER_PROPERTIES(bpy.types.PropertyGroup):
    # Adjust Empties Options
    vertical_align_reference: bpy.props.EnumProperty(
        name        = '',
        description = 'Empty that serves as reference to align the z axis',
        items       = [('left_knee', 'left_knee', ''),
                       ('trunk_center', 'trunk_center', ''),
                       ('right_knee', 'right_knee', '')]
    )
    vertical_align_angle_offset: bpy.props.FloatProperty(
        name        = '',
        default     = 0,
        description = 'Angle offset to adjust the vertical alignement of the z axis (in degrees)'
    )
    ground_align_reference: bpy.props.EnumProperty(
        name        = '',
        description = 'Empty that serves as ground reference to the axes origin',
        items       = [('left_foot_index', 'left_foot_index', ''),
                       ('right_foot_index', 'right_foot_index', ''),
                       ('left_heel', 'left_heel', ''),
                       ('right_heel', 'right_heel', '')]
    )
    vertical_align_position_offset: bpy.props.FloatProperty(
        name        = '',
        default     = 0,
        precision   = 3,
        description = 'Additional z offset to the axes origin relative to the imaginary ground level'
    )
    
    # Reduce Bone Length Dispersion Options
    interval_variable: bpy.props.EnumProperty(
        name        = '',
        description = 'Variable used to define the new length dispersion interval',
        items       = [('median', 'Median', 'Defines the new dispersion interval as [median*(1-interval_factor),median*(1+interval_factor)]'),
                       ('stdev', 'Standard Deviation', 'Defines the new dispersion interval as [median-interval_factor*stdev,median+interval_factor*stdev]')]
    )
    interval_factor: bpy.props.FloatProperty(
        name        = '',
        default     = 0.01,
        min         = 0,
        precision   = 3,
        description = 'Factor to multiply the variable and form the limits of the dispersion interval like [median-factor*variable,median+factor*variable]. ' +
                      'If variable is median, the factor will be limited to values inside [0, 1].' + 
                      'If variable is stdev, the factor will be limited to values inside [0, median/stdev]'
    )

    # Add Rig Options
    bone_length_method: bpy.props.EnumProperty(
        name        = '',
        description = 'Method use to calculate length of major bones',
        items       = [('median_length', 'Median Length', ''),
                       #('current_frame', 'Current Frame', '')]
                       ]
    )
    keep_symmetry: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Keep right/left side symmetry (use average right/left side bone length)'
    )
    use_limit_rotation: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Add rotation limits (human skeleton) to the bones constraints (experimental)'
    )
    
    # Add Body Mesh Options
    body_mesh_mode: bpy.props.EnumProperty(
        name        = '',
        description = 'Mode (source) for adding the mesh to the rig',
        items       = [('file', 'file', ''),
                       ('custom', 'custom', '')]
    )
    
# UI Panel Class
class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "UI"
    bl_category     = "Freemocap Adapter"
    bl_label        = "Freemocap Adapter"
    
    def draw(self, context):
        layout              = self.layout
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool
        
        # Adjust Empties Options
        box = layout.box()
        #box.label(text='Adjust Empties Options')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Align Reference')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_reference')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Angle Offset')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_angle_offset')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Ground Reference')
        split.split().column().prop(fmc_adapter_tool, 'ground_align_reference')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Vertical Position Offset')
        split.split().column().prop(fmc_adapter_tool, 'vertical_align_position_offset')
        
        box.operator('fmc_adapter.adjust_empties', text='Adjust Empties')

        # Reduce Bone Length Dispersion Options
        box = layout.box()
        #box.label(text='Reduce Bone Length Dispersion Options')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Variable')
        split.split().column().prop(fmc_adapter_tool, 'interval_variable')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Factor')
        split.split().column().prop(fmc_adapter_tool, 'interval_factor')

        box.operator('fmc_adapter.reduce_bone_length_dispersion', text='Reduce Bone Length Dispersion')
        
        # Add Rig Options
        box = layout.box()
        #box.label(text='Add Rig Options')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Bone Length Method')
        split.split().column().prop(fmc_adapter_tool, 'bone_length_method')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Keep right/left symmetry')
        split.split().column().prop(fmc_adapter_tool, 'keep_symmetry')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add rotation limits')
        split.split().column().prop(fmc_adapter_tool, 'use_limit_rotation')
        
        box.operator('fmc_adapter.add_rig', text='Add Rig')
        
        # Add Body Mesh Options
        box = layout.box()
        #box.label(text='Add Body Mesh Options')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')
        
        #box.operator('fmc_adapter.actions_op', text='Add Body Mesh').action = 'ADD_BODY_MESH'
        box.operator('fmc_adapter.add_body_mesh', text='Add Body Mesh')

# Operator classes that executes the methods
class FMC_ADAPTER_OT_adjust_empties(Operator):
    bl_idname       = 'fmc_adapter.adjust_empties'
    bl_label        = 'Freemocap Adapter - Adjust Empties'
    bl_description  = "Change the position of the freemocap_origin_axes empty to so it is placed in an imaginary ground plane of the capture between the actor's feet"
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Adjust Empties...')

        adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                       z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                       ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                       z_translation_offset=fmc_adapter_tool.vertical_align_position_offset                       
                       )
        
        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))
        return {'FINISHED'}

class FMC_ADAPTER_OT_reduce_bone_length_dispersion(Operator):
    bl_idname       = 'fmc_adapter.reduce_bone_length_dispersion'
    bl_label        = 'Freemocap Adapter - Reduce Bone Length Dispersion'
    bl_description  = 'Reduce the bone length dispersion by moving the tail empty and its children along the bone projection so the bone new length is within the interval'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Reduce Bone Length Dispersion...')

        reduce_bone_length_dispersion(interval_variable=fmc_adapter_tool.interval_variable,
                                      interval_factor=fmc_adapter_tool.interval_factor)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_add_rig(Operator):
    bl_idname       = 'fmc_adapter.add_rig'
    bl_label        = 'Freemocap Adapter - Add Rig'
    bl_description  = 'Add a Rig to the capture empties. The method sets the rig rest pose as a TPose'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

        if not adjust_empties_executed:
            print('Executing First Adjust Empties...')

            # Execute Adjust Empties first
            adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                        z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                        ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                        z_translation_offset=fmc_adapter_tool.vertical_align_position_offset                       
                        )
        
        print('Executing Add Rig...')

        add_rig(bone_length_method=fmc_adapter_tool.bone_length_method,
                keep_symmetry=fmc_adapter_tool.keep_symmetry,
                use_limit_rotation=fmc_adapter_tool.use_limit_rotation)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_add_body_mesh(Operator):
    bl_idname       = 'fmc_adapter.add_body_mesh'
    bl_label        = 'Freemocap Adapter - Add Body Mesh'
    bl_description  = 'Add a body mesh to the rig. The mesh can be a file or a custom mesh made with basic shapes. This method first executes Add Empties and Add Rig(if no rig available)'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        # Reset the scene frame to the start
        scene.frame_set(scene.frame_start)

        if not adjust_empties_executed:
            print('Executing First Adjust Empties...')

            # Execute Adjust Empties first
            adjust_empties(z_align_ref_empty=fmc_adapter_tool.vertical_align_reference,
                        z_align_angle_offset=fmc_adapter_tool.vertical_align_angle_offset,
                        ground_ref_empty=fmc_adapter_tool.ground_align_reference,
                        z_translation_offset=fmc_adapter_tool.vertical_align_position_offset                       
                        )
        
        # Execute Add Rig if there is no rig in the scene
        try:
            root = bpy.data.objects['root']
        except:
            print('Executing Add Rig to have a rig for the mesh...')
            add_rig(use_limit_rotation=fmc_adapter_tool.use_limit_rotation)
        
        print('Executing Add Body Mesh...')
        add_mesh_to_rig(body_mesh_mode=fmc_adapter_tool.body_mesh_mode)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}


classes = [FMC_ADAPTER_PROPERTIES,
           VIEW3D_PT_freemocap_adapter,
           FMC_ADAPTER_OT_adjust_empties,
           FMC_ADAPTER_OT_reduce_bone_length_dispersion,
           FMC_ADAPTER_OT_add_rig,
           FMC_ADAPTER_OT_add_body_mesh
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type = FMC_ADAPTER_PROPERTIES)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.fmc_adapter_tool

# Register the Add-on
if __name__ == "__main__":
    register()

