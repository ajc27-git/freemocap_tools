import logging

import bpy

from freemocap_adapter.system.configure_logging import configure_logging
from freemocap_adapter.user_interface import USER_INTERFACE_CLASSES, FMC_ADAPTER_PROPERTIES

configure_logging()

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
    logger.info(f"Unregistering {__file__} as add-on")
    for cls in USER_INTERFACE_CLASSES:
        logger.info(f"Unregistering class {cls.__name__}")
        bpy.utils.unregister_class(cls)

    logger.info(f"Unregistering property group FMC_ADAPTER_PROPERTIES")
    del bpy.types.Scene.fmc_adapter_tool


def register():
    logger.info(f"Registering {__file__} as add-on")
    for cls in USER_INTERFACE_CLASSES:
        logger.info(f"Registering class {cls.__name__}")
        bpy.utils.register_class(cls)

    logger.info(f"Registering property group FMC_ADAPTER_PROPERTIES")
    bpy.types.Scene.fmc_adapter_tool = bpy.props.PointerProperty(type=FMC_ADAPTER_PROPERTIES)

    logger.info(f"Finished registering {__file__} as add-on!")


if __name__ == "__main__":
    print("HHHHEEEEE")
    logger.info(f"Running {__file__} as main file ")
    register()
