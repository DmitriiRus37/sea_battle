from bot_init import parties
from player_profile import PlayerProfile
from wrap import WrapValue


class Party:

    def __init__(self):
        self.players: list[PlayerProfile] = []
        # 0: 'awaiting players',
        # 1: 'assign_ships',
        # 2: 'game_is_running',
        # 3: 'game_finished'
        self.stage: WrapValue = WrapValue(0)

    @staticmethod
    def get_current_party_by_player(player: PlayerProfile):
        for p in parties:
            for pl in p.players:
                if pl == player:
                    return p
        return None
