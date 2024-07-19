import bpy
from .property_types import PropertyTypes

class ReduceBoneLengthDispersionProperties(bpy.types.PropertyGroup):
    show_reduce_bone_length_dispersion: PropertyTypes.Bool(
        description = 'Toggle Reduce Bone Length Dispersion Options'
    ) # type: ignore
    interval_variable: PropertyTypes.Enum(
        description = 'Variable used to define the new length dispersion '
                      'interval',
        items = [
            ('capture_median',
             'Capture Median',
             'Use the bones median length from the capture. Defines the '
             'new dispersion interval as '
             '[median*(1-interval_factor),median*(1+interval_factor)]'),
            ('standard_length',
             'Standard length',
             'Use the standard lengths based on the total body (rig) '
             'height. Defines the new dispersion interval as '
             '[length*(1-interval_factor),length*(1+interval_factor)]'),
            ('capture_stdev',
             'Capture Std Dev',
             'Use the bones length standard deviation from the capture. '
             'Defines the new dispersion interval as '
             '[median-interval_factor*stdev,median+interval_factor*stdev]')]
    ) # type: ignore
    interval_factor: PropertyTypes.Float(
        min = 0,
        description = 'Factor to multiply the variable and form the limits of '
                      'the dispersion interval like '
                      '[median-factor*variable,median+factor*variable]. '
                      'If variable is median, the factor will be limited to '
                      'values inside [0, 1]. '  
                      'If variable is stdev, the factor will be limited to '
                      'values inside [0, median/stdev]'
    ) # type: ignore
    body_height: PropertyTypes.Float(
        default = 1.75,
        min = 0,
        description = 'Body height in meters. This value is used when the '
                      'interval variable is set to standard length. If a rig '
                      'is added after using Reduce Dispersion with standard '
                      'length, it will have this value as height and the '
                      'bones length will be proporions of this height'
    ) # type: ignore
    