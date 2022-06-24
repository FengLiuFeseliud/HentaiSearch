import os
from typing import Any, Callable, Union, Optional
import logging


class Log:

    def __init__(self, level=logging.DEBUG):
        logger = logging.getLogger()
        logger.setLevel(level)

        sh = logging.StreamHandler()
        
        logger.addHandler(sh)

        formatter = logging.Formatter(
            self.setFormat()
        )
        sh.setFormatter(formatter)
        
    def setFormat(self):
        return "\033[0m[%(asctime)s][%(levelname)s] %(message)s\033[0m"


def _select(list_: Union[list, dict], callable: Optional[Callable[[Any], str]]=None, 
        exit_func: Optional[Callable[[], str]]=None) -> list:
    """
    选择器
    """

    type_len = len(list_) - 1
    select_list: list[Any] = []

    while True:
        str_ = input(">> ")

        if str_ == "exit":
            if exit_func is not None:
                exit_func()

            break
        
        if str_ in ["c", "clear"]:
            os.system("clear")
            continue
        
        try:
            index = int(str_)
        except ValueError as err:
            logging.error("无效的字符")
            continue

        if index > type_len:
            print("过大的序号")
        elif index < 0:
            print("过小的序号")
        else:
            if type(list_) == dict:
                select_list.append(list(list_.values())[index])
            else:
                select_list.append(list_[index])

            if callable is None:
                continue

            str_ = callable(select_list[-1])
            if str_ == "exit":
                break

    return select_list


def select_book(book_list: list[dict[str, Any]]) -> list:
    """
    本子选择器
    """
    for index, book in enumerate(book_list):
        print("\n[%s] %s | %s" % (index, book["title"], book["language"]))
        print(book["url"])

    print("[exit] 结束选择")
    return _select(book_list)
    

def select(type: dict[str, Callable[[], None]], exit_func: Optional[Callable[[], str]]=None) -> None:
    """
    序号选择器
    """
    str_ = "\n[exit] 退出 "
    for index, item in enumerate(type):
        str_ = f"{str_}[{index}] {item} "
    
    print(str_)

    def run(item):
        item()
        return "exit"

    _select(type, run, exit_func=exit_func)
