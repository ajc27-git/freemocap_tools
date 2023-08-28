import io
import logging
import urllib.request
import zipfile
from pathlib import Path

FIGSHARE_TEST_ZIP_FILE_URL = "https://figshare.com/ndownloader/files/40293973"
FREEMOCAP_TEST_DATA_RECORDING_NAME = "freemocap_sample_data"
FIGSHARE_SAMPLE_ZIP_FILE_URL = "https://figshare.com/ndownloader/files/41368323"

logger = logging.getLogger(__name__)


def get_sample_data_path() -> str:
    return str(Path(Path.home()) / "freemocap_data" / "sample_data" )





def download_sample_data(sample_data_zip_file_url: str = FIGSHARE_TEST_ZIP_FILE_URL) -> str:
    try:
        logger.info(f"Downloading sample data from {sample_data_zip_file_url}...")

        recording_session_folder_path = Path(get_sample_data_path())
        recording_session_folder_path.mkdir(parents=True, exist_ok=True)

        # Download the file and convert it to bytes
        with urllib.request.urlopen(sample_data_zip_file_url) as response:
            data = response.read()

        z = zipfile.ZipFile(io.BytesIO(data))
        z.extractall(recording_session_folder_path)

        figshare_sample_data_path = recording_session_folder_path / FREEMOCAP_TEST_DATA_RECORDING_NAME
        logger.info(f"Sample data extracted to {str(figshare_sample_data_path)}")
        return str(figshare_sample_data_path)

    except urllib.error.URLError as e:
        logger.error(f"Request failed: {e}")
    except zipfile.BadZipFile as e:
        logger.error(f"Failed to unzip the file: {e}")

if __name__ == "__main__":
    sample_data_path = download_sample_data()
    print(f"Sample data downloaded successfully to path: {str(sample_data_path)}")
