import json
import uuid
from pprint import pprint

import settings
import requests
import time


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
        return (self.last_time + 1500) < time.time()

    @property
    def token(self) -> str | None:
        if self._token is None or self.expired:
            self._token = self._get_new_token()
            self.last_time = time.time()
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

    def get_chat_completion(self, prompt: str) -> str | None:
        payload = {
            "model": "GigaChat",
            "messages": [{
                "role": "user",
                "content": prompt
                }],
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
            return response.json()["choices"][0]["message"]["content"]
        print(f"Произошла ошибка {response.status_code} во время получения ответа от GigaChat: {response.content}. \n{response.request.body}")

        return response.json()["choices"][0]["message"]["content"] if response.ok else None

