from typing import Dict


import bpy

from freemocap_adapter.data_models.mediapipe_names.trajectory_names import MEDIAPIPE_TRAJECTORY_NAMES
from freemocap_adapter.data_models.mediapipe_names.virtual_trajectories import MEDIAPIPE_VIRTUAL_TRAJECTORY_DEFINITIONS


def freemocap_empties_from_parent_object(parent_empty: bpy.types.Object) -> Dict[str, Dict[str, bpy.types.Object]]:
    all_empties = {empty.name: empty for empty in parent_empty.children}

    arranged_empties = {
        "body": {},
        "hands": {"right": {}, "left": {}},
        "face": {},
        "other": {},
    }

    for empty_name, empty in all_empties.items():
        empty_added = False
        for component_name in (key for key in arranged_empties.keys() if key != 'other'):

            if component_name == "hands":
                if "right_hand" in empty_name or "left_hand" in empty_name:
                    in_component = True
                else:
                    in_component = False
            elif component_name == "body":
                virtual_trajectory = empty_name in MEDIAPIPE_VIRTUAL_TRAJECTORY_DEFINITIONS.keys()
                body_trajectory = empty_name in MEDIAPIPE_TRAJECTORY_NAMES["body"]
                in_component = virtual_trajectory or body_trajectory
            else:
                in_component = empty_name in MEDIAPIPE_TRAJECTORY_NAMES[component_name]

            if in_component:
                if component_name == "hands":
                    if "right" in empty_name:
                        arranged_empties["hands"]["right"][empty_name] = empty
                    elif "left" in empty_name:
                        arranged_empties["hands"]["left"][empty_name] = empty
                    else:
                        raise ValueError(f"Empty name {empty_name} is not a valid hand name")
                else:
                    arranged_empties[component_name][empty_name] = empty
                empty_added = True
                break

        if not empty_added:
            arranged_empties["other"][empty_name] = empty

    return arranged_empties
