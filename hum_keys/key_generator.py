import requests
import json
import time
import random
import uuid
import datetime

# Конфигурации промоакций для различных игр
game_promo_configs = {
    "MyCloneArmy": {
        "appToken": "74ee0b5b-775e-4bee-974f-63e7f4d5bacb",
        "promoId": "fe693b26-b342-4159-8808-15e3ff7f8767"
    },
    "ChainCube2048": {
        "appToken": "d1690a07-3780-4068-810f-9b5bbf2931b2",
        "promoId": "b4170868-cef0-424f-8eb9-be0622e8e8e3"
    },
    "TrainMiner": {
        "appToken": "82647f43-3f87-402d-88dd-09a90025313f",
        "promoId": "c4480ac7-e178-4973-8061-9ed5b2e17954"
    },
    "BikeRide3D": {
        "appToken": "d28721be-fd2d-4b45-869e-9f253b554e50",
        "promoId": "43e35910-c168-4634-ad4f-52fd764a843f"
    },
    "MergeAway": {
        "appToken": "8d1cc2ad-e097-4b86-90ef-7a27e19fb833",
        "promoId": "dc128d28-c45b-411c-98ff-ac7726fbaea4"
    },
    "TwerkRace3D": {
        "appToken": "61308365-9d16-4040-8bb0-2f4a4c69074c",
        "promoId": "61308365-9d16-4040-8bb0-2f4a4c69074c"
    }     
}

# Выбор текущей конфигурации


# Генерация уникального clientId
def generate_client_id():
    timestamp = int(time.time() * 1000)
    random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(19)])
    return f"{timestamp}-{random_numbers}"

# Логин для получения clientToken
def login(client_id, current_app_config):
    url = "https://api.gamepromo.io/promo/login-client"
    payload = {
        "appToken": current_app_config["appToken"],
        "clientId": client_id,
        "clientOrigin": "ios"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["clientToken"]

# Генерация UUID
def generate_uuid():
    return str(uuid.uuid4())

# Регистрация события
def emulate_progress(client_token, current_app_config):
    print(client_token)
    url = "https://api.gamepromo.io/promo/register-event"
    payload = {
        "promoId": current_app_config["promoId"],
        "eventId": generate_uuid(),
        "eventOrigin": "undefined"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client_token}",
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
    except:
        print("bad_req")
        
    return response.json().get("hasCode", False)

# Генерация промокода
def generate_key(client_token, current_app_config):
    url = "https://api.gamepromo.io/promo/create-code"
    payload = {
        "promoId": current_app_config["promoId"]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client_token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["promoCode"]

# Функция для генерации ключей с эмуляцией прогресса
def generate_keys(key_count, game_name):
    current_app_config = game_promo_configs[game_name]
    client_id = generate_client_id()
    client_token = login(client_id, current_app_config)
    
    time_wait = 40
    keys = []
    
    for _ in range(key_count):
        counter = 0
        while emulate_progress(client_token, current_app_config) == False:
            if counter > 75:
                break
            time.sleep(time_wait + (random.choice([1, 2, 3, 7, 18])))
            counter += 1
        key = generate_key(client_token, current_app_config)
        keys.append(key)
        print(f"Generated key: {key}")
    
    return keys

