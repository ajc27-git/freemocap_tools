import logging

from freemocap_adapter.core_functions.bones.reduce_bone_length_dispersion import reduce_bone_length_dispersion
from freemocap_adapter.core_functions.empties.adjust_empties import adjust_empties
from freemocap_adapter.core_functions.export.fbx import export_fbx
from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene
from freemocap_adapter.core_functions.load_data.download_sample_data import get_or_download_sample_data
from freemocap_adapter.core_functions.load_data.load_freemocap_data import load_freemocap_data
from freemocap_adapter.core_functions.rig.add_rig import add_rig
from freemocap_adapter.core_functions.rig.attach_mesh import add_mesh_to_rig

logger = logging.getLogger(__name__)

def main():
    logger.info("Running RUN_ME.py...")
    logger.info("Clearing scene...")
    clear_scene()
    logger.info("Loading FreeMoCap data...")
    load_freemocap_data()

    logger.info("Adjusting empties...")
    adjust_empties()

    logger.info("Reducing bone length dispersion...")
    reduce_bone_length_dispersion()

    logger.info("Adding rig...")
    add_rig()

    logger.info("Adding body mesh...")
    add_mesh_to_rig()

    logger.info("Exporting FBX...")
    export_fbx()

    logger.success("Done!")


if __name__ == "__main__":
    logging.info(f"Running {__file__}...")
    recording_path = get_or_download_sample_data()

    main(recording_path=recording_path)
