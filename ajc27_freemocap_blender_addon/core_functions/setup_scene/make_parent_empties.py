import bpy

def create_parent_empty(name: str,
                        type: str,
                        scale: tuple = (1.0, 1.0, 1.0),
                        parent_object: bpy.types.Object = None):
    print("Creating freemocap parent empty...")
    bpy.ops.object.empty_add(type=type)
    parent_empty = bpy.context.active_object
    parent_empty.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parent_empty.name = name
 

    if parent_object is not None:
        print(f"Setting parent of {parent_empty.name} to {parent_object.name}")
        parent_empty.parent = parent_object


    return parent_empty
