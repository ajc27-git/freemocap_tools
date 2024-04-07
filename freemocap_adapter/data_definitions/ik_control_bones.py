"""
Dictionary of the control bones parameters to animate when adding the
rig with IK constraints.
"""
ik_control_bones = {
    'hand.IK.R': {
        'controlled_bone': 'hand.R',
        'tail_relative_position': (-0.1, 0, 0),
    },
    'hand.IK.L': {
        'controlled_bone': 'hand.L',
        'tail_relative_position': (0.1, 0, 0),
    },
    'foot.IK.R': {
        'controlled_bone': 'foot.R',
        'tail_relative_position': (-0.1, 0, 0),
    },
    'foot.IK.L': {
        'controlled_bone': 'foot.L',
        'tail_relative_position': (0.1, 0, 0),
    },
}