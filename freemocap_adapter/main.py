import logging

from freemocap_adapter.core_functions.setup_scene.clear_scene import clear_scene
from freemocap_adapter.data_models.parameter_models.load_parameters_config import load_default_parameters_config
from freemocap_adapter.data_models.parameter_models.parameter_models import Config
from freemocap_adapter.user_interfaces.run_as_main_script.helpers import validate_recording_path, main_load_freemocap, \
    main_create_empties, main_reorient_empties, main_save_data_to_disk, main_add_rig, main_attach_mesh_to_rig, \
    main_add_videos

logger = logging.getLogger(__name__)


def main(recording_path: str,
         config: Config = load_default_parameters_config()):
    validate_recording_path(recording_path)

    # Clear scene
    # logger.info("Clearing scene...")
    # clear_scene()

    freemocap_data_handler, freemocap_origin_axes = main_load_freemocap(recording_path=recording_path)

    empties = main_create_empties(freemocap_data_handler=freemocap_data_handler,
                                  freemocap_origin_axes=freemocap_origin_axes)

    logger.info("Re orient empties so the skeleton data aligns with gravity with the feet on the ground (Z=0) plane...")
    reoriented_empties = main_reorient_empties(config=config,
                                               empties=empties,
                                               freemocap_origin_axes=freemocap_origin_axes,
                                               good_clean_frame=freemocap_data_handler.good_clean_frame,
                                               )
 
    main_save_data_to_disk(freemocap_data_handler=freemocap_data_handler,
                           recording_path=recording_path,
                           empties=reoriented_empties)

    main_add_rig(config = config,
                 empties=reoriented_empties,)

    main_attach_mesh_to_rig(config=config)

    main_add_videos(recording_path=recording_path)

    # logger.info("Exporting FBX...")
    # export_fbx(recording_path=recording_path, )

    logger.success("Done!")


if __name__ == "__main__" or __name__ == "<run_path>":
    print('hello\n hello \n hello')
    logging.info(f"Running {__file__}...")
    recording_path = r"C:\Users\jonma\freemocap_data\recording_sessions\freemocap_sample_data"
    main(recording_path=recording_path)
