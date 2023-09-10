from freemocap_adapter.user_interfaces.blender.operators import BLENDER_OPERATORS
from freemocap_adapter.user_interfaces.blender.properties import FMC_ADAPTER_PROPERTIES
from freemocap_adapter.user_interfaces.blender.view3d_panel import VIEW3D_PT_freemocap_adapter

BLENDER_USER_INTERFACE_CLASSES = [FMC_ADAPTER_PROPERTIES,
                                  VIEW3D_PT_freemocap_adapter,
                                  *BLENDER_OPERATORS,
                                  ]
