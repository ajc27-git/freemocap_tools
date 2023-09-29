from freemocap_blender.layer0_user_interface.main_view3d_panel import VIEW3D_PT_freemocap_panel
from freemocap_blender.layer0_user_interface.operators import BLENDER_OPERATORS
from freemocap_blender.layer0_user_interface.properties.data_properties import FREEMOCAP_DATA_PROPERTIES
from freemocap_blender.layer0_user_interface.properties.ui_properties import FREEMOCAP_UI_PROPERTIES

BLENDER_USER_INTERFACE_CLASSES = [FREEMOCAP_DATA_PROPERTIES,
                                  FREEMOCAP_UI_PROPERTIES,
                                  VIEW3D_PT_freemocap_panel,
                                  *BLENDER_OPERATORS,
                                  ]
