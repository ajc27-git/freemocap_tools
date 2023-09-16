import logging
import math as m
from copy import deepcopy
from typing import Dict, Any

from freemocap_adapter.core_functions.bones.calculate_bone_length_statistics import calculate_bone_length_statistics
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler
from freemocap_adapter.data_models.bones.bone_definitions import BONE_DEFINITIONS
from freemocap_adapter.data_models.mediapipe_names.mediapipe_heirarchy import MEDIAPIPE_HIERARCHY

logger = logging.getLogger(__name__)


def enforce_rigid_bones(freemocap_data_handler: FreemocapDataHandler,
                        bones: Dict[str, Dict[str, Any]] = BONE_DEFINITIONS):
    logger.info('Enforcing rigid bones - altering bone lengths to ensure they are the same length on each frame...')
    original_trajectories = freemocap_data_handler.trajectories
    updated_trajectories = deepcopy(original_trajectories)

    # Update the information of the virtual bones
    bones = calculate_bone_length_statistics(trajectories=original_trajectories, bones=bones)

    # Print the current bones length median, standard deviation and coefficient of variation
    log_bone_statistics(bones=bones, type='original')

    # Iterate through the lengths array of each bone and check if the length is outside the interval defined by x*stdev with x as a factor
    # If the bone length is outside the interval, adjust the coordinates of the tail empty and its children so the new bone length is at the border of the interval

    for name, bone in bones.items():
        logger.info(f"Reducing bone length dispersion for bone: {name}...")
        for frame_index, original_length in enumerate(bone['lengths']):

            # If the length is equal to nan (bone head or/and tail is nan) then continue with the next length
            if m.isnan(original_length):
                continue

            # Get the bone median and stdev values
            median_length = bone['median']

            # Make bone length match the median length

            head = bone['head']
            tail = bone['tail']
            # Get vector between the bone's tail and head empties
            head_position = original_trajectories[head][frame_index, :]
            tail_position = original_trajectories[tail][frame_index, :]
            bone_vector = tail_position - head_position

            # Get the normalized bone vector by dividing the bone_vector by its length
            bone_vector_norm = bone_vector / original_length

            # Get the tail position delta by multiplying the normalized bone vector by the substraction of new_length and original_length
            position_delta = bone_vector_norm * (median_length - original_length)

            def translate_trajectory_and_its_children(name: str):
                # recursively translate the tail empty and its children by the position delta.
                try:
                    logger.debug(f"Translating {name}...")

                    updated_trajectories[name][frame_index, :] = updated_trajectories[name][frame_index, :] + position_delta

                    if name in MEDIAPIPE_HIERARCHY.keys():
                        logger.debug(
                            f"Translating children of {name}: {MEDIAPIPE_HIERARCHY[name]['children']}")
                        for child_name in MEDIAPIPE_HIERARCHY[name]['children']:
                            translate_trajectory_and_its_children(name=child_name)
                            
                except Exception as e:
                    logger.error(f"Error while adjusting trajectory `{name}` and its children: {e}")
                    logger.exception(e)
                    raise Exception(f"Error while adjusting trajectory and its children: {e}")


            translate_trajectory_and_its_children(name=tail)

    # Update the information of the virtual bones
    updated_bones = calculate_bone_length_statistics(trajectories=updated_trajectories, bones=bones)

    # Print the current bones length median, standard deviation and coefficient of variation
    log_bone_statistics(bones=updated_bones, type='updated')

    for name, trajectory in updated_trajectories.items():
        freemocap_data_handler.set_trajectory(name=name, data=trajectory)

    freemocap_data_handler.mark_processing_stage(name='enforced_rigid_bones',
                                                 metadata={'bones': updated_bones,
                                                           'hierarchy': MEDIAPIPE_HIERARCHY},
                                                 )
    logger.success('Bone lengths enforced successfully!')
    return freemocap_data_handler



def log_bone_statistics(bones: Dict[str, Dict[str, Any]], type: str):
    log_string = f'\n\n[{type}] Bone Length Statistics:\n'
    header_string = f"{'BONE':<15} {'MEDIAN (cm)':>12} {'STDEV (cm)':>12} {'CV (%)':>12}"
    log_string += header_string + '\n'
    for name, bone in bones.items():
        # Get the statistic values
        median_string = str(round(bone['median'] * 100, 7))
        stdev_string = str(round(bone['stdev'] * 100, 7))
        cv_string = str(round(bone['stdev'] / bone['median'] * 100, 4))
        log_string += f"{name:<15} {median_string:>12} {stdev_string:>12} {cv_string:>12}\n"

    logger.info(log_string)