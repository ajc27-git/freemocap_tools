from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.helpers.put_freemocap_data_into_inertial_reference_frame import \
    get_lowest_body_trajectories, get_frame_with_lowest_velocity

import logging
logger = logging.getLogger(__name__)


def estimate_good_clean_frame(freemocap_data_handler: FreemocapDataHandler) -> int:

    lowest_trajectories = get_lowest_body_trajectories(freemocap_data_handler)
    good_clean_frame_index = get_frame_with_lowest_velocity(lowest_trajectories)
    logger.info(f"Good clean frame index: {good_clean_frame_index}")
    return good_clean_frame_index
