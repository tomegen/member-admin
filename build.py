"""Build the app with PyInstaller and package it as zip: python build.py [version]

Windows: release/Mitgliederverwaltung_<version>_windows.zip (folder with Mitgliederverwaltung.exe)
macOS:   release/Mitgliederverwaltung_<version>_mac.zip (Mitgliederverwaltung.app)
Needs: pip install -r requirements-dev.txt
"""
import os
import shutil
import subprocess
import sys

import PyInstaller.__main__

APP_NAME = "Mitgliederverwaltung"
ROOT = os.path.dirname(os.path.abspath(__file__))
RELEASE = os.path.join(ROOT, "release")
# these files are delivered next to the app; config.ini can be edited by the users
EXTRA_FILES = ["config.ini", "README.md", "Release_Notes.md", "example_file.xlsx"]
IS_MAC = sys.platform == "darwin"


def build_app():
    PyInstaller.__main__.run([
        os.path.join(ROOT, "mitgliederverwaltung.py"),
        "--name", APP_NAME,
        "--windowed",
        "--noconfirm",
        "--clean",
        "--distpath", RELEASE,
        "--workpath", os.path.join(RELEASE, "work"),
        "--specpath", os.path.join(RELEASE, "work"),
        "--icon", os.path.join(ROOT, "member.ico"),
        # default config inside the app, used if there is no config.ini next to it
        "--add-data", os.path.join(ROOT, "config.ini") + os.pathsep + ".",
        # pandas loads the old excel reader only when needed
        "--hidden-import", "xlrd",
        "--exclude-module", "tkinter",
    ])


def package(version):
    platform_name = "mac" if IS_MAC else "windows"
    package_name = "%s_%s_%s" % (APP_NAME, version, platform_name)
    package_dir = os.path.join(RELEASE, package_name)
    shutil.rmtree(package_dir, ignore_errors=True)
    os.makedirs(package_dir)

    if IS_MAC:
        content_dir = package_dir  # the config.ini lies next to the .app
        shutil.copytree(os.path.join(RELEASE, APP_NAME + ".app"), os.path.join(package_dir, APP_NAME + ".app"),
                        symlinks=True)
    else:
        content_dir = os.path.join(package_dir, APP_NAME)  # the config.ini lies next to the .exe
        shutil.copytree(os.path.join(RELEASE, APP_NAME), content_dir)
    for name in EXTRA_FILES:
        shutil.copy(os.path.join(ROOT, name), content_dir)

    zip_path = os.path.join(RELEASE, package_name + ".zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if IS_MAC:
        # ditto keeps the structure of the .app intact (shutil would break links inside it)
        subprocess.run(["ditto", "-c", "-k", "--keepParent", package_dir, zip_path], check=True)
    else:
        shutil.make_archive(os.path.join(RELEASE, package_name), "zip", RELEASE, package_name)
    print("Package created: " + zip_path)
    return zip_path


if __name__ == "__main__":
    build_app()
    package(sys.argv[1] if len(sys.argv) > 1 else "dev")
