import asyncio
import logging
import os
import platform
from HentaiSearch import HentaiSearchMode
import log

log.Log()

logo = """=================================================================
 _   _            _        _   _____                     _     
| | | |          | |      (_) /  ___|                   | |    
| |_| | ___ _ __ | |_ __ _ _  \ `--.  ___  __ _ _ __ ___| |__  
|  _  |/ _ \ '_ \| __/ _` | |  `--. \/ _ \/ _` | '__/ __| '_ \ 
| | | |  __/ | | | || (_| | | /\__/ /  __/ (_| | | | (__| | | |
\_| |_/\___|_| |_|\__\__,_|_| \____/ \___|\__,_|_|  \___|_| |_|
                                        v0.1.1 By FengLiu
================================================================="""

print(logo)

plat = platform.system().lower()
if plat == 'linux':
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError as err:
        logging.warning('Linux 下可以安装 uvloop 提高异步性能, 使用 "pip install uvloop" 安装 uvloop')

if plat == "windows":
    clear_ = "cls"
else:
    clear_ = "clear"

hs_mode = HentaiSearchMode()
print("欢迎使用 HentaiSearch!!!")

def exit_func():
    import sys
    
    print("Bye ~")
    sys.exit()

def clear():
    os.system(clear_)

modes = hs_mode.get_modes()
log.COMMIT_DICT = {
    "c": clear,
    "clear": clear,
    "config": hs_mode.set_config
}

while True:
    log.select({
        "Nhentai": modes["nhentai"].use,
        # "ehentai": None,
        "Imhentai": modes["imhentai"].use,
        "Kemono": modes["kemono"].use,
        "全部搜索": hs_mode.all_search,
        "下载Url": hs_mode.download_url,
        "设置": hs_mode.set_config
    }, exit_func)
