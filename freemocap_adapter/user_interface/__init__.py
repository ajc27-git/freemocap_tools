from freemocap_adapter.user_interface.operators.FMC_ADAPTER_OT_add_body_mesh import FMC_ADAPTER_OT_add_body_mesh
from freemocap_adapter.user_interface.operators.FMC_ADAPTER_OT_add_rig import FMC_ADAPTER_OT_add_rig
from freemocap_adapter.user_interface.operators.FMC_ADAPTER_OT_adjust_empties import FMC_ADAPTER_OT_adjust_empties
from freemocap_adapter.user_interface.operators.FMC_ADAPTER_OT_export_fbx import FMC_ADAPTER_OT_export_fbx
from freemocap_adapter.user_interface.operators.FMC_ADAPTER_OT_reduce_bone_length_dispersion import \
    FMC_ADAPTER_OT_reduce_bone_length_dispersion
from freemocap_adapter.user_interface.operators.FMC_ADAPTER_OT_reduce_shakiness import FMC_ADAPTER_OT_reduce_shakiness
from freemocap_adapter.user_interface.properties import FMC_ADAPTER_PROPERTIES
from freemocap_adapter.user_interface.view3d_panel import VIEW3D_PT_freemocap_adapter

USER_INTERFACE_CLASSES = [FMC_ADAPTER_PROPERTIES,
                          VIEW3D_PT_freemocap_adapter,
                          FMC_ADAPTER_OT_adjust_empties,
                          FMC_ADAPTER_OT_reduce_bone_length_dispersion,
                          FMC_ADAPTER_OT_reduce_shakiness,
                          FMC_ADAPTER_OT_add_rig,
                          FMC_ADAPTER_OT_add_body_mesh,
                          FMC_ADAPTER_OT_export_fbx
                          ]
