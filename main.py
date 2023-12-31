import urllib.request
import os
import zipfile
import subprocess
import shutil
from git import Repo
import sys

# 这些文件来自于乐鑫  https://github.com/espressif/idf-installer/blob/main/Build-Installer.ps1
IdfPythonVersion = "3.11.2"
GitVersion = "2.39.2"
IdfVersion = sys.argv[1]  # 从命令行获取版本号

python_url = f"https://dl.espressif.com/dl/idf-python/idf-python-{IdfPythonVersion}-embed-win64.zip"
python_dir = f"tools/python"
python_path = "tools/python/python.exe"

git_url = f"https://dl.espressif.com/dl/idf-git/idf-git-{GitVersion}-win64.zip"
git_dir = "tools/git"

idf_url = f"https://github.com/espressif/esp-idf.git"
idf_dir = "idf"

print(f"easy-esp-idf now build IDF {IdfVersion} !")


def git_clone(url, extract_path):
    extract_path = f"IDF{IdfVersion}/{extract_path}/esp-idf-{IdfVersion}"
    #                                      克隆子模块                 子模块只克隆表层     仓库只克隆表层
    extra_args = ['--recurse-submodules', '--shallow-submodules', '--depth=1']
    Repo.clone_from(url, extract_path, branch=IdfVersion, multi_options=extra_args)


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


os.mkdir(f"IDF{IdfVersion}")

# 未来用这个文件进入idf环境
idf_env_bat = fr"""
@echo off
set IDF_PATH=%~dp0\idf\esp-idf-{IdfVersion}
set IDF_PYTHON=%~dp0\tools\python\python.exe
set IDF_PYTHON_DIR=%~dp0tools\python
set IDF_GIT_DIR=%~dp0\tools\git\cmd
set IDF_TOOLS_PATH=%~dp0

for /D %%G in ("%~dp0\python_env\*") do (
rem     这是python虚拟环境的配置文件，里面保存python本体的路径，为防止移动文件夹后不能用，每次都重新生成
    echo home=%IDF_PYTHON_DIR%>%%G\pyvenv.cfg
)

rem 还是上边的问题，虚拟环境虽然改了配置文件就能用，但是pip不认，这里pip删了重装
rem path-fix.txt保存了idf安装目录，如果这个目录和当前目录不一样，证明python被移动了，需要重装pip
set /P pathFix=<%~dp0path-fix.txt

if "%pathFix%" neq "%~dp0" (
    echo New install detected! Reinstalling pip!

    for /D %%G in ("%~dp0\python_env\*") do (

        for /D %%F in ("%%G\Lib\site-packages\pip*") do (
            echo deleting %%F 
            rmdir /s /q "%%F"
        )
        echo Reinstalling!
        %IDF_PYTHON% -m venv --upgrade-dep "%%G"
        echo back to IDF!
    )
)

echo %~dp0>%~dp0path-fix.txt

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
f = open(fr"IDF{IdfVersion}\idf.bat", "w", encoding="utf8")
f.write(idf_env_bat)
f.close()

# 这个脚本让idf自动下载编译器和普通包
idf_env_install_bat = fr"""
@echo off
set IDF_PATH=%~dp0\idf\esp-idf-{IdfVersion}
set IDF_PYTHON=%~dp0\tools\python\python.exe
set IDF_PYTHON_DIR=%~dp0\tools\python
set IDF_GIT_DIR=%~dp0\tools\git\cmd
set IDF_TOOLS_PATH=%~dp0


echo %~dp0>%~dp0path-fix.txt

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
IDF{IdfVersion}\idf\esp-idf-{IdfVersion}\install.bat"
"""
f = open(fr"IDF{IdfVersion}\idf_install.bat", "w", encoding="utf8")
f.write(idf_env_install_bat)
f.close()


# idf只需要python，git，和idf这三个东西，之后能自动下载python依赖包和gcc等工具。
print("download python")
download_and_extract_zip(python_url, python_dir)
print("download git")
download_and_extract_zip(git_url, git_dir)
print("clone idf")
git_clone(idf_url, idf_dir)

# 执行idf安装
print("::group::install idf")
subprocess.run(rf'IDF{IdfVersion}\idf_install.bat', check=True)
os.remove(rf'IDF{IdfVersion}\idf_install.bat')
print("::endgroup::")


# 修复 windows-curses
print("::group::fix windows-curses")
# 执行一个编译测试
fix_windows_curses = f"""cd IDF{IdfVersion}
call idf.bat
pip install windows-curses
"""
f = open(fr"IDF{IdfVersion}\fix_windows_curses.bat", "w", encoding="utf8")
f.write(fix_windows_curses)
f.close()
subprocess.run(rf'IDF{IdfVersion}\fix_windows_curses.bat', check=True)
print("::endgroup::")


print("::group::testing idf")
# 执行一个编译测试
build_test_bat = f"""cd IDF{IdfVersion}
call idf.bat
idf.py create-project test
cd test
idf.py build
"""
f = open(fr"IDF{IdfVersion}\build_test.bat", "w", encoding="utf8")
f.write(build_test_bat)
f.close()
subprocess.run(rf'IDF{IdfVersion}\build_test.bat', check=True)
exists = os.path.exists(rf"IDF{IdfVersion}\test\build\test.bin")
print("::endgroup::")
if exists:
    print("build test pass!")
else:
    print("build test fail!")
    exit(-1)
shutil.rmtree(rf"IDF{IdfVersion}\test")
os.remove(rf'IDF{IdfVersion}\build_test.bat')
# 删除下载缓存
shutil.rmtree(rf"IDF{IdfVersion}\dist")
