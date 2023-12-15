import bpy
from dataclasses import dataclass

from ajc27_freemocap_blender_addon.core_functions.materials.create_checkerboard_material import \
    create_checkerboard_material


@dataclass
class GroundplaneConfig:
    size: float = 10
    square_scale: float = 100
    base_color: tuple = (0.5, 0.5, 0.5, 1)
    roughness: float = 0.5
    metallic: float = 0.0
    noise_scale: float = 0.5


def create_groundplane_with_config(config: GroundplaneConfig):
    # Create a plane object
    bpy.ops.mesh.primitive_plane_add(size=config.size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    groundplane_mesh = bpy.context.object
    groundplane_mesh.name = "groundplane"
    
    groundplane_material = create_checkerboard_material(name="groundplane_material",
                                                        base_color=config.base_color,
                                                        roughness=config.roughness,
                                                        metallic=config.metallic,
                                                        noise_scale=config.noise_scale)
    
    groundplane_mesh.active_material = groundplane_material
    groundplane_mesh.data.materials.append(groundplane_material)


if __name__ == '__main__':
    create_groundplane_with_config(GroundplaneConfig())