from vk_api import VkApi
from vk_api.longpoll import *
from .utils import *

import base64
import requests
import time
import threading
import random


char_map = "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮqwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890,'[]?!. "


class VkBot(object):
    def __init__(self, ai):
        self.ai = ai
        self.queue = {}
        self.context = {}

    def captcha_handler(self, captcha):
        captcha_token = load_tokens()[1]
        if captcha_token:
            captcha_url = captcha.get_url().strip()
            captcha_image = requests.get(captcha_url, timeout=7)

            request_data = {'method': 'base64', 'key': captcha_token, 'body': base64.b64encode(captcha_image.content)}
            response = requests.post('http://rucaptcha.com/in.php', data=request_data).text
            if response[:2] != "OK":
                log(current_time() + "[ - ] Ошибка при обработке каптчи... " + response)
            else:
                log(current_time() + "[ ~ ] Отправка каптчи...")
                captcha_id = response[3:]

            while True:
                time.sleep(2)
                request_data = {'key': captcha_token, 'id':captcha_id, 'action':'get'}
                response = requests.post('http://rucaptcha.com/res.php', data=request_data).text

                if response[:2] == "OK":
                    log(current_time() + "[ + ] Каптча решена!")
                    break
            return captcha.try_again(response[3:])
        else:
            log(current_time() + "[ - ] Ошибка! Невозможно получить ruCaptcha токен!")
            return None

    def start_threads(self):
        threading.Thread(target=self.sender, daemon=True).start()
        threading.Thread(target=self.context_cleaner, daemon=True).start()
        threading.Thread(target=self.infinite_online, daemon=True).start()

    def auth(self):
        try:
            session = VkApi(token=load_tokens()[0], captcha_handler=self.captcha_handler)
            self.bot = session.get_api()
            self.lonpoll = VkLongPoll(session)
            return True

        except Exception as e:
            log(current_time() + "[ - ] Ошибка при авторизации! " + str(e))
            return False
        time.sleep(1)

    def clean_message(self, message):
        if type(message) == str:
            message = "".join([symbol for symbol in message if symbol in char_map])
        else:
            return None

        for symbol in ".?! ":
            message = message.replace(symbol*2, "")

        if not message:
            return None

        if len(message) >= 2:
            return message
        else:
            return None

    def messages_handler(self, event):
        log(current_time() + "[ + ] Новое сообщение от: " + str(event.peer_id))

        message = event.message
        peer_id = event.peer_id

        message = self.clean_message(message)
        if message:
            if peer_id not in self.queue:
                self.queue[peer_id] = {"message": "",
                                       "update_time": time.time()}

            if len(self.queue[peer_id]["message"]):
                if self.queue[peer_id]["message"][-1] not in ".?!":
                    self.queue[peer_id]["message"] += ","
                self.queue[peer_id]["message"] += " "

            self.queue[peer_id]["message"] += message
            self.queue[peer_id]["update_time"] = time.time()

    def sender(self):
        while True:
            for peer_id in self.queue.copy():
                self.process_user(peer_id)
                time.sleep(random.uniform(1, 2))

    def infinite_online(self):
        while True:
            self.set_online()
            time.sleep((5 * 60) - 1)

    def set_online(self, depth=0):
        try:
            self.bot.account.setOnline()
        except Exception as e:
            if depth >= 3:
                log("[ - ] Ошибка при попытке установить онлайн! " + str(e))
                return False
            self.auth()
            self.set_online(depth=depth + 1)

    def process_user(self, peer_id):
        if time.time() - self.queue[peer_id]["update_time"] >= random.randint(5, 12):
            threading.Thread(target=self.response, args=[peer_id], daemon=True).start()
        elif time.time() - self.queue[peer_id]["update_time"] >= random.uniform(0.0, 1.1):
            threading.Thread(target=self.make_activity, args=[peer_id], daemon=True).start()

    def context_cleaner(self):
        while True:
            for peer_id, info in self.context.copy().items():
                if time.time() - info["update_time"] >= 15 * 60:
                    del self.context[peer_id]

    def response(self, peer_id):
        if peer_id not in self.context:
            self.context[peer_id] = {"peer_messages":[], "replies":[], "update_time":0}

        if self.queue[peer_id]["message"][-1] not in ".?!":
            self.queue[peer_id]["message"] += "."
        self.queue[peer_id]["message"] += " "

        self.context[peer_id]["peer_messages"].append(self.queue[peer_id]["message"])
        self.context[peer_id]["update_time"] = time.time()
        del self.queue[peer_id]

        if len(self.context[peer_id]["peer_messages"]) > 5:
            self.context[peer_id]["peer_messages"] = self.context[peer_id]["peer_messages"][-5:]

        replie = self.ai.generate_replie(self.context[peer_id])

        if replie:
            self.context[peer_id]["replies"].append(replie)

            if len(self.context[peer_id]["replies"]) > 5:
                self.context[peer_id]["replies"] = self.context[peer_id]["replies"][-5:]

            log(current_time() + f"[ + ] Пользователь {peer_id} получит ответ: {replie} \n")

            try:
                self.bot.messages.send(peer_id=peer_id,
                                       random_id=random.randint(-1000000, 1000000),
                                       message=replie)
            except Exception as exception:
                if str(exception) != "Captcha Needed":
                    log(current_time() + f"[ ! ] Api error! Невозможно отправить сообщение к {peer_id}...")
                    del self.context[peer_id]
                    return None
        else:
            log(current_time() + "[ - ] Порфирьевич не смог выдать ответ!")

    def make_activity(self, peer_id, depth=0):
        try:
            self.bot.messages.markAsRead(peer_id=peer_id)
            time.sleep(random.uniform(0.5, 1.7))
            self.bot.messages.setActivity(peer_id=peer_id, type="typing")
        except Exception as e:
            if depth >= 3:
                log("[ - ] Ошибка при попытке прочитать сообщения! " + str(e))
                return False
            self.auth()
            self.make_activity(peer_id, depth=depth+1)
