"""Build the app with PyInstaller and package it for download: python build.py [version]

Windows: release/Mitgliederverwaltung-Windows-Setup.exe (installer, needs Inno Setup 6)
         release/Mitgliederverwaltung-Windows.zip (folder with Mitgliederverwaltung.exe, without installation)
macOS:   release/Mitgliederverwaltung-Mac.dmg (Mitgliederverwaltung.app and a link to the programs folder)
The file names have no version, so the link .../releases/latest/download/<file name> always gets the newest one.
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
# these files are delivered next to the Windows app; config.ini can be edited by the users
# (the Mac app uses the config.ini built into it)
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


def find_inno_setup():
    candidates = [shutil.which("iscc"), r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                  r"C:\Program Files\Inno Setup 6\ISCC.exe"]
    return next((path for path in candidates if path and os.path.exists(path)), None)


def package_windows(version):
    package_dir = os.path.join(RELEASE, "%s_%s_windows" % (APP_NAME, version))
    shutil.rmtree(package_dir, ignore_errors=True)
    content_dir = os.path.join(package_dir, APP_NAME)  # the config.ini lies next to the .exe
    shutil.copytree(os.path.join(RELEASE, APP_NAME), content_dir)
    for name in EXTRA_FILES:
        shutil.copy(os.path.join(ROOT, name), content_dir)

    zip_base = os.path.join(RELEASE, APP_NAME + "-Windows")
    shutil.make_archive(zip_base, "zip", package_dir, APP_NAME)
    files = [zip_base + ".zip"]

    iscc = find_inno_setup()
    if iscc:
        subprocess.run([iscc, "/Q", "/DAppVersion=" + version, "/DSourceDir=" + content_dir,
                        "/DOutputDir=" + RELEASE, "/DRootDir=" + ROOT,
                        os.path.join(ROOT, "installer", "windows.iss")], check=True)
        files.append(os.path.join(RELEASE, APP_NAME + "-Windows-Setup.exe"))
    else:
        print("Inno Setup 6 not found: no installer built (only the zip)")
    return files


def package_mac():
    # the disk image shows the app next to a link to the programs folder: drag it over to install
    package_dir = os.path.join(RELEASE, APP_NAME + "-Mac")
    shutil.rmtree(package_dir, ignore_errors=True)
    os.makedirs(package_dir)
    shutil.copytree(os.path.join(RELEASE, APP_NAME + ".app"), os.path.join(package_dir, APP_NAME + ".app"),
                    symlinks=True)  # keep the links inside the .app
    os.symlink("/Applications", os.path.join(package_dir, "Programme"))
    dmg_path = os.path.join(RELEASE, APP_NAME + "-Mac.dmg")
    subprocess.run(["hdiutil", "create", "-volname", APP_NAME, "-srcfolder", package_dir, "-fs", "HFS+",
                    "-format", "UDZO", "-ov", dmg_path], check=True)
    return [dmg_path]


def package(version):
    files = package_mac() if IS_MAC else package_windows(version)
    for path in files:
        print("Package created: " + path)
    return files


if __name__ == "__main__":
    build_app()
    package(sys.argv[1] if len(sys.argv) > 1 else "dev")
