import math as m
import statistics

import bpy

from freemocap_adapter.core_functions.empties.empties import EMPTY_POSITIONS
from freemocap_adapter.data_models.bones.bone_definitions import VIRTUAL_BONES


def update_virtual_bones_info():
    print('Updating Virtual Bones Information...')

    # Reset the lengths list for every virtual bone
    for bone in VIRTUAL_BONES:
        VIRTUAL_BONES[bone]['lengths'] = []

    # Adjust tail empty of hand bones depending if hand_middle empties exist or not
    try:
        right_hand_middle_name = bpy.data.objects['right_hand_middle'].name
        VIRTUAL_BONES['hand.R']['tail'] = 'right_hand_middle'
        VIRTUAL_BONES['hand.L']['tail'] = 'left_hand_middle'
    except:
        VIRTUAL_BONES['hand.R']['tail'] = 'right_index'
        VIRTUAL_BONES['hand.L']['tail'] = 'left_index'

    # Iterate through the empty_positions dictionary and calculate the distance between the head and tail and append it to the lengths list
    for frame in range(0, len(EMPTY_POSITIONS['hips_center']['x'])):

        # Iterate through each bone
        for bone in VIRTUAL_BONES:
            # Calculate the length of the bone for this frame
            head = VIRTUAL_BONES[bone]['head']
            tail = VIRTUAL_BONES[bone]['tail']
            head_pos = (
                EMPTY_POSITIONS[head]['x'][frame], EMPTY_POSITIONS[head]['y'][frame], EMPTY_POSITIONS[head]['z'][frame])
            tail_pos = (
                EMPTY_POSITIONS[tail]['x'][frame], EMPTY_POSITIONS[tail]['y'][frame], EMPTY_POSITIONS[tail]['z'][frame])

            VIRTUAL_BONES[bone]['lengths'].append(m.dist(head_pos, tail_pos))

    # Update the length median and stdev values for each bone
    for bone in VIRTUAL_BONES:
        # Exclude posible length NaN (produced by an empty with NaN values as position) values from the median and standard deviation
        VIRTUAL_BONES[bone]['median'] = statistics.median(
            [length for length in VIRTUAL_BONES[bone]['lengths'] if not m.isnan(length)])
        # virtual_bones[bone]['median'] = statistics.median(virtual_bones[bone]['lengths'])
        VIRTUAL_BONES[bone]['stdev'] = statistics.stdev(
            [length for length in VIRTUAL_BONES[bone]['lengths'] if not m.isnan(length)])
        # virtual_bones[bone]['stdev'] = statistics.stdev(virtual_bones[bone]['lengths'])

    print('Virtual Bones Information update completed.')
