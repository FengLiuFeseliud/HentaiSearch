import logging
from time import sleep
from typing import Any, Optional, Coroutine
from tqdm import tqdm
from asyncio import AbstractEventLoop
from modes.kemono import Kemono
from modes.nhentai import Nhentai
from modes.imhentai import Imhentai
import aiohttp
import asyncio


class Http:

    def __init__(self, config) -> None:
        self.__session: Optional[aiohttp.ClientSession] = None
        self._download_path: str = config["download_path"]
        self._limit: int = config["http"]["limit"]
        self._proxy: Optional[str] = config["http"]["proxy"]
        self._reconnection: Optional[int] = config["http"]["reconnection"]
        self._reconnection_sleep: Optional[int] = config["http"]["reconnection_sleep"]
    
    async def get_session(self) -> aiohttp.ClientSession:
        """
        获取 ClientSession 会话
        """
        if self.__session is None:
            conn = aiohttp.TCPConnector(limit=self._limit)
            self.__session = aiohttp.ClientSession(connector=conn)
        
        return self.__session
    
    async def get(self, url, data={}, headers={}, json=False, reconnection_count=0):
        try:
            session = await self.get_session()
            async with session.get(url, data=data, headers=headers, proxy=self._proxy) as req:
                if json:
                    data = await req.json()
                else:
                    data = await req.content.read()
                
                return data
        except Exception as err:
            logging.error(f"get err: {err} 重新连接 ({reconnection_count}/{self._reconnection})")
            if self._reconnection is None:
                return

            reconnection_count += 1
            if reconnection_count > self._reconnection:
                return

            return await self.get(url, data, headers, json, reconnection_count)
    
    async def post(self, url, data={}, headers={}, json=False, reconnection_count=0):
        try:
            session = await self.get_session()
            async with session.post(url, data=data, headers=headers, proxy=self._proxy) as req:
                if json:
                    data = await req.json()
                else:
                    data = await req.content
                
                return data
        except Exception as err:
            logging.error(f"post err: {err} 重新连接 ({reconnection_count}/{self._reconnection})")
            if self._reconnection is None:
                return

            reconnection_count += 1
            if reconnection_count > self._reconnection:
                return

            return await self.post(url, data, headers, json, reconnection_count)
    
    async def _qdm_up(self, func: Coroutine, qdm: tqdm):
        func_return_data = await func
        qdm.update(1)
        return func_return_data
    
    async def run_tasks(self, tasks: list[Coroutine]):
        try:
            new_tasks, qdm = [], tqdm(total=len(tasks))
            for task in tasks:
                new_tasks.append(asyncio.create_task(self._qdm_up(task, qdm)))

            await asyncio.wait(new_tasks)

            sleep(0.2)
        except Exception as err:
            logging.error(f"run_tasks err: {err}")
            logging.exception(err)


class createMode:
    
    def __init__(self, loop: AbstractEventLoop, config: dict[str, Any]) -> None:
        self._httpObj = Http(config)
        self._mainLoop = loop

        self._modes = {
            "nhentai": self.nhentai(),
            "kemono": self.kemono(),
            "imhentai": self.imhentai()
        }

    def kemono(self) -> Kemono:
        return Kemono(self._httpObj, self._mainLoop)
    
    def nhentai(self) -> Nhentai:
        return Nhentai(self._httpObj, self._mainLoop)
    
    def imhentai(self) -> Imhentai:
        return Imhentai(self._httpObj, self._mainLoop)