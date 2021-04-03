# -*- coding: utf-8 -*-

from modules.porfirevich import Porfirevich
from modules.vk_utils import VkBot
from modules.utils import *
from vk_api.longpoll import *

__version__ = open("version.txt", "r").read().strip()

banner = f"""
 __________              _____.__         __________ ___________________
 \______   \____________/ ____\__|______  \______   \\_____  \__    ___/
  |     ___/  _ \_  __ \   __\|  \_  __ \  |    |  _/ /   |   \|    |
  |    |  (  <_> )  | \/|  |  |  ||  | \/  |    |   \/    |    \    |
  |____|   \____/|__|   |__|  |__||__|     |______  /\_______  /____|
                                                 \/         \/
 [ * ] Version: {__version__}
"""


def handler(event, bot, ai):
    bulling_list = get_bulling_list()
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and not event.from_chat and event.peer_id in bulling_list:
        bot.messages_handler(event)


if __name__ == '__main__':
    print(banner)
    ai = Porfirevich()
    bot = VkBot(ai)

    if bot.auth():
        bot.start_threads()
        log(current_time() + "[ + ] Бот запущен! Ждем новых сообщений...\n")
    else:
        exit()

    while True:
        try:
            for event in bot.lonpoll.listen():
                handler(event, bot, ai)

        except KeyboardInterrupt:
            log(" [ - ] Keyboard Interrupt!")
            break

        except Exception as e:
            log(current_time() + "[ - ] Ошибка! " + str(e))
