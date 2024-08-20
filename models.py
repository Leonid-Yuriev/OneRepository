import json
import uuid

import settings
import requests
from time import time


class Tokenizer:
    """
    Класс для получения актуального API-токена ГигаЧата

    Attributes:
        config (settings.Config): Настройки приложения
        last_time (int): Время последнего изменения токена
    """
    PAYLOAD = {'scope': 'GIGACHAT_API_PERS'}
    URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    def __init__(self, config: settings.Config):
        self.last_time = 0
        self.config = config
        self._token: str | None = None

    @property
    def expired(self) -> bool:
        return (self.last_time + 1500) < time()

    @property
    def token(self) -> str | None:
        if self._token is None or self.expired:
            self._token = self._get_new_token()
            self.last_time = time()
        return self._token

    def _get_new_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f"Basic {self.config.gigachat_api_key}"
        }

        response = requests.post(
            self.URL,
            headers=headers,
            data=self.PAYLOAD,
            verify=False,
        ).json()

        self.expires_at = response.get("expires_at")

        return response.get("access_token")


class LLM:
    URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    def __init__(self, config: settings.Config,
                 temperature: float = 1) -> None:
        self.tokenizer = Tokenizer(config)
        self.temperature: float = temperature

    def get_chat_completion(self, chat_id) -> str | None:
        payload = {
            "model": "GigaChat",
            "messages": User.get_messages(chat_id),
            "temperature": self.temperature,
            "top_p": 0.1,
            "n": 1,
            "stream": False,
            "max_tokens": 200,
            "repetition_penalty": 1,
            "update_interval": 0
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.tokenizer.token}'
        }

        response = requests.post(
            self.URL,
            headers=headers,
            json=payload,
            verify=False,
        )

        if response.ok:
            User.add_answer(chat_id, response.json()["choices"][0]["message"]["content"])
            return response.json()["choices"][0]["message"]["content"]
        print(f"Произошла ошибка {response.status_code} во время получения ответа от GigaChat:"
              f" {response.content}. \n{response.request.body}")

        User.add_answer(chat_id, " ")
        return response.json()["choices"][0]["message"]["content"] if response.ok else None


class User:

    @staticmethod
    def create_chat_id(chat_id):
        if User.check_chat_id(chat_id):
            with open('sw_templates.json') as f:
                templates = json.load(f)

            templates["chat_id"].append(chat_id)
            templates["messages"].append([time()])

            with open('sw_templates.json', 'w') as f:
                f.write(json.dumps(templates))


    @staticmethod
    def check_chat_id(chat_id):
        with open('sw_templates.json') as f:
            templates = json.load(f)

        for i in range(len(templates["chat_id"])):
            if chat_id == templates["chat_id"][i]:
                return False

        return True


    @staticmethod
    def add_question(chat_id, question):
        with open('sw_templates.json') as f:
            templates = json.load(f)

            for i in range(len(templates["chat_id"])):
                if chat_id == templates["chat_id"][i]:
                    if templates["messages"][i][-1] + 1800 > time():
                        templates["messages"][i].pop(-1)
                        templates["messages"][i].append({"role": "user", "content": question})
                    else:
                        templates["messages"][i].clear()
                        templates["messages"][i].append({"role": "user", "content": question})

        with open('sw_templates.json', 'w') as f:
            json.dump(templates, f)


    @staticmethod
    def add_answer(chat_id, answer):
        with open('sw_templates.json') as f:
            templates = json.load(f)

            for i in range(len(templates["chat_id"])):
                if chat_id == templates["chat_id"][i]:
                    templates["messages"][i].append({"role": "assistant", "content": answer})
                    templates["messages"][i].append(time())

        with open('sw_templates.json', 'w') as f:
            json.dump(templates, f)


    @staticmethod
    def get_messages(chat_id):
        with open('sw_templates.json') as f:
            templates = json.load(f)

            for i in range(len(templates["chat_id"])):
                if chat_id == templates["chat_id"][i]:
                    return templates["messages"][i]