from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class FreemocapComponentData:
    name: str
    data_frame_name_xyz: np.ndarray
    data_source: str
    trajectory_names: List[str]

    def __post_init__(self):
        assert self.data_frame_name_xyz.ndim == 3, \
            f"Data frame shape {self.data_frame_name_xyz.shape} does not have 3 dimensions (frame, marker, xyz)"
        assert self.data_frame_name_xyz.shape[1] == len(self.trajectory_names), \
            f"Data frame shape {self.data_frame_name_xyz.shape} does not match trajectory names length {len(self.trajectory_names)}"
        assert self.data_frame_name_xyz.shape[2] == 3, \
            f"Data frame shape {self.data_frame_name_xyz.shape} does not have 3 columns (xyz)"
