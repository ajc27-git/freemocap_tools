"""
Dictionary with the rotations of the T-Pose of the FreeMoCap armature.
"""
import math as m

freemocap_tpose = {
    'pelvis': {
        'rotation': (0, 0, 0),
        'roll': 0,
    },
    'pelvis.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'pelvis.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'spine': {
        'rotation': (0, 0, 0),
        'roll': 0,
    },
    'spine.001': {
        'rotation': (0, 0, 0),
        'roll': 0,
    },
    'neck': {
        'rotation': (0, 0, 0),
        'roll': 0,
    },
    'face': {
        'rotation': (m.radians(110), 0, 0),
        'roll': 0,
    },
    'shoulder.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'shoulder.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'upper_arm.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': m.radians(-90),
    },
    'upper_arm.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': m.radians(90),
    },
    'forearm.R': {
        'rotation': (0, m.radians(-90), m.radians(1)),
        'roll': m.radians(-90),
    },
    'forearm.L': {
        'rotation': (0, m.radians(90), m.radians(-1)),
        'roll': m.radians(90),
    },
    'hand.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': m.radians(-90),
    },
    'hand.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': m.radians(90),
    },
    'thumb.carpal.R': {
        'rotation': (0, m.radians(-90), m.radians(45)),
        'roll': 0,
    },
    'thumb.carpal.L': {
        'rotation': (0, m.radians(90), m.radians(-45)),
        'roll': 0,
    },
    'thumb.01.R': {
        'rotation': (0, m.radians(-90), m.radians(45)),
        'roll': 0,
    },
    'thumb.01.L': {
        'rotation': (0, m.radians(90), m.radians(-45)),
        'roll': 0,
    },
    'thumb.02.R': {
        'rotation': (0, m.radians(-90), m.radians(45)),
        'roll': 0,
    },
    'thumb.02.L': {
        'rotation': (0, m.radians(90), m.radians(-45)),
        'roll': 0,
    },
    'thumb.03.R': {
        'rotation': (0, m.radians(-90), m.radians(45)),
        'roll': 0,
    },
    'thumb.03.L': {
        'rotation': (0, m.radians(90), m.radians(-45)),
        'roll': 0,
    },
    'palm.01.R': {
        'rotation': (0, m.radians(-90), m.radians(17)),
        'roll': 0,
    },
    'palm.01.L': {
        'rotation': (0, m.radians(90), m.radians(-17)),
        'roll': 0,
    },
    'f_index.01.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_index.01.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_index.02.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_index.02.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_index.03.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_index.03.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'palm.02.R': {
        'rotation': (0, m.radians(-90), m.radians(5.5)),
        'roll': 0,
    },
    'palm.02.L': {
        'rotation': (0, m.radians(90), m.radians(-5.5)),
        'roll': 0,
    },
    'f_middle.01.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_middle.01.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_middle.02.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_middle.02.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_middle.03.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_middle.03.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'palm.03.R': {
        'rotation': (0, m.radians(-90), m.radians(-7.3)),
        'roll': 0,
    },
    'palm.03.L': {
        'rotation': (0, m.radians(90), m.radians(7.3)),
        'roll': 0,
    },
    'f_ring.01.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_ring.01.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_ring.02.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_ring.02.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_ring.03.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_ring.03.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'palm.04.R': {
        'rotation': (0, m.radians(-90), m.radians(-19)),
        'roll': 0,
    },
    'palm.04.L': {
        'rotation': (0, m.radians(90), m.radians(19)),
        'roll': 0,
    },
    'f_pinky.01.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_pinky.01.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_pinky.02.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_pinky.02.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'f_pinky.03.R': {
        'rotation': (0, m.radians(-90), 0),
        'roll': 0,
    },
    'f_pinky.03.L': {
        'rotation': (0, m.radians(90), 0),
        'roll': 0,
    },
    'thigh.R': {
        'rotation': (m.radians(1), m.radians(180), 0),
        'roll': 0,
    },
    'thigh.L': {
        'rotation': (m.radians(1), m.radians(180), 0),
        'roll': 0,
    },
    'shin.R': {
        'rotation': (m.radians(-1), m.radians(180), 0),
        'roll': 0,
    },
    'shin.L': {
        'rotation': (m.radians(-1), m.radians(180), 0),
        'roll': 0,
    },
    'foot.R': {
        'rotation': (m.radians(113), 0, 0),
        'roll': 0,
    },
    'foot.L': {
        'rotation': (m.radians(113), 0, 0),
        'roll': 0,
    },
    'heel.02.R': {
        'rotation': (m.radians(195), 0, 0),
        'roll': 0,
    },
    'heel.02.L': {
        'rotation': (m.radians(195), 0, 0),
        'roll': 0,
    },
}
