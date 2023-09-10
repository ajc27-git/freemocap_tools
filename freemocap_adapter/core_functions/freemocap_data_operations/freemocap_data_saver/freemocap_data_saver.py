import json
import logging
import pickle
from pathlib import Path
from typing import Union

import numpy as np

from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.freemocap_data_handler import \
    FreemocapDataHandler
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_saver.data_readme_text import DATA_README_TEXT

logger = logging.getLogger(__name__)


class FreemocapDataSaver:
    def __init__(self, freemocap_data_handler: FreemocapDataHandler):
        self.handler = freemocap_data_handler

    def save(self, recording_path: Union[str, Path]):
        recording_path = Path(recording_path)
        try:
            save_path = Path(recording_path) / "saved_data"
            save_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Saving freemocap data to {save_path}")


            self._save_data_readme(save_path=save_path)

            # save trajectory names
            trajectory_names_path = save_path / "trajectory_names.json"
            trajectory_names = {
                "body": self.handler.body_names,
                "right_hand": self.handler.right_hand_names,
                "left_hand": self.handler.left_hand_names,
                "face": self.handler.face_names,
                "other": {other_component.name: other_component.trajectory_names for other_component in
                          self.handler.freemocap_data.other}
            }
            trajectory_names_path.write_text(json.dumps(trajectory_names, indent=4))

            self._save_npy(save_path)
            self._save_csv(save_path)
            self._save_pickle(save_path)
            logger.success(f"Saved freemocap data to {save_path}")

        except Exception as e:
            logger.error(f"Failed to save data to disk: {e}")
            logger.exception(e)
            raise e

    def _save_csv(self, save_path):
        csv_path = save_path / "csv"
        csv_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving csv files to {csv_path}")
        components = {
            'body': self.handler.body_frame_name_xyz,
            'right_hand': self.handler.right_hand_frame_name_xyz,
            'left_hand': self.handler.left_hand_frame_name_xyz,
            'face': self.handler.face_frame_name_xyz
        }

        for name, other_component in self.handler.freemocap_data.other.items():
            components[name] = other_component.data_frame_name_xyz

        all_csv_header = ""

        for component_name, component_data in components.items():
            csv_header = "".join(
                [f"{name}_x, {name}_y, {name}_z," for name in getattr(self.handler, f"{component_name}_names")])
            all_csv_header += csv_header

            reshaped_data = component_data.reshape(component_data.shape[0], -1)
            np.savetxt(str(csv_path / f"{component_name}_frame_name_xyz.csv"), reshaped_data, delimiter=",",
                       fmt='%s', header=csv_header)
            logger.debug(f"Saved {component_name}_frame_name_xyz to {csv_path / f'{component_name}_frame_name_xyz.csv'}")

        np.savetxt(str(save_path / "all_frame_name_xyz.csv"),
                   self.handler.all_frame_name_xyz.reshape(self.handler.all_frame_name_xyz.shape[0], -1), delimiter=",",
                   fmt='%s', header=all_csv_header)
        logger.debug(f"Saved all_frame_name_xyz to {csv_path / 'all_frame_name_xyz.csv'}")

    def _save_npy(self, save_path):

        npy_path = save_path / "npy"
        npy_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving npy files to {npy_path}")


        np.save(str(npy_path / "body_frame_name_xyz.npy"), self.handler.body_frame_name_xyz)
        logger.debug(f"Saved body_frame_name_xyz to {npy_path / 'body_frame_name_xyz.npy'}")

        np.save(str(npy_path / "right_hand_frame_name_xyz.npy"), self.handler.right_hand_frame_name_xyz)
        logger.debug(f"Saved right_hand_frame_name_xyz to {npy_path / 'right_hand_frame_name_xyz.npy'}")

        np.save(str(npy_path / "left_hand_frame_name_xyz.npy"), self.handler.left_hand_frame_name_xyz)
        logger.debug(f"Saved left_hand_frame_name_xyz to {npy_path / 'left_hand_frame_name_xyz.npy'}")

        np.save(str(npy_path / "face_frame_name_xyz.npy"), self.handler.face_frame_name_xyz)
        logger.debug(f"Saved face_frame_name_xyz to {npy_path / 'face_frame_name_xyz.npy'}")

        for other_component in self.handler.freemocap_data.other:
            np.save(str(npy_path / f"{other_component.name}_frame_name_xyz.npy"),
                    other_component.data_frame_name_xyz)
            logger.debug(f"Saved {other_component.name}_frame_name_xyz to {npy_path / f'{other_component.name}_frame_name_xyz.npy'}")

        np.save(str(save_path / "all_frame_name_xyz.npy"), self.handler.all_frame_name_xyz)
        logger.debug(f"Saved all_frame_name_xyz to {npy_path / 'all_frame_name_xyz.npy'}")


    def _save_data_readme(self, save_path: Union[str, Path]):
        logger.info(f"Saving data readme to {save_path}")
        readme_path = Path(save_path) / "freemocap_data_read_me.md"
        readme_path.write_text(DATA_README_TEXT, encoding="utf-8")

    def _save_pickle(self, save_path):
        logger.info(f"Saving `FreemocapDataHandler` pickle to {save_path}")
        pickle_path = save_path / "freemocap_data_handler.pkl"
        with open(str(pickle_path), "wb") as f:
            pickle.dump(self.handler, f)
