import os
from dataclasses import dataclass

import dotenv


dotenv.load_dotenv('.env')


@dataclass
class Config:
    tg_token: str
    llm_url: str
    tokenizer_url: str
    authorization: str
    accept: str
    content_type: str


def load_config() -> Config:

    return Config(
        tg_token=os.getenv('TG_TOKEN'),
        llm_url=os.getenv('url2'),
        tokenizer_url=os.getenv('url1'),
        accept=os.getenv('accept'),
        content_type=os.getenv('content_type'),
        authorization=os.getenv('authorization'),
    )
