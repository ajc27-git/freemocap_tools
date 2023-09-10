DATA_README_TEXT = f"""# Freemocap Data
This folder contains the data extracted from the recording.
## Data
The data is stored in the following files:
### `trajectory_names.json`
A json file containing the names of the trajectories in the data. The format is as follows:
```json
{{
"body": ["nose", "left_eye", "right_eye", ...],
    "hands": {"right": ["wrist", "thumb", "index", ...], "left": ["wrist", "thumb", "index", ...]},
    "face": ["nose", "left_eye", "right_eye", ...],
    "other": {"other_component_name": ["trajectory_name_1", "trajectory_name_2", ...]}
}}
```

The order of the trajectories is the same as the order of the data in the npy files, and was used to make the headers in the .csv files.

### `/npy` folder
- `body_frame_name_xyz.npy`: Body trajectory data in the format, dimensions: (frame, trajectory_name, xyz)
- `right_hand_frame_name_xyz.npy`: Right hand trajectory data in the format, dimensions: (frame, trajectory_name, xyz)
- `left_hand_frame_name_xyz.npy`: Left hand trajectory data in the format, dimensions: (frame, trajectory_name, xyz)
- `face_frame_name_xyz.npy`: Face trajectory data in the format, dimensions: (frame, trajectory_name, xyz)
- `other_frame_name_xyz.npy`: Other component trajectory data in the format, dimensions: (frame, trajectory_name, xyz)
- `all_frame_name_xyz.npy`: All trajectory data in the format, dimensions: (frame, trajectory_name, xyz)

Numpy arrays containing the trajectory data. Note that the data is stored in the format (frame, trajectory_name, xyz).
Numpy arrays are stored in binary format - this means that they are not human-readable, but they are much faster to load and manipulate.

All of these files share a common format - they are three-dimensional arrays with the following dimensions:
- `frame`: The frame number
- `name`: The index of the name of this trajectory (e.g. `head`, `left_hand_index`, etc.) in the relevant entry `trajectory_names.json` file. (i.e. for `mediapipe` data, the 'nose' trajectory is the 0th entry in the list under `body` key). For `all_frame_name_xyz.npy`, this is the index of the trajectory name in the list of all trajectory names concatenated together. 
- `xyz`: The x, y, and z coordinates of the trajectory at the given frame number (x = 0, y = 1, z = 2)

To access a specific data point, you can think of the name (`..._frame_name_xyz`) as an 'address' for where the point lives in the 3d matrix.
For example, to access the y data of the nose trajectory (0th name) at frame 100, you would do:
```python
import numpy as np
nose_y = np.load("body_frame_name_xyz.npy")[100, 0, 1] # data from the 100th frame, of the 0th trajectory, at the 1st dimension (y)
```
You can also use the `.json` data as a look up table to find the index of a trajectory name, e.g. 
```python
import json
trajectory_names = json.load("trajectory_names.json")
nose_index = trajectory_names["body"].index("nose")
nose_y = np.load("body_frame_name_xyz.npy")[100, nose_index, 1] # data from the 100th frame, of the nose trajectory, at the 1st dimension (y)
```

### `/csv` folder
- `body_frame_name_xyz.csv`: Body trajectory data in the `csv` format
- `right_hand_frame_name_xyz.csv`: Right hand trajectory data in the `csv` format
- `left_hand_frame_name_xyz.csv`: Left hand trajectory data in the `csv` format
- `face_frame_name_xyz.csv`: Face trajectory data in the `csv` format
- `other_frame_name_xyz.csv`: Other component trajectory data in the `csv` format
- `all_frame_name_xyz.csv`: All trajectory data in the `csv` format

The header of each file is the list of trajectory names, with each marker's x, y, and z coordinates as a separate column (format: `[name]_x`, `[name]_y`, `[name]_z`).                 
"""
