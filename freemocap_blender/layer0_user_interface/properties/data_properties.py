import logging

import bpy
from bpy.props import StringProperty, BoolProperty

logger = logging.getLogger(__name__)


class FREEMOCAP_DATA_PROPERTIES(bpy.types.PropertyGroup):
    logger.info("Initializing FREEMOCAP_ADAPTER_PROPERTIES class...")

    data_parent_empty: bpy.props.PointerProperty(
        name="FreeMoCap data parent empty",
        description="Empty that serves as parent for all the freemocap empties",
        type=bpy.types.Object,
        poll=lambda self, object: object.type == 'EMPTY',
    )

    recording_path: StringProperty(
        name="FreeMoCap recording path",
        description="Path to a freemocap recording",
        default="",
        subtype='FILE_PATH',
    )

