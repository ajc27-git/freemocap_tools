import logging

from freemocap_adapter.data_models.parameter_models.load_parameters_config import load_default_parameters_config
from freemocap_adapter.data_models.parameter_models.parameter_models import Config
from freemocap_adapter.user_interfaces.run_as_main_script.run_as_main import RunAsMain

logger = logging.getLogger(__name__)


def main(recording_path: str,
         config: Config = load_default_parameters_config()):
    logger.info(f"Initializing `run_as_main` object with recording_path={recording_path} and config={config}")
    run_as_main = RunAsMain(recording_path=recording_path,
                            config=config)

    logger.info("Loading freemocap data...")
    run_as_main.load_freemocap_data()
    
    logger.info("Creating empties...")
    run_as_main.create_empties()

    # logger.info("Reorienting empties...")
    # run_as_main.reorient_empties()

    logger.info("Saving data to disk...")
    run_as_main.save_data_to_disk()

    logger.info("Adding rig...")
    run_as_main.add_rig()

    logger.info("Attaching empties to rig...")
    run_as_main.attach_mesh_to_rig()

    logger.info("Adding videos...")
    run_as_main.add_videos()

    # logger.info("Exporting FBX...")
    # export_fbx(recording_path=recording_path, )

    logger.success("Done!!!")


if __name__ == "__main__" or __name__ == "<run_path>":
    from freemocap_adapter.core_functions.setup_scene.get_path_to_sample_data import get_path_to_sample_data

    recording_path = get_path_to_sample_data()
    logging.info(f"Running {__file__} with recording_path={recording_path}")
    main(recording_path=recording_path)
