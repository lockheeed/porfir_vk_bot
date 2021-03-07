import os.path
import json
from datetime import datetime


current_time = lambda: " [ " + str(datetime.now()).split(".")[0] + " ] "


def log(info):
    print(info)
    if not os.path.isfile("log.txt"):
        f = open("log.txt", "w")
    else:
        f = open("log.txt", "a")

    f.write(info + "\n")
    f.close()


def get_bulling_list():
    bulling_list = []
    try:
        with open("users.txt", "r") as f:
            for line in f.readlines():
                try:
                    id = line.split("#")[0].strip().replace(" ", "")
                    bulling_list.append(int(id))
                except Exception:
                    pass
            f.close()
    except Exception:
        with open("users.txt", "w") as f:
            f.close()
        return []
    else:
        return bulling_list


def load_tokens():
    if os.path.isfile("tokens.json"):
        with open("tokens.json", "r") as f:
            tokens = json.load(f)

    else:
        with open("tokens.json", "w") as f:
            json.dump({"vk_admin": "", "rucaptcha": ""}, f, indent=2)
        tokens = {"vk_admin": "", "rucaptcha": ""}

    vk_admin = tokens["vk_admin"]
    rucaptcha = tokens["rucaptcha"]

    if len(vk_admin) != 85:
        vk_admin = ""
    if len(rucaptcha) != 32:
        rucaptcha = ""

    return vk_admin, rucaptcha
