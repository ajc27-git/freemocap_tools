"""
This module defines bone constraints for a skeletal animation system.

Each bone in the system can have a list of constraints associated with it.
Constraints dictate how bones should be tracked and manipulated during
animation.

The available constraint types are:
- 'COPY_LOCATION': Copies the location of a target bone or point.
- 'LOCKED_TRACK': Locks a specific axis of the target bone to an axis of the
  tracked object.
- 'DAMPED_TRACK': Dampens the tracking of a specific axis of the target bone.
- 'LIMIT_ROTATION': Limits the rotation of a specific axis of the target bone.
- 'IK': Inverse Kinematics

This module is used in the animation processing pipeline to handle bone
behavior during animations.
"""
import math as m

bone_constraints = {
    "pelvis": [
        {'type':'COPY_LOCATION','target':'hips_center','use_offset':False},
        {'type':'LOCKED_TRACK','target':'right_hip',
            'track_axis': {
                'freemocap_apose': 'TRACK_NEGATIVE_X',
                'freemocap_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_default': 'TRACK_NEGATIVE_X',
                'ue_metahuman_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_realtime': 'TRACK_Z',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Z',
                'freemocap_tpose': 'LOCK_Z',
                'ue_metahuman_default': 'LOCK_Z',
                'ue_metahuman_tpose': 'LOCK_Z',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0},
        {'type':'LOCKED_TRACK','target':'right_hip',
            'track_axis': {
                'freemocap_apose': 'TRACK_NEGATIVE_X',
                'freemocap_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_default': 'TRACK_NEGATIVE_X',
                'ue_metahuman_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_realtime': 'TRACK_Z',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_X',
            },
            'influence':1.0}],
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
        {'type':'LOCKED_TRACK','target':'right_shoulder',
            'track_axis': {
                'freemocap_apose': 'TRACK_NEGATIVE_X',
                'freemocap_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_default': 'TRACK_NEGATIVE_X',
                'ue_metahuman_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_realtime': 'TRACK_Z',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0},
        {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':22,'use_limit_y':True,'min_y':-45,'max_y':45,'use_limit_z':True,'min_z':-30,'max_z':30,'owner_space':'LOCAL'}],
    "neck": [
        {'type':'DAMPED_TRACK','target':'head_center','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'nose',
            'track_axis': {
                'freemocap_apose': 'TRACK_Z',
                'freemocap_tpose': 'TRACK_Z',
                'ue_metahuman_default': 'TRACK_Z',
                'ue_metahuman_tpose': 'TRACK_Z',
                'ue_metahuman_realtime': 'TRACK_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0},
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
            'pole_angle': {
                'freemocap_apose': m.radians(-90),
                'freemocap_tpose': m.radians(-90),
                'ue_metahuman_default': m.radians(180),
                'ue_metahuman_tpose': m.radians(-90),
                'ue_metahuman_realtime': m.radians(180),
            },
            'chain_count':2,'lock_ik_x':False,'lock_ik_y':False,'lock_ik_z':False,
            'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
            'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -1.5708,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
        {'type':'COPY_ROTATION','target':'root','subtarget':'hand.IK.R','use_x':False,'use_y':True,'use_z':False,'target_space':'LOCAL','owner_space':'LOCAL','influence':0.3},
        {'type':'DAMPED_TRACK','target':'right_wrist','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'right_hand_thumb_cmc',
            'track_axis': {
                'freemocap_apose': 'TRACK_Z',
                'freemocap_tpose': 'TRACK_Z',
                'ue_metahuman_default': 'TRACK_Z',
                'ue_metahuman_tpose': 'TRACK_Z',
                'ue_metahuman_realtime': 'TRACK_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':0.3},
        {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':0,'max_y':146,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
    "forearm.L": [
        {'type':'IK','target':'root','subtarget':'hand.IK.L','pole_target':'root','pole_subtarget':'arm_pole_target.L',
            'pole_angle': {
                'freemocap_apose': m.radians(-90),
                'freemocap_tpose': m.radians(-90),
                'ue_metahuman_default': 0,
                'ue_metahuman_tpose': m.radians(-90),
                'ue_metahuman_realtime': 0,
            },
            'chain_count':2,'lock_ik_x':False,'lock_ik_y':False,'lock_ik_z':False,
            'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
            'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -1.5708,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
        {'type':'COPY_ROTATION','target':'root','subtarget':'hand.IK.L','use_x':False,'use_y':True,'use_z':False,'target_space':'LOCAL','owner_space':'LOCAL','influence':0.3},
        {'type':'DAMPED_TRACK','target':'left_wrist','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'left_hand_thumb_cmc',
            'track_axis': {
                'freemocap_apose': 'TRACK_Z',
                'freemocap_tpose': 'TRACK_Z',
                'ue_metahuman_default': 'TRACK_Z',
                'ue_metahuman_tpose': 'TRACK_Z',
                'ue_metahuman_realtime': 'TRACK_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':0.3},
        {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-90,'max_x':79,'use_limit_y':True,'min_y':-146,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
    "hand.IK.R": [
        {'type':'COPY_LOCATION','target':'right_wrist','use_offset':False},
        {'type':'DAMPED_TRACK','target':'right_hand_middle','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'right_hand_index_finger_mcp',
            'track_axis': {
                'freemocap_apose': 'TRACK_X',
                'freemocap_tpose': 'TRACK_X',
                'ue_metahuman_default': 'TRACK_X',
                'ue_metahuman_tpose': 'TRACK_X',
                'ue_metahuman_realtime': 'TRACK_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0}],
    "hand.IK.L": [
        {'type':'COPY_LOCATION','target':'left_wrist','use_offset':False},
        {'type':'DAMPED_TRACK','target':'left_hand_middle','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'left_hand_index_finger_mcp',
            'track_axis': {
                'freemocap_apose': 'TRACK_X',
                'freemocap_tpose': 'TRACK_X',
                'ue_metahuman_default': 'TRACK_X',
                'ue_metahuman_tpose': 'TRACK_X',
                'ue_metahuman_realtime': 'TRACK_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0}],
    "hand.R": [
        {'type':'DAMPED_TRACK','target':'right_hand_middle','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'right_hand_thumb_cmc',
            'track_axis': {
                'freemocap_apose': 'TRACK_Z',
                'freemocap_tpose': 'TRACK_Z',
                'ue_metahuman_default': 'TRACK_Z',
                'ue_metahuman_tpose': 'TRACK_Z',
                'ue_metahuman_realtime': 'TRACK_Z',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0},
        {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':-45,'max_x':45,'use_limit_y':True,'min_y':-36,'max_y':25,'use_limit_z':True,'min_z':-86,'max_z':90,'owner_space':'LOCAL'}],
    "hand.L": [
        {'type':'DAMPED_TRACK','target':'left_hand_middle','track_axis':'TRACK_Y'},
        {'type':'LOCKED_TRACK','target':'left_hand_thumb_cmc',
            'track_axis': {
                'freemocap_apose': 'TRACK_Z',
                'freemocap_tpose': 'TRACK_Z',
                'ue_metahuman_default': 'TRACK_Z',
                'ue_metahuman_tpose': 'TRACK_Z',
                'ue_metahuman_realtime': 'TRACK_NEGATIVE_Z',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Y',
                'freemocap_tpose': 'LOCK_Y',
                'ue_metahuman_default': 'LOCK_Y',
                'ue_metahuman_tpose': 'LOCK_Y',
                'ue_metahuman_realtime': 'LOCK_Y',
            },
            'influence':1.0},
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
            'pole_angle': {
                'freemocap_apose': m.radians(-90),
                'freemocap_tpose': m.radians(-90),
                'ue_metahuman_default': m.radians(1.8),
                'ue_metahuman_tpose': m.radians(1.8),
                'ue_metahuman_realtime': m.radians(1.8),
            },
            'chain_count':2,'lock_ik_x':False,'lock_ik_y':False,'lock_ik_z':False,
            'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
            'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -0.174533,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
        {'type':'DAMPED_TRACK','target':'right_ankle','track_axis':'TRACK_Y'},
        {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
    "shin.L": [
        {'type':'IK','target':'root','subtarget':'foot.IK.L','pole_target':'root','pole_subtarget':'leg_pole_target.L',
            'pole_angle': {
                'freemocap_apose': m.radians(-90),
                'freemocap_tpose': m.radians(-90),
                'ue_metahuman_default': m.radians(178.2),
                'ue_metahuman_tpose': m.radians(178.2),
                'ue_metahuman_realtime': m.radians(178.2),
            },
            'chain_count':2,'lock_ik_x':False,'lock_ik_y':False,'lock_ik_z':False,
            'use_ik_limit_x':False,'use_ik_limit_y':False,'use_ik_limit_z':False,
            'ik_min_x': -0.174533,'ik_max_x': 2.61799,'ik_min_y': -0.174533,'ik_max_y': 1.74533,'ik_min_z': -0.174533,'ik_max_z': 0.174533},
        {'type':'DAMPED_TRACK','target':'left_ankle','track_axis':'TRACK_Y'},
        {'type':'LIMIT_ROTATION','use_limit_x':True,'min_x':0,'max_x':150,'use_limit_y':True,'min_y':0,'max_y':0,'use_limit_z':True,'min_z':0,'max_z':0,'owner_space':'LOCAL'}],
    "foot.IK.R": [
        {'type':'COPY_LOCATION','target':'right_ankle','use_offset':False},
        {'type':'LOCKED_TRACK','target':'right_foot_index',
            'track_axis': {
                'freemocap_apose': 'TRACK_NEGATIVE_X',
                'freemocap_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_default': 'TRACK_NEGATIVE_X',
                'ue_metahuman_tpose': 'TRACK_NEGATIVE_X',
                'ue_metahuman_realtime': 'TRACK_NEGATIVE_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Z',
                'freemocap_tpose': 'LOCK_Z',
                'ue_metahuman_default': 'LOCK_Z',
                'ue_metahuman_tpose': 'LOCK_Z',
                'ue_metahuman_realtime': 'LOCK_Z',
            },
            'influence':1.0}],
    "foot.IK.L": [
        {'type':'COPY_LOCATION','target':'left_ankle','use_offset':False},
        {'type':'LOCKED_TRACK','target':'left_foot_index',
            'track_axis': {
                'freemocap_apose': 'TRACK_X',
                'freemocap_tpose': 'TRACK_X',
                'ue_metahuman_default': 'TRACK_X',
                'ue_metahuman_tpose': 'TRACK_X',
                'ue_metahuman_realtime': 'TRACK_X',
            },
            'lock_axis': {
                'freemocap_apose': 'LOCK_Z',
                'freemocap_tpose': 'LOCK_Z',
                'ue_metahuman_default': 'LOCK_Z',
                'ue_metahuman_tpose': 'LOCK_Z',
                'ue_metahuman_realtime': 'LOCK_Z',
            },
            'influence':1.0}],
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
