import settings
import requests
import json
import time


class Token:
    def __init__(self, last_time=0):
        self.last_time = last_time
        self.token = ""

    def token_withdrawal(self):
        if (self.last_time + 1500) < time.time():
            self.token = Token.new_token_create()
            self.last_time = time.time()
            return self.token
        else:
            return self.token

    @staticmethod
    def new_token_create():
        url = settings.url1

        payload = 'scope=GIGACHAT_API_PERS'
        headers = {
            'Content-Type': f'{settings.content_type}',
            'Accept': f'{settings.accept}',
            'RqUID': '07e173e8-6b39-45d7-8021-06b8db7dd0cc',
            'Authorization': f'{settings.authorization}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response.json()["access_token"]


def get_chat_completion(message):
    url = settings.url2

    payload = json.dumps({
        "model": "GigaChat",
        "messages": [{
            "role": "user",
            "content": message
            }],
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 200,
        "repetition_penalty": 1,
        "update_interval": 0
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token.token_withdrawal()}'

    }
    answer = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return answer.json()["choices"][0]["message"]["content"]


token = Token()
