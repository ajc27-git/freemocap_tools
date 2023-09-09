import logging

from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

logger = logging.getLogger(__name__)


def load_freemocap_data(
        recording_path: str,
):
    logger.info("Loading freemocap_data....")

    try:
        freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)
        freemocap_data.mark_processing_stage("original_from_file")
        logger.info(f"Loaded freemocap_data from {recording_path} successfully: \n{freemocap_data}")
        logger.debug(str(freemocap_data))
        return freemocap_data
    except Exception as e:
        logger.info("Failed to load freemocap freemocap_data")
        raise e


