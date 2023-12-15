import bpy
from dataclasses import dataclass

from ajc27_freemocap_blender_addon.core_functions.materials.create_checkerboard_material import \
    create_checkerboard_material


@dataclass
class ground_planeConfig:
    size: float = 10
    square_scale: float = 100
    base_color: tuple = (0.5, 0.5, 0.5, 1)
    roughness: float = 0.5
    metallic: float = 0.0
    noise_scale: float = 0.5


def create_ground_plane(config: ground_planeConfig):
    # Create a plane object
    bpy.ops.mesh.primitive_plane_add(size=config.size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    ground_plane_mesh = bpy.context.object
    ground_plane_mesh.name = "ground_plane"
    
    ground_plane_material = create_checkerboard_material(name="ground_plane_material",
                                                        base_color=config.base_color,
                                                        roughness=config.roughness,
                                                        metallic=config.metallic,
                                                        noise_scale=config.noise_scale)
    
    ground_plane_mesh.active_material = ground_plane_material
    ground_plane_mesh.data.materials.append(ground_plane_material)


if __name__ == '__main__':
    create_ground_plane(ground_planeConfig())