import logging

import bpy

from freemocap_adapter.user_interface import USER_INTERFACE_CLASSES
from freemocap_adapter.user_interface.properties import FMC_ADAPTER_PROPERTIES

logger = logging.getLogger(__name__)

def register():
    logger.info(f"Registering {__file__} as add-on")
    for cls in USER_INTERFACE_CLASSES:
        logger.info(f"Registering class {cls.__name__}")
        bpy.utils.register_class(cls)

    logger.info(f"Registering property group FMC_ADAPTER_PROPERTIES")
    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type=FMC_ADAPTER_PROPERTIES)

    logger.info(f"Finished registering {__file__} as add-on!")

if __name__ == "__main__":
    logger.info(f"Running {__file__} as main file ")
    register()