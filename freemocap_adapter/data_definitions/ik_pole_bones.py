"""
Dictionary of the pole bones parameters to animate when adding the
rig with IK constraints.
"""
ik_pole_bones = {
    'arm_pole_target.R': {
        'base_marker':      'right_shoulder',
        'pole_marker':      'right_elbow',
        'target_marker':    'right_wrist',
        'aux_markers': ['right_wrist', 'right_hand_thumb_cmc'],
        'head_position': (0, 0, 0),
        'tail_position': (0, 0.25, 0),
    },
    'arm_pole_target.L': {
        'base_marker':      'left_shoulder',
        'pole_marker':      'left_elbow',
        'target_marker':    'left_wrist',
        'aux_markers': ['left_wrist', 'left_hand_thumb_cmc'],
        'head_position': (0, 0, 0),
        'tail_position': (0, 0.25, 0),
    },
    'leg_pole_target.R': {
        'base_marker':      'right_hip',
        'pole_marker':      'right_knee',
        'target_marker':    'right_ankle',
        'aux_markers': ['right_ankle', 'right_heel'],
        'head_position': (0, 0, 0),
        'tail_position': (0, 0.25, 0),
    },
    'leg_pole_target.L': {
        'base_marker':          'left_hip',
        'pole_marker':          'left_knee',
        'target_marker':        'left_ankle',
        'aux_markers': ['left_ankle', 'left_heel'],
        'head_position': (0, 0, 0),
        'tail_position': (0, 0.25, 0),
    },
}
