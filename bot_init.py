import config
import telebot

from player_profile import PlayerProfile


class WrapValue:
    def __init__(self, v):
        self.v = v


bot = telebot.TeleBot(config.telegram_bot_token)

players: list[PlayerProfile] = []

# 0: 'awaiting players',
# 1: 'assign_ships',
# 2: 'game_is_running',
# 3: 'game_finished'
stage: WrapValue = WrapValue(0)
