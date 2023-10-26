<<<<<<<< HEAD:ajc_freemocap_blender_addon/blender_interface/utilities/get_or_create_freemocap_data_handler.py
from ajc27_freemocap_blender_addon.core_functions.freemocap_data_handler.handler import FreemocapDataHandler
========
from ..handler import FreemocapDataHandler
>>>>>>>> origin/main:ajc_freemocap_blender_addon/core_functions/freemocap_data_handler/helpers/get_or_create_freemocap_data_handler.py

FREEMOCAP_DATA_HANDLER = None


def get_or_create_freemocap_data_handler(recording_path: str):
    global FREEMOCAP_DATA_HANDLER
    if FREEMOCAP_DATA_HANDLER is None:
        FREEMOCAP_DATA_HANDLER = FreemocapDataHandler.from_recording_path(recording_path=recording_path)
    return FREEMOCAP_DATA_HANDLER


def create_freemocap_data_handler(recording_path: str):
    global FREEMOCAP_DATA_HANDLER
    FREEMOCAP_DATA_HANDLER = FreemocapDataHandler.from_recording_path(recording_path=recording_path)
    return FREEMOCAP_DATA_HANDLER
