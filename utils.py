import requests
import re


def get_all_IDF_tags():
    tags_url = f"https://api.github.com/repos/espressif/esp-idf/tags"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    tags = []

    # 递归获取所有分页的标签
    def get_tags(url):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tags.extend(response.json())
        link_header = response.headers.get('Link')
        if link_header:
            next_url = find_next_url(link_header)
            if next_url:
                get_tags(next_url)

    # 从Link头信息中找到下一页的URL
    def find_next_url(link_header):
        links = link_header.split(', ')
        for link in links:
            url, rel = link.split('; ')
            url = url[1:-1]  # 去除尖括号
            rel = rel.split('=')[1][1:-1]  # 去除引号
            if rel == 'next':
                return url
        return None

    get_tags(tags_url)
    # 5.x及以上版本，只包含正式版本，rc，beta版本，
    return [x["name"] for x in tags if re.fullmatch(r"v[>=5]\..*", x["name"]) and "dev" not in x["name"]]


if __name__ == '__main__':
    # 指定仓库的拥有者和仓库名
    owner = "espressif"
    repo = "esp-idf"

    # 获取所有标签
    tags = get_all_IDF_tags()

    print(tags)
