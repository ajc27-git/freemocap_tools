# Freemocap Adapter
Add-on to adapt the Freemocap Blender output. It can adjust the markers position, add an armature and a body mesh among other functions. The resulting armature and animation can be imported in platforms like Unreal Engine.

# Requirements
1. Activate the Rigify add-on in Blender preferences.
2. Make sure the scipy python package is installed in your Blender's python folder. If it's not installed you will get a "ModuleNotFoundError: No module named scipy"
   when installing the addon. To install the scipy package run the command `python -m pip install scipy` inside your Blender python folder.

   For example:
   `C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin> .\python.exe -m pip install scipy`.
   

# Installation
Download the latest freemocap_adapter addon zip file and install as a regular *.zip add-on in Edit->Preferences-Add-ons.

# Function Instructions (v1.6.1).
## Adjust Empties
This function is no longer necessary as in the current version of FreeMoCap, the marker empties come already aligned to the world origin. The purpose of this function was to rotate the empties to align to Blender world origin assuming the character had a standing still position in the frame were the function was executed.

![image](https://github.com/user-attachments/assets/bec7b4d5-90d8-46e7-afcf-6599fc94356b)

Here is a description of its parameters:

- Align Reference: Marker to use as reference to align the empties on the z axis. Knee or trunk center are the options.
- Vertical Angle Offset: Adds an angle offset to the z axis alignement.
- Ground Reference: Marker to use for aligning the body to the ground level (z=0)
- Vertical Position Offset: A distance offset to add to the z alignment.
- Correct Fingers Empties: Fingers markers used to come separately from the wrist empties so this option was for align them to the wrist. This now comes by default with the export.
- Add Hand Middle Empty: This additional empty between the index and middle mcp was for the hand orientation.

## Reduce Bone Length Dispersion
This function was also useful for previous versions of FreeMoCap, now this comes by default with the export. The objective of this function was to reduce the variation of the bone segments formed by the marker empties. As the capture process is not 100% correct the lengths of the bones vary from frame to frame. This can produce unwanted armature bone rotations as the the bones have a fixed length.

Currently, this function is used to fix the lengths to the median value of the whole capture. For example the upperarm bone segment formed by the shoulder and elbow empties. The function will register the distance between these two empties for every frame of the capture and then calculate the median length from that.

![image](https://github.com/user-attachments/assets/449b1286-78f0-4ff2-8a74-5f812d8dae69)

Here is a description of its parameters:

- Dispersion Interval Variable: Variable used to define the new length dispersion interval.
- Dispersion Interval Factor: Factor to multiply the variable and form the limits of the dispersion interval. If the factor is set to zero then it will force each frame bone length to be equal to the interval variable.
- Body (Rig) Height [m]: Body height in meters. This value is used when the interval variable is set to standard length. If a rig is added after using Reduce Dispersion with standard length, it will have this value as height and the bones length will be proporions of this height.

## Apply Butterworth Filters (Blender 4.0+)
This function helps to smooth the animation curves by applying a Butterworth filter to them. This filter can be applied manually using the curve editor in Blender. This functions allows to easily apply the filter for different sections of the body and with different cut-off frequencies. It also allows to apply a local filter with an origin point different than the world origin. For example, a filter can be applied to the fingers markers based on their variation related to the wrist empty.

![image](https://github.com/user-attachments/assets/e552139e-696d-4657-b261-633c11e709cf)

Here is a description of its parameters:
- Section: Part of the body to apply the filter to.
- Global (Freq.): Cut-off frequency of the global filter.
- Local (Freq.): Cut-off frequency of the local filter.
- Origin: Marker empty origin for the local filter.

Here is a tutorial of this function: https://youtu.be/33OhM5xFUlg

# Considerations:
The rig has a TPose as rest pose for easier retargeting.
For best results, when the adjust empties function is executed the empties should be forming a standing still pose with arms open similar to A or T Pose.

# Mesh attribution
The meshes used in some assets come from the following sources:
1. https://sketchfab.com/3d-models/free-low-poly-pbr-bsdf-textured-human-skeleton-d0c9919aec004fd39d65ce7a7960969b
2. https://free3d.com/3d-model/skull-v3--785914.html
