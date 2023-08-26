from freemocap_adapter import logger, USER_INTERFACE_CLASSES


def unregister():
    logger.info(f"Unregistering {__file__} as add-on")
    for cls in USER_INTERFACE_CLASSES:
        logger.info(f"Unregistering class {cls.__name__}")
        bpy.utils.unregister_class(cls)

    logger.info(f"Unregistering property group FMC_ADAPTER_PROPERTIES")
    del bpy.types.Scene.fmc_adapter_tool

if __name__ == "__main__":
    logger.info(f"Running {__file__} as main file ")
    unregister()