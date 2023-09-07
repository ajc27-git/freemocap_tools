import logging

from freemocap_adapter.core_functions.bones.reduce_bone_length_dispersion import reduce_bone_length_dispersion
from freemocap_adapter.core_functions.empties.creation.create_freemocap_empties import create_freemocap_empties
from freemocap_adapter.core_functions.empties.reorient_empties import reorient_empties
from freemocap_adapter.core_functions.export.fbx import export_fbx
from freemocap_adapter.core_functions.load_data.clear_scene import clear_scene
from freemocap_adapter.core_functions.load_data.get_path_to_sample_data import get_or_download_sample_data
from freemocap_adapter.core_functions.rig.add_rig import add_rig
from freemocap_adapter.core_functions.rig.attach_mesh import add_mesh_to_rig
from freemocap_adapter.data_models.bones.bone_definitions import BONE_DEFINITIONS
from freemocap_adapter.data_models.freemocap_data.freemocap_data import FreemocapData

logger = logging.getLogger(__name__)


def main(recording_path: str):
    logger.info("Clearing scene...")
    clear_scene()

    logger.info("Loading FreeMoCap data...")
    freemocap_data = FreemocapData.from_recording_path(recording_path=recording_path)



    logger.info("Create keyframed empties...")
    raw_empties = create_freemocap_empties(freemocap_data=freemocap_data)

    logger.info("Re orient empties so the skeleton data aligns with gravity with the feet on the ground (Z=0) plane...")
    oriented_empties = reorient_empties(empties=raw_empties)

    logger.info("Reducing bone length dispersion...")
    bones = reduce_bone_length_dispersion(empties=oriented_empties,
                                          bones=BONE_DEFINITIONS, )

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
