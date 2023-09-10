from dataclasses import dataclass
from pathlib import Path


@dataclass
class FreemocapDataPaths:
    body_npy: Path
    right_hand_npy: Path
    left_hand_npy: Path
    face_npy: Path
    center_of_mass_npy: Path
    segment_centers_of_mass_npy: Path
    reprojection_error_npy: Path

    @classmethod
    def from_recording_folder(cls, path: str):
        recording_path = Path(path)
        output_data_path = recording_path / "output_data"
        return cls(
            body_npy=output_data_path / "mediapipe_body_3d_xyz.npy",
            right_hand_npy=output_data_path / "mediapipe_right_hand_3d_xyz.npy",
            left_hand_npy=output_data_path / "mediapipe_left_hand_3d_xyz.npy",
            face_npy=output_data_path / "mediapipe_face_3d_xyz.npy",

            center_of_mass_npy=output_data_path / "center_of_mass" / "total_body_center_of_mass_xyz.npy",
            segment_centers_of_mass_npy=output_data_path / "center_of_mass" / "segmentCOM_frame_joint_xyz.npy",

            reprojection_error_npy=output_data_path / "raw_data" / "mediapipe3dData_numFrames_numTrackedPoints_reprojectionError.npy",
        )
