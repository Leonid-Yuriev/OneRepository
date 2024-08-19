import os
from dataclasses import dataclass

import dotenv


dotenv.load_dotenv('.env')


@dataclass
class Config:
    tg_token: str
    gigachat_api_key: str


def load_config() -> Config:

    return Config(
        tg_token=os.getenv('TG_TOKEN'),
        gigachat_api_key=os.getenv('GIGACHAT_API_KEY'),
    )
