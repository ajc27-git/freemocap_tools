import bpy 




def create_material_for_mesh():
    material = bpy.data.materials.new('')
    material.name = "center_of_mass_material"
    material.use_nodes = True
    return material


def create_checker_texture(material):
   nodes = material.node_tree.nodes
   nodes.remove(nodes.get('Principled BSDF'))
   checker_node = nodes.new(type='ShaderNodeTexChecker')

   checker_node.inputs[1].default_value = (0, .5, 1, 1) # color1
   checker_node.inputs[2].default_value = (1, 0, 1, 1)  # color2
   checker_node.inputs[3].default_value = 2.0  # scale

   return nodes, checker_node


def create_bsdf_and_output_nodes(nodes):
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    output_node = nodes.get('Material Output')
    return bsdf_node, output_node

def create_center_of_mass_material():
    material = create_material_for_mesh()
    nodes, checker_node = create_checker_texture(material)
    bsdf_node, output_node = create_bsdf_and_output_nodes(nodes)
    # Connect the Checker Texture node to the BSDF
    material.node_tree.links.new(bsdf_node.inputs['Base Color'], checker_node.outputs['Color'])
    # Connect the BSDF to the output
    material.node_tree.links.new(output_node.inputs['Surface'], bsdf_node.outputs['BSDF'])
    return material
