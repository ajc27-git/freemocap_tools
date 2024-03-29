# Freemocap Adapter
Add-on to adapt the Freemocap Blender output. It can adjust the empties position, add a rig and a body mesh. The resulting rig and animation can be imported in platforms like Unreal Engine.

# Requirements
1. Activate the Rigify add-on in Blender preferences.
2. Make sure the scipy python package is installed in your Blender's python folder. If it's not installed you will get a "ModuleNotFoundError: No module named scipy"
   when installing the addon. To install the scipy package run the command `python -m pip install scipy` inside your Blender python folder.

   For example:
   `C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin> .\python.exe -m pip install scipy`.
   

# Installation
Install as a regular *.zip add-on in Edit->Preferences-Add-ons.

# Considerations:
The rig has a TPose as rest pose for easier retargeting.
For best results, when the adjust empties function is executed the empties should be forming a standing still pose with arms open similar to A or T Pose.

# Mesh attribution
The meshes used in some assets come from the following sources:
1. https://sketchfab.com/3d-models/free-low-poly-pbr-bsdf-textured-human-skeleton-d0c9919aec004fd39d65ce7a7960969b
2. https://free3d.com/3d-model/skull-v3--785914.html
