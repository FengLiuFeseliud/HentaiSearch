import asyncio
import json
import logging
from typing import Any
import aiofiles
import os
import log
from lxml import etree
from time import time
from modes.mode import Mode


class Kemono(Mode):

    def __init__(self, httpObj, mainLoop) -> None:
        super().__init__(httpObj, mainLoop)
        self._file_kemono_path = "%s/.config/hentaiSearch/kemono_data.json" % os.path.expanduser("~")
        self.headers["cookie"] = "__ddg1_=l5gn1dnm7XogehBgTspc"


    def use(self):
        str_ = input("搜索 >> ")
        creators_list = self.mainLoop.run_until_complete(self.search_creators(str_))
        for index, creators in enumerate(creators_list):
            print("\n[%s] %s | %s | %s" % (index, creators["name"], creators["service"], creators["id"]))

        print("[exit] 结束选择")
        creators_list = log._select(creators_list)
        if not creators_list:
            return
        
        book_list = []
        tasks = [self.search_book(self.get_creators_url(creators)) for creators in creators_list]
        for book_end in self.mainLoop.run_until_complete(asyncio.wait(tasks)):
            book_end = list(book_end)
            if not book_end:
                continue

            book_list += book_end[0].result()

        book_list = log.select_book(book_list)
        if not book_list:
            return
            
        tasks = [self.download_book(book["url"]) for book in book_list]
        self.mainLoop.run_until_complete(asyncio.wait(tasks))
            

    def get_creators_url(self, creators_data: dict[str, Any]) -> str:
        type_, id_ = creators_data["service"], creators_data["id"]
        return f"https://kemono.party/{type_}/user/{id_}"
    
    async def get_kemono_search_json(self):
        api = "https://kemono.party/api/creators"
        creators_list = await self.http.get(api, json=True)
        if creators_list is None:
            return

        async with aiofiles.open(self._file_kemono_path, "w") as file:
            await file.write(json.dumps(creators_list))
        
        return creators_list

    async def search_creators(self, search_name: str) -> list[dict[str, Any]]:
        creators_list = []
        if not os.path.isfile(self._file_kemono_path):
            creators_list = await self.get_kemono_search_json()
        else:
            file_update_time = os.path.getmtime(self._file_kemono_path)
            if time() > file_update_time + 86400:
                creators_list = await self.get_kemono_search_json()

        if creators_list is None:
            logging.error("获取 kemono 搜索 json 失败, 请检查网络设置")
            return

        if not creators_list:
            async with aiofiles.open(self._file_kemono_path, "r") as file:
                creators_list = json.loads(await file.read())
        
        creators_data_list: list[dict[str, Any]] = []
        for creators in creators_list:
            if search_name not in creators["name"]:
                continue

            creators_data_list.append(creators)
        
        return creators_data_list
    
    async def search_book(self, search_name: str) -> list[dict[str, Any]]:
        book_list: list[dict[str, Any]] = []
        if not (search_name[:8] == "https://" or search_name[:7] == "http://"):
            book_item_list_ = await self.search_creators(search_name)
            for book_ in book_item_list_:
                book_list.append({
                    "title": book_["name"],
                    "img": book_["service"],
                    "url": self.get_creators_url(book_),
                    "language": "作者页无法下载",
                })
            
            return book_list

        html = await self.http.get(search_name)
        html = etree.HTML(html)
        book_item_list = html.xpath('//div[@class="card-list__items"]/article')

        for book in book_item_list:
            book_list.append({
                "title": book.xpath('.//h2[@class="post-card__heading"]/a/text()')[0].replace(" ", "").replace("\n", ""),
                "img": book.xpath('.//img[@class="post-card__image"]/@src'),
                "url": "https://kemono.party%s" % book.xpath('.//h2[@class="post-card__heading"]/a/@href')[0],
                "language": "未知",
            })

        return book_list
    
    async def get_book(self, book_url: str) -> list[str]:
        html = await self.http.get(book_url)
        html = etree.HTML(html)
        downloads = html.xpath('//a[@class="post__attachment-link"]/@href')
        imgs = html.xpath('//a[@class="fileThumb"]/@href')
        files = ["https://kemono.party%s" % file_ for file_ in imgs + downloads]

        return files