import requests
import subprocess
import json
from utils import get_all_IDF_tags

IDF_versions = get_all_IDF_tags()


# 获取已构建的版本
def get_git_tags():
    command = "git tag"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout.strip().split("\n")


# 已构建的版本
IDF_versions_exist = get_git_tags()

# 挑选出未构建的版本
IDF_versions_need_to_build = [x for x in IDF_versions if x not in IDF_versions_exist]
print("matrix=" + json.dumps(IDF_versions_need_to_build))
