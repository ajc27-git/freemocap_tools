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
            body_stats=calculate_stats(freemocap_data.body.data),
            right_hand_stats=calculate_stats(freemocap_data.hands['right'].data),
            left_hand_stats=calculate_stats(freemocap_data.hands['left'].data),
            face_stats=calculate_stats(freemocap_data.face.data),
        )

    def __str__(self):
        from pprint import pformat

        return pformat(
            self.__dict__,
            indent=4,
            compact=True,
        )
