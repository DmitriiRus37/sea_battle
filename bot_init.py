import config
import telebot

from party import Party


class WrapValue:
    def __init__(self, v):
        self.v = v


bot = telebot.TeleBot(config.telegram_bot_token)

parties: list[Party] = []
