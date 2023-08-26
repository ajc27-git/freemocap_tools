import bpy

def translate_empty(empties_dict, empty, frame_index, delta):
    try:
        # Translate the empty in the animation location curve
        actual_x = bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty].animation_data.action.fcurves[0].keyframe_points[frame_index].co[1] = actual_x + delta[
            0]
        actual_y = bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty].animation_data.action.fcurves[1].keyframe_points[frame_index].co[1] = actual_y + delta[
            1]
        actual_z = bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1]
        bpy.data.objects[empty].animation_data.action.fcurves[2].keyframe_points[frame_index].co[1] = actual_z + delta[
            2]
    except:
        # Empty does not exist or does not have animation data
        # print('Empty ' + empty + ' does not have animation data on frame ' + str(frame_index))
        pass

    # If empty has children then call this function for every child
    if empty in empties_dict:
        for child in empties_dict[empty]['children']:
            translate_empty(empties_dict, child, frame_index, delta)
