import bpy
import math as m
import mathutils

#######################################################################
### Script to adapt the Freemocap Blender output to an armature with
### mesh and animation that can be imported in Unreal Engine.
### The armature has a TPose as rest pose for easier retargeting
### For best results, when the script is ran the empties should be
### forming a standing still pose with arms open similar to A or T Pose
### The body_mesh.ply file should be in the same folder as the
### Blender file before manually opening it
#######################################################################

def main():
    # Play and stop the animation in case the first frame empties are in a strange position
    bpy.ops.screen.animation_play()
    bpy.ops.screen.animation_cancel()
    
    # Adjust the origin, position and rotation of the empties
    adjust_empties(z_align_angle_offset=0,
                   z_translation_offset=-0.01,
                   z_align_ref_empty='left_knee',
                   ground_ref_empty='left_foot_index')
    
    # Add an armature, bone constraints, set TPose as rest pose and bake the animation
    add_armature(use_limit_rotation=False)
    
    # Add a mesh to the armature for export
    add_mesh_to_armature(mode="file")

######################################################################
######################### ADJUST EMPTIES #############################
######################################################################

def adjust_empties(z_align_angle_offset: float=0,
                   z_translation_offset: float=-0.01,
                   z_align_ref_empty: str='left_knee',
                   ground_ref_empty: str='left_foot_index',
                   ):

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
    # Calculate angle from origin x axis to projection of left_hip on xy plane
    left_hip_xy_angle = m.atan(left_hip_y_from_origin / left_hip_x_from_origin)
    # Rotate origin around the z axis to point at left_hip
    origin.rotation_euler[2] = left_hip_xy_angle

    # Calculate left_hip z position from origin (inverted operators to produce the correspondent angle sign
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

######################################################################
########################### ADD ARMATURE #############################
######################################################################

def add_armature(use_limit_rotation: bool=False):
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
    
    # Scale armature so it fits capture empties height. The reference point will be hips_center
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
    spine.head = hips_center_glob_pos
    pelvis_R.head = hips_center_glob_pos
    pelvis_L.head = hips_center_glob_pos
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

    ### Add bone constrains ###
    # Change to pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Create a dictionary with the different bone constraints
    constraints = {
        "pelvis": [
            {'type':'COPY_LOCATION','target':'hips_center'},
            {'type':'LOCKED_TRACK','target':'right_hip','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Z','influence':1.0}],
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
        "shoulder.L": [
            {'type':'COPY_LOCATION','target':'neck_center'},
            {'type':'DAMPED_TRACK','target':'left_shoulder','track_axis':'TRACK_Y'}],
        "shoulder.R": [
            {'type':'COPY_LOCATION','target':'neck_center'},
            {'type':'DAMPED_TRACK','target':'right_shoulder','track_axis':'TRACK_Y'}],
        "upper_arm.L": [
            {'type':'DAMPED_TRACK','target':'left_elbow','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-135,'max_x':90,'use_limit_y':True,'min_y':-180,'max_y':98,'use_limit_z':True,'min_z':-91,'max_z':97,'owner_space':'LOCAL'}],
        "upper_arm.R": [
            {'type':'DAMPED_TRACK','target':'right_elbow','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-135,'max_x':90,'use_limit_y':True,'min_y':-98,'max_y':180,'use_limit_z':True,'min_z':-97,'max_z':91,'owner_space':'LOCAL'}],
        "forearm.L": [
            {'type':'DAMPED_TRACK','target':'left_wrist','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':-146,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "forearm.R": [
            {'type':'DAMPED_TRACK','target':'right_wrist','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':0,'max_y':146,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "hand.L": [
            {'type':'DAMPED_TRACK','target':'left_index','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'left_thumb','track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':0.8},
            {'type':'LOCKED_TRACK','target':'left_thumb','track_axis':'TRACK_X','lock_axis':'LOCK_Y','influence':0.2},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-25,'max_y':36,'use_limit_z':True,'min_z':-90,'max_z':86,'owner_space':'LOCAL'}],
        "hand.R": [
            {'type':'DAMPED_TRACK','target':'right_index','track_axis':'TRACK_Y'},
            {'type':'LOCKED_TRACK','target':'right_thumb','track_axis':'TRACK_Z','lock_axis':'LOCK_Y','influence':0.8},
            {'type':'LOCKED_TRACK','target':'right_thumb','track_axis':'TRACK_NEGATIVE_X','lock_axis':'LOCK_Y','influence':0.2},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-36,'max_y':25,'use_limit_z':True,'min_z':-86,'max_z':90,'owner_space':'LOCAL'}],
        "thigh.L": [
            {'type':'COPY_LOCATION','target':'left_hip'},
            {'type':'DAMPED_TRACK','target':'left_knee','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-155,'max_x':45,'use_limit_y':True,'min_y':-85,'max_y':105,'use_limit_z':True,'min_z':-17,'max_z':88,'owner_space':'LOCAL'}],
        "thigh.R": [
            {'type':'COPY_LOCATION','target':'right_hip'},
            {'type':'DAMPED_TRACK','target':'right_knee','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-155,'max_x':45,'use_limit_y':True,'min_y':-105,'max_y':85,'use_limit_z':True,'min_z':-88,'max_z':17,'owner_space':'LOCAL'}],
        "shin.L": [
            {'type':'DAMPED_TRACK','target':'left_ankle','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "shin.R": [
            {'type':'DAMPED_TRACK','target':'right_ankle','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
        "foot.L": [
            {'type':'DAMPED_TRACK','target':'left_foot_index','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-31,'max_x':63,'use_limit_y':True,'min_y':-26,'max_y':26,'use_limit_z':True,'min_z':-74,'max_z':15,'owner_space':'LOCAL'}],
        "foot.R": [
            {'type':'DAMPED_TRACK','target':'right_foot_index','track_axis':'TRACK_Y'},
            {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-31,'max_x':63,'use_limit_y':True,'min_y':-26,'max_y':26,'use_limit_z':True,'min_z':-15,'max_z':74,'owner_space':'LOCAL'}],
        "heel.02.L": [
            {'type':'DAMPED_TRACK','target':'left_ankle','track_axis':'TRACK_Y'}],
        "heel.02.R": [
            {'type':'DAMPED_TRACK','target':'right_ankle','track_axis':'TRACK_Y'}],
        "toe.L": [
            {'type':'DAMPED_TRACK','target':'left_foot_index','track_axis':'TRACK_Y'}],
        "toe.R": [
            {'type':'DAMPED_TRACK','target':'right_foot_index','track_axis':'TRACK_Y'}]
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

######################################################################
######################## ADD MESH TO ARMATURE ########################
######################################################################

def add_mesh_to_armature(mode: str="file"):
    
    if mode == "file":
        
        try:
            bpy.ops.import_mesh.ply(filepath="body_mesh.ply")
            
        except:
            print("\nCould not find body_mesh file.")
            return

        # Get reference to armature
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
        
    elif mode == "custom":
    
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
    
    else:
        print("Unknown add armature mode")

# Execute main function
if __name__ == "__main__":
    main()

