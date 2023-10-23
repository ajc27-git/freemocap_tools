from .main_view3d_panel import VIEW3D_PT_freemocap_adapter
from .operators import BLENDER_OPERATORS
from .properties import FMC_ADAPTER_PROPERTIES

BLENDER_USER_INTERFACE_CLASSES = [FMC_ADAPTER_PROPERTIES,
                                  VIEW3D_PT_freemocap_adapter,
                                  *BLENDER_OPERATORS,
                                  ]
