import requests
import os
def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {destination}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def check_file_exists(file_path, file_description):
    """Raise an error if a specified file does not exist."""
    if not os.path.exists(file_path):
        raise FileNotFounderror(f"❌​ ​{file_description} not found: {file_path}")