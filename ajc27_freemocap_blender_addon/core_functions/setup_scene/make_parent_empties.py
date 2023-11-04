import logging

import bpy

import sys


def create_freemocap_parent_empty(name: str = "freemocap_data_parent_empty",
                                  parent_object: bpy.types.Object = None):
    print("Creating freemocap parent empty...")
    bpy.ops.object.empty_add(type="ARROWS")
    parent_empty = bpy.context.active_object
    parent_empty.name = name

    if parent_object is not None:
        print(f"Setting parent of {parent_empty.name} to {parent_object.name}")
        parent_empty.parent = parent_object

    return parent_empty


def create_video_parent_empty(name: str = "video_parent_empty"):
    print("Creating video parent empty...")
    bpy.ops.object.empty_add()
    parent_empty = bpy.context.editable_objects[-1]
    parent_empty.name = name
    parent_empty.scale = (1, 1, 1)
    return parent_empty
