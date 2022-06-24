import asyncio
import logging
from typing import Any
from log import select_book
from modes.mode import Mode
from lxml import etree


class Nhentai(Mode):

    def use(self):
        str_ = input("搜索 >> ")
        data = self.mainLoop.run_until_complete(self.search_book(str_))
        book_list = select_book(data)
        if not book_list:
            return

        tasks = [self.download_book(book["url"]) for book in book_list]
        self.mainLoop.run_until_complete(asyncio.wait(tasks))

    async def get_book(self, book_url: str) -> list[str]:
        html = str(await self.http.get(book_url), encoding="utf-8")
        page_url_list = etree.HTML(html).xpath('//div[@class="thumb-container"]//img[@class="lazyload"]/@data-src')
        for index, page_url in enumerate(page_url_list):
            # 原图 url
            page_url_list[index] = page_url.replace("/t", "/i", 1).replace("t.", ".", 1)
        
        return page_url_list

    def get_language(self, tar_list):
        """
        本子语言

        存在 6346 日语
        存在 29963 中文
        存在 12227 英语
        """

        if "6346" in tar_list:
            return "日语"
        
        if "29963" in tar_list:
            return "中文"
        
        if "12227" in tar_list:
            return "英语"
        
        return "未知"
    
    async def search_book(self, search_name: str) -> list[dict[str, Any]]:
        try:
            api = f"https://nhentai.net/search/?q={search_name}"
            html = str(await self.http.get(api), encoding="utf-8")
            html_etree = etree.HTML(html)

            book_data_list = []
            div_list = html_etree.xpath('//div[@class="gallery"]')
            for div in div_list:
                book_language = self.get_language(div.xpath('./@data-tags')[0])
                book_data_list.append({
                    "title": div.xpath('.//div[@class="caption"]/text()')[0],
                    "img": div.xpath('.//img[@class="lazyload"]/@data-src')[0],
                    "url": "https://nhentai.net%s" % div.xpath('./a/@href')[0],
                    "language": book_language
                })
            
            return book_data_list
        except Exception as err:
            logging.error("nhentai 查询错误 error: %s" % err)
            logging.exception(err)
        
        return []