import bpy
from .property_types import PropertyTypes

class AdjustEmptiesProperties(bpy.types.PropertyGroup):
    show_adjust_empties: PropertyTypes.Bool(
        # name='',
        # default=False,
        description='Toggle Adjust Empties Options'
    ) # type: ignore
    vertical_align_reference: PropertyTypes.Enum(
        # name='',
        description='Empty that serves as reference to align the z axis',
        items=[
            ('left_knee', 'left_knee', ''),
            ('trunk_center', 'trunk_center', ''),
            ('right_knee', 'right_knee', '')
        ]
    ) # type: ignore
    vertical_align_angle_offset: PropertyTypes.Float(
        # name='',
        # default=0,
        description='Angle offset to adjust the vertical alignement of the z axis (in degrees)'
    ) # type: ignore
    ground_align_reference: PropertyTypes.Enum(
        # name='',
        description='Empty that serves as ground reference to the axes origin',
        items=[
            ('left_foot_index', 'left_foot_index', ''),
            ('right_foot_index', 'right_foot_index', ''),
            ('left_heel', 'left_heel', ''),
            ('right_heel', 'right_heel', '')
        ]
    ) # type: ignore
    vertical_align_position_offset: PropertyTypes.Float(
        # name='',
        # default=0,
        # precision=3,
        description='Additional z offset to the axes origin relative to the imaginary ground level'
    ) # type: ignore
    # correct_fingers_empties: bpy.props.BoolProperty(
    #     name='',
    #     default=True,
    #     description='Correct the fingers empties. Match hand_wrist (axis empty) position to wrist (sphere empty)'
    # ) # type: ignore
    correct_fingers_empties: PropertyTypes.Bool(
        # name='',
        # default=True,
        description='Correct the fingers empties. Match hand_wrist (axis empty) position to wrist (sphere empty)'
    ) # type: ignore
    add_hand_middle_empty: PropertyTypes.Bool(
        # name='',
        # default=False,
        description='Add an empty in the middle of the hand between index and pinky empties. This empty is used for a better orientation of the hand (experimental)'
    ) # type: ignore
