from dataclasses import dataclass
import numpy as np

def calculate_stats(data):
    return {
        'shape': data.shape if data.size > 0 else np.nan,
        'mean': np.nanmean(data) if data.size > 0 else np.nan,
        'std_dev': np.nanstd(data) if data.size > 0 else np.nan,
    }

@dataclass
class FreemocapDataStats:
    body_stats: dict
    right_hand_stats: dict
    left_hand_stats: dict
    face_stats: dict

    @classmethod
    def from_freemocap_data(cls, freemocap_data):
        return cls(
            body_stats=calculate_stats(freemocap_data.body_fr_mar_xyz),
            right_hand_stats=calculate_stats(freemocap_data.right_hand_fr_mar_xyz),
            left_hand_stats=calculate_stats(freemocap_data.left_hand_fr_mar_xyz),
            face_stats=calculate_stats(freemocap_data.face_fr_mar_xyz),
        )

    def __str__(self):
        from pprint import pformat

        return pformat(
            self.__dict__,
            indent=4,
            compact=True,
        )