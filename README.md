# Freemocap Adapter

Add-on to adapt the Freemocap Blender output. It can adjust the empties position, add a rig and a body mesh. The
resulting rig and animation can be imported in platforms like Unreal Engine.

# Requirements

1. Activate the Rigify add-on in Blender preferences.

# Installation

Install as a regular *.py add-on in Edit->Preferences-Add-ons.

# Considerations:

The rig has a TPose as rest pose for easier retargeting.
For best results, when the adjust empties function is executed the empties should be forming a standing still pose with
arms open similar to A or T Pose.
The body_mesh.ply file should be in the same folder as the Blender file before manually opening it.
