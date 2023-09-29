from freemocap_adapter.blender_interface.main_view3d_panel import VIEW3D_PT_freemocap_adapter
from freemocap_adapter.blender_interface.operators import BLENDER_OPERATORS
from freemocap_adapter.blender_interface.properties import FMC_DATA_PROPERTIES, FMC_UI_PROPERTIES

BLENDER_USER_INTERFACE_CLASSES = [FMC_DATA_PROPERTIES,
                                  FMC_UI_PROPERTIES,
                                  VIEW3D_PT_freemocap_adapter,
                                  *BLENDER_OPERATORS,
                                  ]
