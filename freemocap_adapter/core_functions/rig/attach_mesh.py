import math as m
import bpy
import logging

logger = logging.getLogger(__name__)


def add_cylinder(name, radius, depth, cuts, loc, rot):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=loc,
        rotation=rot
    )
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=cuts)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.object.name = name


def add_sphere(name, radius, loc, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=loc,
        scale=scale
    )
    bpy.context.object.name = name


def join_objects(name):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[name]
    for obj in bpy.data.objects:
        if obj.name != name:
            obj.select_set(True)
    bpy.ops.object.join()


def parent_to_rig(child):
    rig = bpy.data.objects['rig']
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    child.select_set(True)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def import_mesh(filepath):
    try:
        bpy.ops.import_mesh.ply(filepath=filepath)
    except:
        logger.error("Could not find body mesh file")
        return

    body_mesh = bpy.context.object
    rig = bpy.data.objects['rig']

    # Scale imported mesh
    rig_scale = rig.dimensions.z
    mesh_scale = body_mesh.dimensions.z
    scale_factor = rig_scale / mesh_scale
    body_mesh.scale = (scale_factor, scale_factor, scale_factor)

    # Apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def add_mesh_to_rig(body_mesh_mode="custom"):
    logger.info("Adding body mesh to rig...")
    if body_mesh_mode == "file":
        logger.info("Importing body mesh from file...")
        import_mesh("body_mesh.ply")

    elif body_mesh_mode == "custom":
        logger.info("Creating body mesh from basic shapes...")
        # Add cylinders
        add_cylinder("trunk", 0.1, 1, 20, (0, 0, 0), (0, 0, 0))
        add_cylinder("neck", 0.05, 0.5, 20, (0, 0, 1), (0, 0, 0))
        add_cylinder("right_arm", 0.05, 0.5, 20, (1, 0, 0), (0, m.radians(90), 0))
        add_cylinder("left_arm", 0.05, 0.5, 20, (-1, 0, 0), (0, m.radians(90), 0))
        add_cylinder("right_leg", 0.05, 1, 20, (0.5, 0, 0), (0, 0, 0))
        add_cylinder("left_leg", 0.05, 1, 20, (-0.5, 0, 0), (0, 0, 0))

        # Add spheres
        add_sphere("head", 0.2, (0, 0, 1.5), (1, 1.2, 1.2))
        add_sphere("right_hand", 0.1, (1.5, 0, 0), (1.4, 0.8, 0.5))
        add_sphere("left_hand", 0.1, (-1.5, 0, 0), (1.4, 0.8, 0.5))
        add_sphere("right_foot", 0.05, (0.5, 0, -1), (1, 2.3, 1.2))
        add_sphere("left_foot", 0.05, (-0.5, 0, -1), (1, 2.3, 1.2))

        # Join objects
        join_objects("trunk")

        # Parent to rig
        parent_to_rig(bpy.data.objects["trunk"])

    else:
        raise ValueError("Invalid body mesh mode. Valid options are 'file' and 'custom'")