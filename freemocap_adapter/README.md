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
This function is no longer necessary as in the current version of FreeMoCap, the marker empties come already aligned to the world origin. The purpose of this function was to rotate the empties to align to Blender world origin assuming the character had a standing still position in the frame were the function was executed. For best results, when the adjust empties function is executed the empties should be forming a standing still pose with arms open similar to A or T Pose.

![image](https://github.com/user-attachments/assets/bec7b4d5-90d8-46e7-afcf-6599fc94356b)

Parameter description:
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

Parameter description:
- Dispersion Interval Variable: Variable used to define the new length dispersion interval.
- Dispersion Interval Factor: Factor to multiply the variable and form the limits of the dispersion interval. If the factor is set to zero then it will force each frame bone length to be equal to the interval variable.
- Body (Rig) Height [m]: Body height in meters. This value is used when the interval variable is set to standard length. If a rig is added after using Reduce Dispersion with standard length, it will have this value as height and the bones length will be proporions of this height.

## Apply Butterworth Filters (Blender 4.0+)
This function helps to smooth the animation curves by applying a Butterworth filter to them. This filter can be applied manually using the curve editor in Blender. This functions allows to easily apply the filter for different sections of the body and with different cut-off frequencies. It also allows to apply a local filter with an origin point different than the world origin. For example, a filter can be applied to the fingers markers based on their variation related to the wrist empty.

![image](https://github.com/user-attachments/assets/e552139e-696d-4657-b261-633c11e709cf)

Parameter description:
- Section: Part of the body to apply the filter to.
- Global (Freq.): Cut-off frequency of the global filter.
- Local (Freq.): Cut-off frequency of the local filter.
- Origin: Marker empty origin for the local filter.

Here is a tutorial of this function: https://youtu.be/33OhM5xFUlg

## Add Finger Rotation Limits
This function translates the finger marker empties so the bones respect the human normal rotation constraints. The idea is that the armature finger bones rotate according to human normal limits. This function was developed as enforcing this limits directly on the armature didn't produce decent results. The function is totally experimental and might produce awkward results. Only use it if the overall benefit is greater than the errors. The function works better if the empties orign has not been rotated.

![image](https://github.com/user-attachments/assets/cabb4ea8-509f-497f-8295-9577bf628f38)

Here is a tutorial of this function: https://youtu.be/vPz6cTT_Iug

## Apply Foot Locking
The objective of this function is to lock the feet markers based on their z axis position. The function's logic tries to fix the z position of the markers gradually when their z position is under a certain threshold for some consecutive frames. It also fix markers positions that are below a ground level. It also has a compensation logic to adjust the markers of the rest of the body.

![image](https://github.com/user-attachments/assets/12d7e5d0-65e2-43a4-8e75-7aa77bb29959)

The following is a representation of the foot locking logic:
![image](https://github.com/user-attachments/assets/41dfef7f-998d-4d73-9891-860ef8170e36)

Parameter description:
- Target Foot: Foot to apply the locking to.
- Target foot base markers: Markers to consider for the locking logic.
- Z Threshold (m): Vertical threshold under which foot markers are considered for applying foot locking.
- Ground Level (m): Ground level for applying foot locking. Markers with z global coordinate lower than this value will be fixed to this level. It must be lower than the z threshold.
- Frame Window Minimum Size: Minimum frame window size for applying foot locking. A marker's z global coordinate has to be lower than the z threshold for a consecutive frames count equal or bigger than this value. It must be equal or greater than initial_attenuation_count + final_attenuation_count.
- Initial Attenuation Count: This are the first frames of the window which have their z coordinate attenuated by the the initial quadratic attenuation function.
- Final Attenuation Count: This are the last frames of the window which have their z coordinate attenuated by the the final quadratic attenuation function.
- Lock XY at Ground Level: When applying foot locking, lock also the x and y coordinates at the ground level. This is useful only when character is standing still as it might leed to "sticky" or "lead" feet effect.
- Knee Hip Compensation Coefficient: After calculating the ankle new z global coordinate, the knee and hip markers will be adjusted on the z axis by the same delta multiplied by this coefficient. A value of 1.0 means knee and hip have the same adjustment as the ankle. A value of 0 means knee and hip have no adjustment at all. Values lower than 1.0 are useful when the rig has IK constraints on the legs. This way the ankle adjustment is compensated by the knee IK bending.
- Compensate Upper Body Markers: Compensate the upper body markers by setting the new z coordinate of the hips_center marker as the average z coordinate of left and right hips markers. Then propagate the new z delta to the upper body markers starting from the trunk_center.

Here is a tutorial of the function: https://youtu.be/OE0ZlG9_My8

## Add Armature
This function deletes the default armature and creates a new one. It was more useful when the default export had a simpler armature. Now the default armature is made using part of this function's logic.

![image](https://github.com/user-attachments/assets/238a2a7a-2d64-4acd-9794-478d67e378c8)

Parameter description:
- Add Armature Method: Method used to create the armature.
- Armature: Armature type.
- Pose: Pose that will be used as rest pose.
- Keep right/left symmetry: Keep right/left side symmetry (use average right/left side bone length).
- Add finger constraints: Add bone constraints for the fingers.
- Add IK constraints: Add IK constraints for arms and legs.
- IK transition threshold: Threshold of parallel degree (dot product) between base and target ik vectors. It is used to transition between vectors to determine the pole bone position.
- Add rotation limits: Add rotation limits (human skeleton) to the bones constraints (experimental).
- Clear constraints: Clear added constraints after baking animation.

## Add Body Mesh
Function to add a mesh to the armature. It was more useful when the export didn't have a body mesh.

![image](https://github.com/user-attachments/assets/4c813c8d-f0cb-4845-a060-f27df47c8397)

Parameter description:
- Body Mesh Mode: Mode for adding the mesh to the armature. The Skelly Parts mode uses the length and rotation of the bones to adjust individual bone meshes to adapt them to the capture armature. 

## FBX Export
This function exports an FBX file of the armature and mesh (including animation) to a folder named "FBX" inside the same folder where the capture .blend file is.

![image](https://github.com/user-attachments/assets/16bf6eb1-1842-4090-ac57-0ea96687d9a4)

Parameter description:
- FBX Export Type: The type of export based on the final platform destination. The Unreal Engine option was necessary when exporting from Blender versions 4.0 or older. In newer Blender versions the Standard mode exports a correct FBX file for importing in UE (tested on UE version 5.3 and 5.4).

## Retarget Animation
This functions helps to retarget the animation from a source armature to a target armature. A source and target armature should be selected in the options. Then the internal logic tries to figure it out the armature type of the target. Currently it has preloaded the bones naming of Rigify, Mixamo and Daz armatures. The function will try to apply bone constraints based on the bone name equivalence detected in the previous step.
The function is just a first iteration so it won't work as expected in most cases, this because of different bone naming and different bone local axis orientation that requires additional bone roll. The target armature should have a T-Pose (equal to the FreeMoCap rest pose) as rest pose so it doesn't add rotationn offsets to the retargeting. 

![image](https://github.com/user-attachments/assets/48250e15-be05-4922-b936-a0320624366c)

Parameter description:
- Source FreeMoCap Armature: Source FreeMoCap armature.
- Target Armature: The armature that the constraints will be aplied to.
- Bake Animation: Bake the animation to the pose bones.
- Clear Constraints: Clear the constraints after the animation bake is made.


# Mesh attribution
The meshes used in some assets come from the following sources:
1. https://sketchfab.com/3d-models/free-low-poly-pbr-bsdf-textured-human-skeleton-d0c9919aec004fd39d65ce7a7960969b
2. https://free3d.com/3d-model/skull-v3--785914.html
