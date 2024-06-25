"""
Dictionary with the rotations of the Metahuman default pose but with the bone 
rolls to match the local axes of the metahuman armature for use in realtime
capture.
"""
import math as m

ue_metahuman_realtime = {
    'pelvis': {
        'rotation' : (
            m.radians(5.313978),
            0,
            0
        ),
        'roll': m.radians(-90),
    },
    'pelvis_r': {
        'rotation' : (
            0,
            m.radians(-90),
            0
        ),
        'roll': 0,
    },
    'pelvis_l': {
        'rotation' : (
            0,
            m.radians(90),
            0
        ),
        'roll': 0,
    },
    'spine_01': {
        'rotation' : (
            m.radians(6),
            0,
            0
        ),
        'roll': m.radians(-90),
    },
    'spine_04': {
        'rotation' : (
            m.radians(-9.86320126530132),
            0,
            0
        ),
        'roll': m.radians(-90),
    },
    'neck_01': {
        'rotation' : (
            m.radians(11.491515802111422),
            0,
            0
        ),
        'roll': m.radians(-90),
    },
    'face': {
        'rotation' : (
            m.radians(110),
            0,
            0
        ),
        'roll': 0,
    },
    'clavicle_r': {
        'rotation' : (
            0,
            m.radians(-90),
            0
        ),
        'roll': 0,
    },
    'clavicle_l': {
        'rotation' : (
            0,
            m.radians(90),
            0
        ),
        'roll': 0,
    },
    'upperarm_r': {
        'rotation' : (
            m.radians(-2.6811034603331763),
            m.radians(-144.74571040036872),
            m.radians(8.424363006256543),
        ),
        'roll': m.radians(130),
    },
    'upperarm_l': {
        'rotation' : (
            m.radians(-2.6811482834496045),
            m.radians(144.74547817393693),
            m.radians(-8.42444582230023),
        ),
        'roll': m.radians(50),
    },
    'lowerarm_r': {
        'rotation' : (
            m.radians(131.9406083482122),
            m.radians(-28.645770690351164),
            m.radians(-59.596439942541906),
        ),
        'roll': m.radians(136),
    },
    'lowerarm_l': {
        'rotation' : (
            m.radians(131.94101815956242),
            m.radians(28.64569726581759),
            m.radians(59.596774621811235),
        ),
        'roll': m.radians(44),
    },
    'hand_r': {
        'rotation' : (
            m.radians(136.60972566483292),
            m.radians(-19.358236551318736),
            m.radians(-46.40956446672754),
        ),
        'roll': m.radians(180),
    },
    'hand_l': {
        'rotation' : (
            m.radians(136.47491139099523),
            m.radians(18.1806521742533),
            m.radians(43.68087998764535),
        ),
        'roll': m.radians(0),
    },

    'thumb_metacarpal_r': {
        'rotation' : (
            m.radians(108.46138911399733),
            m.radians(29.91067562086063),
            m.radians(40.68765203672481),
        ),
        'roll' : m.radians(118.0)
    },
    'thumb_01_r': {
        'rotation' : (
            m.radians(117.97956508092275),
            m.radians(12.793343881500329),
            m.radians(21.12921239554925),
        ),
        'roll' : m.radians(22.0)
    },
    'thumb_02_r': {
        'rotation' : (
            m.radians(139.66359886539402),
            m.radians(4.185290621479108),
            m.radians(11.362482429632479),
        ),
        'roll' : m.radians(58.0)
    },
    'thumb_03_r': {
        'rotation' : (
            m.radians(139.66359886539402),
            m.radians(4.185290621479108),
            m.radians(11.362482429632479),
        ),
        'roll' : m.radians(58.0)
    },
    'thumb_metacarpal_l': {
        'rotation' : (
            m.radians(129.87864253967706),
            m.radians(-29.566061841382222),
            m.radians(-58.87750789088471),
        ),
        'roll' : m.radians(-118.0)
    },
    'thumb_01_l': {
        'rotation' : (
            m.radians(122.88600415044473),
            m.radians(-10.369630763953793),
            m.radians(-18.93130874705792),
        ),
        'roll' : m.radians(150.0)
    },
    'thumb_02_l': {
        'rotation' : (
            m.radians(152.60762696526857),
            m.radians(0.13829642967458847),
            m.radians(0.5674746878854321),
        ),
        'roll' : m.radians(120.0)
    },
    'thumb_03_l': {
        'rotation' : (
            m.radians(152.60762696526857),
            m.radians(0.13829642967458847),
            m.radians(0.5674746878854321),
        ),
        'roll' : m.radians(120.0)
    },
    'index_metacarpal_r': {
        'rotation' : (
            m.radians(123.54290442405987),
            m.radians(-18.78471410444923),
            m.radians(-34.25055391382464),
        ),
        'roll' : m.radians(-168.0)
    },
    'index_01_r': {
        'rotation' : (
            m.radians(146.31965919270647),
            m.radians(-5.665469027362211),
            m.radians(-18.568524956839983),
        ),
        'roll' : m.radians(140.0)
    },
    'index_02_r': {
        'rotation' : (
            m.radians(161.1726022221945),
            m.radians(1.1799849751152838),
            m.radians(7.108271784333358),
        ),
        'roll' : m.radians(130.0)
    },
    'index_03_r': {
        'rotation' : (
            m.radians(161.1726022221945),
            m.radians(1.1799725953974132),
            m.radians(7.108197079139311),
        ),
        'roll' : m.radians(130.0)
    },
    'index_metacarpal_l': {
        'rotation' : (
            m.radians(122.2014689314477),
            m.radians(16.459003956208623),
            m.radians(29.36308910981695),
        ),
        'roll' : m.radians(168.0)
    },
    'index_01_l': {
        'rotation' : (
            m.radians(149.08048995711732),
            m.radians(-5.445986874799375),
            m.radians(-19.515243817317113),
        ),
        'roll' : m.radians(40.0)
    },
    'index_02_l': {
        'rotation' : (
            m.radians(162.15751550051036),
            m.radians(-9.685690625188213),
            m.radians(-56.71468750906515),
        ),
        'roll' : m.radians(40.0)
    },
    'index_03_l': {
        'rotation' : (
            m.radians(162.15748817975367),
            m.radians(-9.685631714806622),
            m.radians(-56.71431867884997),
        ),
        'roll' : m.radians(40.0)
    },
    'middle_metacarpal_r': {
        'rotation' : (
            m.radians(135.85862342218496),
            m.radians(-27.633989155387788),
            m.radians(-62.47886173455733),
        ),
        'roll' : m.radians(-163.0)
    },
    'middle_01_r': {
        'rotation' : (
            m.radians(150.7975995144585),
            m.radians(-8.823725874574482),
            m.radians(-32.99580376706369),
        ),
        'roll' : m.radians(160.0)
    },
    'middle_02_r': {
        'rotation' : (
            m.radians(164.517796651235),
            m.radians(12.618237467975066),
            m.radians(78.24571139574978),
        ),
        'roll' : m.radians(130.0)
    },
    'middle_03_r': {
        'rotation' : (
            m.radians(164.517796651235),
            m.radians(12.618237467975066),
            m.radians(78.24571139574978),
        ),
        'roll' : m.radians(130.0)
    },
    'middle_metacarpal_l': {
        'rotation' : (
            m.radians(133.36464814864652),
            m.radians(26.383403716473257),
            m.radians(57.07447455378474),
        ),
        'roll' : m.radians(163.0)
    },
    'middle_01_l': {
        'rotation' : (
            m.radians(151.15604784210078),
            m.radians(0.7369838147467227),
            m.radians(2.8652406646016657),
        ),
        'roll' : m.radians(30.0)
    },
    'middle_02_l': {
        'rotation' : (
            m.radians(-14.502737032626712),
            m.radians(-159.1776405694172),
            m.radians(69.40651770402616),
        ),
        'roll' : m.radians(60.0)
    },
    'middle_03_l': {
        'rotation' : (
            m.radians(-14.502800211876535),
            m.radians(-159.17787279584897),
            m.radians(69.40735781729407),
        ),
        'roll' : m.radians(60.0)
    },
    'ring_metacarpal_r': {
        'rotation' : (
            m.radians(-35.38173227812171),
            m.radians(-144.13648484716026),
            m.radians(89.17283244504377),
        ),
        'roll' : m.radians(-158.0)
    },
    'ring_01_r': {
        'rotation' : (
            m.radians(157.3626134201347),
            m.radians(-10.553912682855323),
            m.radians(-49.541062767205815),
        ),
        'roll' : m.radians(165.0)
    },
    'ring_02_r': {
        'rotation' : (
            m.radians(166.01302068319916),
            m.radians(5.336361484847024),
            m.radians(41.603730668585264),
        ),
        'roll' : m.radians(140.0)
    },
    'ring_03_r': {
        'rotation' : (
            m.radians(166.01302068319916),
            m.radians(5.336361484847024),
            m.radians(41.603730668585264),
        ),
        'roll' : m.radians(140.0)
    },
    'ring_metacarpal_l': {
        'rotation' : (
            m.radians(146.77786926336594),
            m.radians(32.463390521261196),
            m.radians(88.60104315867615),
        ),
        'roll' : m.radians(158.0)
    },
    'ring_01_l': {
        'rotation' : (
            m.radians(163.9742228763287),
            m.radians(-3.292757359234985),
            m.radians(-23.080197875355445),
        ),
        'roll' : m.radians(30.0)
    },
    'ring_02_l': {
        'rotation' : (
            m.radians(-10.792441671692385),
            m.radians(-168.8315665460966),
            m.radians(88.02622809850622),
        ),
        'roll' : m.radians(40.0)
    },
    'ring_03_l': {
        'rotation' : (
            m.radians(-10.79249972830033),
            m.radians(-168.83142994231324),
            m.radians(88.02582511734519),
        ),
        'roll' : m.radians(40.0)
    },
    'pinky_metacarpal_r': {
        'rotation' : (
            m.radians(-22.97185570719341),
            m.radians(-145.80376134431705),
            m.radians(66.89572650475114),
        ),
        'roll' : m.radians(-157.0)
    },
    'pinky_01_r': {
        'rotation' : (
            m.radians(163.10432998363586),
            m.radians(-13.879361888778927),
            m.radians(-78.67092482252893),
        ),
        'roll' : m.radians(175.0)
    },
    'pinky_02_r': {
        'rotation' : (
            m.radians(168.97607968855576),
            m.radians(4.6775274139231175),
            m.radians(45.879312975797355),
        ),
        'roll' : m.radians(150.0)
    },
    'pinky_03_r': {
        'rotation' : (
            m.radians(162.22981988306412),
            m.radians(2.758289507152786),
            m.radians(17.509948088325558),
        ),
        'roll' : m.radians(150.0)
    },
    'pinky_metacarpal_l': {
        'rotation' : (
            m.radians(-21.697345823163616),
            m.radians(145.0464436295244),
            m.radians(-62.65498499249528),
        ),
        'roll' : m.radians(157.0)
    },
    'pinky_01_l': {
        'rotation' : (
            m.radians(170.0127658007803),
            m.radians(9.673059897865567),
            m.radians(88.15997003264424),
        ),
        'roll' : m.radians(20.0)
    },
    'pinky_02_l': {
        'rotation' : (
            m.radians(-3.8516281965611694),
            m.radians(-172.1824573529049),
            m.radians(52.40465031258493),
        ),
        'roll' : m.radians(40.0)
    },
    'pinky_03_l': {
        'rotation' : (
            m.radians(169.1304966053114),
            m.radians(-7.058825483610697),
            m.radians(-65.9096042829522),
        ),
        'roll' : m.radians(40.0)
    },
    'thigh_r': {
        'rotation' : (
            m.radians(1),
            m.radians(-176.63197042733134),
            m.radians(4.106872792731369),
        ),
        'roll': m.radians(-79),
    },
    'thigh_l': {
        'rotation' : (
            m.radians(1),
            m.radians(176.63197042733134),
            m.radians(-4.106635016770888),
        ),
        'roll': m.radians(-101),
    },
    'calf_r': {
        'rotation' : (
            m.radians(-175.12260790378525),
            m.radians(-2.6481038282450826),
            m.radians(56.97761905625937),
        ),
        'roll': m.radians(-79),
    },
    'calf_l': {
        'rotation' : (
            m.radians(-175.12259424340692),
            m.radians(2.648141394285518),
            m.radians(-56.97820303743341),
        ),
        'roll': m.radians(-101),
    },
    'foot_r': {
        'rotation' : (
            m.radians(106.8930615673465),
            m.radians(-8.188085418524645),
            m.radians(-11.028648396211644),
        ),
        'roll': m.radians(-35),
    },
    'foot_l': {
        'rotation' : (
            m.radians(107.86645231653254),
            m.radians(8.93590490150277),
            m.radians(12.247207078107985),
        ),
        'roll': m.radians(-145),
    },
    'heel_r': {
        'rotation' : (
            m.radians(195),
            0,
            0
        ),
        'roll': 0,
    },
    'heel_l': {
        'rotation' : (
            m.radians(195),
            0,
            0
        ),
        'roll': 0,
    },
}
