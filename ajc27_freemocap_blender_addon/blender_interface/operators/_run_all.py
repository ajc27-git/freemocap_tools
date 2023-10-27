import logging
from pathlib import Path

import bpy



import sys


class FMC_ADAPTER_run_all(bpy.types.Operator):
    bl_idname = 'fmc_adapter._run_all'
    bl_label = "Run All"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        from ...core_functions.main_controller import MainController
        from ...data_models.parameter_models.load_parameters_config import load_default_parameters_config
        fmc_adapter_tool = context.scene.fmc_adapter_properties
        recording_path = fmc_adapter_tool.recording_path
        if recording_path == "":
            print("No recording path specified")
            return {'CANCELLED'}
        config = load_default_parameters_config()
        try:
            print(f"Executing `main_contoller.run_all() with config:{config}")
            controller = MainController(recording_path=recording_path,
                                        save_path=str(Path(recording_path)/(Path(recording_path).stem+".blend")),
                                        config=config)
            controller.run_all()
        except Exception as e:
            print(f"Failed to run main_controller.run_all() with config:{config}: `{e}`")
            print(e)
            return {'CANCELLED'}
        return {'FINISHED'}


