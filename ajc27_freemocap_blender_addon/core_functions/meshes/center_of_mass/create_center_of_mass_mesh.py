import numpy as np
import bpy

def create_center_of_mass_mesh(center_of_mass_xyz:np.ndarray,
                               center_of_mass_empty: bpy.types.Object):
    # Create a mesh object for the center of mass, with a default sphere mesh that is a sphere with radius .05 and a material that is a "checkboard" pattern with a scale of 2.0 and colors that are Blue and Yellow
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    center_of_mass_mesh = bpy.context.active_object
    center_of_mass_mesh.name = "center_of_mass_mesh"
    center_of_mass_mesh.data.name = "center_of_mass_mesh_data"
    center_of_mass_mesh.location = center_of_mass_xyz
    center_of_mass_mesh.parent = center_of_mass_empty

    # Create a material for the center of mass mesh
    bpy.ops.material.new(name="center_of_mass_material")
    material = bpy.data.materials["center_of_mass_material"]
    material.use_nodes = True
    # Get the material nodes
    nodes = material.node_tree.nodes
    # Remove the default 'Principled BSDF'
    nodes.remove(nodes['Principled BSDF'])
    # Create a new 'Checker Texture' node
    checker_node = nodes.new(type='ShaderNodeTexChecker')




