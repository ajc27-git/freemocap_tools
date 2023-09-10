import json
from dataclasses import dataclass


# Define the data classes to represent the JSON structure

@dataclass
class AdjustEmpties:
    vertical_align_reference: str
    vertical_align_angle_offset: float
    ground_align_reference: str
    vertical_align_position_offset: float
    correct_fingers_empties: bool
    add_hand_middle_empty: bool


@dataclass
class ReduceBoneLengthDispersion:
    interval_variable: str
    interval_factor: float


@dataclass
class ReduceShakiness:
    recording_fps: float


@dataclass
class AddRig:
    bone_length_method: str
    keep_symmetry: bool
    add_fingers_constraints: bool
    use_limit_rotation: bool


@dataclass
class AddBodyMesh:
    body_mesh_mode: str


@dataclass
class Config:
    # recording_path: str
    adjust_empties: AdjustEmpties
    reduce_bone_length_dispersion: ReduceBoneLengthDispersion
    reduce_shakiness: ReduceShakiness
    add_rig: AddRig
    add_body_mesh: AddBodyMesh


def load_default_parameters_config(filename: str = "default_parameters.json") -> Config:
    with open(filename, "r") as f:
        data = json.load(f)
    # if not 'recording_path' in data:
    #     data['recording_path'] = get_path_to_sample_data()
    # Parse JSON data into the dataclass structure
    return Config(
        # recording_path=data['recording_path'],
        adjust_empties=AdjustEmpties(**data['adjust_empties']),
        reduce_bone_length_dispersion=ReduceBoneLengthDispersion(**data['reduce_bone_length_dispersion']),
        reduce_shakiness=ReduceShakiness(**data['reduce_shakiness']),
        add_rig=AddRig(**data['add_rig']),
        add_body_mesh=AddBodyMesh(**data['add_body_mesh'])
    )


if __name__ == "__main__":
    from pprint import pprint as print

    default_parameters_filename = "default_parameters.json"
    config = load_default_parameters_config("default_parameters.json")
    print(config.__dict__)
