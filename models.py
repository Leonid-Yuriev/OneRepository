import settings
import requests
import json
import time


class Tokenizer:
    """
    Класс для получения актуального API-токена ГигаЧата

    Attributes:
        config (settings.Config): Настройки приложения
        last_time (int): Время последнего изменения токена
    """
    PAYLOAD = {'scope': 'GIGACHAT_API_PERS'}
    RqUID = "07e173e8-6b39-45d7-8021-06b8db7dd0cc"
    URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    def __init__(self, config: settings.Config, last_time: int = 0):
        self.last_time = last_time
        self.config = config
        self._token: str | None = None

    @property
    def expired(self):
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
            'RqUID': self.RqUID,
            'Authorization': f"Basic {self.config.authorization}"
        }

        response = requests.post(
            self.config.url1,
            headers=headers,
            data=self.PAYLOAD,
            verify=False,
        )

        return response.json().get("access_token")


class LLM:
    URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    def __init__(self, config: settings.Config,
                 temperature: float = 1.) -> None:
        self.tokenizer = Tokenizer(config)
        self.temperature: float = temperature
        self.url = config.url2

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
        answer = requests.post(self.url, headers=headers, data=payload, verify=False)
        return answer.json()["choices"][0]["message"]["content"]

