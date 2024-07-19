import bpy
# from freemocap_adapter.addon_interface import get_pose_items, update_menu
from .property_types import PropertyTypes

def update_menu(self, context, menu_name):
    if menu_name == 'armature':
        self.pose = get_pose_items(self, context)[0][0]

def get_pose_items(self, context):
    if self.armature == 'armature_freemocap':
        items = [('freemocap_tpose', 'FreeMoCap T-Pose', ''),
                ('freemocap_apose', 'FreeMoCap A-Pose', '')]
    elif self.armature == 'armature_ue_metahuman_simple':
        items = [('ue_metahuman_tpose', 'UE Metahuman T-Pose', ''),
                 ('ue_metahuman_default', 'UE Metahuman Default', '')]
    return items

class AddArmatureProperties(bpy.types.PropertyGroup):
    show_add_rig: PropertyTypes.Bool(
        description = 'Toggle Add Rig Options'
    ) # type: ignore
    add_rig_method: PropertyTypes.Enum(
        description = 'Method used to create the rig',
        items = [('bone_by_bone', 'Bone by Bone', ''),
                 ('using_rigify', 'Using Rigify', '')]
    ) # type: ignore
    armature: PropertyTypes.Enum(
        description = 'Armature that will be used to create the rig',
        items = [('armature_freemocap', 'FreeMoCap', ''),
                 ('armature_ue_metahuman_simple', 'UE Metahuman Simple', '')],
        update = lambda a,b: update_menu(a,
                                         b,
                                         'armature')
    ) # type: ignore
    pose: PropertyTypes.Enum(
        description = 'Pose that will be used to create the rig',
        items = get_pose_items,
    ) # type: ignore
    bone_length_method: PropertyTypes.Enum(
        description = 'Method use to calculate length of major bones',
        items = [('median_length', 'Median Length', '')]
    ) # type: ignore
    keep_symmetry: PropertyTypes.Bool(
        description = 'Keep right/left side symmetry (use average right/left '
                      'side bone length)'
    ) # type: ignore
    add_fingers_constraints: PropertyTypes.Bool(
        default = True,
        description = 'Add bone constraints for fingers'
    ) # type: ignore
    add_ik_constraints: PropertyTypes.Bool(
        description = 'Add IK constraints for arms and legs'
    ) # type: ignore
    ik_transition_threshold: PropertyTypes.Float(
        default = 0.9,
        min = 0,
        max = 1,
        precision = 2,
        description = 'Threshold of parallel degree (dot product) between '
                      'base and target ik vectors. It is used to transition '
                      'between vectors to determine the pole bone position'
    ) # type: ignore
    use_limit_rotation: PropertyTypes.Bool(
        description = 'Add rotation limits (human skeleton) to the bones '
                      'constraints (experimental)'
    ) # type: ignore
    clear_constraints: PropertyTypes.Bool(
        description = 'Clear added constraints after baking animation'
    ) # type: ignore
