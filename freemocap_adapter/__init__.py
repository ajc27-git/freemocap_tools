import logging

from freemocap_adapter.user_interface.setup.register import register

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

if __name__ == "__main__":
    logger.info(f"Running {__file__} as main file ")
    register()
