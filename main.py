from telebot import TeleBot
from telebot.types import Message

from models import LLM
from models import User
from settings import load_config, Config


config: Config = load_config()
bot = TeleBot(config.tg_token)
llm = LLM(config)


@bot.message_handler(commands=['help', 'start'])
def welcome(message: Message) -> None:
    User.create_chat_id(message.chat.id)

    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}.'
                                      f' Я telegram bot, который поможет вам '
                                      f'во всех ваших вопросах!')
    bot.send_message(message.chat.id, 'Вы можете задавать вопросы когда '
                                      'угодно!')



@bot.message_handler(func=lambda message: True)
def user_question(message: Message) -> Message:
    User.add_question(message.chat.id, message.text)

    answer = llm.get_chat_completion(message.chat.id)
    if answer:
        return bot.send_message(message.chat.id, answer)
    return bot.send_message(message.chat.id, "Произошла ошибка :(")


def main() -> None:
    print("Запуск бота")
    return bot.polling(True)


if __name__ == '__main__':
    main()
