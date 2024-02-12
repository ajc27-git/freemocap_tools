bl_info = {
    'name'          : 'Freemocap Adapter Alt',
    'author'        : 'ajc27',
    'version'       : (1, 3, 2),
    'blender'       : (3, 0, 0),
    'location'      : '3D Viewport > Sidebar > Freemocap Adapter Alt',
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
import numpy as np

scipy_available = True
try:
    from scipy.signal import butter, filtfilt
except ImportError:
    scipy_available = False
    print("scipy is not installed. Please install scipy to use this addon.")

from .io_scene_fbx_functions_blender3 import *
# from .io_scene_fbx_functions_blender4 import *

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

# Location and rotation vectors of the empties_parent in the Adjust Empties method just before resetting its location and rotation to (0, 0, 0)
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
        'head'              : 'hips_center',
        'tail'              : 'right_hip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'pelvis.L': {
        'head'              : 'hips_center',
        'tail'              : 'left_hip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'spine': {
        'head'              : 'hips_center',
        'tail'              : 'trunk_center',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'spine.001': {
        'head'              : 'trunk_center',
        'tail'              : 'neck_center',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'neck': {
        'head'              : 'neck_center',
        'tail'              : 'head_center',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'head_nose': { # Auxiliary bone from head center to nose tip to align the face bones 
        'head'              : 'head_center',
        'tail'              : 'nose',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'shoulder.R': {
        'head'              : 'neck_center',
        'tail'              : 'right_shoulder',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'shoulder.L': {
        'head'              : 'neck_center',
        'tail'              : 'left_shoulder',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'upper_arm.R': {
        'head'              : 'right_shoulder',
        'tail'              : 'right_elbow',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'upper_arm.L': {
        'head'              : 'left_shoulder',
        'tail'              : 'left_elbow',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'forearm.R': {
        'head'              : 'right_elbow',
        'tail'              : 'right_wrist',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'forearm.L': {
        'head'              : 'left_elbow',
        'tail'              : 'left_wrist',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'hand.R': {
        'head'              : 'right_wrist',
        'tail'              : 'right_hand_middle',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'hand.L': {
        'head'              : 'left_wrist',
        'tail'              : 'left_hand_middle',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.carpal.R': { # Auxiliary bone to align the right_hand_thumb_cmc empty
        'head'              : 'right_hand_wrist',
        'tail'              : 'right_hand_thumb_cmc',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'hands',
        'parent_bone'       : 'hand.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.carpal.L': { # Auxiliary bone to align the left_hand_thumb_cmc empty
        'head'              : 'left_hand_wrist',
        'tail'              : 'left_hand_thumb_cmc',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'hands',
        'parent_bone'       : 'hand.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.01.R': {
        'head'              : 'right_hand_thumb_cmc',
        'tail'              : 'right_hand_thumb_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'thumb.carpal.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -50,
        'rot_limit_max_x'   : 50,
        'rot_limit_min_z'   : -60,
        'rot_limit_max_z'   : 30,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.01.L': {
        'head'              : 'left_hand_thumb_cmc',
        'tail'              : 'left_hand_thumb_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'thumb.carpal.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -50,
        'rot_limit_max_x'   : 50,
        'rot_limit_min_z'   : -60,
        'rot_limit_max_z'   : 30,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.02.R': {
        'head'              : 'right_hand_thumb_mcp',
        'tail'              : 'right_hand_thumb_ip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'thumb.01.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 40,
        'rot_limit_min_z'   : -10,
        'rot_limit_max_z'   : 10,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.02.L': {
        'head'              : 'left_hand_thumb_mcp',
        'tail'              : 'left_hand_thumb_ip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'thumb.01.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -40,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : -10,
        'rot_limit_max_z'   : 10,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.03.R': {
        'head'              : 'right_hand_thumb_ip',
        'tail'              : 'right_hand_thumb_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'thumb.02.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -10,
        'rot_limit_max_x'   : 90,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thumb.03.L': {
        'head'              : 'left_hand_thumb_ip',
        'tail'              : 'left_hand_thumb_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'thumb.02.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -90,
        'rot_limit_max_x'   : 10,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.01.R': {
        'head'              : 'right_hand_wrist',
        'tail'              : 'right_hand_index_finger_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -360,
        'rot_limit_max_x'   : 360,
        'rot_limit_min_z'   : 14,
        'rot_limit_max_z'   : 16,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.01.L': {
        'head'              : 'left_hand_wrist',
        'tail'              : 'left_hand_index_finger_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : 14,
        'rot_limit_max_z'   : 16,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_index.01.R': {
        'head'              : 'right_hand_index_finger_mcp',
        'tail'              : 'right_hand_index_finger_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.01.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -30,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : -30,
        'rot_limit_max_z'   : 40,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_index.01.L': {
        'head'              : 'left_hand_index_finger_mcp',
        'tail'              : 'left_hand_index_finger_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.01.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 30,
        'rot_limit_min_z'   : -30,
        'rot_limit_max_z'   : 40,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_index.02.R': {
        'head'              : 'right_hand_index_finger_pip',
        'tail'              : 'right_hand_index_finger_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_index.01.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 90,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : True,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_index.02.L': {
        'head'              : 'left_hand_index_finger_pip',
        'tail'              : 'left_hand_index_finger_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_index.01.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -90,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_index.03.R': {
        'head'              : 'right_hand_index_finger_dip',
        'tail'              : 'right_hand_index_finger_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_index.02.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : True,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_index.03.L': {
        'head'              : 'left_hand_index_finger_dip',
        'tail'              : 'left_hand_index_finger_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_index.02.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.02.R': {
        'head'              : 'right_hand_wrist',
        'tail'              : 'right_hand_middle_finger_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.02.L': {
        'head'              : 'left_hand_wrist',
        'tail'              : 'left_hand_middle_finger_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_middle.01.R': {
        'head'              : 'right_hand_middle_finger_mcp',
        'tail'              : 'right_hand_middle_finger_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.02.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -30,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : -30,
        'rot_limit_max_z'   : 30,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_middle.01.L': {
        'head'              : 'left_hand_middle_finger_mcp',
        'tail'              : 'left_hand_middle_finger_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.02.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 30,
        'rot_limit_min_z'   : -30,
        'rot_limit_max_z'   : 30,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_middle.02.R': {
        'head'              : 'right_hand_middle_finger_pip',
        'tail'              : 'right_hand_middle_finger_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_middle.01.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 90,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_middle.02.L': {
        'head'              : 'left_hand_middle_finger_pip',
        'tail'              : 'left_hand_middle_finger_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_middle.01.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -90,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_middle.03.R': {
        'head'              : 'right_hand_middle_finger_dip',
        'tail'              : 'right_hand_middle_finger_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_middle.02.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_middle.03.L': {
        'head'              : 'left_hand_middle_finger_dip',
        'tail'              : 'left_hand_middle_finger_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_middle.02.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.03.R': {
        'head'              : 'right_hand_wrist',
        'tail'              : 'right_hand_ring_finger_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : -16,
        'rot_limit_max_z'   : -14,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.03.L': {
        'head'              : 'left_hand_wrist',
        'tail'              : 'left_hand_ring_finger_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : -16,
        'rot_limit_max_z'   : -14,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_ring.01.R': {
        'head'              : 'right_hand_ring_finger_mcp',
        'tail'              : 'right_hand_ring_finger_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.03.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -30,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : -20,
        'rot_limit_max_z'   : 30,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_ring.01.L': {
        'head'              : 'left_hand_ring_finger_mcp',
        'tail'              : 'left_hand_ring_finger_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.03.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 30,
        'rot_limit_min_z'   : -20,
        'rot_limit_max_z'   : 30,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_ring.02.R': {
        'head'              : 'right_hand_ring_finger_pip',
        'tail'              : 'right_hand_ring_finger_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_ring.01.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 90,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_ring.02.L': {
        'head'              : 'left_hand_ring_finger_pip',
        'tail'              : 'left_hand_ring_finger_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_ring.01.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -90,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_ring.03.R': {
        'head'              : 'right_hand_ring_finger_dip',
        'tail'              : 'right_hand_ring_finger_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_ring.02.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_ring.03.L': {
        'head'              : 'left_hand_ring_finger_dip',
        'tail'              : 'left_hand_ring_finger_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_ring.02.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.04.R': {
        'head'              : 'right_hand_wrist',
        'tail'              : 'right_hand_pinky_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : -31,
        'rot_limit_max_z'   : -29,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'palm.04.L': {
        'head'              : 'left_hand_wrist',
        'tail'              : 'left_hand_pinky_mcp',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'hand.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -180,
        'rot_limit_max_x'   : 180,
        'rot_limit_min_z'   : -31,
        'rot_limit_max_z'   : -29,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_pinky.01.R': {
        'head'              : 'right_hand_pinky_mcp',
        'tail'              : 'right_hand_pinky_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.04.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -30,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : -30,
        'rot_limit_max_z'   : 40,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_pinky.01.L': {
        'head'              : 'left_hand_pinky_mcp',
        'tail'              : 'left_hand_pinky_pip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'palm.04.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 30,
        'rot_limit_min_z'   : -30,
        'rot_limit_max_z'   : 40,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_pinky.02.R': {
        'head'              : 'right_hand_pinky_pip',
        'tail'              : 'right_hand_pinky_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_pinky.01.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 90,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_pinky.02.L': {
        'head'              : 'left_hand_pinky_pip',
        'tail'              : 'left_hand_pinky_dip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_pinky.01.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -90,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_pinky.03.R': {
        'head'              : 'right_hand_pinky_dip',
        'tail'              : 'right_hand_pinky_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_pinky.02.R',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 60,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'f_pinky.03.L': {
        'head'              : 'left_hand_pinky_dip',
        'tail'              : 'left_hand_pinky_tip',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : 'fingers',
        'parent_bone'       : 'f_pinky.02.L',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : -60,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thigh.R': {
        'head'              : 'right_hip',
        'tail'              : 'right_knee',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'thigh.L': {
        'head'              : 'left_hip',
        'tail'              : 'left_knee',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'shin.R': {
        'head'              : 'right_knee',
        'tail'              : 'right_ankle',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'shin.L': {
        'head'              : 'left_knee',
        'tail'              : 'left_ankle',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'foot.R': {
        'head'              : 'right_ankle',
        'tail'              : 'right_foot_index',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'foot.L': {
        'head'              : 'left_ankle',
        'tail'              : 'left_foot_index',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'heel.02.R': {
        'head'              : 'right_ankle',
        'tail'              : 'right_heel',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
    'heel.02.L': {
        'head'              : 'left_ankle',
        'tail'              : 'left_heel',
        'lengths'           : [],
        'median'            : 0,
        'stdev'             : 0,
        'category'          : '',
        'parent_bone'       : '',
        'bone_x_axis'       : (0,0,0),
        'bone_y_axis'       : (0,0,0),
        'bone_z_axis'       : (0,0,0),
        'rot_limit_min_x'   : 0,
        'rot_limit_max_x'   : 0,
        'rot_limit_min_z'   : 0,
        'rot_limit_max_z'   : 0,
        'has_skelly_part'   : False,
        'default_origin'    : (0, 0, 0),
        'default_length'    : 0,},
}

# Dictionary containing the empty children for each of the capture empties.
# This will be used to correct the position of the empties (and its children) that are outside the bone length interval defined by x*stdev
empties_dict = {
    'hips_center': {
        'children'      : ['right_hip', 'left_hip', 'trunk_center'],
        'category'      : 'core',
        'tail_of_bone'  : ''},
    'trunk_center': {
        'children'      : ['neck_center'],
        'category'      : 'core',
        'tail_of_bone'  : 'spine'},
    'neck_center': {
        'children'      : ['right_shoulder', 'left_shoulder', 'head_center'],
        'category'      : 'core',
        'tail_of_bone'  : 'spine.001'},
    'head_center': {
        'children'      : ['nose', 'mouth_right', 'mouth_left', 'right_eye', 'right_eye_inner', 'right_eye_outer', 'left_eye', 'left_eye_inner', 'left_eye_outer', 'right_ear', 'left_ear'],
        'category'      : 'core',
        'tail_of_bone'  : 'neck'},
    'right_shoulder': {
        'children'      : ['right_elbow'],
        'category'      : 'arms',
        'tail_of_bone'  : 'shoulder.R'},
    'left_shoulder': {
        'children'      : ['left_elbow'],
        'category'      : 'arms',
        'tail_of_bone'  : 'shoulder.L'},
    'right_elbow': {
        'children'      : ['right_wrist'],
        'category'      : 'arms',
        'tail_of_bone'  : 'upper_arm.R'},
    'left_elbow': {
        'children'      : ['left_wrist'],
        'category'      : 'arms',
        'tail_of_bone'  : 'upper_arm.L'},
    'right_wrist': {
        'children'      : ['right_thumb', 'right_index', 'right_pinky', 'right_hand', 'right_hand_middle', 'right_hand_wrist'],
        'category'      : 'hands',
        'tail_of_bone'  : 'forearm.R'},
    'left_wrist': {
        'children'      : ['left_thumb', 'left_index', 'left_pinky', 'left_hand', 'left_hand_middle', 'left_hand_wrist'],
        'category'      : 'hands',
        'tail_of_bone'  : 'forearm.L'},
    'right_hand_middle': {
        'children'      : [],
        'category'      : 'hands',
        'tail_of_bone'  : 'hand.R'},
    'left_hand_middle': {
        'children'      : [],
        'category'      : 'hands',
        'tail_of_bone'  : 'hand.L'},
    'right_hand_wrist': {
        'children'      : ['right_hand_thumb_cmc', 'right_hand_index_finger_mcp', 'right_hand_middle_finger_mcp', 'right_hand_ring_finger_mcp', 'right_hand_pinky_mcp'],
        'category'      : 'hands',
        'tail_of_bone'  : ''},
    'left_hand_wrist': {
        'children'      : ['left_hand_thumb_cmc', 'left_hand_index_finger_mcp', 'left_hand_middle_finger_mcp', 'left_hand_ring_finger_mcp', 'left_hand_pinky_mcp'],
        'category'      : 'hands',
        'tail_of_bone'  : ''},
    'right_hand_thumb_cmc': {
        'children'      : ['right_hand_thumb_mcp'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.carpal.R'},
    'left_hand_thumb_cmc': {
        'children'      : ['left_hand_thumb_mcp'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.carpal.L'},
    'right_hand_thumb_mcp': {
        'children'      : ['right_hand_thumb_ip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.01.R'},
    'left_hand_thumb_mcp': {
        'children'      : ['left_hand_thumb_ip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.01.L'},
    'right_hand_thumb_ip': {
        'children'      : ['right_hand_thumb_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.02.R'},
    'left_hand_thumb_ip': {
        'children'      : ['left_hand_thumb_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.02.L'},
    'right_hand_thumb_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.03.R'},
    'left_hand_thumb_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'thumb.03.L'},
    'right_hand_index_finger_mcp': {
        'children'      : ['right_hand_index_finger_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.01.R'},
    'left_hand_index_finger_mcp': {
        'children'      : ['left_hand_index_finger_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.01.L'},
    'right_hand_index_finger_pip': {
        'children'      : ['right_hand_index_finger_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_index.01.R'},
    'left_hand_index_finger_pip': {
        'children'      : ['left_hand_index_finger_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_index.01.L'},
    'right_hand_index_finger_dip': {
        'children'      : ['right_hand_index_finger_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_index.02.R'},
    'left_hand_index_finger_dip': {
        'children'      : ['left_hand_index_finger_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_index.02.L'},
    'right_hand_index_finger_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_index.03.R'},
    'left_hand_index_finger_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_index.03.L'},
    'right_hand_middle_finger_mcp': {
        'children'      : ['right_hand_middle_finger_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.02.R'},
    'left_hand_middle_finger_mcp': {
        'children'      : ['left_hand_middle_finger_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.02.L'},
    'right_hand_middle_finger_pip': {
        'children'      : ['right_hand_middle_finger_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_middle.01.R'},
    'left_hand_middle_finger_pip': {
        'children'      : ['left_hand_middle_finger_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_middle.01.L'},
    'right_hand_middle_finger_dip': {
        'children'      : ['right_hand_middle_finger_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_middle.02.R'},
    'left_hand_middle_finger_dip': {
        'children'      : ['left_hand_middle_finger_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_middle.02.L'},
    'right_hand_middle_finger_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_middle.03.R'},
    'left_hand_middle_finger_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_middle.03.L'},
    'right_hand_ring_finger_mcp': {
        'children'      : ['right_hand_ring_finger_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.03.R'},
    'left_hand_ring_finger_mcp': {
        'children'      : ['left_hand_ring_finger_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.03.L'},
    'right_hand_ring_finger_pip': {
        'children'      : ['right_hand_ring_finger_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_ring.01.R'},
    'left_hand_ring_finger_pip': {
        'children'      : ['left_hand_ring_finger_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_ring.01.L'},
    'right_hand_ring_finger_dip': {
        'children'      : ['right_hand_ring_finger_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_ring.02.R'},
    'left_hand_ring_finger_dip': {
        'children'      : ['left_hand_ring_finger_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_ring.02.L'},
    'right_hand_ring_finger_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_ring.03.R'},
    'left_hand_ring_finger_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_ring.03.L'},
    'right_hand_pinky_mcp': {
        'children'      : ['right_hand_pinky_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.04.R'},
    'left_hand_pinky_mcp': {
        'children'      : ['left_hand_pinky_pip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'palm.04.L'},
    'right_hand_pinky_pip': {
        'children'      : ['right_hand_pinky_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_pinky.01.R'},
    'left_hand_pinky_pip': {
        'children'      : ['left_hand_pinky_dip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_pinky.01.L'},
    'right_hand_pinky_dip': {
        'children'      : ['right_hand_pinky_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_pinky.02.R'},
    'left_hand_pinky_dip': {
        'children'      : ['left_hand_pinky_tip'],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_pinky.02.L'},
    'right_hand_pinky_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_pinky.03.R'},
    'left_hand_pinky_tip': {
        'children'      : [],
        'category'      : 'fingers',
        'tail_of_bone'  : 'f_pinky.03.L'},
    'right_hip': {
        'children'      : ['right_knee'],
        'category'      : 'legs',
        'tail_of_bone'  : 'pelvis.R'},
    'left_hip': {
        'children'      : ['left_knee'],
        'category'      : 'legs',
        'tail_of_bone'  : 'pelvis.L'},
    'right_knee': {
        'children'      : ['right_ankle'],
        'category'      : 'legs',
        'tail_of_bone'  : 'thigh.R'},
    'left_knee': {
        'children'      : ['left_ankle'],
        'category'      : 'legs',
        'tail_of_bone'  : 'thigh.L'},
    'right_ankle': {
        'children'      : ['right_foot_index', 'right_heel'],
        'category'      : 'feet',
        'tail_of_bone'  : 'shin.R'},
    'left_ankle': {
        'children'      : ['left_foot_index', 'left_heel'],
        'category'      : 'feet',
        'tail_of_bone'  : 'shin.L'},
    'right_heel': {
        'children'      : [],
        'category'      : 'feet',
        'tail_of_bone'  : 'heel.02.R'},
    'left_heel': {
        'children'      : [],
        'category'      : 'feet',
        'tail_of_bone'  : 'heel.02.L'},
    'right_foot_index': {
        'children'      : [],
        'category'      : 'feet',
        'tail_of_bone'  : 'foot.R'},
    'left_foot_index': {
        'children'      : [],
        'category'      : 'feet',
        'tail_of_bone'  : 'foot.L'},
}

# Dictionary of the bones ik constraints parameters
ik_constraint_parameters = {
    'forearm.R': {
        'base_bone_name': 'upper_arm.R',
        'pole_target_bone_name': 'arm_pole_target.R',
        'base_empty_marker_name': 'right_shoulder',
        'pole_target_empty_marker_name': 'right_elbow',
        'ik_empty_marker_name': 'right_wrist'},
    'forearm.L': {
        'base_bone_name': 'upper_arm.L',
        'pole_target_bone_name': 'arm_pole_target.L',
        'base_empty_marker_name': 'left_shoulder',
        'pole_target_empty_marker_name': 'left_elbow',
        'ik_empty_marker_name': 'left_wrist'},
    'shin.R': {
        'base_bone_name': 'thigh.R',
        'pole_target_bone_name': 'leg_pole_target.R',
        'base_empty_marker_name': 'right_hip',
        'pole_target_empty_marker_name': 'right_knee',
        'ik_empty_marker_name': 'right_ankle'},
    'shin.L': {
        'base_bone_name': 'thigh.L',
        'pole_target_bone_name': 'leg_pole_target.L',
        'base_empty_marker_name': 'left_hip',
        'pole_target_empty_marker_name': 'left_knee',
        'ik_empty_marker_name': 'left_ankle'},
}

# Dictionary of the pole bones parameters
ik_pole_bones = {
    'arm_pole_target.R': {
        'base_marker':      'right_shoulder',
        'pole_marker':      'right_elbow',
        'target_marker':    'right_wrist',
        'aux_markers': ['right_wrist', 'right_hand_thumb_cmc']},
    'arm_pole_target.L': {
        'base_marker':      'left_shoulder',
        'pole_marker':      'left_elbow',
        'target_marker':    'left_wrist',
        'aux_markers': ['left_wrist', 'left_hand_thumb_cmc']},
    'leg_pole_target.R': {
        'base_marker':      'right_hip',
        'pole_marker':      'right_knee',
        'target_marker':    'right_ankle',
        'aux_markers': ['right_ankle', 'right_heel']},
    'leg_pole_target.L': {
        'base_marker':          'left_hip',
        'pole_marker':          'left_knee',
        'target_marker':        'left_ankle',
        'aux_markers': ['left_ankle', 'left_heel']},
}

# Dictionary with all the Skelly mesh parts
skelly_parts = {
    'head': {
        'bones'                 : ['face'],         # List of bones represented by the mesh
        'bones_origin'          : (0, 0, 0),        # Origin of the bones
        'bones_end'             : (0, 0, 0),        # End of the bones
        'bones_length'          : 0,                # Total length of the bones
        'mesh_length'           : 0.044658516812,   # Length of the mesh
        # 'mesh_length'           : 0.014658516812, # Big Head Skelly
        'position_offset'       : (0, 0.03, 0.03),  # Position offset of the mesh as units of the bones length
        # 'position_offset'       : (0, 0.03, 0.23), # Big Head Skelly
        'adjust_rotation'       : False,            # Adjust the rotation of the mesh after applying the position offset
    },
    'spine': {
        'bones'                 : ['spine', 'spine.001', 'neck'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.70856,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'upper_arm.R': {
        'bones'                 : ['upper_arm.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.325418,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'upper_arm.L': {
        'bones'                 : ['upper_arm.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.325418,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'forearm.R': {
        'bones'                 : ['forearm.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.255504,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'forearm.L': {
        'bones'                 : ['forearm.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.255504,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'hand.R': {
        'bones'                 : ['hand.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.0845,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'hand.L': {
        'bones'                 : ['hand.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.0845,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thumb.01.R': {
        'bones'                 : ['thumb.01.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.03675,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thumb.01.L': {
        'bones'                 : ['thumb.01.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.03675,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thumb.02.R': {
        'bones'                 : ['thumb.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.032224,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thumb.02.L': {
        'bones'                 : ['thumb.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.032224,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thumb.03.R': {
        'bones'                 : ['thumb.03.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.023374,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thumb.03.L': {
        'bones'                 : ['thumb.03.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.023374,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'palm.01.R': {
        'bones'                 : ['palm.01.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.085891,
        'position_offset'       : (-0.02, -0.025, 0),
        'adjust_rotation'       : True,
    },
    'palm.01.L': {
        'bones'                 : ['palm.01.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.085891,
        'position_offset'       : (0.02, -0.025, 0),
        'adjust_rotation'       : True,
    },
    'palm.02.R': {
        'bones'                 : ['palm.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.085828,
        'position_offset'       : (-0.02, -0.005, 0),
        'adjust_rotation'       : True,
    },
    'palm.02.L': {
        'bones'                 : ['palm.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.085828,
        'position_offset'       : (0.02, -0.005, 0),
        'adjust_rotation'       : True,
    },
    'palm.03.R': {
        'bones'                 : ['palm.03.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.082869,
        'position_offset'       : (-0.02, 0.01, 0),
        'adjust_rotation'       : True,
    },
    'palm.03.L': {
        'bones'                 : ['palm.03.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.082869,
        'position_offset'       : (0.02, 0.01, 0),
        'adjust_rotation'       : True,
    },
    'palm.04.R': {
        'bones'                 : ['palm.04.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.070385,
        'position_offset'       : (-0.02, 0.025, 0),
        'adjust_rotation'       : True,
    },
    'palm.04.L': {
        'bones'                 : ['palm.04.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.070385,
        'position_offset'       : (0.02, 0.025, 0),
        'adjust_rotation'       : True,
    },
    'f_index.01.R': {
        'bones'                 : ['f_index.01.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.053961,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_index.01.L': {
        'bones'                 : ['f_index.01.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.053961,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_index.02.R': {
        'bones'                 : ['f_index.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.033378,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_index.02.L': {
        'bones'                 : ['f_index.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.033378,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_index.03.R': {
        'bones'                 : ['f_index.03.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.024385,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_index.03.L': {
        'bones'                 : ['f_index.03.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.024385,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_middle.01.R': {
        'bones'                 : ['f_middle.01.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.053792,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_middle.01.L': {
        'bones'                 : ['f_middle.01.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.053792,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_middle.02.R': {
        'bones'                 : ['f_middle.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.03347,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_middle.02.L': {
        'bones'                 : ['f_middle.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.03347,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_middle.03.R': {
        'bones'                 : ['f_middle.03.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.028028,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_middle.03.L': {
        'bones'                 : ['f_middle.03.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.028028,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_ring.01.R': {
        'bones'                 : ['f_ring.01.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.046598,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_ring.01.L': {
        'bones'                 : ['f_ring.01.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.046598,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_ring.02.R': {
        'bones'                 : ['f_ring.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.036003,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_ring.02.L': {
        'bones'                 : ['f_ring.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.036003,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_ring.03.R': {
        'bones'                 : ['f_ring.03.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.024413,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_ring.03.L': {
        'bones'                 : ['f_ring.03.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.024413,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_pinky.01.R': {
        'bones'                 : ['f_pinky.01.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.039485,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_pinky.01.L': {
        'bones'                 : ['f_pinky.01.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.039485,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_pinky.02.R': {
        'bones'                 : ['f_pinky.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.027034,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_pinky.02.L': {
        'bones'                 : ['f_pinky.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.027034,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_pinky.03.R': {
        'bones'                 : ['f_pinky.03.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.020288,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'f_pinky.03.L': {
        'bones'                 : ['f_pinky.03.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.020288,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'thigh.R': {
        'bones'                 : ['thigh.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.42875,
        'position_offset'       : (0, -0.04, 0),
        'adjust_rotation'       : False,
    },
    'thigh.L': {
        'bones'                 : ['thigh.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.42875,
        'position_offset'       : (0, -0.04, 0),
        'adjust_rotation'       : False,
    },
    'shin.R': {
        'bones'                 : ['shin.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.412281,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'shin.L': {
        'bones'                 : ['shin.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.412281,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'foot.R': {
        'bones'                 : ['foot.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.226,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'foot.L': {
        'bones'                 : ['foot.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.226,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'heel.02.R': {
        'bones'                 : ['heel.02.R'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.150255,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
    'heel.02.L': {
        'bones'                 : ['heel.02.L'],
        'bones_origin'          : (0, 0, 0),
        'bones_end'             : (0, 0, 0),
        'bones_length'          : 0,
        'mesh_length'           : 0.150255,
        'position_offset'       : (0, 0, 0),
        'adjust_rotation'       : False,
    },
}

# Function to update all the empties positions in the dictionary
def update_empty_positions(target_empty: str=''):

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

            # Iterate through each scene frame and save the coordinates of the empties in the dictionary.
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
            #  Reset the empties position
            empty_positions[empty] = {'x': [], 'y': [], 'z': []}

        # Iterate through each scene frame and save the coordinates of each empty in the dictionary.
        for frame in range (scene.frame_start, scene.frame_end):
            # Set scene frame
            scene.frame_set(frame)
            # Iterate through each empty
            for empty in marker_empties:
                # Save the x, y, z position of the empty
                empty_positions[empty]['x'].append(bpy.data.objects[empty].location[0])
                empty_positions[empty]['y'].append(bpy.data.objects[empty].location[1])
                empty_positions[empty]['z'].append(bpy.data.objects[empty].location[2])

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
        if object.type == 'EMPTY' and object.name != 'empties_parent' and '_origin' not in object.name and 'center_of_mass' not in object.name and object.name != 'rigid_body_meshes_parent':
            empty_speeds[object.name] = {'speed': [0]}

    # Iterate through each scene frame starting from frame start + 1 and save the speed of each empty in the dictionary
    for frame in range (scene.frame_start + 1, scene.frame_end + 1):
        # Set scene frame
        scene.frame_set(frame)
        # Iterate through each object
        for object in bpy.data.objects:
            if object.type == 'EMPTY' and object.name != 'empties_parent' and '_origin' not in object.name and 'center_of_mass' not in object.name and object.name != 'rigid_body_meshes_parent':
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

### NOT IN USE ###
# Function to calculate the pole angle necessary to make the ik base bone point to the pole target empty marker
def calculate_ik_pole_angle(rig_name: str='root',
                            base_bone_name: str='upper_arm.L',
                            pole_target_bone_name: str='arm_pole_target.L',
                            base_empty_marker_name: str='left_shoulder',
                            pole_target_empty_marker_name: str='left_elbow',
                            ik_empty_marker_name: str='left_wrist') -> float:
    
    # Get reference to the armature
    rig = bpy.data.objects[rig_name]

    # Get references to the base, ik and pole_target bones
    base_bone           = rig.pose.bones[base_bone_name]
    pole_target_bone    = rig.pose.bones[pole_target_bone_name]

    # Get the empty marker objects
    base_empty_marker           = bpy.data.objects[base_empty_marker_name]
    pole_target_empty_marker    = bpy.data.objects[pole_target_empty_marker_name]
    ik_empty_marker             = bpy.data.objects[ik_empty_marker_name]

    # Get the IK vector (from ik_empty_marker to base_empty_marker, example: shoulder to wrist)
    ik_vector = ik_empty_marker.matrix_world.translation - base_empty_marker.matrix_world.translation
    
    # Get the vector from base bone head to the pole target bone head
    base_to_pole_target_vector = pole_target_bone.head - base_bone.head

    # Get the pole axis vector (perpendicular projection of pole target position on the ik_vector
    pole_axis_vector = base_to_pole_target_vector - ik_vector * (ik_vector.dot(base_to_pole_target_vector) / ik_vector.length_squared)

    # Get the vector from the base bone head to the pole_target_empty_marker (example: shoulder to elbow)
    base_to_pole_target_empty_vector = pole_target_empty_marker.matrix_world.translation - base_empty_marker.matrix_world.translation

    # Get the base bone local y axis (example: upper_arm y axis)
    base_bone_y_axis = base_bone.y_axis

    # Normalize the vectors
    ik_vector.normalize()
    base_to_pole_target_empty_vector.normalize()
    base_bone_y_axis.normalize()

    # Calculate the perpendicular vectors to the ik_vector
    y_axis_perpendicular_vector                     = base_bone_y_axis - ik_vector * (base_bone_y_axis.dot(ik_vector) / ik_vector.magnitude)
    base_to_pole_target_empty_perpendicular_vector  = base_to_pole_target_empty_vector - ik_vector * (base_to_pole_target_empty_vector.dot(ik_vector) / ik_vector.magnitude)

    # Calculate the cosine of the angle between the perpendicular vectors
    perpendicular_vectors_cosine = base_to_pole_target_empty_perpendicular_vector.dot(y_axis_perpendicular_vector) / (y_axis_perpendicular_vector.magnitude * base_to_pole_target_empty_perpendicular_vector.magnitude)

    # Calculate the angle between the perpendicular vectors in radians
    if perpendicular_vectors_cosine > 1:
        perpendicular_vectors_angle_radians = m.acos(1)
    elif perpendicular_vectors_cosine < -1:
        perpendicular_vectors_angle_radians = m.acos(-1)
    else:
        perpendicular_vectors_angle_radians = m.acos(perpendicular_vectors_cosine)

    # Calculate the cross product of the perpendicular vectors to get the rotation axis
    perpendicular_vector_cross_product = y_axis_perpendicular_vector.cross(base_to_pole_target_empty_perpendicular_vector)

    # Calculate the dot product of the perpendicular cross product and the ik vector to get the direction of the rotation axis
    perpendicular_cross_product_ik_vector_dot_product = perpendicular_vector_cross_product.dot(ik_vector)

    # If the dot product is negative, multiply the angle by -1
    if perpendicular_cross_product_ik_vector_dot_product < 0:
        perpendicular_vectors_angle_radians *= -1

    # Calculate the rotation matrix to rotate the the axis of the base bone
    rotation_matrix = mathutils.Matrix.Rotation(perpendicular_vectors_angle_radians, 4, ik_vector)

    # Calculate the expected x and z axis when y axis points towards the pole_target_empty_marker
    base_bone_expected_x_axis = rotation_matrix @ base_bone.x_axis
    base_bone_expected_z_axis = rotation_matrix @ base_bone.z_axis
    base_bone_expected_y_axis = rotation_matrix @ base_bone.y_axis

    # Calculate the coplanar component of the pole_axis_vector on the base bone xz local plane
    pole_axis_vector_xz_projection = pole_axis_vector - pole_axis_vector.project(base_bone_expected_x_axis.cross(base_bone_expected_z_axis))

    # Calculate the cosine of the angle between the pole_axis_vector_xz_projection and the base_bone_expected_x_axis
    pole_angle_cosine = pole_axis_vector_xz_projection.dot(base_bone_expected_x_axis) / (base_bone_expected_x_axis.magnitude * pole_axis_vector_xz_projection.magnitude)

    # Calculate the angle in radians between the vectors
    if pole_angle_cosine > 1:
        pole_angle_radians = m.acos(1)
    elif pole_angle_cosine < -1:
        pole_angle_radians = m.acos(-1)
    else:
        pole_angle_radians = m.acos(pole_angle_cosine)

    # Calculate the cross product between the pole_axis_vector_xz_projection and the base_bone_expected_x_axis to get the rotation axis
    pole_axis_vector_xz_projection_base_bone_expected_x_axis_cross_product = pole_axis_vector_xz_projection.cross(base_bone_expected_x_axis)

    # Calculate the dot product between the cross product and the ik vector to get the direction of the rotation axis
    cross_product_ik_vector_dot_product = pole_axis_vector_xz_projection_base_bone_expected_x_axis_cross_product.dot(ik_vector)

    # If the dot product is negative, multiply the angle by -1
    if cross_product_ik_vector_dot_product < 0:
        pole_angle_radians *= -1

    return pole_angle_radians

#  Function to define a quadratic function for the ik pole bone position calculus transition
def ik_pole_quadratic_function(t1, t2, t3, y1, y2, y3):
    A = np.array([
        [t1**2, t1, 1],
        [t2**2, t2, 1],
        [t3**2, t3, 1]
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

######################################################################
#################### REDUCE BONE LENGTH DISPERSION ###################
######################################################################

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
                            
                            # Get the otation matrix
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

    # NOT IN USE IN THE CURRENT VERSION
    # Check the position_correction_mode parameter to correct the position of each children after applying the filter to one empty.
    # Or, first apply the filter to all the selected categories empties and after that execute reduce_bone_length_dispersion once.
    if 'false' == 'each_children':

        # Iterate through the empties_dict
        for empty in empties_dict:

            if empties_dict[empty]['category'] in local_filter_categories:

                # Update the empty's position dictionary
                update_empty_positions(target_empty=empty)

                # Save the unfiltered empty positions
                unfiltered_positions = empty_positions[empty]

                # Select the empty
                bpy.data.objects[empty].select_set(True)

                # Save the current area
                current_area = bpy.context.area.type

                # Change the current area to the graph editor
                bpy.context.area.type = "GRAPH_EDITOR"

                # Apply the butterworth filter
                bpy.ops.graph.butterworth_smooth(cutoff_frequency=local_cutoff_frequencies[empties_dict[empty]['category']],
                                                filter_order=4,
                                                samples_per_frame=1,
                                                blend=1.0,
                                                blend_in_out=1)

                # Adjust the length dispersion of the bone whose tail is the empty. Only if the empty is the tail of a bone
                if empties_dict[empty]['tail_of_bone'] != '':
                    reduce_bone_length_dispersion(interval_variable=interval_variable,
                                                  interval_factor=interval_factor,
                                                  body_height=body_height,
                                                  target_bone=empties_dict[empty]['tail_of_bone'])

                # Update again the empty's position dictionary
                update_empty_positions(target_empty=empty)

                # Iterate through all the empty's position dictionary (i.e frames) and calculate the position delta due to the filtering and reduce bone lenght dispersion
                # Then translate all the empty children recursively by that delta
                for frame_index in range (0, len(empty_positions[empty]['x'])):

                    # Check if at least one of the position components changed
                    if (unfiltered_positions['x'][frame_index] != empty_positions[empty]['x'][frame_index] or
                        unfiltered_positions['y'][frame_index] != empty_positions[empty]['y'][frame_index] or
                        unfiltered_positions['z'][frame_index] != empty_positions[empty]['z'][frame_index]):
                        # Get the unfiltered and filtered positions
                        unfiltered_position = mathutils.Vector([unfiltered_positions['x'][frame_index], unfiltered_positions['y'][frame_index], unfiltered_positions['z'][frame_index]])
                        filtered_position  = mathutils.Vector([empty_positions[empty]['x'][frame_index], empty_positions[empty]['y'][frame_index], empty_positions[empty]['z'][frame_index]])
                        # Get the position delta vector
                        delta_vector     = filtered_position - unfiltered_position

                        #  Translate the empty's children recursively by the delta vector
                        for child in empties_dict[empty]['children']:
                            translate_empty(empties_dict, child, frame_index=frame_index, delta=delta_vector, recursivity=True)
                        
                # Restore the area
                bpy.context.area.type = current_area

                # Unselect the empty
                bpy.data.objects[empty].select_set(False)

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


######################################################################
############################# ADD RIG ################################
######################################################################

def add_rig(keep_symmetry: bool=False,
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
            
    # Move the face bone head to the spine.004 tail
    face.head[1] = spine_004.tail[1]
    face.head[2] = spine_004.tail[2]
    # Move the face bone tail to point 18º down (towards nose bone tip)
    face.tail[1] = face.head[1] - (virtual_bones['head_nose']['median'] * m.cos(m.radians(18)) / 2)
    face.tail[2] = face.head[2] - (virtual_bones['head_nose']['median'] * m.sin(m.radians(18)) / 2)

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
            {'type':'COPY_LOCATION','target':'hips_center','use_offset':False},
            {'type':'LOCKED_TRACK','target':'right_hip','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Z','influence':1.0}],
        "pelvis.R": [
            {'type':'DAMPED_TRACK','target':'right_hip','track_axis':'TRACK_Y'}],
        "pelvis.L": [
            {'type':'DAMPED_TRACK','target':'left_hip','track_axis':'TRACK_Y'}],
        "spine": [
            {'type':'COPY_LOCATION','target':'hips_center','use_offset':False},
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
            {'type':'COPY_LOCATION','target':'neck_center','use_offset':False},
            {'type':'DAMPED_TRACK','target':'right_shoulder','track_axis':'TRACK_Y'}],
        "shoulder.L": [
            {'type':'COPY_LOCATION','target':'neck_center','use_offset':False},
            {'type':'DAMPED_TRACK','target':'left_shoulder','track_axis':'TRACK_Y'}],
        "upper_arm.R": [
            {'type':'DAMPED_TRACK','target':'right_elbow','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-135,'max_x':90,'use_limit_y':True,'min_y':-98,'max_y':180,'use_limit_z':True,'min_z':-97,'max_z':91,'owner_space':'LOCAL'}],
        "upper_arm.L": [
            {'type':'DAMPED_TRACK','target':'left_elbow','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-135,'max_x':90,'use_limit_y':True,'min_y':-180,'max_y':98,'use_limit_z':True,'min_z':-91,'max_z':97,'owner_space':'LOCAL'}],
        "forearm.R": [
            {'type':'IK','target':'root','subtarget':'hand.IK.R','pole_target':'root','pole_subtarget':'arm_pole_target.R',
                'pole_angle':-1.570795,'chain_count':2,'lock_ik_x':False,'lock_ik_y':True,'lock_ik_z':True,
                'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
                'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -1.5708,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
            {'type':'COPY_ROTATION','target':'root','subtarget':'hand.IK.R','use_x':False,'use_y':True,'use_z':False,'target_space':'LOCAL','owner_space':'LOCAL','influence':0.3},
            {'type':'DAMPED_TRACK','target':'right_wrist','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':0.3},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':0,'max_y':146,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "forearm.L": [
            {'type':'IK','target':'root','subtarget':'hand.IK.L','pole_target':'root','pole_subtarget':'arm_pole_target.L',
                'pole_angle':-1.570795,'chain_count':2,'lock_ik_x':False,'lock_ik_y':True,'lock_ik_z':True,
                'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
                'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -1.5708,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
            {'type':'COPY_ROTATION','target':'root','subtarget':'hand.IK.L','use_x':False,'use_y':True,'use_z':False,'target_space':'LOCAL','owner_space':'LOCAL','influence':0.3},
            {'type':'DAMPED_TRACK','target':'left_wrist','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'left_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':0.3},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':-146,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "hand.IK.R": [
            {'type':'COPY_LOCATION','target':'right_wrist','use_offset':False},
            {'type':'DAMPED_TRACK','target':'right_' + hand_damped_track_target,'track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_hand_index_finger_mcp','track_axis':'TRACK_X','lock_axis':'LOCK_Y','influence':1.0}],
        "hand.IK.L": [
            {'type':'COPY_LOCATION','target':'left_wrist','use_offset':False},
            {'type':'DAMPED_TRACK','target':'left_' + hand_damped_track_target,'track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'left_hand_index_finger_mcp','track_axis':'TRACK_X','lock_axis':'LOCK_Y','influence':1.0}],
        # "arm_pole_target.R": [
        #     {'type':'COPY_LOCATION','target':'right_elbow','use_offset':True}],
        # "arm_pole_target.L": [
        #     {'type':'COPY_LOCATION','target':'left_elbow','use_offset':True}],
        "hand.R": [
            {'type':'DAMPED_TRACK','target':'right_' + hand_damped_track_target,'track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-36,'max_y':25,'use_limit_z':True,'min_z':-86,'max_z':90,'owner_space':'LOCAL'}],
        "hand.L": [
            {'type':'DAMPED_TRACK','target':'left_' + hand_damped_track_target,'track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'left_' + hand_locked_track_target,'track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':1.0},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-25,'max_y':36,'use_limit_z':True,'min_z':-90,'max_z':86,'owner_space':'LOCAL'}],
        "thigh.R": [
            {'type':'COPY_LOCATION','target':'right_hip','use_offset':False},
            {'type':'DAMPED_TRACK','target':'right_knee','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-155,'max_x':45,'use_limit_y':True,'min_y':-105,'max_y':85,'use_limit_z':True,'min_z':-88,'max_z':17,'owner_space':'LOCAL'}],
        "thigh.L": [
            {'type':'COPY_LOCATION','target':'left_hip','use_offset':False},
            {'type':'DAMPED_TRACK','target':'left_knee','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-155,'max_x':45,'use_limit_y':True,'min_y':-85,'max_y':105,'use_limit_z':True,'min_z':-17,'max_z':88,'owner_space':'LOCAL'}],
        "shin.R": [
            {'type':'IK','target':'root','subtarget':'foot.IK.R','pole_target':'root','pole_subtarget':'leg_pole_target.R',
                'pole_angle':-1.570795,'chain_count':2,'lock_ik_x':False,'lock_ik_y':True,'lock_ik_z':True,
                'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
                'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -0.174533,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
            {'type':'DAMPED_TRACK','target':'right_ankle','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "shin.L": [
            {'type':'IK','target':'root','subtarget':'foot.IK.L','pole_target':'root','pole_subtarget':'leg_pole_target.L',
                'pole_angle':-1.570795,'chain_count':2,'lock_ik_x':False,'lock_ik_y':True,'lock_ik_z':True,
                'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
                'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -0.174533,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
            {'type':'DAMPED_TRACK','target':'left_ankle','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "foot.IK.R": [
            {'type':'COPY_LOCATION','target':'right_ankle','use_offset':False},
            {'type':'LOCKED_TRACK','target':'right_foot_index','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Z','influence':1.0}],
        "foot.IK.L": [
            {'type':'COPY_LOCATION','target':'left_ankle','use_offset':False},
            {'type':'LOCKED_TRACK','target':'left_foot_index','track_axis':'TRACK_X','lock_axis':'LOCK_Z','influence':1.0}],
        # "leg_pole_target.R": [
        #     {'type':'COPY_LOCATION','target':'right_knee','use_offset':True}],
        # "leg_pole_target.L": [
        #     {'type':'COPY_LOCATION','target':'left_knee','use_offset':True}],
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
                bone_cons.use_offset    = cons['use_offset']
            elif cons['type'] == 'LOCKED_TRACK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.track_axis    = cons['track_axis']
                bone_cons.lock_axis     = cons['lock_axis']
                bone_cons.influence     = cons['influence']
            elif cons['type'] == 'DAMPED_TRACK':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.track_axis    = cons['track_axis']
            elif cons['type'] == 'IK':
                bone_cons.target                    = bpy.data.objects[cons['target']]
                bone_cons.subtarget                 = rig.pose.bones[cons['subtarget']].name
                bone_cons.pole_target               = bpy.data.objects[cons['pole_target']]
                bone_cons.pole_subtarget            = rig.pose.bones[cons['pole_subtarget']].name
                bone_cons.chain_count               = cons['chain_count']
                bone_cons.pole_angle                = cons['pole_angle']
                rig.pose.bones[bone].lock_ik_x      = cons['lock_ik_x']
                rig.pose.bones[bone].lock_ik_y      = cons['lock_ik_y']
                rig.pose.bones[bone].lock_ik_z      = cons['lock_ik_z']
                rig.pose.bones[bone].use_ik_limit_x = cons['use_ik_limit_x']
                rig.pose.bones[bone].use_ik_limit_y = cons['use_ik_limit_y']
                rig.pose.bones[bone].use_ik_limit_z = cons['use_ik_limit_z']
                rig.pose.bones[bone].ik_min_x       = cons['ik_min_x']
                rig.pose.bones[bone].ik_max_x       = cons['ik_max_x']
                rig.pose.bones[bone].ik_min_y       = cons['ik_min_y']
                rig.pose.bones[bone].ik_max_y       = cons['ik_max_y']
                rig.pose.bones[bone].ik_min_z       = cons['ik_min_z']
                rig.pose.bones[bone].ik_max_z       = cons['ik_max_z']
            elif cons['type'] == 'COPY_ROTATION':
                bone_cons.target        = bpy.data.objects[cons['target']]
                bone_cons.subtarget     = rig.pose.bones[cons['subtarget']].name
                bone_cons.use_x         = cons['use_x']
                bone_cons.use_y         = cons['use_y']
                bone_cons.use_z         = cons['use_z']
                bone_cons.target_space  = cons['target_space']
                bone_cons.owner_space   = cons['owner_space']
                bone_cons.influence     = cons['influence']

    if add_ik_constraints:

        # Get the transition quadratic function
        quadratic_function = ik_pole_quadratic_function(t1=ik_transition_threshold,
                                                        t2=((ik_transition_threshold + 1)/2),
                                                        t3=1,
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
                                                                quadratic_function)

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

    elif body_mesh_mode == "skelly_parts":

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
            skelly_parts[part]['bones_origin']  = mathutils.Vector(rig.data.edit_bones[skelly_parts[part]['bones'][0]].head)
            skelly_parts[part]['bones_end']     = mathutils.Vector(rig.data.edit_bones[skelly_parts[part]['bones'][-1]].tail)
            skelly_parts[part]['bones_length']  = (skelly_parts[part]['bones_end'] - skelly_parts[part]['bones_origin']).length

            if part == 'thumb.01.R':
                print("\nPart: " + str(part) +
                    "\nOrigin: " + str(skelly_parts[part]['bones_origin']) +
                    "\nLength: " + str(skelly_parts[part]['bones_length']))

        # Change to object mode
        bpy.ops.object.mode_set(mode='OBJECT')        

        # Get the script filepath
        script_file = os.path.realpath(__file__)
        # Get the script folder
        directory = os.path.dirname(script_file)

        # Define the list that will contain the different Skelly meshes
        skelly_meshes = []

        # Iterate through the skelly parts dictionary and add the corresppondent skelly part
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

######################################################################
########################### EXPORT TO FBX ############################
######################################################################

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

    def fbx_animations_do_blender4(scene_data, ref_id, f_start, f_end, start_zero, objects=None, force_keep=False):
        """
        Generate animation data (a single AnimStack) from objects, for a given frame range.
        """
        bake_step = scene_data.settings.bake_anim_step
        simplify_fac = scene_data.settings.bake_anim_simplify_factor
        scene = scene_data.scene
        depsgraph = scene_data.depsgraph
        force_keying = scene_data.settings.bake_anim_use_all_bones
        force_sek = scene_data.settings.bake_anim_force_startend_keying
        gscale = scene_data.settings.global_scale

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
            acnode_lens = AnimationCurveNodeWrapper(cam_key, 'CAMERA_FOCAL', force_key, force_sek, (cam.lens,))
            acnode_focus_distance = AnimationCurveNodeWrapper(cam_key, 'CAMERA_FOCUS_DISTANCE', force_key,
                                                            force_sek, (cam.dof.focus_distance,))
            animdata_cameras[cam_key] = (acnode_lens, acnode_focus_distance, cam)

        # Get all parent bdata of animated dupli instances, so that we can quickly identify which instances in
        # `depsgraph.object_instances` are animated and need their ObjectWrappers' matrices updated each frame.
        dupli_parent_bdata = {dup.get_parent().bdata for dup in animdata_ob if dup.is_dupli}
        has_animated_duplis = bool(dupli_parent_bdata)

        # Initialize keyframe times array. Each AnimationCurveNodeWrapper will share the same instance.
        # `np.arange` excludes the `stop` argument like when using `range`, so we use np.nextafter to get the next
        # representable value after f_end and use that as the `stop` argument instead.
        currframes = np.arange(f_start, np.nextafter(f_end, np.inf), step=bake_step)

        # Convert from Blender time to FBX time.
        fps = scene.render.fps / scene.render.fps_base
        real_currframes = currframes - f_start if start_zero else currframes
        real_currframes = (real_currframes / fps * FBX_KTIME).astype(np.int64)

        # Generator that yields the animated values of each frame in order.
        def frame_values_gen():
            # Precalculate integer frames and subframes.
            int_currframes = currframes.astype(int)
            subframes = currframes - int_currframes

            # Create simpler iterables that return only the values we care about.
            animdata_shapes_only = [shape for _anim_shape, _me, shape in animdata_shapes.values()]
            animdata_cameras_only = [camera for _anim_camera_lens, _anim_camera_focus_distance, camera
                                    in animdata_cameras.values()]
            # Previous frame's rotation for each object in animdata_ob, this will be updated each frame.
            animdata_ob_p_rots = p_rots.values()

            # Iterate through each frame and yield the values for that frame.
            # Iterating .data, the memoryview of an array, is faster than iterating the array directly.
            for int_currframe, subframe in zip(int_currframes.data, subframes.data):
                scene.frame_set(int_currframe, subframe=subframe)

                if has_animated_duplis:
                    # Changing the scene's frame invalidates existing dupli instances. To get the updated matrices of duplis
                    # for this frame, we must get the duplis from the depsgraph again.
                    for dup in depsgraph.object_instances:
                        if (parent := dup.parent) and parent.original in dupli_parent_bdata:
                            # ObjectWrapper caches its instances. Attempting to create a new instance updates the existing
                            # ObjectWrapper instance with the current frame's matrix and then returns the existing instance.
                            ObjectWrapper(dup)
                next_p_rots = []
                for ob_obj, p_rot in zip(animdata_ob, animdata_ob_p_rots):
                    # We compute baked loc/rot/scale for all objects (rot being euler-compat with previous value!).
                    loc, rot, scale, _m, _mr = ob_obj.fbx_object_tx(scene_data, rot_euler_compat=p_rot)
                    next_p_rots.append(rot)
                    yield from loc
                    yield from rot
                    yield from scale
                animdata_ob_p_rots = next_p_rots
                for shape in animdata_shapes_only:
                    yield shape.value
                for camera in animdata_cameras_only:
                    yield camera.lens
                    yield camera.dof.focus_distance

        # Providing `count` to np.fromiter pre-allocates the array, avoiding extra memory allocations while iterating.
        num_ob_values = len(animdata_ob) * 9  # Location, rotation and scale, each of which have x, y, and z components
        num_shape_values = len(animdata_shapes)  # Only 1 value per shape key
        num_camera_values = len(animdata_cameras) * 2  # Focal length (`.lens`) and focus distance
        num_values_per_frame = num_ob_values + num_shape_values + num_camera_values
        num_frames = len(real_currframes)
        all_values_flat = np.fromiter(frame_values_gen(), dtype=float, count=num_frames * num_values_per_frame)

        # Restore the scene's current frame.
        scene.frame_set(back_currframe, subframe=0.0)

        # View such that each column is all values for a single frame and each row is all values for a single curve.
        all_values = all_values_flat.reshape(num_frames, num_values_per_frame).T
        # Split into views of the arrays for each curve type.
        split_at = [num_ob_values, num_shape_values, num_camera_values]
        # For unequal sized splits, np.split takes indices to split at, which can be acquired through a cumulative sum
        # across the list.
        # The last value isn't needed, because the last split is assumed to go to the end of the array.
        split_at = np.cumsum(split_at[:-1])
        all_ob_values, all_shape_key_values, all_camera_values = np.split(all_values, split_at)

        all_anims = []

        # Set location/rotation/scale curves.
        # Split into equal sized views of the arrays for each object.
        split_into = len(animdata_ob)
        per_ob_values = np.split(all_ob_values, split_into) if split_into > 0 else ()
        for anims, ob_values in zip(animdata_ob.values(), per_ob_values):
            # Split again into equal sized views of the location, rotation and scaling arrays.
            loc_xyz, rot_xyz, sca_xyz = np.split(ob_values, 3)
            # In-place convert from Blender rotation to FBX rotation.
            np.rad2deg(rot_xyz, out=rot_xyz)
            anim_loc, anim_rot, anim_scale = anims
            anim_loc.set_keyframes(real_currframes, loc_xyz)
            anim_rot.set_keyframes(real_currframes, rot_xyz)
            anim_scale.set_keyframes(real_currframes, sca_xyz)
            all_anims.extend(anims)

        # Set shape key curves.
        # There's only one array per shape key, so there's no need to split `all_shape_key_values`.
        for (anim_shape, _me, _shape), shape_key_values in zip(animdata_shapes.values(), all_shape_key_values):
            # In-place convert from Blender Shape Key Value to FBX Deform Percent.
            shape_key_values *= 100.0
            anim_shape.set_keyframes(real_currframes, shape_key_values)
            # anim_shape.set_keyframes(real_currframes, _shape.value * SCALE_FACTOR_Blender4)
            all_anims.append(anim_shape)

        # Set camera curves.
        # Split into equal sized views of the arrays for each camera.
        split_into = len(animdata_cameras)
        per_camera_values = np.split(all_camera_values, split_into) if split_into > 0 else ()
        zipped = zip(animdata_cameras.values(), per_camera_values)
        for (anim_camera_lens, anim_camera_focus_distance, _camera), (lens_values, focus_distance_values) in zipped:
            # In-place convert from Blender focus distance to FBX.
            focus_distance_values *= (1000 * gscale)
            anim_camera_lens.set_keyframes(real_currframes, lens_values)
            anim_camera_focus_distance.set_keyframes(real_currframes, focus_distance_values)
            all_anims.append(anim_camera_lens)
            all_anims.append(anim_camera_focus_distance)

        animations = {}

        # And now, produce final data (usable by FBX export code)
        for anim in all_anims:
            anim.simplify(simplify_fac, bake_step, force_keep)
            if not anim:
                continue
            for obj_key, group_key, group, fbx_group, fbx_gname in anim.get_final_data(scene, ref_id, force_keep):
                anim_data = animations.setdefault(obj_key, ("dummy_unused_key", {}))
                anim_data[1][fbx_group] = (group_key, group, fbx_gname)

        astack_key = get_blender_anim_stack_key(scene, ref_id)
        alayer_key = get_blender_anim_layer_key(scene, ref_id)
        name = (get_blenderID_name(ref_id) if ref_id else scene.name).encode()

        if start_zero:
            f_end -= f_start
            f_start = 0.0

        return (astack_key, animations, alayer_key, name, f_start, f_end) if animations else None

    def fbx_data_armature_elements_blender4(root, arm_obj, scene_data):
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
            elem_props_template_set(tmpl, props, "p_double", b"Size", bo.head_radius * bone_radius_scale * SCALE_FACTOR_Blender4)

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

                # Pre-process vertex weights so that the vertices only need to be iterated once.
                ob = ob_obj.bdata
                bo_vg_idx = {bo_obj.bdata.name: ob.vertex_groups[bo_obj.bdata.name].index
                            for bo_obj in clusters.keys() if bo_obj.bdata.name in ob.vertex_groups}
                valid_idxs = set(bo_vg_idx.values())
                vgroups = {vg.index: {} for vg in ob.vertex_groups}
                for idx, v in enumerate(me.vertices):
                    for vg in v.groups:
                        if (w := vg.weight) and (vg_idx := vg.group) in valid_idxs:
                            vgroups[vg_idx][idx] = w

                for bo_obj, clstr_key in clusters.items():
                    bo = bo_obj.bdata
                    # Find which vertices are affected by this bone/vgroup pair, and matching weights.
                    # Note we still write a cluster for bones not affecting the mesh, to get 'rest pose' data
                    # (the TransformBlah matrices).
                    vg_idx = bo_vg_idx.get(bo.name, None)
                    indices, weights = ((), ()) if vg_idx is None or not vgroups[vg_idx] else zip(*vgroups[vg_idx].items())

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
                    
                    transform_matrix = mat_world_bones[bo_obj].inverted_safe() @ mat_world_obj

                    transform_matrix = transform_matrix.LocRotScale(
                    [i * SCALE_FACTOR_Blender4 for i in transform_matrix.to_translation()],
                    transform_matrix.to_quaternion(),
                    [i * SCALE_FACTOR_Blender4 for i in transform_matrix.to_scale()],
                    )
                    
                    elem_data_single_float64_array(fbx_clstr, b"Transform",matrix4_to_array(transform_matrix))
                    elem_data_single_float64_array(fbx_clstr, b"TransformLink", matrix4_to_array(mat_world_bones[bo_obj]))
                    elem_data_single_float64_array(fbx_clstr, b"TransformAssociateModel", matrix4_to_array(mat_world_arm))

    def fbx_data_object_elements_blender4(root, ob_obj, scene_data):
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
        model = elem_data_single_int64(root, b"Model", ob_obj.fbx_uuid)
        model.add_string(fbx_name_class(ob_obj.name.encode(), b"Model"))
        model.add_string(obj_type)

        elem_data_single_int32(model, b"Version", FBX_MODELS_VERSION)

        # Object transform info.
        loc, rot, scale, matrix, matrix_rot = ob_obj.fbx_object_tx(scene_data)
        rot = tuple(convert_rad_to_deg_iter(rot))

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
        # This is probably the FbxNode.EShadingMode enum. Not directly used by the FBX SDK, but the SDK guarantees that the
        # value will be passed through from an imported file to an exported one. Common values are 'Y' and 'T'. 'U' and 'W'
        # have also been seen in older FBX files. It's not clear which enum member each of these values corresponds to or if
        # these values are actually application specific. Blender had been exporting this as a `True` bool for a long time
        # seemingly without issue. The '\x01' char is the same value as `True` in raw bytes.
        elem_data_single_char(model, b"Shading", b"\x01")
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

    def fbx_data_bindpose_element_blender4(root, me_obj, me, scene_data, arm_obj=None, mat_world_arm=None, bones=[]):
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
            
            # UE modification
            mat_world_arm = mat_world_arm.LocRotScale(
                mat_world_arm.to_translation(),
                mat_world_arm.to_quaternion(),
                [i / SCALE_FACTOR_Blender4 for i in mat_world_arm.to_scale()],
            )
            
            elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(mat_world_arm))
        
        # And all bones of armature!
        mat_world_bones = {}
        for bo_obj in bones:
            bomat = bo_obj.fbx_object_matrix(scene_data, rest=True, global_space=True)
            mat_world_bones[bo_obj] = bomat
            fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
            elem_data_single_int64(fbx_posenode, b"Node", bo_obj.fbx_uuid)

            bomat = bomat.LocRotScale(
                bomat.to_translation(),
                bomat.to_quaternion(),
                [i / SCALE_FACTOR_Blender4 for i in bomat.to_scale()]
            )

            elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(bomat))

        return mat_world_obj, mat_world_bones



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
            # export_fbx_bin.fbx_data_object_elements     = fbx_data_object_elements_blender4
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

# Class with the different properties of the methods
class FMC_ADAPTER_PROPERTIES(bpy.types.PropertyGroup):
    # Adjust Empties Options
    show_adjust_empties: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )
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
        default     = False,
        description = 'Correct the fingers empties. Match hand_wrist (axis empty) position to wrist (sphere empty)'
    )
    add_hand_middle_empty: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Add an empty in the middle of the hand between index and pinky empties. This empty is used for a better orientation of the hand (experimental)'
    )
    
    # Reduce Bone Length Dispersion Options
    show_reduce_bone_length_dispersion: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )
    interval_variable: bpy.props.EnumProperty(
        name        = '',
        description = 'Variable used to define the new length dispersion interval',
        items       = [ ('capture_median', 'Capture Median', 'Use the bones median length from the capture. Defines the new dispersion interval as [median*(1-interval_factor),median*(1+interval_factor)]'),
                        ('standard_length', 'Standard length', 'Use the standard lengths based on the total body (rig) height. Defines the new dispersion interval as [length*(1-interval_factor),length*(1+interval_factor)]'),
                        ('capture_stdev', 'Capture Std Dev', 'Use the bones length standard deviation from the capture. Defines the new dispersion interval as [median-interval_factor*stdev,median+interval_factor*stdev]')]
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
        description = 'Body height in meters. This value is used when the interval variable is set to standard length. If a rig is added after using Reduce Dispersion with standard length, it will have this value as height and the bones length will be proporions of this height'
    )
    # Add Rig Options
    show_add_rig: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )
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
    add_ik_constraints: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Add IK constraints for arms and legs'
    )
    ik_transition_threshold: bpy.props.FloatProperty(
        name        = '',
        default     = 0.5,
        min         = 0,
        max         = 1,
        precision   = 2,
        description = 'Threshold of parallel degree (dot product) between base and target ik vectors. It is used to transition between vectors to determine the pole bone position'
    )
    use_limit_rotation: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Add rotation limits (human skeleton) to the bones constraints (experimental)'
    )
    clear_constraints: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Clear added constraints after baking animation'
    )
    
    # Add Body Mesh Options
    show_add_body_mesh: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )
    body_mesh_mode: bpy.props.EnumProperty(
        name        = '',
        default     = 'skelly_parts',
        description = 'Mode (source) for adding the mesh to the rig',
        items       = [('skelly_parts', 'Skelly Parts', ''),
                       ('skelly', 'Skelly', ''),
                       ('can_man', 'Custom', ''),
                       ]
    )

    # Export FBX Options
    show_export_fbx: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )
    fbx_type: bpy.props.EnumProperty(
        name        = '',
        description = 'Type of the FBX file',
        items       = [('standard', 'Standard', ''),
                       ('unreal_engine', 'Unreal Engine', '')
                       ]
    )

    # Add Finger Rotation Limits Options
    show_add_finger_rotation_limits: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )

    # Apply Butterworth Filters Options
    show_apply_butterworth_filters: bpy.props.BoolProperty(
        name        = '',
        default     = False,
    )
    position_correction_mode: bpy.props.EnumProperty(
        name        = '',
        description = 'Position correction mode',
        items       = [('overall', 'Overall (Faster)', ''),
                       ('each_children', 'Each Children (Slower)', '')],
    )
    apply_global_filter_core: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply global Butterworth filter to core empties (hips_center, trunk_center and neck_center)'
    )
    global_filter_core_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Core empties global Butterworth filter cutoff frequency (Hz)'
    )
    apply_local_filter_core: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply local Butterworth filter to core empties'
    )
    local_filter_origin_core: bpy.props.EnumProperty(
        name        = '',
        description = 'Local filter origin',
        items       = [('hips_center', 'Hips', ''),
                       ],
    )
    local_filter_core_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Core empties local Butterworth filter cutoff frequency (Hz)'
    )
    apply_global_filter_arms: bpy.props.BoolProperty(
        name        = 'Arms',
        default     = False,
        description = 'Apply global Butterworth filter to arms empties (shoulde and elbow)'
    )
    global_filter_arms_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Arms empties global Butterworth filter cutoff frequency (Hz)'
    )
    apply_local_filter_arms: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply local Butterworth filter to arms empties'
    )
    local_filter_origin_arms: bpy.props.EnumProperty(
        name        = '',
        description = 'Local filter origin',
        items       = [('neck_center', 'Neck', ''),
                       ],
    )
    local_filter_arms_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Arms empties local Butterworth filter cutoff frequency (Hz)'
    )
    apply_global_filter_hands: bpy.props.BoolProperty(
        name        = 'Hands',
        default     = False,
        description = 'Apply global Butterworth filter to hands empties (wrist and hand)'
    )
    global_filter_hands_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Hands empties global Butterworth filter cutoff frequency (Hz)'
    )
    apply_local_filter_hands: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply local Butterworth filter to hands empties'
    )
    local_filter_origin_hands: bpy.props.EnumProperty(
        name        = '',
        description = 'Local filter origin',
        items       = [('side_elbow', 'Elbow', ''),
                       ],
    )
    local_filter_hands_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Hands empties local Butterworth filter cutoff frequency (Hz)'
    )
    apply_global_filter_fingers: bpy.props.BoolProperty(
        name        = 'Fingers',
        default     = False,
        description = 'Apply global Butterworth filter to fingers empties (_ip, _pip, _dip and _tip)'
    )
    global_filter_fingers_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Fingers empties global Butterworth filter cutoff frequency (Hz)'
    )
    apply_local_filter_fingers: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply local Butterworth filter to fingers empties'
    )
    local_filter_origin_fingers: bpy.props.EnumProperty(
        name        = '',
        description = 'Local filter origin',
        items       = [('side_wrist', 'Wrist', ''),
                       ],
    )
    local_filter_fingers_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Fingers empties local Butterworth filter cutoff frequency (Hz)'
    )
    apply_global_filter_legs: bpy.props.BoolProperty(
        name        = 'Legs',
        default     = False,
        description = 'Apply global Butterworth filter to legs empties (hips and knees)'
    )
    global_filter_legs_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Legs empties global Butterworth filter cutoff frequency (Hz)'
    )
    apply_local_filter_legs: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply local Butterworth filter to legs empties'
    )
    local_filter_origin_legs: bpy.props.EnumProperty(
        name        = '',
        description = 'Local filter origin',
        items       = [('hips_center', 'Hips', ''),
                       ],
    )
    local_filter_legs_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Legs empties local Butterworth filter cutoff frequency (Hz)'
    )
    apply_global_filter_feet: bpy.props.BoolProperty(
        name        = 'Feet',
        default     = False,
        description = 'Apply global Butterworth filter to feet empties (ankle, heel and foot_index)'
    )
    global_filter_feet_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Feet empties global Butterworth filter cutoff frequency (Hz)'
    )
    apply_local_filter_feet: bpy.props.BoolProperty(
        name        = '',
        default     = False,
        description = 'Apply local Butterworth filter to feet empties'
    )
    local_filter_origin_feet: bpy.props.EnumProperty(
        name        = '',
        description = 'Local filter origin',
        items       = [('side_knee', 'Knee', ''),
                       ],
    )
    local_filter_feet_frequency: bpy.props.FloatProperty(
        name        = '',
        default     = 7,
        min         = 0,
        precision   = 2,
        description = 'Feet empties local Butterworth filter cutoff frequency (Hz)'
    )
    
# UI Panel Class
class VIEW3D_PT_freemocap_adapter(Panel):
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "UI"
    bl_category     = "Freemocap Adapter Alt"
    bl_label        = "Freemocap Adapter Alt"
    
    def draw(self, context):
        layout              = self.layout
        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool
        
        # Create a button to toggle Adjust Empties Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_adjust_empties", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_adjust_empties else 'TRIA_RIGHT', emboss=False)
        row.label(text="Adjust Empties")

        if fmc_adapter_tool.show_adjust_empties:

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

        # Create a button to toggle Reduce Bone Length Dispersion Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_reduce_bone_length_dispersion", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_reduce_bone_length_dispersion else 'TRIA_RIGHT', emboss=False)
        row.label(text="Reduce Bone Length Dispersion")

        if fmc_adapter_tool.show_reduce_bone_length_dispersion:

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

        # Create a button to toggle Apply Butterwort Filters Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_apply_butterworth_filters", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_apply_butterworth_filters else 'TRIA_RIGHT', emboss=False)
        row.label(text="Apply Butterworth Filters (Blender 4.0+)")

        if fmc_adapter_tool.show_apply_butterworth_filters:

            # Apply Butterwort Filters
            box = layout.box()

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Section')
            split_titles = split.column().split(factor=0.3)
            split_titles.split().column().label(text='Global (Freq)')
            split_titles.split().column().label(text='Local (Freq, Origin)')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Core')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool, 'apply_global_filter_core')
            split1.column().prop(fmc_adapter_tool, 'global_filter_core_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool, 'apply_local_filter_core')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool, 'local_filter_core_frequency')
                split3.column().prop(fmc_adapter_tool, 'local_filter_origin_core')
            
            split = box.column().row().split(factor=0.15)
            split.column().label(text='Arms')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool, 'apply_global_filter_arms')
            split1.column().prop(fmc_adapter_tool, 'global_filter_arms_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool, 'apply_local_filter_arms')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool, 'local_filter_arms_frequency')
                split3.column().prop(fmc_adapter_tool, 'local_filter_origin_arms')
            
            split = box.column().row().split(factor=0.15)
            split.column().label(text='Hands')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool, 'apply_global_filter_hands')
            split1.column().prop(fmc_adapter_tool, 'global_filter_hands_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool, 'apply_local_filter_hands')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool, 'local_filter_hands_frequency')
                split3.column().prop(fmc_adapter_tool, 'local_filter_origin_hands')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Fingers')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool, 'apply_global_filter_fingers')
            split1.column().prop(fmc_adapter_tool, 'global_filter_fingers_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool, 'apply_local_filter_fingers')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool, 'local_filter_fingers_frequency')
                split3.column().prop(fmc_adapter_tool, 'local_filter_origin_fingers')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Legs')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool, 'apply_global_filter_legs')
            split1.column().prop(fmc_adapter_tool, 'global_filter_legs_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool, 'apply_local_filter_legs')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool, 'local_filter_legs_frequency')
                split3.column().prop(fmc_adapter_tool, 'local_filter_origin_legs')

            split = box.column().row().split(factor=0.15)
            split.column().label(text='Feet')
            split_params = split.column().split(factor=0.3)
            split1 = split_params.column().split(factor=0.15)
            split1.column().prop(fmc_adapter_tool, 'apply_global_filter_feet')
            split1.column().prop(fmc_adapter_tool, 'global_filter_feet_frequency')
            if not scipy_available:
                split_params.column().label(text='Install scipy module')
            else:
                split2 = split_params.column().split(factor=0.07)
                split2.column().prop(fmc_adapter_tool, 'apply_local_filter_feet')
                split3 = split2.column().split(factor=0.5)
                split3.column().prop(fmc_adapter_tool, 'local_filter_feet_frequency')
                split3.column().prop(fmc_adapter_tool, 'local_filter_origin_feet')
            
            box.operator('fmc_adapter.apply_butterworth_filters', text='3. Apply Butterworth Filters')

        # Create a button to toggle Add Finger Rotation Limits Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_add_finger_rotation_limits", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_add_finger_rotation_limits else 'TRIA_RIGHT', emboss=False)
        row.label(text="Add Finger Rotation Limits")

        if fmc_adapter_tool.show_add_finger_rotation_limits:

            # Add Finger Rotation Limits
            box = layout.box()
            box.operator('fmc_adapter.add_finger_rotation_limits', text='4. Add Finger Rotation Limits')

        # Create a button to toggle Rig Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_add_rig", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_add_rig else 'TRIA_RIGHT', emboss=False)
        row.label(text="Add Rig")

        if fmc_adapter_tool.show_add_rig:

            # Add Rig Options
            box = layout.box()
            split = box.column().row().split(factor=0.6)
            split.column().label(text='Keep right/left symmetry')
            split.split().column().prop(fmc_adapter_tool, 'keep_symmetry')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add finger constraints')
            split.split().column().prop(fmc_adapter_tool, 'add_fingers_constraints')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add IK constraints')
            split.split().column().prop(fmc_adapter_tool, 'add_ik_constraints')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='IK transition threshold')
            split.split().column().prop(fmc_adapter_tool, 'ik_transition_threshold')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Add rotation limits')
            split.split().column().prop(fmc_adapter_tool, 'use_limit_rotation')

            split = box.column().row().split(factor=0.6)
            split.column().label(text='Clear constraints')
            split.split().column().prop(fmc_adapter_tool, 'clear_constraints')
            
            box.operator('fmc_adapter.add_rig', text='5. Add Rig')

        # Create a button to toggle Add Body Mesh Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_add_body_mesh", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_add_body_mesh else 'TRIA_RIGHT', emboss=False)
        row.label(text="Add Body Mesh")

        if fmc_adapter_tool.show_add_body_mesh:
        
            # Add Body Mesh Options
            box = layout.box()
            #box.label(text='Add Body Mesh Options')
            
            split = box.column().row().split(factor=0.6)
            split.column().label(text='Body Mesh Mode')
            split.split().column().prop(fmc_adapter_tool, 'body_mesh_mode')
            
            box.operator('fmc_adapter.add_body_mesh', text='6. Add Body Mesh')

        # Create a button to toggle FBX Export Options visibility
        row = layout.row(align=True)
        row.prop(fmc_adapter_tool, "show_export_fbx", text="", icon='TRIA_DOWN' if fmc_adapter_tool.show_export_fbx else 'TRIA_RIGHT', emboss=False)
        row.label(text="FBX Export")

        if fmc_adapter_tool.show_export_fbx:

            # FBX Export
            box = layout.box()
            split = box.column().row().split(factor=0.6)
            split.column().label(text='FBX Export Type')
            split.split().column().prop(fmc_adapter_tool, 'fbx_type')

            box.operator('fmc_adapter.export_fbx', text='7. Export FBX')


# Operator classes that executes the methods
class FMC_ADAPTER_OT_adjust_empties(Operator):
    bl_idname       = 'fmc_adapter.adjust_empties'
    bl_label        = 'Freemocap Adapter - Adjust Empties'
    bl_description  = "Change the position of the empties_parent empty so it is placed in an imaginary ground plane of the capture between the actor's feet"
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

        print('Executing Add Rig...')

        add_rig(keep_symmetry=fmc_adapter_tool.keep_symmetry,
                add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
                add_ik_constraints=fmc_adapter_tool.add_ik_constraints,
                ik_transition_threshold=fmc_adapter_tool.ik_transition_threshold,
                use_limit_rotation=fmc_adapter_tool.use_limit_rotation,
                clear_constraints=fmc_adapter_tool.clear_constraints)

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

        # Execute Add Rig if there is no rig in the scene
        scene_has_rig = False
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                scene_has_rig = True
                break

        if not scene_has_rig:
            print('Executing Add Rig to have a rig for the mesh...')
            add_rig(keep_symmetry=fmc_adapter_tool.keep_symmetry,
                    add_fingers_constraints=fmc_adapter_tool.add_fingers_constraints,
                    add_ik_constraints=fmc_adapter_tool.add_ik_constraints,
                    ik_transition_threshold=fmc_adapter_tool.ik_transition_threshold,
                    use_limit_rotation=fmc_adapter_tool.use_limit_rotation,
                    clear_constraints=fmc_adapter_tool.clear_constraints)
        
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

        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Export FBX...')

        # Execute export fbx function
        export_fbx(self,
                   fbx_type=fmc_adapter_tool.fbx_type)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}
    
class FMC_ADAPTER_OT_add_finger_rotation_limits(Operator):
    bl_idname       = 'fmc_adapter.add_finger_rotation_limits'
    bl_label        = 'Freemocap Adapter - Add Finger Rotation Limits'
    bl_description  = 'Translate the finger marker empties so the bones respect the rotation constraint'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Add Finger Rotation Limits...')

        # Execute export fbx function
        add_finger_rotation_limits()

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}
    
class FMC_ADAPTER_OT_apply_butterworth_filters(Operator):
    bl_idname       = 'fmc_adapter.apply_butterworth_filters'
    bl_label        = 'Freemocap Adapter - Apply Butterworth Filters'
    bl_description  = 'Apply Butterworth filters to the marker empties'
    bl_options      = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):

        scene               = context.scene
        fmc_adapter_tool    = scene.fmc_adapter_tool

        # Get start time
        start = time.time()

        print('Executing Apply Butterworth Filters...')

        # Create the global and local filter categories lists
        global_filter_categories=[]
        if fmc_adapter_tool.apply_global_filter_core:
            global_filter_categories.append('core')
        if fmc_adapter_tool.apply_global_filter_arms:
            global_filter_categories.append('arms')
        if fmc_adapter_tool.apply_global_filter_hands:
            global_filter_categories.append('hands')
        if fmc_adapter_tool.apply_global_filter_fingers:
            global_filter_categories.append('fingers')
        if fmc_adapter_tool.apply_global_filter_legs:
            global_filter_categories.append('legs')
        if fmc_adapter_tool.apply_global_filter_feet:
            global_filter_categories.append('feet')

        local_filter_categories=[]
        if scipy_available:
            if fmc_adapter_tool.apply_local_filter_core:
                local_filter_categories.append('core')
            if fmc_adapter_tool.apply_local_filter_arms:
                local_filter_categories.append('arms')
            if fmc_adapter_tool.apply_local_filter_hands:
                local_filter_categories.append('hands')
            if fmc_adapter_tool.apply_local_filter_fingers:
                local_filter_categories.append('fingers')
            if fmc_adapter_tool.apply_local_filter_legs:
                local_filter_categories.append('legs')
            if fmc_adapter_tool.apply_local_filter_feet:
                local_filter_categories.append('feet')

        if global_filter_categories == [] and local_filter_categories == []:
            print('No category selected')
            return {'FINISHED'}
        
        # Create the cutoff frequencies dictionary
        global_cutoff_frequencies={}
        if fmc_adapter_tool.apply_global_filter_core:
            global_cutoff_frequencies['core'] = fmc_adapter_tool.global_filter_core_frequency
        if fmc_adapter_tool.apply_global_filter_arms:
            global_cutoff_frequencies['arms'] = fmc_adapter_tool.global_filter_arms_frequency
        if fmc_adapter_tool.apply_global_filter_hands:
            global_cutoff_frequencies['hands'] = fmc_adapter_tool.global_filter_hands_frequency
        if fmc_adapter_tool.apply_global_filter_fingers:
            global_cutoff_frequencies['fingers'] = fmc_adapter_tool.global_filter_fingers_frequency
        if fmc_adapter_tool.apply_global_filter_legs:
            global_cutoff_frequencies['legs'] = fmc_adapter_tool.global_filter_legs_frequency
        if fmc_adapter_tool.apply_global_filter_feet:
            global_cutoff_frequencies['feet'] = fmc_adapter_tool.global_filter_feet_frequency

        local_cutoff_frequencies={}
        if scipy_available:
            if fmc_adapter_tool.apply_local_filter_core:
                local_cutoff_frequencies['core'] = fmc_adapter_tool.local_filter_core_frequency
            if fmc_adapter_tool.apply_local_filter_arms:
                local_cutoff_frequencies['arms'] = fmc_adapter_tool.local_filter_arms_frequency
            if fmc_adapter_tool.apply_local_filter_hands:
                local_cutoff_frequencies['hands'] = fmc_adapter_tool.local_filter_hands_frequency
            if fmc_adapter_tool.apply_local_filter_fingers:
                local_cutoff_frequencies['fingers'] = fmc_adapter_tool.local_filter_fingers_frequency
            if fmc_adapter_tool.apply_local_filter_legs:
                local_cutoff_frequencies['legs'] = fmc_adapter_tool.local_filter_legs_frequency
            if fmc_adapter_tool.apply_local_filter_feet:
                local_cutoff_frequencies['feet'] = fmc_adapter_tool.local_filter_feet_frequency

        local_filter_origins={}
        if scipy_available:
            if fmc_adapter_tool.apply_local_filter_core:
                local_filter_origins['core'] = fmc_adapter_tool.local_filter_origin_core
            if fmc_adapter_tool.apply_local_filter_arms:
                local_filter_origins['arms'] = fmc_adapter_tool.local_filter_origin_arms
            if fmc_adapter_tool.apply_local_filter_hands:
                local_filter_origins['hands'] = fmc_adapter_tool.local_filter_origin_hands
            if fmc_adapter_tool.apply_local_filter_fingers:
                local_filter_origins['fingers'] = fmc_adapter_tool.local_filter_origin_fingers
            if fmc_adapter_tool.apply_local_filter_legs:
                local_filter_origins['legs'] = fmc_adapter_tool.local_filter_origin_legs
            if fmc_adapter_tool.apply_local_filter_feet:
                local_filter_origins['feet'] = fmc_adapter_tool.local_filter_origin_feet

        # Execute export fbx function
        apply_butterworth_filters(global_filter_categories=global_filter_categories,
                                  global_cutoff_frequencies=global_cutoff_frequencies,
                                  local_filter_categories=local_filter_categories,
                                  local_cutoff_frequencies=local_cutoff_frequencies,
                                  local_filter_origins=local_filter_origins,
                                  interval_variable=fmc_adapter_tool.interval_variable,
                                  interval_factor=fmc_adapter_tool.interval_factor,
                                  body_height=fmc_adapter_tool.body_height)

        # Get end time and print execution time
        end = time.time()
        print('Finished. Execution time (s): ' + str(m.trunc((end - start)*1000)/1000))

        return {'FINISHED'}

classes = [FMC_ADAPTER_PROPERTIES,
           VIEW3D_PT_freemocap_adapter,
           FMC_ADAPTER_OT_adjust_empties,
           FMC_ADAPTER_OT_reduce_bone_length_dispersion,
           FMC_ADAPTER_OT_add_rig,
           FMC_ADAPTER_OT_add_body_mesh,
           FMC_ADAPTER_OT_export_fbx,
           FMC_ADAPTER_OT_add_finger_rotation_limits,
           FMC_ADAPTER_OT_apply_butterworth_filters,
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
