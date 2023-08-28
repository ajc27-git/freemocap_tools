import logging
import bpy
import bpy_extras

from freemocap_adapter.core_functions.load_data.load_freemocap_data import load_freemocap_data

logger = logging.getLogger(__name__)

class FMC_ADAPTER_load_freemocap_data(bpy.types.Operator):#, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'fmc_adapter.load_freemocap_data'
    bl_label = "Load FreeMoCap Data"

    def execute(self, context):
        logger.info("Loading data....")
        scene = context.scene
        fmc_adapter_tool = scene.fmc_adapter_tool

        # if fmc_adapter_tool.recording_path == "":
        #     load_freemocap_data(recording_path=self.filepath)
        # else:

        load_freemocap_data(recording_path=fmc_adapter_tool.recording_path)
        return {'FINISHED'}



