import logging
from typing import Dict

import numpy as np
from numpy.linalg import svd

from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler

logger = logging.getLogger(__name__)

def estimate_good_clean_frame(freemocap_data_handler: FreemocapDataHandler) -> int:

    lowest_trajectories = get_lowest_body_trajectories(freemocap_data_handler)
    good_clean_frame_index = get_frame_with_lowest_velocity(lowest_trajectories)
    logger.info(f"Good clean frame index: {good_clean_frame_index}")
    return good_clean_frame_index


def get_frame_with_lowest_velocity(trajectories: Dict[str, np.ndarray]) -> int:
    """
    trajectories: Dict[str, np.ndarray] (number_of_frames, number_of_dimensions[x,y,z])

    Returns the frame number where all trajectories are visible and have the lowest velocity.
    """
    # Initialize list to store total velocity of each frame
    frame_velocities = []

    # Number of frames
    number_of_frames = next(iter(trajectories.values())).shape[0]

    for frame in range(number_of_frames):
        velocities = []
        all_visible = True

        for trajectory_name, trajectory in trajectories.items():
            # Check if trajectory is visible in this frame
            if np.isnan(trajectory[frame]).any():
                all_visible = False
                break

            # Calculate velocity if this is not the last frame
            if frame < number_of_frames - 1:
                velocity = np.linalg.norm(trajectory[frame+1] - trajectory[frame])
                velocities.append(velocity)

        # If all trajectories are visible in this frame, calculate total velocity
        if all_visible and velocities:
            total_velocity = sum(velocities)
            frame_velocities.append(total_velocity)
        else:
            frame_velocities.append(float('inf'))

    # Return the frame with the lowest total velocity
    return int(np.argmin(frame_velocities))


def get_low_velocity_points(trajectories: Dict[str, np.ndarray],
                            percentile: float) -> np.ndarray:
    """
    trajectories: Dict[str, np.ndarray] (number_of_frames, number_of_dimensions[x,y,z])
    percentile: float (0.0, 1.0) - the percentile of velocity to use as a cutoff
    """
    points = []
    velocities = []

    for trajectory_name, trajectory in trajectories.items():
        if trajectory.shape[0] < 2:
            raise Exception(f"Trajectory {trajectory_name} has less than 2 points. Cannot calculate velocity.")
        if np.isnan(trajectory).all():
            logger.warning(f"Trajectory {trajectory_name} is all nan. Cannot calculate velocity.")
            continue
        if trajectory.shape[1] != 3:
            raise Exception(
                f"Trajectory {trajectory_name} has {trajectory.shape[1]} dimensions (should be 3). Cannot calculate velocity.")

        velocity = np.linalg.norm(np.diff(trajectory, axis=0), axis=-1)
        points.extend(trajectory[:-1])
        velocities.extend(velocity)

    # Convert lists to numpy arrays
    points = np.array(points)
    velocities = np.array(velocities)

    # Sort points by velocity
    sorted_indices = np.argsort(velocities)
    points = points[sorted_indices]

    number_of_lowest_points = int(len(points) * percentile)
    logger.info(f"Getting {number_of_lowest_points} lowest velocity points from trajectories...")

    lowest_velocity_points = points[:number_of_lowest_points]
    return lowest_velocity_points


def get_plane_definition_from_points(points: np.ndarray) -> Dict[str, np.ndarray]:
    """
    points: np.ndarray (number_of_points, number_of_dimensions[x,y,z])

    Fit a plane to the points

    :return: Dict[str, np.ndarray] - {"center": np.ndarray (number_of_dimensions[x,y,z]),
                                      "normal": np.ndarray (number_of_dimensions[x,y,z])}
    """
    logger.info("Finding a plane that passes through the provided points.")
    # https://stackoverflow.com/questions/12299540/plane-fitting-to-4-or-more-xyz-points

    assert points.shape[0] >= 3, "At least 3 points are required to define a plane."
    center = points.mean(axis=0)
    x = points - center  # Shift points to be relative to center
    M = np.cov(x.T)  # Covariance matrix
    _, _, Vh = np.linalg.svd(M)  # Singular Value Decomposition
    normal = Vh[0]  # The normal of the plane is the first row of Vh
    return {"center": center,
            "normal": normal}


def put_freemocap_data_into_inertial_reference_frame(
        freemocap_data_handler: FreemocapDataHandler) -> FreemocapDataHandler:
    logger.info(
        "Putting freemocap data in inertial reference frame...\n freemocap_data(before):\n{freemocap_data_handler}")
    lowest_trajectories = get_lowest_body_trajectories(freemocap_data_handler)

    lowest_slowest_points = get_low_velocity_points(trajectories=lowest_trajectories,
                                                    percentile=0.25)
    freemocap_data_handler.add_metadata({"slow_points": lowest_slowest_points})

    ground_plane_definition = get_plane_definition_from_points(points=lowest_slowest_points)

    freemocap_data_handler.add_metadata({"unrotated_ground_plane_definition": ground_plane_definition})

    # freemocap_data_handler.translate_by(-ground_plane_definition["center"])
    # freemocap_data_handler.mark_processing_stage("translated_to_origin")

    # rotation_matrix = find_rotation_matrix_to_put_groundplane_at_z_equal_zero(ground_plane_definition)

    # for trajectory_name, trajectory in freemocap_data_handler.trajectories.items():
    #     freemocap_data_handler.trajectories[trajectory_name] = rotation_matrix @ trajectory.T
    
    # freemocap_data_handler.mark_processing_stage("inertial_reference_frame")

    logger.success(
        "Finished putting freemocap data in inertial reference frame.\n freemocap_data(after):\n{freemocap_data_handler}")
    return freemocap_data_handler


def find_rotation_matrix_to_put_groundplane_at_z_equal_zero(ground_plane_definition: Dict[str, np.ndarray]):
    # Validate input
    validate_groundplane_definition(ground_plane_definition)

    # Compute normalized vector
    ground_plane_normal_zeroed = ground_plane_definition["normal"] - ground_plane_definition["center"]
    ground_plane_normal_zeroed_normalized = ground_plane_normal_zeroed / np.linalg.norm(ground_plane_normal_zeroed)

    # Define z-axis
    z_axis = np.array([0, 0, 1])

    # Compute rotation axis and angle
    rotation_axis = np.cross(ground_plane_normal_zeroed_normalized, z_axis)
    rotation_axis_normalized = rotation_axis / np.linalg.norm(rotation_axis)
    rotation_angle = np.arccos(np.dot(ground_plane_normal_zeroed_normalized, z_axis))

    # Define elements for easier access
    u_x, u_y, u_z = rotation_axis_normalized
    cos_theta = np.cos(rotation_angle)
    sin_theta = np.sin(rotation_angle)

    # Compute rotation matrix
    rotation_matrix = np.array([
        [cos_theta + u_x**2 * (1 - cos_theta), u_x*u_y*(1 - cos_theta) - u_z*sin_theta, u_x*u_z*(1 - cos_theta) + u_y*sin_theta],
        [u_y*u_x*(1 - cos_theta) + u_z*sin_theta, cos_theta + u_y**2 * (1 - cos_theta), u_y*u_z*(1 - cos_theta) - u_x*sin_theta],
        [u_z*u_x*(1 - cos_theta) - u_y*sin_theta, u_z*u_y*(1 - cos_theta) + u_x*sin_theta, cos_theta + u_z**2 * (1 - cos_theta)]
    ])

    return rotation_matrix


def validate_groundplane_definition(ground_plane_definition):
    if isinstance(ground_plane_definition["normal"], list):
        ground_plane_definition["normal"] = np.array(ground_plane_definition["normal"])
    if isinstance(ground_plane_definition["center"], list):
        ground_plane_definition["center"] = np.array(ground_plane_definition["center"])
    if ground_plane_definition["normal"].shape != (3,):
        raise Exception(
            f"ground_plane_definition['normal'] has shape {ground_plane_definition['normal'].shape} (should be (3,)).")
    if ground_plane_definition["center"].shape != (3,):
        raise Exception(
            f"ground_plane_definition['center'] has shape {ground_plane_definition['center'].shape} (should be (3,)).")


def get_lowest_body_trajectories(freemocap_data_handler) -> Dict[str, np.ndarray]:
    body_names = freemocap_data_handler.body_names

    # checking for markers from the ground up!
    trajectory_parts = [
        ("feet", ["right_heel", "left_heel", "right_foot_index", "left_foot_index"]),
        ("ankle", ["right_ankle", "left_ankle"]),
        ("knee", ["right_knee", "left_knee"]),
        ("hip", ["right_hip", "left_hip"]),
        ("shoulder", ["right_shoulder", "left_shoulder"]),
        ("head", ["nose", "right_eye_inner", "right_eye",
                  "right_eye_outer", "left_eye_inner",
                  "left_eye", "left_eye_outer",
                  "right_ear", "left_ear",
                  "mouth_right", "mouth_left"]),
    ]

    for part_name, part_list in trajectory_parts:
        if all([part in body_names for part in part_list]):
            logger.debug(f"Trying to use {part_name} trajectories to define ground plane.")
            part_trajectories = freemocap_data_handler.get_trajectories(part_list)

            for trajectory_name, trajectory in part_trajectories.items():
                if np.isnan(trajectory).all():
                    logger.warning(f"Trajectory {trajectory_name} is all nan. Removing from lowest body trajectories.")
                    del part_trajectories[trajectory_name]

            if len(part_trajectories) < 2:
                logger.debug(f"Found less than 2 {part_name} trajectories. Trying next part..")
            else:
                logger.info(f"Found {part_name} trajectories. Using {part_name} as lowest body trajectories.")
                return part_trajectories

    logger.error(f"Found less than 2 head trajectories. Cannot find lowest body trajectories!")
    raise Exception("Cannot find lowest body trajectories!")
