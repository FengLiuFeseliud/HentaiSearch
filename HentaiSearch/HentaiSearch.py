import asyncio
import os
import log
import logging
import yaml
import platform
from typing import Optional
from create import createMode


CONFIG = """# HentaiSearch Config

# 下载路径
download_path: download_book
# 多 url 下载保存 url 文件名称
downloadUrlListTxtName: download_url_list.txt
http:
    # 最大并发请求数
    limit: 8
    # 网络代理 (http)
    proxy: http://127.0.0.1:7890
    # 最大重连次数
    reconnection: 3
    # 多少秒后重连
    reconnection_sleep: null

# HentaiSearch 使用的文件编辑器
editor: {editor}
"""


class HentaiSearchMode:

    def __init__(self) -> None:
        self.mainLoop = asyncio.get_event_loop()
        self._config_path = "%s/.config/hentaiSearch/config.yaml" % os.path.expanduser("~")
        self._config = self.get_config()
        self.__createMode = createMode(self.mainLoop, self._config)
        self.modes = self.get_modes()
    
    def _open_file(slef, path: str, mode="r", data=None) -> Optional[str]:
        file_dir = path.rsplit("/", maxsplit=1)[0]
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        with open(path, mode=mode, encoding="utf-8") as file:
            if mode in ["w", "wb"]:
                file.write(data)
            else:
                return file.read()
            
            return None

    def get_config(self):
        try:
            data = self._open_file(self._config_path)
            return yaml.safe_load(data)
        except FileNotFoundError as ferr:
            logging.warning(f"没有配置文件自动生成 path: {self._config_path}")

            plat = platform.system().lower()
            if plat == 'windows':
                editor = "notepad"
            else:
                editor = "vim"

            config = CONFIG.format(editor)
            self._open_file(self._config_path, mode="w", data=config)
            return yaml.safe_load(config)
    
    def set_config(self):
        self._set_file()
        # reload HentaiSearchMode
        self.__init__()
    
    def _set_file(self, file_path=None):
        if file_path is None:
            file_path = self._config_path

        editor = self._config["editor"]
        os.system(f"{editor} {file_path}")

        if editor not in ["vi", "vim"]:
            input("编辑完了? 回车继续 >>")
    
    def get_createModes(self):
        return self.__createMode
    
    def get_modes(self):
        return self.__createMode._modes
    
    def all_search(self):
        str_ = input("搜索 >> ")
        all_book_list = []
        tasks = [mode.search_book(str_) for mode in list(self.modes.values())]
        for book_list in self.mainLoop.run_until_complete(asyncio.wait(tasks))[0]:
            all_book_list += book_list.result()
        
        all_book_list = log.select_book(all_book_list)
        self._download_url_list(all_book_list)

    def _download_url_list(self, url_list):
        async def run():
            tasks = []
            for url in url_list:
                if not (url[:8] == "https://" or url[:7] == "http://"):
                    logging.warning(f"非法的 url: {url}")
                    continue

                for mode in self.modes:
                    if mode not in url:
                        continue

                    tasks.append(asyncio.create_task(self.modes[mode].download_book(url)))
            
            if not tasks:
                logging.error("没有待下载的 url")
                return

            await asyncio.wait(tasks)

        self.mainLoop.run_until_complete(run())

    def download_url(self):
        def download_url_txt():
            config_dir = self._config_path.rsplit("/", maxsplit=1)[0]
            download_txt_path = os.path.join(config_dir, self._config["downloadUrlListTxtName"])
            self._set_file(download_txt_path)
            
            url_list = self._open_file(download_txt_path).split("\n")
            if not url_list or url_list[0] == "":
                logging.error("没有待下载的 url")
                return

            self._download_url_list(url_list)
            self._open_file(download_txt_path, mode="w", data="")
        
        def _download_url():
            url = input("url >> ")

            download_in = False
            for mode in self.modes:
                if mode not in url:
                    continue
                
                download_in = True
                self.mainLoop.run_until_complete(self.modes[mode].download_book(url))
            
            if not download_in:
                logging.warning("不支持的下载站点")

            
        log.select({
            "下载单个url": _download_url,
            "下载多个url": download_url_txt
        })
