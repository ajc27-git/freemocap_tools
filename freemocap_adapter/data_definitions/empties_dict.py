# Dictionary containing empty children for each of the capture empties.
# This will be used to correct the position of the empties
# (and its children) that are outside the bone length interval defined
# by x*stdev
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
        'children'      : [
            'nose',
            'mouth_right',
            'mouth_left',
            'right_eye',
            'right_eye_inner',
            'right_eye_outer',
            'left_eye',
            'left_eye_inner',
            'left_eye_outer',
            'right_ear',
            'left_ear'],
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
        'children'      : [
            'right_thumb',
            'right_index',
            'right_pinky',
            'right_hand',
            'right_hand_middle',
            'right_hand_wrist'],
        'category'      : 'hands',
        'tail_of_bone'  : 'forearm.R'},
    'left_wrist': {
        'children'      : [
            'left_thumb',
            'left_index',
            'left_pinky',
            'left_hand',
            'left_hand_middle',
            'left_hand_wrist'],
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
        'children'      : [
            'right_hand_thumb_cmc',
            'right_hand_index_finger_mcp',
            'right_hand_middle_finger_mcp',
            'right_hand_ring_finger_mcp',
            'right_hand_pinky_mcp'],
        'category'      : 'hands',
        'tail_of_bone'  : ''},
    'left_hand_wrist': {
        'children'      : [
            'left_hand_thumb_cmc',
            'left_hand_index_finger_mcp',
            'left_hand_middle_finger_mcp',
            'left_hand_ring_finger_mcp',
            'left_hand_pinky_mcp'],
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
