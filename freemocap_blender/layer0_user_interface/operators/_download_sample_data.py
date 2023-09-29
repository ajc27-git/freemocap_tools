import logging

import bpy
import bpy_extras

logger = logging.getLogger(__name__)


class FREEMOCAP_ADAPTER_download_sample_data(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'freemocap_blender._download_sample_data'
    bl_label = "Download Sample Data"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        logger.info("Downloading sample data....")
        download_sample_data()
        return {'FINISHED'}
