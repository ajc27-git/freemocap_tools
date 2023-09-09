import logging

from freemocap_adapter.system.configure_logging.configure_logging import configure_logging, LogLevel

DEBUG_UI = False

configure_logging(LogLevel.TRACE)
# configure_logging(LogLevel.DEBUG)
# configure_logging(LogLevel.INFO)
# configure_logging(LogLevel.WARNING)

logger = logging.getLogger(__name__)


#######################################################################
### Add-on to adapt the Freemocap Blender output. It can adjust the
### empties position, add a rig and a body mesh. The resulting rig
### and animation can be imported in platforms like Unreal Engine.
### The rig has a TPose as rest pose for easier retargeting.
### For best results, when the script is ran the empties should be
### forming a standing still pose with arms open similar to A or T Pose

### The body_mesh.ply file should be in the same folder as the
### Blender file before manually opening it.
#######################################################################

bl_info = {
    'name': 'Freemocap Adapter',
    'author': 'ajc27',
    'version': (1, 1, 7),
    'blender': (3, 0, 0),
    'location': '3D Viewport > Sidebar > Freemocap Adapter',
    'description': 'Add-on to adapt the Freemocap Blender output',
    'category': 'Development',
}


def unregister():
    import bpy
    from freemocap_adapter.blender_user_interface import USER_INTERFACE_CLASSES

    logger.info(f"Unregistering {__file__} as add-on")
    for cls in USER_INTERFACE_CLASSES:
        logger.trace(f"Unregistering class {cls.__name__}")
        bpy.utils.unregister_class(cls)

    logger.info(f"Unregistering property group FMC_ADAPTER_PROPERTIES")
    del bpy.types.Scene.fmc_adapter_tool


def register():
    import bpy
    from freemocap_adapter.blender_user_interface import USER_INTERFACE_CLASSES, FMC_ADAPTER_PROPERTIES

    logger.info(f"Registering {__file__} as add-on")
    logger.debug(f"Registering classes {USER_INTERFACE_CLASSES}")
    for cls in USER_INTERFACE_CLASSES:
        logger.trace(f"Registering class {cls.__name__}")
        bpy.utils.register_class(cls)

    logger.info(f"Registering property group FMC_ADAPTER_PROPERTIES")
    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type=FMC_ADAPTER_PROPERTIES)


    try:
        from freemocap_adapter.core_functions.export.get_io_scene_fbx_addon import get_io_scene_fbx_addon
        get_io_scene_fbx_addon()
    except Exception as e:
        logger.error(f"Error loading io_scene_fbx addon: {str(e)}")
        raise

    logger.success(f"Finished registering {__file__} as add-on!")


if __name__ == "__main__":
    print("HHHHEEEEE")
    logger.info(f"Running {__file__} as main file ")
    register()
    logger.success(f"Finished running {__file__} as main file!")
