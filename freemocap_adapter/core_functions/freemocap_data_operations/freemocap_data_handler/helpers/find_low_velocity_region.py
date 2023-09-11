import logging
from typing import Dict

import numpy as np

logger = logging.getLogger(__name__)


def find_low_velocity_region_around_frame(trajectories: Dict[str, np.ndarray],
                                          frame_number: int, ):
    velocities = {}
    for trajectory_name, trajectory in trajectories.items():
        velocities[trajectory_name] = np.diff(trajectory, axis=0)

    mean_velocities = np.mean(np.nanmean(np.array(list(velocities.values())), axis=0), axis=1)

    input_frame_velocity = mean_velocities[frame_number]

    low_velocity_indices = np.where(mean_velocities <= input_frame_velocity)[0]

    low_velocity_regions = []
    start_frame = low_velocity_indices[0]
    for index in range(1, len(low_velocity_indices)):
        if low_velocity_indices[index] != low_velocity_indices[index - 1] + 1:
            end_frame = low_velocity_indices[index - 1]
            low_velocity_regions.append((start_frame, end_frame))
            start_frame = low_velocity_indices[index]

    end_frame = low_velocity_indices[-1]
    low_velocity_regions.append((start_frame, end_frame))

    closest_region = min(low_velocity_regions, key=lambda region: min(abs(region[0]-frame_number), abs(region[1]-frame_number))) 

    mean_velocity_in_region = np.nanmean(mean_velocities[closest_region[0]:closest_region[1] + 1])

    logger.info(f"Found low velocity region closest to good frame: {closest_region}, mean velocity: {mean_velocity_in_region}")
    return closest_region