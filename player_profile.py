from helpers import bited_cell, empty_field
from ship import Ship


class PlayerProfile:

    def __init__(self, user_id):
        self.ships: list[Ship] = []
        self.ready_to_play: bool = False
        self.player_number: str = None
        self.player_id: int = user_id
        self.field: list = empty_field()
        self.enemy: PlayerProfile = None
        self.cell_to_attack: str = ''
        self.turn: bool = None
        self.shooted = []

    def find_ship_by_cell_attacked(self, cell: int) -> tuple[bool, Ship]:
        for sh in self.ships:
            if cell in sh.cells.keys():
                return True, sh
        return False, None

    def attack_ship(self, coord_to_attack: int, ship: Ship):
        ship.hit_cell(coord_to_attack)
        self.field[coord_to_attack] = bited_cell
        if ship.dead:
            ship.assign_nearby_cells_to_missed(self.field)

    def remove_ship_assignation(self):
        self.ships = []
        self.field = empty_field()
