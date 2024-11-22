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

# Considerations:
The rig has a TPose as rest pose for easier retargeting.
For best results, when the adjust empties function is executed the empties should be forming a standing still pose with arms open similar to A or T Pose.

# Mesh attribution
The meshes used in some assets come from the following sources:
1. https://sketchfab.com/3d-models/free-low-poly-pbr-bsdf-textured-human-skeleton-d0c9919aec004fd39d65ce7a7960969b
2. https://free3d.com/3d-model/skull-v3--785914.html
