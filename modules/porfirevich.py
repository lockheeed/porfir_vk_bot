import requests
import random
import time

latin = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"

class Porfirevich(object):
    def __init__(self):
        pass

    def generate_replie(self, context):
        url = "https://pelevin.gpt.dobro.ai/generate/"

        generator_base, context_has_latin = self.generate_context_base(context)

        payload = {"prompt": generator_base, "length": self.get_length()}

        while True:
            response = requests.post(url, json=payload, timeout=13)
            if response.status_code == 200:
                replies = response.json()["replies"]
                random.shuffle(replies)

                for replie in replies:
                    normalized_replie = replie[1:].split("q:")[0].split("–")[0]
                    if self.validate_replie(normalized_replie[1:], context_has_latin):
                        if normalized_replie[-1] == ".":
                            return normalized_replie[:-1]
                        else:
                            return normalized_replie

                time.sleep(1.1)

            else:
                print(" [ - ] Ошибка сервера! Порфирьевич послал нас! " + response.text)
                return None

    def generate_context_base(self, context):
        base = ""
        context_has_latin = False
        peers_messages_length = len(context["peer_messages"])
        for i in range(peers_messages_length):
            if len([symbol for symbol in context["peer_messages"][i] if symbol in latin]) > 0:
                context_has_latin = True

            base += "Q: " + context["peer_messages"][i] + "\nA:"
            if i < peers_messages_length - 1:
                base += " " + context["replies"][i] + "\n"
        return base, context_has_latin

    def validate_replie(self, replie, context_may_has_latin):
        bad_symbols = "\\:"
        if len([symbol for symbol in replie if symbol in latin]) > 0:
            context_has_latin = True
        else:
            context_has_latin = False

        if len(replie) > 1 and replie[0] not in "«»–-!?.,: " and len([symbol for symbol in replie if symbol in bad_symbols]) == 0 and (not context_has_latin or (context_has_latin == context_may_has_latin)):
            return True
        return False

    def get_length(self):
        value = random.randint(0, 100)
        if value >= 80:
            return random.randint(20, 60)
        else:
            return random.randint(5, 20)
