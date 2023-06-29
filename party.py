from bot_init import WrapValue
from player_profile import PlayerProfile


class Party:

    def __init__(self):
        self.players: list[PlayerProfile] = []
        # 0: 'awaiting players',
        # 1: 'assign_ships',
        # 2: 'game_is_running',
        # 3: 'game_finished'
        self.stage: WrapValue = WrapValue(0)
