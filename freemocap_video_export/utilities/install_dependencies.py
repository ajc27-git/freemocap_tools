import subprocess
import sys

REQUIRED_LIBRARIES = ["opencv-contrib-python", "matplotlib"]


def check_and_install_dependencies():
    print("Checking if required packages are installed...")
    # get path of blender internal python executable
    python_executable = str(sys.executable)

    try:
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    except:
        subprocess.call([python_executable, "-m", "ensurepip", "--user"])
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])

    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

    print("\nInstalled packages:", installed_packages, "\n")

    packages_to_install = []
    for library in REQUIRED_LIBRARIES:
        if library in installed_packages:
            print(f"{library!r} already installed!")
        else:
            print(f"{library!r} not installed, will install...")
            packages_to_install.append(library)

    if len(packages_to_install) > 0:
        subprocess.call([python_executable, "-m", "ensurepip", "--user"])
        # update pip
        subprocess.call([python_executable, "-m", "pip", "install", "--upgrade", "pip"])

    for library in REQUIRED_LIBRARIES:
        print(f"Installing {library!r}...")
        subprocess.call([python_executable, "-m", "pip", "install", library])

        print(f"{library!r} installed successfully!")

    print("All required packages installed! Done!")


if __name__ == "__main__":
    check_and_install_dependencies()
