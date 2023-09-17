from typing import Union, Tuple, List

import bpy

def create_material(
    name: str = "Generic",
    color: Union[str, Tuple, List] = "#00FFFF",
    emission_strength: float = 1.0,
):
    """
    Create a material with the given name and color, with a strong emission.

    :param name: The name of the material.
    :param color: The color of the material, in hex format.
    :return: The created material.
    """
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear all nodes to start clean
    nodes.clear()

    # Create necessary nodes
    output = nodes.new(type="ShaderNodeOutputMaterial")
    emission = nodes.new(type="ShaderNodeEmission")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    mix = nodes.new(type="ShaderNodeMixShader")

    # Set the locations
    output.location = (300, 0)
    mix.location = (100, 0)
    bsdf.location = (-100, 50)
    emission.location = (-100, -50)

    # Set node links
    links.new(output.inputs[0], mix.outputs[0])
    links.new(mix.inputs[1], bsdf.outputs[0])
    links.new(mix.inputs[2], emission.outputs[0])

    # Convert color from hex to RGB
    if isinstance(color, str) and color.startswith("#"):
        color_rgb = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]  # skips the "#" and separates R, G, and B
    elif isinstance(color, list) or isinstance(color, tuple):
        color_rgb = color

    # Set the colors
    bsdf.inputs[0].default_value = (*color_rgb, 1)
    emission.inputs[0].default_value = (*color_rgb, 1)  # RGB + Alpha

    # Set the strength of the emission
    emission.inputs[1].default_value = emission_strength  # The higher this value, the more the material will glow

    return material
