import subprocess
import os
import shutil

# Function to check if addon is installed in Blender
def is_addon_installed(addon_name: str) -> bool:
    result = subprocess.run(['blender', '-b', '-P', 
        'import bpy;print(bpy.context.preferences.addons.keys())'], 
        capture_output=True, text=True)
    installed_addons = result.stdout.split('\n')[-2]
    return addon_name in installed_addons

# Define your addon's name and root directory
addon_name = 'ajc27_freemocap_blender_addon'
addon_root_dir = str(Path(__file__).parent.parent)

# Check if the addon is already installed
if not is_addon_installed(addon_name):
    # If not, create a temporary zipfile
    shutil.make_archive(addon_name, 'zip', addon_root_dir)
    
    # Install the addon via a subprocess call
    install_script = f"""
    import bpy
    bpy.ops.preferences.addon_install(filepath='{addon_name}.zip')
    bpy.ops.preferences.addon_enable(module='{addon_name}')
    bpy.ops.wm.save_userpref()
    """
    subprocess.run(['blender', '-b', '-P', install_script])
    
    # Remove the temporary zipfile
    os.remove(f'{addon_name}.zip')