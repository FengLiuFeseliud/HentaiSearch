# HentaiSearch

异步高性能的涩涩下载器, 支持多个站点

## 支持站点

imhentai, kemono, nhentai

(目标支持: pixiv, e-hentai(exhentai) )

## 使用

```bash
git clone https://github.com/FengLiuFeseliud/HentaiSearch && cd ./HentaiSearch
pip install -r ./reqirements.txt
python3 ./HentaiSearch/main.py
```

## 配置

配置文件在用户家目录下的 `.config/hentaiSearch/config.yaml`

也可以在 HentaiSearch 中选择`设置`将直接打开配置文件, 保存后 HentaiSearch 使用新配置

Linux 下会自动加载 uvloop 提高性能

## 混合搜索

选择`全部搜索` HentaiSearch 将搜索所有支持站点

## 多 url 下载

支持 HentaiSearch 支持站点的资源页混合下载

可以一次在用户家目录下的 `.config/hentaiSearch/download_url_list.txt` 添加多个站点的资源页

也可以在 HentaiSearch 中选择`下载url > 多url下载` 直接保存添加

HentaiSearch 会自动爬取并下载

### 什么是资源页?

可以查看作品缩略图的页面, 例子:

https://nhentai.net/g/298053/

https://imhentai.xxx/gallery/874030/

https://kemono.party/fanbox/user/49494721/post/3819603