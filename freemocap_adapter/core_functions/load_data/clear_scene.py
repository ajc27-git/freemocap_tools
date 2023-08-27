def clear_scene():
    ###%% clear the scene - Scorch the earth \o/
    print("Clearing scene...")
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except:
        pass
    try:
        bpy.ops.object.select_all(action="SELECT")  # select all objects
        bpy.ops.object.delete(use_global=True)  # delete all objects from all scenes
    except:
        pass
