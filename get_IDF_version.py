import requests
import subprocess
import json
response = requests.get("https://dl.espressif.com/dl/esp-idf/idf_versions.txt")
strip = response.text.strip()
# idf目前最新的若干版本
IDF_versions = [x for x in strip.split() if x.startswith('v')]


def get_git_tags():
    command = "git tag"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout.strip().split("\n")


# 已构建的版本
IDF_versions_exist = get_git_tags()

# 挑选出未构建的版本
IDF_versions_need_to_build = [x for x in IDF_versions if x not in IDF_versions_exist]
print(json.dumps(IDF_versions_need_to_build))
