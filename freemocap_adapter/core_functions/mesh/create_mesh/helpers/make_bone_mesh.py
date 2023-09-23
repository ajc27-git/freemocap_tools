import bmesh
import bpy
import numpy as np

from freemocap_adapter.core_functions.mesh.create_mesh.helpers.create_material import create_material


def make_cone_mesh(name: str = "cone_mesh",
                   color: str = "#00FFFF",
                   emission_strength: float = 1.0,
                   transmittance: float = 0.0,
                   vertices: int = 8,
                   radius1: float = 0.1,
                   radius2: float = 0.05,
                   depth: float = 2,
                   end_fill_type: str = 'TRIFAN',
                   align: str = 'WORLD',
                   location: tuple = (0, 0, 0),
                   scale: tuple = (1, 1, 1)):
    bpy.context.scene.cursor.location = (0, 0, 0)

    # define cone object
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,
                                    radius1=radius1,
                                    radius2=radius2,
                                    depth=depth,
                                    end_fill_type=end_fill_type,
                                    align=align,
                                    location=location,
                                    scale=scale)

    cone = bpy.context.active_object
    cone.name = name

    material = create_material(
        color=color,
        name=name,
        emission_strength=emission_strength,
        transmittance=transmittance,
    )

    cone_object = bpy.data.objects[name]
    cone_mesh = cone_object.data

    # Go into edit mode
    bpy.context.view_layer.objects.active = cone_object
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all vertices
    bm = bmesh.from_edit_mesh(cone_mesh)
    bm.select_mode = {'VERT'}
    bpy.ops.mesh.select_all(action='DESELECT')

    bm.verts.ensure_lookup_table()  # This is important to access vertices by index
    # Select the vertex you want to move the cursor to (i.e. center of the cone base)
    for vertex in bm.verts:
        print(vertex.index, vertex.co)
        x = vertex.co.x
        y = vertex.co.y
        z = vertex.co.z
        if np.allclose(x, 0) and np.allclose(y, 0) and z < 0:
            vertex.select = True
            break

    bpy.context.scene.cursor.location = bpy.context.object.matrix_world @ vertex.co

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    cone.location = (0, 0, 0)
    bpy.context.scene.cursor.location = (0, 0, 0)

    return cone


def make_joint_sphere_mesh(name: str = "joint_sphere_mesh",
                           subdivisions: int = 2,
                           radius: float = 0.3,
                           align: str = 'WORLD',
                           location: tuple = (0, 0, 0),
                           scale: tuple = (1, 1, 1)
                           ):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions,
                                          radius=radius,
                                          align=align,
                                          location=location,
                                          scale=scale)
    joint_sphere = bpy.context.active_object
    joint_sphere.name = name
    return joint_sphere


def make_bone_mesh(name: str = "bone_mesh"):
    cone = make_cone_mesh(name=f"{name}_cone_mesh")
    joint_sphere = make_joint_sphere_mesh(name=f"{name}_joint_sphere_mesh")
    bpy.ops.object.select_all(action='DESELECT')
    cone.select_set(True)
    joint_sphere.select_set(True)
    bpy.context.view_layer.objects.active = cone
    bpy.ops.object.join()
    bone_mesh = bpy.context.active_object
    bone_mesh.name = name
    return bone_mesh


if __name__ == "__main__" or __name__ == "<run_path>":
    make_bone_mesh()
