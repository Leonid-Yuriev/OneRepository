import GigaChat
import settings
import telebot

bot = telebot.TeleBot(settings.tg_token)


@bot.message_handler(commands=['help', 'start'])
def main(message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}.'
                                      f' Я telegram bot, который поможет вам во всех ваших вопросах!')
    bot.send_message(message.chat.id, 'Вы можете задавать вопросы когда угодно!')


@bot.message_handler()
def user_question(message):

    answer = GigaChat.get_chat_completion(message.text)
    bot.send_message(message.chat.id, answer)


bot.polling(True)
