import subprocess
import os
import shutil
from pathlib import Path
import sys

BASE_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(BASE_PATH)

from bpy_install_addon import INSTALL_ADDON_SCRIPT_PATH





def install_to_blender(blender_path: str,
                       addon_root_directory: str,
                       addon_name ='ajc27_freemocap_blender_addon'):
    
    # Define your addon's name and root directory
    subprocess_command =         [
            blender_path,
            "--background",
            "--python",
            INSTALL_ADDON_SCRIPT_PATH,
            "--",
            addon_root_directory,
            addon_name
        ]
    # use CLI to install the addon passing in the addon name and zip file path
    subprocess.run(subprocess_command    )



if __name__ == "__main__":
    blender_path_in = r"C:\Users\jonma\Blender Foundation\stable\blender-3.6.5+stable.cf1e1ed46b7e\blender.exe"
    addon_root_directory_in = str(Path(__file__).parent.parent.parent)  # Path to the root directory of the addon's code

    install_to_blender(blender_path=blender_path_in,
                       addon_root_directory=addon_root_directory_in)
