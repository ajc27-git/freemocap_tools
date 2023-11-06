import bpy

from ajc27_freemocap_blender_addon.core_functions.meshes.center_of_mass.center_of_mass_material import create_center_of_mass_material


def create_center_of_mass_mesh(parent_object: bpy.types.Object,
                             center_of_mass_empty: bpy.types.Object):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, enter_editmode=False,
                                         align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    mesh = bpy.context.active_object
    mesh.name = "center_of_mass_mesh"
    mesh.parent = parent_object
    mesh.parent = center_of_mass_empty
    location_constraint = mesh.constraints.new(type="COPY_LOCATION")
    location_constraint.target = center_of_mass_empty

    material = create_center_of_mass_material()

    mesh.active_material = material
    mesh.data.materials.append(material)
