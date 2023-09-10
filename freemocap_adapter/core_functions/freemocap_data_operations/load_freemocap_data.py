import logging

from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler
from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

logger = logging.getLogger(__name__)


def load_freemocap_data(
        recording_path: str,
) -> FreemocapDataHandler:
    logger.info("Loading freemocap_data....")

    try:
        freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)
        logger.info(f"Loaded freemocap_data from {recording_path} successfully: \n{freemocap_data}")
        logger.debug(str(freemocap_data))
        freemocap_data_handler = FreemocapDataHandler(freemocap_data=freemocap_data)
        freemocap_data_handler.calculate_virtual_trajectories()
        return freemocap_data_handler
    except Exception as e:
        logger.error(f"Failed to load freemocap freemocap_data: {e}")
        raise e


