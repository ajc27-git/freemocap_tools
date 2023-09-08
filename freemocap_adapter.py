bl_info = {
    'name'          : 'Freemocap Adapter',
    'author'        : 'ajc27',
    'version'       : (1, 1, 8),
    'blender'       : (3, 0, 0),
    'location'      : '3D Viewport > Sidebar > Freemocap Adapter',
    'description'   : 'Add-on to adapt the Freemocap Blender output',
    'category'      : 'Development',
}

import bpy
import os
from pathlib import Path
from importlib.machinery import SourceFileLoader
import addon_utils
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

# Location and rotation vectors of the freemocap_origin_axes in the Adjust Empties method just before resetting its location and rotation to (0, 0, 0)
origin_location_pre_reset = (0, 0, 0)
origin_rotation_pre_reset = (0, 0, 0)

# Dictionary to save the global vector position of all the empties for every animation frame
empty_positions = {}

# Dictionary to save the speed of all the empties for every animation frame
empty_speeds = {}

# Dictionary with the Anthropomorphic human dimensions by Winter, D. This values will be used the specified actor height when using standard bone lengths
anthropomorphic_dimensions = {
    'pelvis.R': {
        'dimension': 0.0955},
    'pelvis.L': {
        'dimension': 0.0955},
    'spine': {
        'dimension': 0.144},
    'spine.001': {
        'dimension': 0.144},
    'neck': {
        'dimension': 0.118},
    'head_nose': { # Auxiliary bone from head center to nose tip to align the face bones 
        'dimension': 0.0743},
    'shoulder.R': {
        'dimension': 0.129},
    'shoulder.L': {
        'dimension': 0.129},
    'upper_arm.R': {
        'dimension': 0.186},
    'upper_arm.L': {
        'dimension': 0.186},
    'forearm.R': {
        'dimension': 0.146},
    'forearm.L': {
        'dimension': 0.146},
    'hand.R': {
        'dimension': 0.054},
    'hand.L': {
        'dimension': 0.054},
    'thumb.carpal.R': { # Auxiliary bone to align the right_hand_thumb_cmc empty
        'dimension': 0.03},
    'thumb.carpal.L': { # Auxiliary bone to align the left_hand_thumb_cmc empty
        'dimension': 0.03},
    'thumb.01.R': {
        'dimension': 0.021},
    'thumb.01.L': {
        'dimension': 0.021},
    'thumb.02.R': {
        'dimension': 0.024},
    'thumb.02.L': {
        'dimension': 0.024},
    'thumb.03.R': {
        'dimension': 0.0192},
    'thumb.03.L': {
        'dimension': 0.0192},
    'palm.01.R': {
        'dimension': 0.054},
    'palm.01.L': {
        'dimension': 0.054},
    'f_index.01.R': {
        'dimension': 0.0282},
    'f_index.01.L': {
        'dimension': 0.0282},
    'f_index.02.R': {
        'dimension': 0.0186},
    'f_index.02.L': {
        'dimension': 0.0186},
    'f_index.03.R': {
        'dimension': 0.015},
    'f_index.03.L': {
        'dimension': 0.015},
    'palm.02.R': {
        'dimension': 0.054},
    'palm.02.L': {
        'dimension': 0.054},
    'f_middle.01.R': {
        'dimension': 0.03},
    'f_middle.01.L': {
        'dimension': 0.03},
    'f_middle.02.R': {
        'dimension': 0.0192},
    'f_middle.02.L': {
        'dimension': 0.0192},
    'f_middle.03.R': {
        'dimension': 0.0156},
    'f_middle.03.L': {
        'dimension': 0.0156},
    'palm.03.R': {
        'dimension': 0.0522},
    'palm.03.L': {
        'dimension': 0.0522},
    'f_ring.01.R': {
        'dimension': 0.0282},
    'f_ring.01.L': {
        'dimension': 0.0282},
    'f_ring.02.R': {
        'dimension': 0.0186},
    'f_ring.02.L': {
        'dimension': 0.0186},
    'f_ring.03.R': {
        'dimension': 0.0156},
    'f_ring.03.L': {
        'dimension': 0.0156},
    'palm.04.R': {
        'dimension': 0.0498},
    'palm.04.L': {
        'dimension': 0.0498},
    'f_pinky.01.R': {
        'dimension': 0.0264},
    'f_pinky.01.L': {
        'dimension': 0.0264},
    'f_pinky.02.R': {
        'dimension': 0.0156},
    'f_pinky.02.L': {
        'dimension': 0.0156},
    'f_pinky.03.R': {
        'dimension': 0.0144},
    'f_pinky.03.L': {
        'dimension': 0.0144},
    'thigh.R': {
        'dimension': 0.245},
    'thigh.L': {
        'dimension': 0.245},
    'shin.R': {
        'dimension': 0.246},
    'shin.L': {
        'dimension': 0.246},
    'foot.R': {
        'dimension': 0.152},
    'foot.L': {
        'dimension': 0.152},
    'heel.02.R': {
        'dimension': 0.039},
    'heel.02.L': {
        'dimension': 0.039},
}

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
    'head_nose': { # Auxiliary bone from head center to nose tip to align the face bones 
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
    'thumb.carpal.R': { # Auxiliary bone to align the right_hand_thumb_cmc empty
        'head'      : 'right_hand_wrist',
        'tail'      : 'right_hand_thumb_cmc',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.carpal.L': { # Auxiliary bone to align the left_hand_thumb_cmc empty
        'head'      : 'left_hand_wrist',
        'tail'      : 'left_hand_thumb_cmc',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.01.R': {
        'head'      : 'right_hand_thumb_cmc',
        'tail'      : 'right_hand_thumb_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.01.L': {
        'head'      : 'left_hand_thumb_cmc',
        'tail'      : 'left_hand_thumb_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.02.R': {
        'head'      : 'right_hand_thumb_mcp',
        'tail'      : 'right_hand_thumb_ip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.02.L': {
        'head'      : 'left_hand_thumb_mcp',
        'tail'      : 'left_hand_thumb_ip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.03.R': {
        'head'      : 'right_hand_thumb_ip',
        'tail'      : 'right_hand_thumb_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'thumb.03.L': {
        'head'      : 'left_hand_thumb_ip',
        'tail'      : 'left_hand_thumb_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.01.R': {
        'head'      : 'right_hand_wrist',
        'tail'      : 'right_hand_index_finger_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.01.L': {
        'head'      : 'left_hand_wrist',
        'tail'      : 'left_hand_index_finger_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_index.01.R': {
        'head'      : 'right_hand_index_finger_mcp',
        'tail'      : 'right_hand_index_finger_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_index.01.L': {
        'head'      : 'left_hand_index_finger_mcp',
        'tail'      : 'left_hand_index_finger_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_index.02.R': {
        'head'      : 'right_hand_index_finger_pip',
        'tail'      : 'right_hand_index_finger_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_index.02.L': {
        'head'      : 'left_hand_index_finger_pip',
        'tail'      : 'left_hand_index_finger_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_index.03.R': {
        'head'      : 'right_hand_index_finger_dip',
        'tail'      : 'right_hand_index_finger_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_index.03.L': {
        'head'      : 'left_hand_index_finger_dip',
        'tail'      : 'left_hand_index_finger_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.02.R': {
        'head'      : 'right_hand_wrist',
        'tail'      : 'right_hand_middle_finger_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.02.L': {
        'head'      : 'left_hand_wrist',
        'tail'      : 'left_hand_middle_finger_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_middle.01.R': {
        'head'      : 'right_hand_middle_finger_mcp',
        'tail'      : 'right_hand_middle_finger_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_middle.01.L': {
        'head'      : 'left_hand_middle_finger_mcp',
        'tail'      : 'left_hand_middle_finger_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_middle.02.R': {
        'head'      : 'right_hand_middle_finger_pip',
        'tail'      : 'right_hand_middle_finger_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_middle.02.L': {
        'head'      : 'left_hand_middle_finger_pip',
        'tail'      : 'left_hand_middle_finger_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_middle.03.R': {
        'head'      : 'right_hand_middle_finger_dip',
        'tail'      : 'right_hand_middle_finger_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_middle.03.L': {
        'head'      : 'left_hand_middle_finger_dip',
        'tail'      : 'left_hand_middle_finger_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.03.R': {
        'head'      : 'right_hand_wrist',
        'tail'      : 'right_hand_ring_finger_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.03.L': {
        'head'      : 'left_hand_wrist',
        'tail'      : 'left_hand_ring_finger_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_ring.01.R': {
        'head'      : 'right_hand_ring_finger_mcp',
        'tail'      : 'right_hand_ring_finger_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_ring.01.L': {
        'head'      : 'left_hand_ring_finger_mcp',
        'tail'      : 'left_hand_ring_finger_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_ring.02.R': {
        'head'      : 'right_hand_ring_finger_pip',
        'tail'      : 'right_hand_ring_finger_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_ring.02.L': {
        'head'      : 'left_hand_ring_finger_pip',
        'tail'      : 'left_hand_ring_finger_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_ring.03.R': {
        'head'      : 'right_hand_ring_finger_dip',
        'tail'      : 'right_hand_ring_finger_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_ring.03.L': {
        'head'      : 'left_hand_ring_finger_dip',
        'tail'      : 'left_hand_ring_finger_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.04.R': {
        'head'      : 'right_hand_wrist',
        'tail'      : 'right_hand_pinky_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'palm.04.L': {
        'head'      : 'left_hand_wrist',
        'tail'      : 'left_hand_pinky_mcp',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_pinky.01.R': {
        'head'      : 'right_hand_pinky_mcp',
        'tail'      : 'right_hand_pinky_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_pinky.01.L': {
        'head'      : 'left_hand_pinky_mcp',
        'tail'      : 'left_hand_pinky_pip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_pinky.02.R': {
        'head'      : 'right_hand_pinky_pip',
        'tail'      : 'right_hand_pinky_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_pinky.02.L': {
        'head'      : 'left_hand_pinky_pip',
        'tail'      : 'left_hand_pinky_dip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_pinky.03.R': {
        'head'      : 'right_hand_pinky_dip',
        'tail'      : 'right_hand_pinky_tip',
        'lengths'   : [],
        'median'    : 0,
        'stdev'     : 0},
    'f_pinky.03.L': {
        'head'      : 'left_hand_pinky_dip',
        'tail'      : 'left_hand_pinky_tip',
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
        'children'    : ['right_thumb', 'right_index', 'right_pinky', 'right_hand', 'right_hand_middle', 'right_hand_wrist']},
    'left_wrist': {
        'children'    : ['left_thumb', 'left_index', 'left_pinky', 'left_hand', 'left_hand_middle', 'left_hand_wrist']},
    'right_hand_wrist': {
        'children'    : ['right_hand_thumb_cmc', 'right_hand_index_finger_mcp', 'right_hand_middle_finger_mcp', 'right_hand_ring_finger_mcp', 'right_hand_pinky_mcp']},
    'left_hand_wrist': {
        'children'    : ['left_hand_thumb_cmc', 'left_hand_index_finger_mcp', 'left_hand_middle_finger_mcp', 'left_hand_ring_finger_mcp', 'left_hand_pinky_mcp']},
    'right_hand_thumb_cmc': {
        'children'    : ['right_hand_thumb_mcp']},
    'left_hand_thumb_cmc': {
        'children'    : ['left_hand_thumb_mcp']},
    'right_hand_thumb_mcp': {
        'children'    : ['right_hand_thumb_ip']},
    'left_hand_thumb_mcp': {
        'children'    : ['left_hand_thumb_ip']},
    'right_hand_thumb_ip': {
        'children'    : ['right_hand_thumb_tip']},
    'left_hand_thumb_ip': {
        'children'    : ['left_hand_thumb_tip']},
    'right_hand_index_finger_mcp': {
        'children'    : ['right_hand_index_finger_pip']},
    'left_hand_index_finger_mcp': {
        'children'    : ['left_hand_index_finger_pip']},
    'right_hand_index_finger_pip': {
        'children'    : ['right_hand_index_finger_dip']},
    'left_hand_index_finger_pip': {
        'children'    : ['left_hand_index_finger_dip']},
    'right_hand_index_finger_dip': {
        'children'    : ['right_hand_index_finger_tip']},
    'left_hand_index_finger_dip': {
        'children'    : ['left_hand_index_finger_tip']},
    'right_hand_middle_finger_mcp': {
        'children'    : ['right_hand_middle_finger_pip']},
    'left_hand_middle_finger_mcp': {
        'children'    : ['left_hand_middle_finger_pip']},
    'right_hand_middle_finger_pip': {
        'children'    : ['right_hand_middle_finger_dip']},
    'left_hand_middle_finger_pip': {
        'children'    : ['left_hand_middle_finger_dip']},
    'right_hand_middle_finger_dip': {
        'children'    : ['right_hand_middle_finger_tip']},
    'left_hand_middle_finger_dip': {
        'children'    : ['left_hand_middle_finger_tip']},
    'right_hand_ring_finger_mcp': {
        'children'    : ['right_hand_ring_finger_pip']},
    'left_hand_ring_finger_mcp': {
        'children'    : ['left_hand_ring_finger_pip']},
    'right_hand_ring_finger_pip': {
        'children'    : ['right_hand_ring_finger_dip']},
    'left_hand_ring_finger_pip': {
        'children'    : ['left_hand_ring_finger_dip']},
    'right_hand_ring_finger_dip': {
        'children'    : ['right_hand_ring_finger_tip']},
    'left_hand_ring_finger_dip': {
        'children'    : ['left_hand_ring_finger_tip']},
    'right_hand_pinky_mcp': {
        'children'    : ['right_hand_pinky_pip']},
    'left_hand_pinky_mcp': {
        'children'    : ['left_hand_pinky_pip']},
    'right_hand_pinky_pip': {
        'children'    : ['right_hand_pinky_dip']},
    'left_hand_pinky_pip': {
        'children'    : ['left_hand_pinky_dip']},
    'right_hand_pinky_dip': {
        'children'    : ['right_hand_pinky_tip']},
    'left_hand_pinky_dip': {
        'children'    : ['left_hand_pinky_tip']},
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
        if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin' and object.name != '_full_body_center_of_mass':
            empty_positions[object.name] = {'x': [], 'y': [], 'z': []}

    # Iterate through each scene frame and save the coordinates of each empty in the dictionary.
    for frame in range (scene.frame_start, scene.frame_end):
        # Set scene frame
        scene.frame_set(frame)
        # Iterate through each object
        for object in bpy.data.objects:
            if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin' and object.name != '_full_body_center_of_mass':
                # Save the x, y, z position of the empty
                empty_positions[object.name]['x'].append(bpy.data.objects[object.name].location[0])
                empty_positions[object.name]['y'].append(bpy.data.objects[object.name].location[1])
                empty_positions[object.name]['z'].append(bpy.data.objects[object.name].location[2])

    # Reset the scene frame to the start
    scene.frame_set(scene.frame_start)

    print('Empty Positions Dictionary update completed.')

# Function to update all the empties speeds in the dictionary
def update_empty_speeds(recording_fps):
    
    print('Updating Empty Speeds Dictionary...')

    # Get the scene context
    scene = bpy.context.scene

    # Change to Object Mode
    bpy.ops.object.mode_set(mode="OBJECT")

    # Reset the empty speeds dictionary with an array with one element of value zero for each empty marker
    for object in bpy.data.objects:
        if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin' and object.name != '_full_body_center_of_mass':
            empty_speeds[object.name] = {'speed': [0]}

    # Iterate through each scene frame starting from frame start + 1 and save the speed of each empty in the dictionary
    for frame in range (scene.frame_start + 1, scene.frame_end + 1):
        # Set scene frame
        scene.frame_set(frame)
        # Iterate through each object
        for object in bpy.data.objects:
            if object.type == 'EMPTY' and object.name != 'freemocap_origin_axes' and object.name != 'world_origin' and object.name != '_full_body_center_of_mass':
                # Save the speed of the empty based on the recording fps and the distance to the position of the empty in the previous frame
                #print('length:' + str(len(empty_positions[object.name]['x'])))
                #print('frame:'+str(frame))
                current_frame_position  = (empty_positions[object.name]['x'][frame-1], empty_positions[object.name]['y'][frame-1], empty_positions[object.name]['z'][frame-1])
                previous_frame_position = (empty_positions[object.name]['x'][frame-2], empty_positions[object.name]['y'][frame-2], empty_positions[object.name]['z'][frame-2])
                seconds_per_frame       = 1 / recording_fps
                empty_speeds[object.name]['speed'].append(m.dist(current_frame_position, previous_frame_position) / seconds_per_frame)

    # Reset the scene frame to the start
    scene.frame_set(scene.frame_start)

    print('Empty Speeds Dictionary update completed.')
    
# Function to update all the information of the virtual bones dictionary (lengths, median and stdev)
def update_virtual_bones_info():

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

        # Move the freemocap_origin_axes empty to the position and rotation previous to the Adjust Empties method ending
        origin = bpy.data.objects['freemocap_origin_axes']
        origin.location         = origin_location_pre_reset
        origin.rotation_euler   = origin_rotation_pre_reset

        # Select the new empties
        right_hand_middle.select_set(True)
        left_hand_middle.select_set(True)

        # Set the origin active in 3Dview
        bpy.context.view_layer.objects.active = bpy.data.objects['freemocap_origin_axes']
        # Parent selected empties to freemocap_origin_axes keeping transforms
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

######################################################################
######################### ADJUST EMPTIES #############################
######################################################################

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

    ### Reparent all the capture empties to the origin (freemocap_origin_axes) ###
    for object in bpy.data.objects:
        if object.type == "EMPTY" and object.name != "freemocap_origin_axes" and object.name != "world_origin":
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
    bpy.data.objects['freemocap_origin_axes'].select_set(True)

    # Change the adjust_empties_executed variable
    adjust_empties_executed = True

######################################################################
#################### REDUCE BONE LENGTH DISPERSION ###################
######################################################################

def reduce_bone_length_dispersion(interval_variable: str='capture_median', interval_factor: float=0.01, body_height: float=1.75):

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
            elif interval_variable == 'standard_lenght':
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
                translate_empty(empties_dict, tail, frame_index, position_delta)

                empties_positions_corrected += 1
            
            frame_index += 1
    
    # Update the empty positions dictionary
    update_empty_positions()
    
    # Update the information of the virtual bones
    update_virtual_bones_info()

    # Print the new bones length median, standard deviation and coefficient of variation
    print('New Virtual Bone Information:')
    print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
    for bone in virtual_bones:

        # Get the statistic values
        new_median  = virtual_bones[bone]['median']
        new_stdev   = virtual_bones[bone]['stdev']
        new_cv      = virtual_bones[bone]['stdev']/virtual_bones[bone]['median']

        print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(new_median*100*10000000)/10000000), str(m.trunc(new_stdev*100*10000000)/10000000), str(m.trunc(new_cv*100*10000)/10000)))

    print('Total empties positions corrected: ' + str(empties_positions_corrected))
    

# Function to translate the empties recursively
def translate_empty(empties_dict, empty, frame_index, delta):

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

    # If empty has children then call this function for every child
    if empty in empties_dict:
        for child in empties_dict[empty]['children']:
            translate_empty(empties_dict, child, frame_index, delta)

# IN DEVELOPMENT
# Function to reduce sudden movements of empties with an acceleration above a threshold
def reduce_shakiness(recording_fps: float=30):
    print('fps: ' + str(recording_fps))
    # Update the empty positions dictionary
    update_empty_positions()

    # Update the empty speeds dictionary
    update_empty_speeds(recording_fps)

    # Get the time of each frame in seconds
    seconds_per_frame   = 1 / recording_fps

    # for f in range(150, 157):
    #     empty_speed         = empty_speeds['left_wrist']['speed'][f-1]
    #     acceleration        = (empty_speed - empty_speeds['left_wrist']['speed'][f-2]) / seconds_per_frame
    #     print('left_wrist frame ' + str(f) + ' speed: ' + str(empty_speed) + ' acceleration: ' + str(acceleration))

    # for f in range(1160, 1180):
    #     empty_speed         = empty_speeds['right_wrist']['speed'][f-1]
    #     acceleration        = (empty_speed - empty_speeds['right_wrist']['speed'][f-2]) / seconds_per_frame
    #     print('right_wrist frame ' + str(f) + ' speed: ' + str(empty_speed) + ' acceleration: ' + str(acceleration))

    for empty in empty_positions:
        for frame_index in range(1, len(empty_speeds[empty]['speed']) - 2):
            empty_speed         = empty_speeds[empty]['speed'][frame_index]
            acceleration        = (empty_speed - empty_speeds[empty]['speed'][frame_index-1]) / seconds_per_frame

            if acceleration > 10:

                # Get the empty position
                empty_position      = mathutils.Vector([empty_positions[empty]['x'][frame_index], empty_positions[empty]['y'][frame_index], empty_positions[empty]['z'][frame_index]])
                # Get the empty position in the previous frame
                empty_position_prev = mathutils.Vector([empty_positions[empty]['x'][frame_index - 1], empty_positions[empty]['y'][frame_index - 1], empty_positions[empty]['z'][frame_index - 1]])
                # Get the empty position in the next frame
                empty_position_next = mathutils.Vector([empty_positions[empty]['x'][frame_index + 1], empty_positions[empty]['y'][frame_index + 1], empty_positions[empty]['z'][frame_index + 1]])

                # Get the direction vector of the empty in the current frame
                empty_direction         = empty_position - empty_position_prev

                # Get the direction vector of the empty in the next current
                empty_direction_next    = empty_position_next - empty_position

                # Get the addition of the direction vectors
                direction_addition      = empty_direction + empty_direction_next

                # Get the the direction addition length
                direction_addition_length = m.dist((0,0,0), direction_addition)

                # If the distance is less than the threshold then the current position of the empty is considered a shake
                if direction_addition_length < 0.02:
                    print(empty + ":" + str(frame_index + 1) + ": shake")

                # print(empty_position)
                # print(empty_position_prev)
                # print(empty_direction)
                # print(empty_direction_next)
                # print(direction_addition)
                # print(m.dist((0,0,0), direction_addition))
                # print('right_wrist frame ' + str(frame_index + 1) + ' speed: ' + str(empty_speed) + ' acceleration: ' + str(acceleration))


######################################################################
############################# ADD RIG ################################
######################################################################

def add_rig(keep_symmetry: bool=False,
            add_fingers_constraints: bool=False,
            use_limit_rotation: bool=False):

    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # If there is an existing metarig, delete it
    try:
        print('Deleting previous metarigs...')
        for object in bpy.data.objects:
            if object.type == "ARMATURE":
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

    # Add the rig setting the bones lenght as the median lenght across all the frames
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

    #############################################################
    ### DEBUG ###
    if False:
        # Add an auxiliary bone to the side of the upperarms and forearms to check their rotation
        upper_arm_R_Rot             = rig.data.edit_bones.new('uppe_rarm.R.Rot')
        upper_arm_R_Rot.head        = (upper_arm_R.head[0] - upper_arm_R_length/2, upper_arm_R.head[1], upper_arm_R.head[2])
        upper_arm_R_Rot.tail        = (upper_arm_R_Rot.head[0], upper_arm_R_Rot.head[1], upper_arm_R_Rot.head[2] + 0.1)
        upper_arm_R_Rot.parent      = upper_arm_R
        upper_arm_R_Rot.use_connect = False
        upper_arm_L_Rot             = rig.data.edit_bones.new('uppe_rarm.L.Rot')
        upper_arm_L_Rot.head        = (upper_arm_L.head[0] + upper_arm_L_length/2, upper_arm_L.head[1], upper_arm_L.head[2])
        upper_arm_L_Rot.tail        = (upper_arm_L_Rot.head[0], upper_arm_L_Rot.head[1], upper_arm_L_Rot.head[2] + 0.1)
        upper_arm_L_Rot.parent      = upper_arm_L
        upper_arm_L_Rot.use_connect = False
        forearm_R_Rot               = rig.data.edit_bones.new('uppe_rarm.R.Rot')
        forearm_R_Rot.head          = (forearm_R.head[0] - forearm_R_length/2, forearm_R.head[1], forearm_R.head[2])
        forearm_R_Rot.tail          = (forearm_R_Rot.head[0], forearm_R_Rot.head[1], forearm_R_Rot.head[2] + 0.1)
        forearm_R_Rot.parent        = forearm_R
        forearm_R_Rot.use_connect   = False
        forearm_L_Rot               = rig.data.edit_bones.new('uppe_rarm.L.Rot')
        forearm_L_Rot.head          = (forearm_L.head[0] + forearm_L_length/2, forearm_L.head[1], forearm_L.head[2])
        forearm_L_Rot.tail          = (forearm_L_Rot.head[0], forearm_L_Rot.head[1], forearm_L_Rot.head[2] + 0.1)
        forearm_L_Rot.parent        = forearm_L
        forearm_L_Rot.use_connect   = False
    #############################################################

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

    # Rotate the forearms on the z axis to bend the elbows a little bit and avoid incorrect rotations
    pose_forearm_R                  = rig.pose.bones['forearm.R']
    pose_forearm_R.rotation_mode    = 'XYZ'
    pose_forearm_R.rotation_euler   = (m.radians(1), m.radians(0), m.radians(0))
    pose_forearm_R.rotation_mode    = 'QUATERNION'
    pose_forearm_L                  = rig.pose.bones['forearm.L']
    pose_forearm_L.rotation_mode    = 'XYZ'
    pose_forearm_L.rotation_euler   = (m.radians(1), m.radians(0), m.radians(0))
    pose_forearm_L.rotation_mode    = 'QUATERNION'

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

    # Define the hand bones damped track target as the hand middle empty if they were already added
    try:
        right_hand_middle_name = bpy.data.objects['right_hand_middle'].name
        # Right Hand Middle Empty exists. Use hand middle as target
        hand_damped_track_target = 'hand_middle'
    except:
        # Hand middle empties do not exist. Use hand_index as target
        hand_damped_track_target = 'index'

    # Define the hands LOCKED_TRACK target empty based on the add_fingers_constraints parameter
    if add_fingers_constraints:
        hand_locked_track_target = 'hand_thumb_cmc'
    else:
        hand_locked_track_target = 'thumb'

    # Create the dictionary with the different bone constraints
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
            #{'type':'LOCKED_TRACK','target':'right_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':0,'max_y':146,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "forearm.L": [
            #{'type':'IK','target':'left_wrist','pole_target':'left_elbow','chain_count':2,'pole_angle':-90},
            {'type':'DAMPED_TRACK','target':'left_wrist','track_axis':'TRACK_Y'},
            #{'type':'LOCKED_TRACK','target':'left_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':-146,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "hand.R": [
            {'type':'DAMPED_TRACK','target':'right_' + hand_damped_track_target,'track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-36,'max_y':25,'use_limit_z':True,'min_z':-86,'max_z':90,'owner_space':'LOCAL'}],
        "hand.L": [
            {'type':'DAMPED_TRACK','target':'left_' + hand_damped_track_target,'track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'left_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
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
        "thumb.carpal.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_thumb_cmc','track_axis':'TRACK_Y'}],
        "thumb.01.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_thumb_mcp','track_axis':'TRACK_Y'}],
        "thumb.02.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_thumb_ip','track_axis':'TRACK_Y'}],
        "thumb.03.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_thumb_tip','track_axis':'TRACK_Y'}],
        "palm.01.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_index_finger_mcp','track_axis':'TRACK_Y'}],
        "f_index.01.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_index_finger_pip','track_axis':'TRACK_Y'}],
        "f_index.02.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_index_finger_dip','track_axis':'TRACK_Y'}],
        "f_index.03.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_index_finger_tip','track_axis':'TRACK_Y'}],
        "palm.02.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_middle_finger_mcp','track_axis':'TRACK_Y'}],
        "f_middle.01.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_middle_finger_pip','track_axis':'TRACK_Y'}],
        "f_middle.02.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_middle_finger_dip','track_axis':'TRACK_Y'}],
        "f_middle.03.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_middle_finger_tip','track_axis':'TRACK_Y'}],
        "palm.03.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_ring_finger_mcp','track_axis':'TRACK_Y'}],
        "f_ring.01.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_ring_finger_pip','track_axis':'TRACK_Y'}],
        "f_ring.02.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_ring_finger_dip','track_axis':'TRACK_Y'}],
        "f_ring.03.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_ring_finger_tip','track_axis':'TRACK_Y'}],
        "palm.04.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_pinky_mcp','track_axis':'TRACK_Y'}],
        "f_pinky.01.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_pinky_pip','track_axis':'TRACK_Y'}],
        "f_pinky.02.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_pinky_dip','track_axis':'TRACK_Y'}],
        "f_pinky.03.R": [
            {'type':'DAMPED_TRACK','target':'right_hand_pinky_tip','track_axis':'TRACK_Y'}],
        "thumb.carpal.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_thumb_cmc','track_axis':'TRACK_Y'}],
        "thumb.01.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_thumb_mcp','track_axis':'TRACK_Y'}],
        "thumb.02.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_thumb_ip','track_axis':'TRACK_Y'}],
        "thumb.03.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_thumb_tip','track_axis':'TRACK_Y'}],
        "palm.01.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_index_finger_mcp','track_axis':'TRACK_Y'}],
        "f_index.01.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_index_finger_pip','track_axis':'TRACK_Y'}],
        "f_index.02.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_index_finger_dip','track_axis':'TRACK_Y'}],
        "f_index.03.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_index_finger_tip','track_axis':'TRACK_Y'}],
        "palm.02.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_middle_finger_mcp','track_axis':'TRACK_Y'}],
        "f_middle.01.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_middle_finger_pip','track_axis':'TRACK_Y'}],
        "f_middle.02.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_middle_finger_dip','track_axis':'TRACK_Y'}],
        "f_middle.03.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_middle_finger_tip','track_axis':'TRACK_Y'}],
        "palm.03.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_ring_finger_mcp','track_axis':'TRACK_Y'}],
        "f_ring.01.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_ring_finger_pip','track_axis':'TRACK_Y'}],
        "f_ring.02.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_ring_finger_dip','track_axis':'TRACK_Y'}],
        "f_ring.03.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_ring_finger_tip','track_axis':'TRACK_Y'}],
        "palm.04.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_pinky_mcp','track_axis':'TRACK_Y'}],
        "f_pinky.01.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_pinky_pip','track_axis':'TRACK_Y'}],
        "f_pinky.02.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_pinky_dip','track_axis':'TRACK_Y'}],
        "f_pinky.03.L": [
            {'type':'DAMPED_TRACK','target':'left_hand_pinky_tip','track_axis':'TRACK_Y'}],
    }

    # Create each constraint
    for bone in constraints:

        # If it is a finger bone amd add_fingers_constraints is False continue with the next bone
        if not add_fingers_constraints and len([finger_part for finger_part in ['palm', 'thumb', 'index', 'middle', 'ring', 'pinky'] if finger_part in bone]) > 0:
            continue

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
            elif cons['type'] == 'IK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.pole_target   = bpy.data.objects[cons['pole_target']]
                bone_cons.chain_count   = cons['chain_count']
                bone_cons.pole_angle    = cons['pole_angle']

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
def add_mesh_to_rig(body_mesh_mode: str="custom", body_height: float=1.75):
    
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
    
        # Change to edit mode
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
        thigh_R     = rig.data.edit_bones['thigh.R']
        thigh_L     = rig.data.edit_bones['thigh.L']
        shin_R      = rig.data.edit_bones['shin.R']
        shin_L      = rig.data.edit_bones['shin.L']
        foot_R      = rig.data.edit_bones['foot.R']
        foot_L      = rig.data.edit_bones['foot.L']

        # Calculate parameters of the different body meshes
        trunk_mesh_radius           = shoulder_R.length
        trunk_mesh_depth            = spine_001.tail[2] - spine.head[2] + 0.05 * body_height
        trunk_mesh_location         = (spine.head[0], spine.head[1], spine.head[2] + trunk_mesh_depth / 2 - 0.025 * body_height)
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

######################################################################
########################### EXPORT TO FBX ############################
######################################################################

def export_fbx(self: Operator):

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    # Select only the rig and the body_mesh
    bpy.data.objects['root'].select_set(True)
    bpy.data.objects['fmc_mesh'].select_set(True)

    # Get the Blender file directory
    file_directory = os.path.dirname(bpy.data.filepath)
    
    # Create an FBX directory inside the blender output file folder
    if not os.path.exists(file_directory + '\\FBX'):
        os.mkdir(Path(file_directory + '\\FBX'), mode=0o777)

    # Define the export parameters dictionary
    export_parameters = {
        'filepath':file_directory + '\\FBX\\fmc_export.fbx',
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

    ################# Use of Blender io_scene_fbx addon + send2UE modifications #############################

    # Load the io_scene_fbx addon
    addons = {os.path.basename(os.path.dirname(module.__file__)): module.__file__ for module in addon_utils.modules()}
    addon_folder_path = os.path.dirname(addons.get('io_scene_fbx'))
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

    convert_rad_to_deg_iter = units_convertor_iter("radian", "degree")

    from io_scene_fbx.export_fbx_bin import fbx_data_element_custom_properties

    # Backup the method original_fbx_data_armature_elements of export_fbx_bin before it is modified
    backup_fbx_animations_do            = export_fbx_bin.fbx_animations_do
    backup_fbx_data_armature_elements   = export_fbx_bin.fbx_data_armature_elements
    backup_fbx_data_object_elements     = export_fbx_bin.fbx_data_object_elements
    backup_fbx_data_bindpose_element    = export_fbx_bin.fbx_data_bindpose_element

    # Modified the functions to adapt the fbx output to UE

    SCALE_FACTOR = 100

    def fbx_animations_do(scene_data, ref_id, f_start, f_end, start_zero, objects=None, force_keep=False):
        """
        Generate animation data (a single AnimStack) from objects, for a given frame range.
        """
        bake_step = scene_data.settings.bake_anim_step
        simplify_fac = scene_data.settings.bake_anim_simplify_factor
        scene = scene_data.scene
        depsgraph = scene_data.depsgraph
        force_keying = scene_data.settings.bake_anim_use_all_bones
        force_sek = scene_data.settings.bake_anim_force_startend_keying

        if objects is not None:
            # Add bones and duplis!
            for ob_obj in tuple(objects):
                if not ob_obj.is_object:
                    continue
                if ob_obj.type == 'ARMATURE':
                    objects |= {bo_obj for bo_obj in ob_obj.bones if bo_obj in scene_data.objects}
                for dp_obj in ob_obj.dupli_list_gen(depsgraph):
                    if dp_obj in scene_data.objects:
                        objects.add(dp_obj)
        else:
            objects = scene_data.objects

        back_currframe = scene.frame_current
        animdata_ob = {}
        p_rots = {}

        for ob_obj in objects:
            if ob_obj.parented_to_armature:
                continue
            ACNW = AnimationCurveNodeWrapper
            loc, rot, scale, _m, _mr = ob_obj.fbx_object_tx(scene_data)
            rot_deg = tuple(convert_rad_to_deg_iter(rot))
            force_key = (simplify_fac == 0.0) or (ob_obj.is_bone and force_keying)

            animdata_ob[ob_obj] = (ACNW(ob_obj.key, 'LCL_TRANSLATION', force_key, force_sek, loc),
                                   ACNW(ob_obj.key, 'LCL_ROTATION', force_key, force_sek, rot_deg),
                                   ACNW(ob_obj.key, 'LCL_SCALING', force_key, force_sek, scale))
            p_rots[ob_obj] = rot

        force_key = (simplify_fac == 0.0)
        animdata_shapes = {}

        for me, (me_key, _shapes_key, shapes) in scene_data.data_deformers_shape.items():
            # Ignore absolute shape keys for now!
            if not me.shape_keys.use_relative:
                continue
            for shape, (channel_key, geom_key, _shape_verts_co, _shape_verts_idx) in shapes.items():
                acnode = AnimationCurveNodeWrapper(channel_key, 'SHAPE_KEY', force_key, force_sek, (0.0,))
                # Sooooo happy to have to twist again like a mad snake... Yes, we need to write those curves twice. :/
                acnode.add_group(me_key, shape.name, shape.name, (shape.name,))
                animdata_shapes[channel_key] = (acnode, me, shape)

        animdata_cameras = {}
        for cam_obj, cam_key in scene_data.data_cameras.items():
            cam = cam_obj.bdata.data
            acnode = AnimationCurveNodeWrapper(cam_key, 'CAMERA_FOCAL', force_key, force_sek, (cam.lens,))
            animdata_cameras[cam_key] = (acnode, cam)

        currframe = f_start
        while currframe <= f_end:
            real_currframe = currframe - f_start if start_zero else currframe
            scene.frame_set(int(currframe), subframe=currframe - int(currframe))

            for dp_obj in ob_obj.dupli_list_gen(depsgraph):
                pass  # Merely updating dupli matrix of ObjectWrapper...

            for ob_obj, (anim_loc, anim_rot, anim_scale) in animdata_ob.items():
                location_multiple = 100
                scale_factor = 1

                # if this curve is the object root then keep its scale at 1
                if len(str(ob_obj).split('|')) == 1:
                    location_multiple = 1
                    # Todo add to FBX addon
                    scale_factor = SCALE_FACTOR

                # We compute baked loc/rot/scale for all objects (rot being euler-compat with previous value!).
                p_rot = p_rots.get(ob_obj, None)
                loc, rot, scale, _m, _mr = ob_obj.fbx_object_tx(scene_data, rot_euler_compat=p_rot)

                # Todo add to FBX addon
                # the armature object's position is the reference we use to offset all location keyframes
                if ob_obj.type == 'ARMATURE':
                    location_offset = loc
                    # subtract the location offset from each location keyframe if the use_object_origin is on
                    if bpy.context.scene.send2ue.use_object_origin:
                        loc = mathutils.Vector(
                            (loc[0] - location_offset[0], loc[1] - location_offset[1], loc[2] - location_offset[2]))

                p_rots[ob_obj] = rot
                anim_loc.add_keyframe(real_currframe, loc * location_multiple)
                anim_rot.add_keyframe(real_currframe, tuple(convert_rad_to_deg_iter(rot)))
                anim_scale.add_keyframe(real_currframe, scale / scale_factor)
            for anim_shape, me, shape in animdata_shapes.values():
                anim_shape.add_keyframe(real_currframe, (shape.value * scale_factor,))
            for anim_camera, camera in animdata_cameras.values():
                anim_camera.add_keyframe(real_currframe, (camera.lens,))
            currframe += bake_step

        scene.frame_set(back_currframe, subframe=0.0)

        animations = {}

        # And now, produce final data (usable by FBX export code)
        # Objects-like loc/rot/scale...
        for ob_obj, anims in animdata_ob.items():
            for anim in anims:
                anim.simplify(simplify_fac, bake_step, force_keep)
                if not anim:
                    continue
                for obj_key, group_key, group, fbx_group, fbx_gname in anim.get_final_data(scene, ref_id, force_keep):
                    anim_data = animations.setdefault(obj_key, ("dummy_unused_key", {}))
                    anim_data[1][fbx_group] = (group_key, group, fbx_gname)

        # And meshes' shape keys.
        for channel_key, (anim_shape, me, shape) in animdata_shapes.items():
            final_keys = {}
            anim_shape.simplify(simplify_fac, bake_step, force_keep)
            if not anim_shape:
                continue
            for elem_key, group_key, group, fbx_group, fbx_gname in anim_shape.get_final_data(scene, ref_id,
                                                                                              force_keep):
                anim_data = animations.setdefault(elem_key, ("dummy_unused_key", {}))
                anim_data[1][fbx_group] = (group_key, group, fbx_gname)

        # And cameras' lens keys.
        for cam_key, (anim_camera, camera) in animdata_cameras.items():
            final_keys = {}
            anim_camera.simplify(simplify_fac, bake_step, force_keep)
            if not anim_camera:
                continue
            for elem_key, group_key, group, fbx_group, fbx_gname in anim_camera.get_final_data(scene, ref_id,
                                                                                               force_keep):
                anim_data = animations.setdefault(elem_key, ("dummy_unused_key", {}))
                anim_data[1][fbx_group] = (group_key, group, fbx_gname)

        astack_key = get_blender_anim_stack_key(scene, ref_id)
        alayer_key = get_blender_anim_layer_key(scene, ref_id)
        name = (get_blenderID_name(ref_id) if ref_id else scene.name).encode()

        if start_zero:
            f_end -= f_start
            f_start = 0.0

        return (astack_key, animations, alayer_key, name, f_start, f_end) if animations else None

    def fbx_data_armature_elements(root, arm_obj, scene_data):
        """
        Write:
            * Bones "data" (NodeAttribute::LimbNode, contains pretty much nothing!).
            * Deformers (i.e. Skin), bind between an armature and a mesh.
            ** SubDeformers (i.e. Cluster), one per bone/vgroup pair.
            * BindPose.
        Note armature itself has no data, it is a mere "Null" Model...
        """
        mat_world_arm = arm_obj.fbx_object_matrix(scene_data, global_space=True)
        bones = tuple(bo_obj for bo_obj in arm_obj.bones if bo_obj in scene_data.objects)

        bone_radius_scale = 33.0

        # Bones "data".
        for bo_obj in bones:
            bo = bo_obj.bdata
            bo_data_key = scene_data.data_bones[bo_obj]
            fbx_bo = elem_data_single_int64(root, b"NodeAttribute", get_fbx_uuid_from_key(bo_data_key))
            fbx_bo.add_string(fbx_name_class(bo.name.encode(), b"NodeAttribute"))
            fbx_bo.add_string(b"LimbNode")
            elem_data_single_string(fbx_bo, b"TypeFlags", b"Skeleton")

            tmpl = elem_props_template_init(scene_data.templates, b"Bone")
            props = elem_properties(fbx_bo)
            elem_props_template_set(tmpl, props, "p_double", b"Size", bo.head_radius * bone_radius_scale * SCALE_FACTOR)
            elem_props_template_finalize(tmpl, props)

            # Custom properties.
            if scene_data.settings.use_custom_props:
                fbx_data_element_custom_properties(props, bo)

            # Store Blender bone length - XXX Not much useful actually :/
            # (LimbLength can't be used because it is a scale factor 0-1 for the parent-child distance:
            # http://docs.autodesk.com/FBX/2014/ENU/FBX-SDK-Documentation/cpp_ref/class_fbx_skeleton.html#a9bbe2a70f4ed82cd162620259e649f0f )
            # elem_props_set(props, "p_double", "BlenderBoneLength".encode(), (bo.tail_local - bo.head_local).length, custom=True)

        # Skin deformers and BindPoses.
        # Note: we might also use Deformers for our "parent to vertex" stuff???
        deformer = scene_data.data_deformers_skin.get(arm_obj, None)
        if deformer is not None:
            for me, (skin_key, ob_obj, clusters) in deformer.items():
                # BindPose.
                mat_world_obj, mat_world_bones = fbx_data_bindpose_element(root, ob_obj, me, scene_data,
                                                                           arm_obj, mat_world_arm, bones)

                # Deformer.
                fbx_skin = elem_data_single_int64(root, b"Deformer", get_fbx_uuid_from_key(skin_key))
                fbx_skin.add_string(fbx_name_class(arm_obj.name.encode(), b"Deformer"))
                fbx_skin.add_string(b"Skin")

                elem_data_single_int32(fbx_skin, b"Version", FBX_DEFORMER_SKIN_VERSION)
                elem_data_single_float64(fbx_skin, b"Link_DeformAcuracy", 50.0)  # Only vague idea what it is...

                # Pre-process vertex weights (also to check vertices assigned ot more than four bones).
                ob = ob_obj.bdata
                bo_vg_idx = {bo_obj.bdata.name: ob.vertex_groups[bo_obj.bdata.name].index
                             for bo_obj in clusters.keys() if bo_obj.bdata.name in ob.vertex_groups}
                valid_idxs = set(bo_vg_idx.values())
                vgroups = {vg.index: {} for vg in ob.vertex_groups}
                verts_vgroups = (
                sorted(((vg.group, vg.weight) for vg in v.groups if vg.weight and vg.group in valid_idxs),
                       key=lambda e: e[1], reverse=True)
                for v in me.vertices)
                for idx, vgs in enumerate(verts_vgroups):
                    for vg_idx, w in vgs:
                        vgroups[vg_idx][idx] = w

                for bo_obj, clstr_key in clusters.items():
                    bo = bo_obj.bdata
                    # Find which vertices are affected by this bone/vgroup pair, and matching weights.
                    # Note we still write a cluster for bones not affecting the mesh, to get 'rest pose' data
                    # (the TransformBlah matrices).
                    vg_idx = bo_vg_idx.get(bo.name, None)
                    indices, weights = ((), ()) if vg_idx is None or not vgroups[vg_idx] else zip(
                        *vgroups[vg_idx].items())

                    # Create the cluster.
                    fbx_clstr = elem_data_single_int64(root, b"Deformer", get_fbx_uuid_from_key(clstr_key))
                    fbx_clstr.add_string(fbx_name_class(bo.name.encode(), b"SubDeformer"))
                    fbx_clstr.add_string(b"Cluster")

                    elem_data_single_int32(fbx_clstr, b"Version", FBX_DEFORMER_CLUSTER_VERSION)
                    # No idea what that user data might be...
                    fbx_userdata = elem_data_single_string(fbx_clstr, b"UserData", b"")
                    fbx_userdata.add_string(b"")
                    if indices:
                        elem_data_single_int32_array(fbx_clstr, b"Indexes", indices)
                        elem_data_single_float64_array(fbx_clstr, b"Weights", weights)
                    # Transform, TransformLink and TransformAssociateModel matrices...
                    # They seem to be doublons of BindPose ones??? Have armature (associatemodel) in addition, though.
                    # WARNING! Even though official FBX API presents Transform in global space,
                    #          **it is stored in bone space in FBX data!** See:
                    #          http://area.autodesk.com/forum/autodesk-fbx/fbx-sdk/why-the-values-return-
                    #                 by-fbxcluster-gettransformmatrix-x-not-same-with-the-value-in-ascii-fbx-file/
                    # test_data[bo_obj.name] = matrix4_to_array(mat_world_bones[bo_obj].inverted_safe() @ mat_world_obj)

                    # Todo add to FBX addon
                    transform_matrix = mat_world_bones[bo_obj].inverted_safe() @ mat_world_obj
                    transform_link_matrix = mat_world_bones[bo_obj]
                    transform_associate_model_matrix = mat_world_arm

                    transform_matrix = transform_matrix.LocRotScale(
                        [i * SCALE_FACTOR for i in transform_matrix.to_translation()],
                        transform_matrix.to_quaternion(),
                        [i * SCALE_FACTOR for i in transform_matrix.to_scale()],
                    )

                    elem_data_single_float64_array(fbx_clstr, b"Transform", matrix4_to_array(transform_matrix))
                    elem_data_single_float64_array(fbx_clstr, b"TransformLink", matrix4_to_array(transform_link_matrix))
                    elem_data_single_float64_array(fbx_clstr, b"TransformAssociateModel",
                                                   matrix4_to_array(transform_associate_model_matrix))

    def fbx_data_object_elements(root, ob_obj, scene_data):
        """
        Write the Object (Model) data blocks.
        Note this "Model" can also be bone or dupli!
        """
        obj_type = b"Null"  # default, sort of empty...
        if ob_obj.is_bone:
            obj_type = b"LimbNode"
        elif (ob_obj.type == 'ARMATURE'):
            if scene_data.settings.armature_nodetype == 'ROOT':
                obj_type = b"Root"
            elif scene_data.settings.armature_nodetype == 'LIMBNODE':
                obj_type = b"LimbNode"
            else:  # Default, preferred option...
                obj_type = b"Null"
        elif (ob_obj.type in BLENDER_OBJECT_TYPES_MESHLIKE):
            obj_type = b"Mesh"
        elif (ob_obj.type == 'LIGHT'):
            obj_type = b"Light"
        elif (ob_obj.type == 'CAMERA'):
            obj_type = b"Camera"

        if ob_obj.type == 'ARMATURE':
            if bpy.context.scene.send2ue.export_object_name_as_root:
                # if the object is already named armature this forces the object name to root
                if 'armature' == ob_obj.name.lower():
                    ob_obj.name = 'root'

            # otherwise don't use the armature objects name as the root in unreal
            else:
                # Rename the armature object to 'Armature'. This is important, because this is a special
                # reserved keyword for the Unreal FBX importer that will be ignored when the bone hierarchy
                # is imported from the FBX file. That way there is not an additional root bone in the Unreal
                # skeleton hierarchy.
                ob_obj.name = 'Armature'

        model = elem_data_single_int64(root, b"Model", ob_obj.fbx_uuid)
        model.add_string(fbx_name_class(ob_obj.name.encode(), b"Model"))
        model.add_string(obj_type)

        elem_data_single_int32(model, b"Version", FBX_MODELS_VERSION)

        # Object transform info.
        loc, rot, scale, matrix, matrix_rot = ob_obj.fbx_object_tx(scene_data)
        rot = tuple(convert_rad_to_deg_iter(rot))

        # Todo add to FBX addon
        if ob_obj.type == 'ARMATURE':
            scale = mathutils.Vector((scale[0] / SCALE_FACTOR, scale[1] / SCALE_FACTOR, scale[2] / SCALE_FACTOR))
            if bpy.context.scene.send2ue.use_object_origin:
                loc = mathutils.Vector((0, 0, 0))

        elif ob_obj.type == 'Ellipsis':
            loc = mathutils.Vector((loc[0] * SCALE_FACTOR, loc[1] * SCALE_FACTOR, loc[2] * SCALE_FACTOR))
        elif ob_obj.type == 'MESH':
            # centers mesh object by their object origin
            if bpy.context.scene.send2ue.use_object_origin:
                asset_id = bpy.context.window_manager.send2ue.asset_id
                asset_data = bpy.context.window_manager.send2ue.asset_data.get(asset_id)
                # if this is a static mesh then check that all other mesh objects in this export are
                # centered relative the asset object
                if asset_data['_asset_type'] == 'StaticMesh':
                    asset_object = bpy.data.objects.get(asset_data['_mesh_object_name'])
                    current_object = bpy.data.objects.get(ob_obj.name)
                    asset_world_location = asset_object.matrix_world.to_translation()
                    object_world_location = current_object.matrix_world.to_translation()
                    loc = mathutils.Vector((
                        (object_world_location[0] - asset_world_location[0]) * SCALE_FACTOR,
                        (object_world_location[1] - asset_world_location[1]) * SCALE_FACTOR,
                        (object_world_location[2] - asset_world_location[2]) * SCALE_FACTOR
                    ))

                    if bpy.context.scene.send2ue.extensions.instance_assets.place_in_active_level:
                        # clear rotation and scale only if spawning actor
                        # https://github.com/EpicGames/BlenderTools/issues/610
                        rot = (0, 0, 0)
                        scale = (1.0 * SCALE_FACTOR, 1.0 * SCALE_FACTOR, 1.0 * SCALE_FACTOR)
                else:
                    loc = mathutils.Vector((0, 0, 0))

        tmpl = elem_props_template_init(scene_data.templates, b"Model")
        # For now add only loc/rot/scale...
        props = elem_properties(model)
        elem_props_template_set(tmpl, props, "p_lcl_translation", b"Lcl Translation", loc,
                                animatable=True, animated=((ob_obj.key, "Lcl Translation") in scene_data.animated))
        elem_props_template_set(tmpl, props, "p_lcl_rotation", b"Lcl Rotation", rot,
                                animatable=True, animated=((ob_obj.key, "Lcl Rotation") in scene_data.animated))
        elem_props_template_set(tmpl, props, "p_lcl_scaling", b"Lcl Scaling", scale,
                                animatable=True, animated=((ob_obj.key, "Lcl Scaling") in scene_data.animated))
        elem_props_template_set(tmpl, props, "p_visibility", b"Visibility", float(not ob_obj.hide))

        # Absolutely no idea what this is, but seems mandatory for validity of the file, and defaults to
        # invalid -1 value...
        elem_props_template_set(tmpl, props, "p_integer", b"DefaultAttributeIndex", 0)

        elem_props_template_set(tmpl, props, "p_enum", b"InheritType", 1)  # RSrs

        # Custom properties.
        if scene_data.settings.use_custom_props:
            # Here we want customprops from the 'pose' bone, not the 'edit' bone...
            bdata = ob_obj.bdata_pose_bone if ob_obj.is_bone else ob_obj.bdata
            fbx_data_element_custom_properties(props, bdata)

        # Those settings would obviously need to be edited in a complete version of the exporter, may depends on
        # object type, etc.
        elem_data_single_int32(model, b"MultiLayer", 0)
        elem_data_single_int32(model, b"MultiTake", 0)
        elem_data_single_bool(model, b"Shading", True)
        elem_data_single_string(model, b"Culling", b"CullingOff")

        if obj_type == b"Camera":
            # Why, oh why are FBX cameras such a mess???
            # And WHY add camera data HERE??? Not even sure this is needed...
            render = scene_data.scene.render
            width = render.resolution_x * 1.0
            height = render.resolution_y * 1.0
            elem_props_template_set(tmpl, props, "p_enum", b"ResolutionMode", 0)  # Don't know what it means
            elem_props_template_set(tmpl, props, "p_double", b"AspectW", width)
            elem_props_template_set(tmpl, props, "p_double", b"AspectH", height)
            elem_props_template_set(tmpl, props, "p_bool", b"ViewFrustum", True)
            elem_props_template_set(tmpl, props, "p_enum", b"BackgroundMode", 0)  # Don't know what it means
            elem_props_template_set(tmpl, props, "p_bool", b"ForegroundTransparent", True)

        elem_props_template_finalize(tmpl, props)

    def fbx_data_bindpose_element(root, me_obj, me, scene_data, arm_obj=None, mat_world_arm=None, bones=[]):
        """
        Helper, since bindpose are used by both meshes shape keys and armature bones...
        """
        if arm_obj is None:
            arm_obj = me_obj
        # We assume bind pose for our bones are their "Editmode" pose...
        # All matrices are expected in global (world) space.
        bindpose_key = get_blender_bindpose_key(arm_obj.bdata, me)
        fbx_pose = elem_data_single_int64(root, b"Pose", get_fbx_uuid_from_key(bindpose_key))
        fbx_pose.add_string(fbx_name_class(me.name.encode(), b"Pose"))
        fbx_pose.add_string(b"BindPose")

        elem_data_single_string(fbx_pose, b"Type", b"BindPose")
        elem_data_single_int32(fbx_pose, b"Version", FBX_POSE_BIND_VERSION)
        elem_data_single_int32(fbx_pose, b"NbPoseNodes", 1 + (1 if (arm_obj != me_obj) else 0) + len(bones))

        # First node is mesh/object.
        mat_world_obj = me_obj.fbx_object_matrix(scene_data, global_space=True)
        fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
        elem_data_single_int64(fbx_posenode, b"Node", me_obj.fbx_uuid)
        elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(mat_world_obj))

        # Second node is armature object itself.
        if arm_obj != me_obj:
            fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
            elem_data_single_int64(fbx_posenode, b"Node", arm_obj.fbx_uuid)

            # Todo merge into blenders FBX addon
            mat_world_arm = mat_world_arm.LocRotScale(
                mat_world_arm.to_translation(),
                mat_world_arm.to_quaternion(),
                [i / SCALE_FACTOR for i in mat_world_arm.to_scale()],
            )

            elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(mat_world_arm))

        # And all bones of armature!
        mat_world_bones = {}
        for bo_obj in bones:
            bomat = bo_obj.fbx_object_matrix(scene_data, rest=True, global_space=True)
            mat_world_bones[bo_obj] = bomat
            fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
            elem_data_single_int64(fbx_posenode, b"Node", bo_obj.fbx_uuid)

            # Todo merge into blenders FBX addon
            bomat = bomat.LocRotScale(
                bomat.to_translation(),
                bomat.to_quaternion(),
                [i / SCALE_FACTOR for i in bomat.to_scale()]
            )

            elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(bomat))

        return mat_world_obj, mat_world_bones

    export_parameters["global_matrix"] = (
        axis_conversion(
            to_forward=export_parameters['axis_forward'],
            to_up=export_parameters['axis_up'],
        ).to_4x4()
    )

    # Replace the modified functions temporarily
    export_fbx_bin.fbx_animations_do            = fbx_animations_do
    export_fbx_bin.fbx_data_armature_elements   = fbx_data_armature_elements
    export_fbx_bin.fbx_data_object_elements     = fbx_data_object_elements
    export_fbx_bin.fbx_data_bindpose_element    = fbx_data_bindpose_element
    
    # Simulate the FBX Export Operator Class
    self = type(
        'FMCExportFBX',
        (object,),
        {'report': print("error")}
    )

    # Export the FBX file
    export_fbx_bin.save(self, bpy.context, **export_parameters)

    # Restore the modified functions with the saved backups
    export_fbx_bin.fbx_animations_do            = backup_fbx_animations_do
    export_fbx_bin.fbx_data_armature_elements   = backup_fbx_data_armature_elements
    export_fbx_bin.fbx_data_object_elements     = backup_fbx_data_object_elements
    export_fbx_bin.fbx_data_bindpose_element    = backup_fbx_data_bindpose_element


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
    correct_fingers_empties: bpy.props.BoolProperty(
        name        = '',
        default     = True,
        description = 'Correct the fingers empties. Match hand_wrist (axis empty) position to wrist (sphere empty)'
    )
    add_hand_middle_empty: bpy.props.BoolProperty(
        name        = '',
        default     = True,
        description = 'Add an empty in the middle of the hand between index and pinky empties. This empty is used for a better orientation of the hand (experimental)'
    )
    
    # Reduce Bone Length Dispersion Options
    interval_variable: bpy.props.EnumProperty(
        name        = '',
        description = 'Variable used to define the new length dispersion interval',
        items       = [ ('standard_lenght', 'Standard Lenght', 'Use the standard lenghts based on the total body (rig) height. Defines the new dispersion interval as [lenght*(1-interval_factor),lenght*(1+interval_factor)]'),
                        ('capture_median', 'Capture Median', 'Use the bones median lenght from the capture. Defines the new dispersion interval as [median*(1-interval_factor),median*(1+interval_factor)]'),
                        ('capture_stdev', 'Capture Std Dev', 'Use the bones lenght standard deviation from the capture. Defines the new dispersion interval as [median-interval_factor*stdev,median+interval_factor*stdev]')]
    )
    interval_factor: bpy.props.FloatProperty(
        name        = '',
        default     = 0,
        min         = 0,
        precision   = 3,
        description = 'Factor to multiply the variable and form the limits of the dispersion interval like [median-factor*variable,median+factor*variable]. ' +
                      'If variable is median, the factor will be limited to values inside [0, 1].' + 
                      'If variable is stdev, the factor will be limited to values inside [0, median/stdev]'
    )
    body_height: bpy.props.FloatProperty(
        name        = '',
        default     = 1.75,
        min         = 0,
        precision   = 3,
        description = 'Body height in meters. This value is used when the interval variable is set to standard lenght. If a rig is added after using Reduce Dispersion with standard length, it will have this value as height and the bones lenght will be proporions of this height'
    )

    # Reduce Shakiness Options
    recording_fps: bpy.props.FloatProperty(
        name        = '',
        default     = 30,
        min         = 0,
        precision   = 3,
        description = 'Frames per second (fps) of the capture recording'
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
    add_fingers_constraints: bpy.props.BoolProperty(
        name        = '',
        default     = True,
        description = 'Add bone constraints for fingers'
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
        items       = [('custom', 'custom', ''),
                       ('file', 'file', '')]
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
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Correct Fingers Empties')
        split.split().column().prop(fmc_adapter_tool, 'correct_fingers_empties')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add hand middle empty')
        split.split().column().prop(fmc_adapter_tool, 'add_hand_middle_empty')

        box.operator('fmc_adapter.adjust_empties', text='1. Adjust Empties')

        # Reduce Bone Length Dispersion Options
        box = layout.box()
        #box.label(text='Reduce Bone Length Dispersion Options')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Variable')
        split.split().column().prop(fmc_adapter_tool, 'interval_variable')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Dispersion Interval Factor')
        split.split().column().prop(fmc_adapter_tool, 'interval_factor')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Body (Rig) Height [m]')
        split.split().column().prop(fmc_adapter_tool, 'body_height')

        box.operator('fmc_adapter.reduce_bone_length_dispersion', text='2. Reduce Bone Length Dispersion')

        # Reduce Shakiness Options
        # box = layout.box()
        # #box.label(text='Reduce Shakiness Options')
        
        # split = box.column().row().split(factor=0.6)
        # split.column().label(text='Recording FPS')
        # split.split().column().prop(fmc_adapter_tool, 'recording_fps')

        # box.operator('fmc_adapter.reduce_shakiness', text='Reduce Shakiness')
        
        # Add Rig Options
        box = layout.box()
        #box.label(text='Add Rig Options')
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Keep right/left symmetry')
        split.split().column().prop(fmc_adapter_tool, 'keep_symmetry')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add finger constraints')
        split.split().column().prop(fmc_adapter_tool, 'add_fingers_constraints')

        split = box.column().row().split(factor=0.6)
        split.column().label(text='Add rotation limits')
        split.split().column().prop(fmc_adapter_tool, 'use_limit_rotation')
        
        box.operator('fmc_adapter.add_rig', text='3. Add Rig')
        
        # Add Body Mesh Options
        box = layout.box()
        #box.label(text='Add Body Mesh Options')
        
        split = box.column().row().split(factor=0.6)
        split.column().label(text='Body Mesh Mode')
        split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')
        
        #box.operator('fmc_adapter.actions_op', text='Add Body Mesh').action = 'ADD_BODY_MESH'
        box.operator('fmc_adapter.add_body_mesh', text='4. Add Body Mesh')

        # FBX Export
        box = layout.box()
        box.operator('fmc_adapter.export_fbx', text='5. Export FBX')

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
                       z_translation_offset=fmc_adapter_tool.vertical_align_position_offset,
                       correct_fingers_empties=fmc_adapter_tool.correct_fingers_empties,
                       add_hand_middle_empty=fmc_adapter_tool.add_hand_middle_empty
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
                                      interval_factor=fmc_adapter_tool.interval_factor,
                                      body_height=fmc_adapter_tool.body_height)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

class FMC_ADAPTER_OT_reduce_shakiness(Operator):
    bl_idname       = 'fmc_adapter.reduce_shakiness'
    bl_label        = 'Freemocap Adapter - Reduce Shakiness'
    bl_description  = 'Reduce the shakiness of the capture empties by restricting their acceleration to a defined threshold'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()
        print('Executing Reduce Shakiness...')

        reduce_shakiness(recording_fps=fmc_adapter_tool.recording_fps)

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
                        z_translation_offset=fmc_adapter_tool.vertical_align_position_offset  ,
                        add_hand_middle_empty=fmc_adapter_tool.add_hand_middle_empty,                     
                        )
        
        print('Executing Add Rig...')

        add_rig(keep_symmetry=fmc_adapter_tool.keep_symmetry,
                add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
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
            add_rig(keep_symmetry=fmc_adapter_tool.keep_symmetry,
                    add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
                    use_limit_rotation=fmc_adapter_tool.use_limit_rotation)
        
        print('Executing Add Body Mesh...')
        add_mesh_to_rig(body_mesh_mode=fmc_adapter_tool.body_mesh_mode,
                        body_height=fmc_adapter_tool.body_height)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}
    
class FMC_ADAPTER_OT_export_fbx(Operator):
    bl_idname       = 'fmc_adapter.export_fbx'
    bl_label        = 'Freemocap Adapter - Export FBX'
    bl_description  = 'Exports a FBX file containing the rig, the mesh and the baked animation'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        # Get start time
        start = time.time()

        print('Executing Export FBX...')

        # Execute export fbx function
        export_fbx(self)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

classes = [FMC_ADAPTER_PROPERTIES,
           VIEW3D_PT_freemocap_adapter,
           FMC_ADAPTER_OT_adjust_empties,
           FMC_ADAPTER_OT_reduce_bone_length_dispersion,
           FMC_ADAPTER_OT_reduce_shakiness,
           FMC_ADAPTER_OT_add_rig,
           FMC_ADAPTER_OT_add_body_mesh,
           FMC_ADAPTER_OT_export_fbx
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

