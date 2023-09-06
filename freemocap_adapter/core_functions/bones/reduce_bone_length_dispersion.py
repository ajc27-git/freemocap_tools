import math as m
from typing import Dict, Any

import bpy
import mathutils

from freemocap_adapter.core_functions.bones.calculate_bone_length_statistics import calculate_bone_length_statistics
from freemocap_adapter.core_functions.empties.translate_empty import translate_empty_and_its_children
from freemocap_adapter.core_functions.empties.update_empty_positions import get_empty_positions
from freemocap_adapter.data_models.mediapipe_names.empties_heirarchy import MEDIAPIPE_EMPTIES_HEIRARCHY

import logging
logger = logging.getLogger(__name__)

def reduce_bone_length_dispersion(empties: Dict[str, bpy.types.Object],
                                  bones: Dict[str, Dict[str, Any]],
                                  interval_variable: str = 'median',
                                  interval_factor: float = 0.01):
    # Update the empty positions dictionary
    empty_positions = get_empty_positions(empties=empties)

    # Update the information of the virtual bones
    bones = calculate_bone_length_statistics(empty_positions=empty_positions, bones=bones)

    # Print the current bones length median, standard deviation and coefficient of variation
    print_virtual_bone_information()

    # Iterate through the lengths array of each bone and check if the length is outside the interval defined by x*stdev with x as a factor
    # If the bone length is outside the interval, adjust the coordinates of the tail empty and its children so the new bone length is at the border of the interval

    for bone in bones:
        logger.info(f"Reducing bone length dispersion for bone: {bone}...")
        for frame_index, original_length in enumerate(bone['lengths']):

            # If the length is equal to nan (bone head or/and tail is nan) then continue with the next length
            if m.isnan(original_length):
                continue

            # Get the bone median and stdev values
            median = bone['median']
            stdev = bone['stdev']

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
            if original_length < inferior_limit or original_length > superior_limit:
                head = bone['head']
                tail = bone['tail']
                # Get vector between the bone's tail and head empties
                head_position = mathutils.Vector(
                    [empty_positions[head]['x'][frame_index],
                     empty_positions[head]['y'][frame_index],
                     empty_positions[head]['z'][frame_index]])
                tail_position = mathutils.Vector(
                    [empty_positions[tail]['x'][frame_index],
                     empty_positions[tail]['y'][frame_index],
                     empty_positions[tail]['z'][frame_index]])
                bone_vector = tail_position - head_position

                # Get the new bone length depending of the actual length value (interval inferior or superior limit)
                new_length = inferior_limit if original_length < inferior_limit else superior_limit

                # Get the normalized bone vector by dividing the bone_vector by its length
                bone_vector_norm = bone_vector / original_length

                # Get the tail position delta by multiplying the normalized bone vector by the substraction of new_length and original_length
                position_delta = bone_vector_norm * (new_length - original_length)

                # Translate the tail empty and its children by the position delta.
                translate_empty_and_its_children(empties_hierarchy=MEDIAPIPE_EMPTIES_HEIRARCHY,
                                                 empty_name=tail,
                                                 frame_index=frame_index,
                                                 delta=position_delta)


    # Update the empty positions dictionary
    get_empty_positions(empties=empties)

    # Update the information of the virtual bones
    calculate_bone_length_statistics()

    # Print the new bones length median, standard deviation and coefficient of variation
    print('New Virtual Bone Information:')
    print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
    for bone in bones:
        # Get the statistic values
        new_median = bones[bone]['median']
        new_stdev = bones[bone]['stdev']
        new_cv = bones[bone]['stdev'] / bones[bone]['median']

        print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(new_median * 100 * 10000000) / 10000000),
                                                   str(m.trunc(new_stdev * 100 * 10000000) / 10000000),
                                                   str(m.trunc(new_cv * 100 * 10000) / 10000)))

    print('Total empties positions corrected: ' + str(empties_positions_corrected))


def print_virtual_bone_information(bones: Dict[str, Dict[str, Any]]):
    print('Current Virtual Bone Information:')
    print('{:<15} {:>12} {:>12} {:>12}'.format('BONE', 'MEDIAN (cm)', 'STDEV (cm)', 'CV (%)'))
    for bone in bones:
        # Get the statistic values
        current_median = bones[bone]['median']
        current_stdev = bones[bone]['stdev']
        current_cv = bones[bone]['stdev'] / bones[bone]['median']

        print('{:<15} {:>12} {:>12} {:>12}'.format(bone, str(m.trunc(current_median * 100 * 10000000) / 10000000),
                                                   str(m.trunc(current_stdev * 100 * 10000000) / 10000000),
                                                   str(m.trunc(current_cv * 100 * 10000) / 10000)))
