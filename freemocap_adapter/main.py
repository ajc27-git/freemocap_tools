import logging

from freemocap_adapter.data_models.parameter_models.load_parameters_config import load_default_parameters_config
from freemocap_adapter.data_models.parameter_models.parameter_models import Config
from freemocap_adapter.user_interfaces.run_as_main_script.run_as_main import MainRunner

logger = logging.getLogger(__name__)


def main(recording_path: str,
         config: Config = load_default_parameters_config()):
    main_runner = MainRunner(recording_path=recording_path,
                             config=config)

    main_runner.load_freemocap_data()

    main_runner.create_empties()

    main_runner.reorient_empties()

    main_runner.save_data_to_disk()

    main_runner.add_rig()

    main_runner.attach_mesh_to_rig()

    main_runner.add_videos()

    # logger.info("Exporting FBX...")
    # export_fbx(recording_path=recording_path, )

    logger.success("Done!!!")


if __name__ == "__main__" or __name__ == "<run_path>":
    from freemocap_adapter.core_functions.setup_scene.get_path_to_sample_data import get_path_to_sample_data

    recording_path = get_path_to_sample_data()
    logging.info(f"Running {__file__} with recording_path={recording_path}")
    main(recording_path=recording_path)
