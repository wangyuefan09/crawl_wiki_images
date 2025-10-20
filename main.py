import os
import re
import requests
from bs4 import BeautifulSoup
from opencc import OpenCC

BASE_SAVE_DIR = "./chinese_emperors_hd"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# 历代君主列表页面URL配置
DYNASTY_URLS = {
    "夏朝": "https://zh.wikipedia.org/wiki/夏朝君主列表",
    "商朝": "https://zh.wikipedia.org/wiki/商朝君主列表",
    "周朝": "https://zh.wikipedia.org/wiki/周朝君主列表",
    "秦朝": "https://zh.wikipedia.org/wiki/秦朝君主列表",
    "汉朝": "https://zh.wikipedia.org/wiki/汉朝皇帝列表",
    "三国": "https://zh.wikipedia.org/wiki/三国皇帝列表",
    "晋朝": "https://zh.wikipedia.org/wiki/晋朝皇帝列表",
    "南北朝": "https://zh.wikipedia.org/wiki/南北朝皇帝列表",
    "隋朝": "https://zh.wikipedia.org/wiki/隋朝皇帝列表",
    "唐朝": "https://zh.wikipedia.org/wiki/唐朝皇帝列表",
    "五代十国": "https://zh.wikipedia.org/wiki/五代十国君主列表",
    "宋朝": "https://zh.wikipedia.org/wiki/宋朝皇帝列表",
    "辽朝": "https://zh.wikipedia.org/wiki/辽朝皇帝列表",
    "金朝": "https://zh.wikipedia.org/wiki/金朝皇帝列表",
    "元朝": "https://zh.wikipedia.org/wiki/元朝皇帝列表",
    "明朝": "https://zh.wikipedia.org/wiki/明朝皇帝列表",
    "清朝": "https://zh.wikipedia.org/wiki/清朝皇帝列表",
}

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

def download_image(url, name, dynasty):
    hd_url = to_hd_url(url)
    # 将繁体中文名称转换为简体中文
    simplified_name = cc.convert(name)
    simplified_dynasty = cc.convert(dynasty)
    
    # 按朝代创建子目录
    save_dir = os.path.join(BASE_SAVE_DIR, simplified_dynasty)
    os.makedirs(save_dir, exist_ok=True)
    
    filename = os.path.join(save_dir, f"{simplified_name}.jpg")
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

def get_emperor_images_from_dynasty(dynasty, list_url):
    """从指定朝代页面获取君主画像"""
    print(f"\n{'='*60}")
    print(f"开始处理：{dynasty}")
    print(f"{'='*60}")
    
    try:
        resp = requests.get(list_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 查找所有wikitable表格
        tables = soup.find_all("table", {"class": "wikitable"})
        if not tables:
            print(f"⚠️ {dynasty} 未找到君主列表表格！")
            return
        
        emperor_count = 0
        success_count = 0
        
        # 遍历所有表格（有些朝代有多个表格）
        for table in tables:
            for row in table.select("tr")[1:]:
                cols = row.select("td")
                if len(cols) < 2:
                    continue
                
                # 尝试从第一列获取君主名称和链接
                link_tag = cols[0].find("a")
                if not link_tag:
                    # 有些表格君主名称在第二列
                    if len(cols) >= 2:
                        link_tag = cols[1].find("a")
                
                if not link_tag or not link_tag.get("href"):
                    continue
                
                emperor_name = link_tag.get_text(strip=True)
                # 过滤掉一些非君主的链接
                if not emperor_name or emperor_name in ["注释", "参考", "来源"]:
                    continue
                
                emperor_count += 1
                emperor_url = "https://zh.wikipedia.org" + link_tag["href"]
                print(f"\n[{dynasty}] 正在处理：{emperor_name}")
                
                try:
                    sub_resp = requests.get(emperor_url, headers=HEADERS, timeout=10)
                    sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
                    img_tag = sub_soup.select_one(".infobox img")
                    
                    if img_tag and img_tag.get("src"):
                        download_image(img_tag["src"], emperor_name, dynasty)
                        success_count += 1
                    else:
                        print(f"⚠️ {emperor_name} 未找到画像")
                except Exception as e:
                    print(f"❌ {emperor_name} 处理失败: {e}")
        
        print(f"\n{dynasty} 完成：共处理 {emperor_count} 位君主，成功下载 {success_count} 张画像")
        
    except Exception as e:
        print(f"❌ {dynasty} 页面访问失败: {e}")

def get_all_emperors():
    """下载所有朝代的君主画像"""
    print("开始下载中国历代君主画像...")
    print(f"保存目录：{BASE_SAVE_DIR}\n")
    
    total_dynasties = len(DYNASTY_URLS)
    for idx, (dynasty, url) in enumerate(DYNASTY_URLS.items(), 1):
        print(f"\n进度：[{idx}/{total_dynasties}]")
        get_emperor_images_from_dynasty(dynasty, url)
    
    print(f"\n{'='*60}")
    print("所有朝代处理完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    get_all_emperors()
