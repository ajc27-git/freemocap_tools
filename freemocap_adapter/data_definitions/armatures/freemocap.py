"""
Dictionary with the bones comforming the freemocap armature.
"""

armature_freemocap = {
    'pelvis': {
        'parent_bone' : 'root',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0.05,
    },
    'pelvis.R': {
        'parent_bone' : 'pelvis',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'pelvis.L': {
        'parent_bone' : 'pelvis',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'spine': {
        'parent_bone' : 'pelvis',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'spine.001': {
        'parent_bone' : 'spine',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'neck': {
        'parent_bone' : 'spine.001',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'face': {
        'parent_bone' : 'neck',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'shoulder.R': {
        'parent_bone' : 'spine.001',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'shoulder.L': {
        'parent_bone' : 'spine.001',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'upper_arm.R': {
        'parent_bone' : 'shoulder.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'upper_arm.L': {
        'parent_bone' : 'shoulder.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'forearm.R': {
        'parent_bone' : 'upper_arm.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'forearm.L': {
        'parent_bone' : 'upper_arm.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'hand.R': {
        'parent_bone' : 'forearm.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'hand.L': {
        'parent_bone' : 'forearm.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thumb.carpal.R': {
        'parent_bone' : 'hand.R',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'thumb.carpal.L': {
        'parent_bone' : 'hand.L',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'thumb.01.R': {
        'parent_bone' : 'thumb.carpal.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thumb.01.L': {
        'parent_bone' : 'thumb.carpal.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thumb.02.R': {
        'parent_bone' : 'thumb.01.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thumb.02.L': {
        'parent_bone' : 'thumb.01.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thumb.03.R': {
        'parent_bone' : 'thumb.02.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thumb.03.L': {
        'parent_bone' : 'thumb.02.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'palm.01.R': {
        'parent_bone' : 'hand.R',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'palm.01.L': {
        'parent_bone' : 'hand.L',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'f_index.01.R': {
        'parent_bone' : 'palm.01.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_index.01.L': {
        'parent_bone' : 'palm.01.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_index.02.R': {
        'parent_bone' : 'f_index.01.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_index.02.L': {
        'parent_bone' : 'f_index.01.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_index.03.R': {
        'parent_bone' : 'f_index.02.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_index.03.L': {
        'parent_bone' : 'f_index.02.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'palm.02.R': {
        'parent_bone' : 'hand.R',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'palm.02.L': {
        'parent_bone' : 'hand.L',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'f_middle.01.R': {
        'parent_bone' : 'palm.02.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_middle.01.L': {
        'parent_bone' : 'palm.02.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_middle.02.R': {
        'parent_bone' : 'f_middle.01.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_middle.02.L': {
        'parent_bone' : 'f_middle.01.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_middle.03.R': {
        'parent_bone' : 'f_middle.02.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_middle.03.L': {
        'parent_bone' : 'f_middle.02.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'palm.03.R': {
        'parent_bone' : 'hand.R',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'palm.03.L': {
        'parent_bone' : 'hand.L',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'f_ring.01.R': {
        'parent_bone' : 'palm.03.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_ring.01.L': {
        'parent_bone' : 'palm.03.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_ring.02.R': {
        'parent_bone' : 'f_ring.01.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_ring.02.L': {
        'parent_bone' : 'f_ring.01.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_ring.03.R': {
        'parent_bone' : 'f_ring.02.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_ring.03.L': {
        'parent_bone' : 'f_ring.02.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'palm.04.R': {
        'parent_bone' : 'hand.R',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'palm.04.L': {
        'parent_bone' : 'hand.L',
        'connected' : False,
        'parent_position' : 'head',
        'default_length' : 0,
    },
    'f_pinky.01.R': {
        'parent_bone' : 'palm.04.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_pinky.01.L': {
        'parent_bone' : 'palm.04.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_pinky.02.R': {
        'parent_bone' : 'f_pinky.01.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_pinky.02.L': {
        'parent_bone' : 'f_pinky.01.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_pinky.03.R': {
        'parent_bone' : 'f_pinky.02.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'f_pinky.03.L': {
        'parent_bone' : 'f_pinky.02.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thigh.R': {
        'parent_bone' : 'pelvis.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'thigh.L': {
        'parent_bone' : 'pelvis.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'shin.R': {
        'parent_bone' : 'thigh.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'shin.L': {
        'parent_bone' : 'thigh.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'foot.R': {
        'parent_bone' : 'shin.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'foot.L': {
        'parent_bone' : 'shin.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'heel.02.R': {
        'parent_bone' : 'shin.R',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
    'heel.02.L': {
        'parent_bone' : 'shin.L',
        'connected' : True,
        'parent_position' : 'tail',
        'default_length' : 0,
    },
}
