import os
import re
import requests
from bs4 import BeautifulSoup
from opencc import OpenCC

SAVE_DIR = "./qing_emperors_hd"
os.makedirs(SAVE_DIR, exist_ok=True)

LIST_URL = "https://zh.wikipedia.org/wiki/清朝皇帝列表"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# 初始化繁简转换器
cc = OpenCC('t2s')  # 繁体转简体

def to_hd_url(url: str) -> str:
    """将维基 thumbnail 链接转换为高清原图"""
    if not url.startswith("http"):
        url = "https:" + url
    # 匹配缩略图路径并替换成原图路径
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/thumb(/.+?)/[^/]+$", url)
    if m:
        return m.group(1) + m.group(2)
    return url

def download_image(url, name):
    hd_url = to_hd_url(url)
    # 将繁体中文名称转换为简体中文
    simplified_name = cc.convert(name)
    filename = os.path.join(SAVE_DIR, f"{simplified_name}.jpg")
    try:
        r = requests.get(hd_url, headers=HEADERS, timeout=10)
        if r.status_code != 200 or len(r.content) < 1000:
            # 如果高清图下载失败，退回原图
            print(f"⚠️ {name} 高清图失败，尝试缩略图")
            r = requests.get(url, headers=HEADERS, timeout=10)
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"✅ {simplified_name} 下载成功 ({len(r.content)//1024} KB)")
    except Exception as e:
        print(f"❌ {simplified_name} 下载失败: {e}")

def get_emperor_images():
    resp = requests.get(LIST_URL, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})
    if not table:
        print("未找到皇帝列表表格！")
        return

    for row in table.select("tr")[1:]:
        cols = row.select("td")
        if len(cols) < 2:
            continue
        emperor_name = cols[0].get_text(strip=True)
        link_tag = cols[0].find("a")
        if not link_tag:
            continue

        emperor_url = "https://zh.wikipedia.org" + link_tag["href"]
        print(f"正在处理：{emperor_name} -> {emperor_url}")

        sub_resp = requests.get(emperor_url, headers=HEADERS)
        sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
        img_tag = sub_soup.select_one(".infobox img")
        if img_tag:
            download_image(img_tag["src"], emperor_name)
        else:
            print(f"⚠️ {emperor_name} 未找到画像")

if __name__ == "__main__":
    get_emperor_images()
