# 清朝皇帝画像下载器

从维基百科自动下载清朝皇帝的高清画像，文件名使用简体中文。

## 功能特点

- 🖼️ 自动从维基百科下载清朝皇帝高清画像
- 📝 文件名自动转换为简体中文
- 🎯 智能获取高清原图（而非缩略图）
- ✅ 下载进度实时显示

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install requests beautifulsoup4 opencc-python-reimplemented
```

## 使用方法

```bash
python main.py
```

下载的图片将保存在 `qing_emperors_hd` 目录中。

## 技术栈

- **requests**: HTTP请求
- **BeautifulSoup4**: HTML解析
- **OpenCC**: 繁简体中文转换

## 输出示例

```
正在处理：努爾哈赤 -> https://zh.wikipedia.org/wiki/努爾哈赤
✅ 努尔哈赤 下载成功 (1574 KB)
正在处理：皇太極 -> https://zh.wikipedia.org/wiki/皇太極
✅ 皇太极 下载成功 (1764 KB)
...
```

## 许可证

MIT License
