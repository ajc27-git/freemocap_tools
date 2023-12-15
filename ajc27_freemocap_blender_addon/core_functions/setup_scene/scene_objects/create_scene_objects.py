from ajc27_freemocap_blender_addon.core_functions.setup_scene.scene_objects.cameras.create_cameras import create_cameras
from ajc27_freemocap_blender_addon.core_functions.setup_scene.scene_objects.ground_plane.create_ground_plane import \
    create_ground_plane
from ajc27_freemocap_blender_addon.core_functions.setup_scene.scene_objects.lights.create_lights import create_lights


def create_scene_objects():
    create_cameras()
    create_lights()
    create_ground_plane()


if __name__ == "__main__":
    create_scene_objects()