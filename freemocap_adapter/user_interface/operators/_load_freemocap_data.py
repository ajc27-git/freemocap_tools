import logging
from pathlib import Path
from typing import Dict, List, Union

import bpy
import numpy as np

from freemocap_adapter.core_functions.empties.creation.create_freemocap_empties import create_freemocap_empties, \
    create_empties
from freemocap_adapter.core_functions.freemocap_data_operations.freemocap_data_handler.put_freemocap_data_into_inertial_reference_frame import \
    put_freemocap_data_into_inertial_reference_frame, estimate_good_clean_frame
from freemocap_adapter.core_functions.freemocap_data_operations.load_freemocap_data import load_freemocap_data
from freemocap_adapter.core_functions.setup_scene.make_parent_empties import create_freemocap_parent_empty
from freemocap_adapter.core_functions.setup_scene.set_start_end_frame import set_start_end_frame

logger = logging.getLogger(__name__)

import bpy
from mathutils import Matrix, Vector

def create_groundplane_mesh(plane_definition: Dict[str, Union[List[float], np.ndarray]],
                            parent_object: bpy.types.Object,
                            ):
    # Define the center and normal vector
    groundplane_center_vector = Vector(plane_definition["center"])
    groundplane_normal_vector = Vector(plane_definition["normal"])

    up_vector = Vector((0, 0, 1)) # This is the default 'normal' for the plane in Blender (it points up)

    # Create a new plane object
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=groundplane_center_vector)

    # Get the created object
    groundplane_mesh = bpy.context.active_object

    # Calculate the rotation matrix from the normal vector
    rotation_matrix = groundplane_normal_vector.rotation_difference(up_vector).to_matrix().to_4x4()

    # Apply the rotation to the object
    groundplane_mesh.matrix_world = Matrix.Translation(groundplane_center_vector) @ rotation_matrix

    groundplane_mesh.parent = parent_object


class FMC_ADAPTER_load_freemocap_data(bpy.types.Operator):  # , bpy_extras.io_utils.ImportHelper):
    bl_idname = 'fmc_adapter.freemocap_data_operations'
    bl_label = "Load FreeMoCap Data"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    def execute(self, context):
        try:
            scene = context.scene
            fmc_adapter_tool = scene.fmc_adapter_tool

            recording_path = fmc_adapter_tool.recording_path
            if recording_path == "":
                logger.error("No recording path specified")
                return {'CANCELLED'}

            recording_name = Path(recording_path).stem
            origin_name = f"{recording_name}_origin"
            freemocap_origin_axes = create_freemocap_parent_empty(name=origin_name)
            fmc_adapter_tool.data_parent_empty = freemocap_origin_axes

            logger.info("Loading freemocap data....")
            freemocap_data_handler = load_freemocap_data(recording_path=recording_path)
            freemocap_data_handler.mark_processing_stage("original_from_file")
            set_start_end_frame(number_of_frames=freemocap_data_handler.number_of_frames)
        except Exception as e:
            logger.error(e)
            return {'CANCELLED'}


        good_clean_frame = estimate_good_clean_frame(freemocap_data_handler=freemocap_data_handler)
        scene.frame_set(good_clean_frame)
        bpy.ops.screen.animation_play()
        bpy.ops.screen.animation_cancel()
        # try:
        #     logger.info("Putting freemocap data into inertial reference frame....")
        #     freemocap_data_handler = put_freemocap_data_into_inertial_reference_frame(
        #         freemocap_data_handler=freemocap_data_handler)
        #     slow_points_name_xyz = freemocap_data_handler.metadata["slow_points"]
        #     plane_definition = freemocap_data_handler.metadata["unrotated_ground_plane_definition"]
        #     create_groundplane_mesh(plane_definition=plane_definition,
        #                             parent_object=freemocap_origin_axes,
        #                             )
        #     # add dimension to slow points so it matches the `frame_name_xyz` shape
        #     slow_points_frame_name_xyz = slow_points_name_xyz[np.newaxis, :, :]
        #     create_empties(trajectory_frame_marker_xyz=slow_points_frame_name_xyz,
        #                    names_list="slow_points",
        #                    empty_scale=0.01,
        #                    empty_type="PLAIN_AXES",
        #                    parent_object=freemocap_origin_axes,
        #                    )
        #     logger.success("Finished putting freemocap data into inertial reference frame!")
        #
        # except Exception as e:
        #     logger.error(f"Failed to put freemocap data into inertial reference frame: {e}")
        #     return {'CANCELLED'}

        try:
            logger.info("Creating keyframed empties....")
            logger.info("Create keyframed empties...")
            empties = create_freemocap_empties(freemocap_data_handler=freemocap_data_handler,
                                               parent_object=freemocap_origin_axes, )
            logger.success(f"Finished creating keyframed empties: {empties.keys()}")
        except Exception as e:
            logger.error(f"Failed to create keyframed empties: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
