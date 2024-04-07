"""
Dictionary with the rotations of the Metahuman pose of the FreeMoCap armature.
"""
import math as m

freemocap_metahuman = {
    'pelvis': {
        'rotation' : (
            m.radians(-90),
            0,
            0
        )
    },
    'pelvis.R': {
        'rotation' : (
            0,
            m.radians(-90),
            0
        )
    },
    'pelvis.L': {
        'rotation' : (
            0,
            m.radians(90),
            0
        )
    },
    'spine': {
        'rotation' : (
            m.radians(6),
            0,
            0
        )
    },
    'spine.001': {
        'rotation' : (
            m.radians(-9.86320126530132),
            0,
            0
        )
    },
    'neck': {
        'rotation' : (
            m.radians(11.491515802111422),
            0,
            0
        )
    },
    'face': {
        'rotation' : (
            m.radians(110),
            0,
            0
        )
    },
    'shoulder.R': {
        'rotation' : (
            0,
            m.radians(-90),
            0
        )
    },
    'shoulder.L': {
        'rotation' : (
            0,
            m.radians(90),
            0
        )
    },
    'upper_arm.R': {
        'rotation' : (
            m.radians(-2.6811034603331763),
            m.radians(-144.74571040036872),
            m.radians(8.424363006256543),
        )
    },
    'upper_arm.L': {
        'rotation' : (
            m.radians(-2.6811482834496045),
            m.radians(144.74547817393693),
            m.radians(-8.42444582230023),
        )
    },
    'forearm.R': {
        'rotation' : (
            m.radians(131.9406083482122),
            m.radians(-28.645770690351164),
            m.radians(-59.596439942541906),
        )
    },
    'forearm.L': {
        'rotation' : (
            m.radians(131.94101815956242),
            m.radians(28.64569726581759),
            m.radians(59.596774621811235),
        )
    },
    'hand.R': {
        'rotation' : (
            m.radians(136.60972566483292),
            m.radians(-19.358236551318736),
            m.radians(-46.40956446672754),
        )
    },
    'hand.L': {
        'rotation' : (
            m.radians(136.47491139099523),
            m.radians(18.1806521742533),
            m.radians(43.68087998764535),
        )
    },
    'thumb.carpal.R': {
        'rotation' : (
            m.radians(127.39066417222988),
            m.radians(23.311534674996484),
            m.radians(45.30160533051392),
        )
    },
    'thumb.carpal.L': {
        'rotation' : (
            m.radians(127.39066417222988),
            m.radians(-23.311534674996484),
            m.radians(-45.30160533051392),
        )
    },
    'thumb.01.R': {
        'rotation' : (
            m.radians(117.97956508092275),
            m.radians(12.793343881500329),
            m.radians(21.12921239554925),
        )
    },
    'thumb.01.L': {
        'rotation' : (
            m.radians(122.88600415044473),
            m.radians(-10.369630763953793),
            m.radians(-18.93130874705792),
        )
    },
    'thumb.02.R': {
        'rotation' : (
            m.radians(139.66359886539402),
            m.radians(4.185290621479108),
            m.radians(11.362482429632479),
        )
    },
    'thumb.02.L': {
        'rotation' : (
            m.radians(152.60762696526857),
            m.radians(0.13829642967458847),
            m.radians(0.5674746878854321),
        )
    },
    'thumb.03.R': {
        'rotation' : (
            m.radians(-2.7266915579484263),
            m.radians(-167.1273523859084),
            m.radians(23.82585133459303),
        )
    },
    'thumb.03.L': {
        'rotation' : (
            m.radians(10.804527691428722),
            m.radians(163.43381830919728),
            m.radians(66.01391493195663),
        )
    },
    'palm.01.R': {
        'rotation' : (
            m.radians(126.9977097289007),
            m.radians(-13.088697482910959),
            m.radians(-25.914318277107828),
        )
    },
    'palm.01.L': {
        'rotation' : (
            m.radians(126.9977097289007),
            m.radians(13.088697482910959),
            m.radians(25.914318277107828),
        )
    },
    'f_index.01.R': {
        'rotation' : (
            m.radians(146.51013950827976),
            m.radians(-6.59417198324296),
            m.radians(-21.67889065202624),
        )
    },
    'f_index.01.L': {
        'rotation' : (
            m.radians(153.311341355455),
            m.radians(-2.1703897255238127),
            m.radians(-9.131485660838793),
        )
    },
    'f_index.02.R': {
        'rotation' : (
            m.radians(157.12713581830934),
            m.radians(5.839566280437605),
            m.radians(28.30145231655436),
        )
    },
    'f_index.02.L': {
        'rotation' : (
            m.radians(163.47826918031572),
            m.radians(-11.34770446158951),
            m.radians(-68.76827067703432),
        )
    },
    'f_index.03.R': {
        'rotation' : (
            m.radians(5.313239586959239),
            m.radians(152.2807477719701),
            m.radians(21.30151074755199),
        )
    },
    'f_index.03.L': {
        'rotation' : (
            m.radians(13.635834909016708),
            m.radians(-148.06406218597104),
            m.radians(-45.35391774936705),
        )
    },
    'palm.02.R': {
        'rotation' : (
            m.radians(138.28724744574475),
            m.radians(-26.7115413721263),
            m.radians(-63.85898341862845),
        )
    },
    'palm.02.L': {
        'rotation' : (
            m.radians(138.28724744574475),
            m.radians(26.7115413721263),
            m.radians(63.85898341862845),
        )
    },
    'f_middle.01.R': {
        'rotation' : (
            m.radians(150.7975995144585),
            m.radians(-8.823725874574482),
            m.radians(-32.99580376706369),
        )
    },
    'f_middle.01.L': {
        'rotation' : (
            m.radians(153.59596899854776),
            m.radians(2.9706012417475782),
            m.radians(12.614850547920385),
        )
    },
    'f_middle.02.R': {
        'rotation' : (
            m.radians(164.517796651235),
            m.radians(12.618237467975066),
            m.radians(78.24571139574978),
        )
    },
    'f_middle.02.L': {
        'rotation' : (
            m.radians(-12.509869686603643),
            m.radians(-161.1841315815135),
            m.radians(66.96937643457139),
        )
    },
    'f_middle.03.R': {
        'rotation' : (
            m.radians(15.758219717176143),
            m.radians(133.4156013598548),
            m.radians(35.6408457495699),
        )
    },
    'f_middle.03.L': {
        'rotation' : (
            m.radians(23.397164756620935),
            m.radians(-128.8472429938701),
            m.radians(-46.789906965754284),
        )
    },
    'palm.03.R': {
        'rotation' : (
            m.radians(-25.336834320519714),
            m.radians(-145.30192002523953),
            m.radians(71.4713795127694),
        )
    },
    'palm.03.L': {
        'rotation' : (
            m.radians(-25.336834320519714),
            m.radians(145.30192002523953),
            m.radians(-71.4713795127694),
        )
    },
    'f_ring.01.R': {
        'rotation' : (
            m.radians(157.3626134201347),
            m.radians(-10.553912682855323),
            m.radians(-49.541062767205815),
        )
    },
    'f_ring.01.L': {
        'rotation' : (
            m.radians(158.7280911786253),
            m.radians(-1.3540651527177525),
            m.radians(-7.201199923085966),
        )
    },
    'f_ring.02.R': {
        'rotation' : (
            m.radians(166.01302068319916),
            m.radians(5.336361484847024),
            m.radians(41.603730668585264),
        )
    },
    'f_ring.02.L': {
        'rotation' : (
            m.radians(163.8374688287667),
            m.radians(-9.297557441639421),
            m.radians(-59.59876903704888),
        )
    },
    'f_ring.03.R': {
        'rotation' : (
            m.radians(-0.6994255649961746),
            m.radians(135.75451767885562),
            m.radians(-1.720409926092497),
        )
    },
    'f_ring.03.L': {
        'rotation' : (
            m.radians(-1.1197764306947984),
            m.radians(-132.1242174934805),
            m.radians(2.5220881187188167),
        )
    },
    'palm.04.R': {
        'rotation' : (
            m.radians(-8.713395267590327),
            m.radians(-143.18446575988722),
            m.radians(25.78783000386836),
        )
    },
    'palm.04.L': {
        'rotation' : (
            m.radians(-8.713395267590327),
            m.radians(143.18446575988722),
            m.radians(-25.78783000386836),
        )
    },
    'f_pinky.01.R': {
        'rotation' : (
            m.radians(163.10432998363586),
            m.radians(-13.879361888778927),
            m.radians(-78.67092482252893),
        )
    },
    'f_pinky.01.L': {
        'rotation' : (
            m.radians(164.59784646830755),
            m.radians(6.764079769036197),
            m.radians(47.212989373512386),
        )
    },
    'f_pinky.02.R': {
        'rotation' : (
            m.radians(168.97607968855576),
            m.radians(4.6775274139231175),
            m.radians(45.879312975797355),
        )
    },
    'f_pinky.02.L': {
        'rotation' : (
            m.radians(-9.264448953411431),
            m.radians(-169.27331586085637),
            m.radians(81.59100144743863),
        )
    },
    'f_pinky.03.R': {
        'rotation' : (
            m.radians(2.95244190317863),
            m.radians(136.37830519537457),
            m.radians(7.3690390153343355),
        )
    },
    'f_pinky.03.L': {
        'rotation' : (
            m.radians(6.822067648202783),
            m.radians(-130.67009753994145),
            m.radians(-14.791051270323997),
        )
    },
    'thigh.R': {
        'rotation' : (
            m.radians(-0.12079388316344568),
            m.radians(-176.63197042733134),
            m.radians(4.106872792731369),
        )
    },
    'thigh.L': {
        'rotation' : (
            m.radians(-0.12078686621129055),
            m.radians(176.63197042733134),
            m.radians(-4.106635016770888),
        )
    },
    'shin.R': {
        'rotation' : (
            m.radians(-175.12260790378525),
            m.radians(-2.6481038282450826),
            m.radians(56.97761905625937),
        )
    },
    'shin.L': {
        'rotation' : (
            m.radians(-175.12259424340692),
            m.radians(2.648141394285518),
            m.radians(-56.97820303743341),
        )
    },
    'foot.R': {
        'rotation' : (
            m.radians(106.8930615673465),
            m.radians(-8.188085418524645),
            m.radians(-11.028648396211644),
        )
    },
    'foot.L': {
        'rotation' : (
            m.radians(107.86645231653254),
            m.radians(8.93590490150277),
            m.radians(12.247207078107985),
        )
    },
    'heel.02.R': {
        'rotation' : (
            m.radians(195),
            0,
            0
        )
    },
    'heel.02.L': {
        'rotation' : (
            m.radians(195),
            0,
            0
        )
    },
}
