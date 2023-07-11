# freemocap2ue
Script to adapt the Freemocap Blender output to an armature with mesh and animation that can be imported in Unreal Engine.

# Requirements
1. Activate the Rigify add-on in Blender preferences.

Considerations:
The armature has a TPose as rest pose for easier retargeting.
For best results, when the script is ran the empties should be forming a standing still pose with arms open similar to A or T Pose.
The body_mesh.ply file should be in the same folder as the Blender file before manually opening it.
