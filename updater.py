# D:\deeplearning\play\updater.py
import os
import sys
import subprocess
import json
import urllib.request
import zipfile
import shutil

GITHUB_REPO = "你的用户名/你的仓库名"  # 改成你的
UPDATE_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(CURRENT_DIR, "version.json")


def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            return json.load(f).get('version', '0.0')
    return '0.0'


def get_latest_version():
    try:
        with urllib.request.urlopen(VERSION_URL) as response:
            data = json.loads(response.read())
            return data.get('version', '0.0')
    except:
        return None


def download_update():
    print("Downloading update...")
    zip_path = os.path.join(CURRENT_DIR, "update.zip")
    urllib.request.urlretrieve(UPDATE_URL, zip_path)
    return zip_path


def apply_update(zip_path):
    print("Applying update...")
    extract_dir = os.path.join(CURRENT_DIR, "_update_temp")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Copy files from extracted folder
    extracted_folder = os.listdir(extract_dir)[0]
    source = os.path.join(extract_dir, extracted_folder)

    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(CURRENT_DIR, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
        elif os.path.isdir(s) and item != '__pycache__':
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)

    # Clean up
    shutil.rmtree(extract_dir)
    os.remove(zip_path)
    print("Update complete!")


def check_and_update():
    current = get_current_version()
    latest = get_latest_version()

    if latest is None:
        print("Cannot check for updates. No internet?")
        return False

    print(f"Current version: {current}")
    print(f"Latest version: {latest}")

    if latest > current:
        print("New version available!")
        response = input("Update now? (y/n): ")
        if response.lower() == 'y':
            zip_path = download_update()
            apply_update(zip_path)
            return True

    print("Already up to date!")
    return False


if __name__ == "__main__":
    check_and_update()
    input("Press Enter to exit...")