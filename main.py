import urllib.request
import os
import zipfile
import subprocess

# 这些文件来自于乐鑫  https://github.com/espressif/idf-installer/blob/main/Build-Installer.ps1
IdfPythonVersion = "3.11.2"
GitVersion = "2.39.2"
IdfVersion = "v5.0.2"

python_url = f"https://dl.espressif.com/dl/idf-python/idf-python-{IdfPythonVersion}-embed-win64.zip"
python_dir = f"tool/python"
python_path = "tool/python/python.exe"

git_url = f"https://dl.espressif.com/dl/idf-git/idf-git-{GitVersion}-win64.zip"
git_dir = "tool/git"

idf_url = f"https://github.com/espressif/esp-idf/releases/download/{IdfVersion}/esp-idf-{IdfVersion}.zip"
idf_dir = "idf"


def download_and_extract_zip(url, extract_path):
    extract_path = f"IDF{IdfVersion}/{extract_path}"

    # 从URL中提取文件名
    file_name = os.path.basename(url)

    # 下载ZIP文件
    urllib.request.urlretrieve(url, file_name)

    # 解压ZIP文件
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    # 删除下载的ZIP文件
    os.remove(file_name)


idf_env_bat = fr"""
@echo off
set IDF_PATH=%~dp0\idf\esp-idf-{IdfVersion}
set IDF_PYTHON=%~dp0\tools\python\python.exe
set IDF_PYTHON_DIR=%~dp0\tools\python
set IDF_GIT_DIR=%~dp0\tools\git\cmd
set IDF_TOOLS_PATH=%~dp0


set PREFIX=%IDF_PYTHON% %IDF_PATH%
DOSKEY idf.py=%PREFIX%\tools\idf.py $*
DOSKEY esptool.py=%PREFIX%\components\esptool_py\esptool\esptool.py $*
DOSKEY espefuse.py=%PREFIX%\components\esptool_py\esptool\espefuse.py $*
DOSKEY espsecure.py=%PREFIX%\components\esptool_py\esptool\espsecure.py $*
DOSKEY otatool.py=%PREFIX%\components\app_update\otatool.py $*
DOSKEY parttool.py=%PREFIX%\components\partition_table\parttool.py $*

set PYTHONPATH=
set PYTHONHOME=
set PYTHONNOUSERSITE=True

set "PATH=%IDF_PYTHON_DIR%;%IDF_GIT_DIR%;%PATH%"
if exist "%IDF_PATH%\export.bat" %IDF_PATH%\export.bat
"""
f = open(f"IDF{IdfVersion}/idf.bat", "w")
f.write(idf_env_bat)
f.close()

download_and_extract_zip(python_url, python_dir)
download_and_extract_zip(git_url, git_dir)
download_and_extract_zip(idf_url, idf_dir)

bat_path = r'IDFv5.0.2\idf.bat'
subprocess.call(bat_path)
