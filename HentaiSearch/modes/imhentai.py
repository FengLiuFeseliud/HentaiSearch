import asyncio
from typing import Any
from log import select_book
from modes.mode import Mode
from lxml import etree


class Imhentai(Mode):

    def use(self) -> None:
        str_ = input("搜索 >> ")
        data = self.mainLoop.run_until_complete(self.search_book(str_))
        book_list = select_book(data)
        if not book_list:
            return

        tasks = [self.download_book(book["url"]) for book in book_list]
        self.mainLoop.run_until_complete(asyncio.wait(tasks))

    async def search_book(self, search_name: str) -> list[dict[str, Any]]:
        api = "https://imhentai.xxx/search/?key=%s&page=0" % search_name
        html = await self.http.get(api, json=False)
        html = etree.HTML(html)

        # page = int(html.xpath('//ul[@class="pagination"]/li')[-2].xpath("./a/text()")[0])
        select_list, book_data_list = html.xpath('//div[@class="thumb"]'), []
        for book_data in select_list:
            book_data_list.append({
                "title": book_data.xpath('.//div[@class="caption"]/a/text()')[0],
                "img": book_data.xpath('.//div[@class="inner_thumb"]/a/img/@src')[0],
                "url": "https://imhentai.xxx%s" % book_data.xpath('.//div[@class="caption"]/a/@href')[0],
                "language": "未知",
            })
        
        return book_data_list
    
    async def get_book(self, book_url: str) -> list[str]:
        html = await self.http.get(book_url)
        html = etree.HTML(html)

        page_url_list = []
        page = int(html.xpath('//li[@class="pages"]/text()')[0].strip("Pages: "))
        img_data_url = html.xpath('//*[@id="append_thumbs"]/div[1]/div/a/img/@data-src')[0].rsplit("/", maxsplit=1)[0]
        for page_in in range(1, page+1):
            page_url_list.append("%s/%s.jpg" % (img_data_url, page_in))
        
        return page_url_list