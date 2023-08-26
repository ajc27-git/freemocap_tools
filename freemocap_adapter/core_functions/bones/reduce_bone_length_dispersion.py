import math as m

import mathutils

from freemocap_adapter.core_functions.bones.update_virtual_bones import update_virtual_bones_info
from freemocap_adapter.core_functions.empties.empties import update_empty_positions, EMPTY_POSITIONS
from freemocap_adapter.core_functions.empties.translate_empty import translate_empty
from freemocap_adapter.data_models.empties_heirarchy import EMPTIES_HEIRARCHY
from freemocap_adapter.data_models.virtual_bones import VIRTUAL_BONES


def reduce_bone_length_dispersion(interval_variable: str = 'median', interval_factor: float = 0.01):
    # Update the empty positions dictionary
    update_empty_positions()

    # Update the information of the virtual bones
    update_virtual_bones_info()

    # Print the current bones length median, standard deviation and coefficient of variation
    print('Current Virtual Bone Information:')
    print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))

    for bone in VIRTUAL_BONES:
        # Get the statistic values
        current_median = VIRTUAL_BONES[bone]['median']
        current_stdev = VIRTUAL_BONES[bone]['stdev']
        current_cv = VIRTUAL_BONES[bone]['stdev'] / VIRTUAL_BONES[bone]['median']

        print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(current_median * 100 * 10000000) / 10000000),
                                                   str(m.trunc(current_stdev * 100 * 10000000) / 10000000),
                                                   str(m.trunc(current_cv * 100 * 10000) / 10000)))

    # Iterate through the lengths array of each bone and check if the length is outside the interval defined by x*stdev with x as a factor
    # If the bone length is outside the interval, adjust the coordinates of the tail empty and its children so the new bone length is at the border of the interval
    empties_positions_corrected = 0

    for bone in VIRTUAL_BONES:

        frame_index = 0

        for length in VIRTUAL_BONES[bone]['lengths']:

            # If the length is equal to nan (bone head or/and tail is nan) then continue with the next length
            if m.isnan(length):
                frame_index += 1
                continue

            # Get the bone median and stdev values
            median = VIRTUAL_BONES[bone]['median']
            stdev = VIRTUAL_BONES[bone]['stdev']

            # Calculate inferior and superior interval limit depending on interval variable
            if interval_variable == 'median':
                # Fix interval_factor to 1 in case is greater than 1
                if interval_factor > 1:
                    interval_factor = 1
                # Calculate limits
                inferior_limit = median * (1 - interval_factor)
                superior_limit = median * (1 + interval_factor)
            elif interval_variable == 'stdev':
                # Fix interval_factor to median/stdev in case is greater than median/stdev
                if interval_factor > (median / stdev):
                    interval_factor = median / stdev
                # Calculate limits
                inferior_limit = median - interval_factor * stdev
                superior_limit = median + interval_factor * stdev

            # Check if bone length is outside the interval
            if length < inferior_limit or length > superior_limit:
                head = VIRTUAL_BONES[bone]['head']
                tail = VIRTUAL_BONES[bone]['tail']
                # Get vector between the bone's tail and head empties
                head_position = mathutils.Vector(
                    [EMPTY_POSITIONS[head]['x'][frame_index], EMPTY_POSITIONS[head]['y'][frame_index],
                     EMPTY_POSITIONS[head]['z'][frame_index]])
                tail_position = mathutils.Vector(
                    [EMPTY_POSITIONS[tail]['x'][frame_index], EMPTY_POSITIONS[tail]['y'][frame_index],
                     EMPTY_POSITIONS[tail]['z'][frame_index]])
                bone_vector = tail_position - head_position
                # Get the new bone length depending of the actual length value (interval inferior or superior limit)
                new_length = inferior_limit if length < inferior_limit else superior_limit
                # Get the normalized bone vector by dividing the bone_vector by its length
                bone_vector_norm = bone_vector / length
                # Get the tail position delta by multiplying the normalized bone vector by the substraction of new_length and length
                position_delta = bone_vector_norm * (new_length - length)
                # Translate the tail empty and its children by the position delta.
                translate_empty(EMPTIES_HEIRARCHY, tail, frame_index, position_delta)

                empties_positions_corrected += 1

            frame_index += 1

    # Update the empty positions dictionary
    update_empty_positions()

    # Update the information of the virtual bones
    update_virtual_bones_info()

    # Print the new bones length median, standard deviation and coefficient of variation
    print('New Virtual Bone Information:')
    print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
    for bone in VIRTUAL_BONES:
        # Get the statistic values
        new_median = VIRTUAL_BONES[bone]['median']
        new_stdev = VIRTUAL_BONES[bone]['stdev']
        new_cv = VIRTUAL_BONES[bone]['stdev'] / VIRTUAL_BONES[bone]['median']

        print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(new_median * 100 * 10000000) / 10000000),
                                                   str(m.trunc(new_stdev * 100 * 10000000) / 10000000),
                                                   str(m.trunc(new_cv * 100 * 10000) / 10000)))

    print('Total empties positions corrected: ' + str(empties_positions_corrected))
