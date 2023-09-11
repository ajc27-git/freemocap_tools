import logging
from pathlib import Path
from typing import Union

from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler

logger = logging.getLogger(__name__)


def load_freemocap_data(
        recording_path: Union[str, Path],
) -> FreemocapDataHandler:
    logger.info(f"Loading freemocap_data from {recording_path}....")

    try:
        freemocap_data_handler = FreemocapDataHandler.from_recording_path(recording_path=recording_path)
        logger.info(f"Loaded freemocap_data from {recording_path} successfully: \n{freemocap_data_handler}")
    except Exception as e:
        logger.error(f"Failed to load freemocap freemocap_data: {e}")
        raise e

    try:
        logger.info("Calculating virtual trajectories....")
        freemocap_data_handler.calculate_virtual_trajectories()
    except Exception as e:
        logger.error(f"Failed to calculate virtual trajectories: {e}")
        logger.exception(e)
        raise e

    try:
        logger.info("Putting freemocap data in inertial reference frame....")
        freemocap_data_handler.put_data_in_inertial_reference_frame()
    except Exception as e:
        logger.error(f"Failed when trying to put freemocap data in inertial reference frame: {e}")
        logger.exception(e)
        raise e
    return freemocap_data_handler
