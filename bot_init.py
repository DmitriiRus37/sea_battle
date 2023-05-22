import config
import telebot

from player_profile import PlayerProfile

bot = telebot.TeleBot(config.telegram_bot_token)

players: list[PlayerProfile] = []

# 0: 'awaiting players',
# 1: 'assign_ships',
# 2: 'game_is_running',
# 3: 'game_finished'
stage: list = [0]
