from __future__ import annotations
import logging
import os
from asyncio import AbstractEventLoop
from typing import TYPE_CHECKING, Any
from abc import ABCMeta, abstractmethod

import aiofiles


if TYPE_CHECKING:
    from create import Http


class Mode(metaclass=ABCMeta):
    """
    必须统一实现 use get_book search_book
    并且可以随意替换使用
    """

    def __init__(self, httpObj: Http, mainLoop: AbstractEventLoop) -> None:
        self.http = httpObj
        self.mainLoop = mainLoop
        self.headers: dict[str, Any] = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }

    @abstractmethod
    def use(self) -> None:
        """
        使用模块
        """
        pass

    @abstractmethod
    async def get_book(self, book_url: str) -> list[str]:
        """
        获取本子

        统一返回原图 url 列表
        """
        pass
    
    @abstractmethod
    async def search_book(self, search_name: str) -> list[dict[str, Any]]:
        """
        搜索本子

        统一返回本子字典列表, key 如下
        "title": 本子标题
        "img": 本子封面
        "url": 本子url
        "language": 本子语言
        """
        pass

    async def _download_book_page(self, book_page_url: str, download_dir: str) -> None:
        """
        下载本子单页
        """
        img_data = await self.http.get(book_page_url, headers=self.headers)
        if img_data is None:
            logging.warning(f"img_data is None url: {book_page_url}")
            return
        
        try:
            file_name = book_page_url.split("?")[0].rsplit("/", maxsplit=1)[-1]
            async with aiofiles.open(os.path.join(download_dir, file_name), mode="wb") as file:
                await file.write(img_data)

        except Exception as err:
            logging.error(f"save img err: {err}")
            logging.exception(err)

    async def download_book(self, book_url: str) -> None:
        """
        下载本子
        """
        book_page = await self.get_book(book_url)
        book_id = book_url.rstrip("/").rsplit("/", maxsplit=1)[-1]

        download_dir = os.path.join(self.http._download_path, f"{self.__class__.__name__}/{book_id}")
        if not os.path.isdir(download_dir):
            os.makedirs(download_dir)

        tasks = [self._download_book_page(page, download_dir) for page in book_page]
        await self.http.run_tasks(tasks)