import logging

import bpy

from freemocap_blender.layer1_core_functions.main_controller import MainController
from freemocap_blender.layer2_data_models.parameter_models.load_parameters_config import load_default_parameters_config

logger = logging.getLogger(__name__)


class FREEMOCAP_ADAPTER_run_all(bpy.types.Operator):
    bl_idname = 'freemocap_adapter._run_all'
    bl_label = "Run All"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        freemocap_adapter_tool = context.scene.freemocap_data_properties
        recording_path = freemocap_adapter_tool.recording_path
        if recording_path == "":
            logger.error("No recording path specified")
            return {'CANCELLED'}
        config = load_default_parameters_config()
        try:
            logger.info(f"Executing `main_contoller.run_all() with config:{config}")
            controller = MainController(recording_path=recording_path,
                                        config=config)
            controller.run_all()
        except Exception as e:
            logger.error(f"Failed to run main_controller.run_all() with config:{config}: `{e}`")
            logger.exception(e)
            return {'CANCELLED'}
        return {'FINISHED'}
