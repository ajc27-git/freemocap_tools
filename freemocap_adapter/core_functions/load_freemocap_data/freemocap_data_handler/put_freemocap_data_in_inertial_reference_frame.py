from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData
import logging

logger = logging.getLogger(__name__)

def put_freemocap_data_in_inertial_reference_frame(freemocap_data: FreemocapData):
    logger.info("Putting freemocap data in inertial reference frame...\n freemocap_data(before):\n{freemocap_data}")



    logger.success("Finished putting freemocap data in inertial reference frame.")
