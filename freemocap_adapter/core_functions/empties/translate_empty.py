import logging
from typing import Dict, List

import bpy

logger = logging.getLogger(__name__)


def translate_empty_and_its_children(empties_hierarchy: Dict[str, Dict[str, List[str]]],
                                     empty_name: str,
                                     frame_index: int,
                                     delta: float):
    try:
        # Translate the empty in the animation location curve
        actual_x = bpy.data.objects[empty_name].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty_name].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1] = actual_x + \
                                                                                                           delta[
                                                                                                               0]
        actual_y = bpy.data.objects[empty_name].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty_name].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1] = actual_y + \
                                                                                                           delta[
                                                                                                               1]
        actual_z = bpy.data.objects[empty_name].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty_name].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1] = actual_z + \
                                                                                                           delta[
                                                                                                               2]
    except:
        # Empty does not exist or does not have animation data
        # print('Empty ' + empty + ' does not have animation data on frame ' + str(frame_index))
        pass

    # If empty has children then call this function for every child
    if empty_name in empties_hierarchy:
        for child in empties_hierarchy[empty_name]['children']:
            translate_empty_and_its_children(empties_hierarchy=empties_hierarchy,
                                             empty_name=child,
                                             frame_index=frame_index,
                                             delta=delta)
