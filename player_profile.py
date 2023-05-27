from cells import bited_cell, empty_field, missed_cell
from ship import Ship


class PlayerProfile:

    def __init__(self, user_id):
        self.ships: list[Ship] = []
        self.ready_to_play: bool = False
        self.player_number: str = None
        self.player_id: int = user_id
        self.field: list = empty_field()
        self.field_to_enemy: list = empty_field()
        self.enemy: PlayerProfile = None
        self.cell_to_attack: str = ''
        self.turn: bool = None
        self.cells_attacked = set()

    def find_ship_by_cell_attacked(self, cell: int) -> tuple[bool, Ship]:
        for sh in self.ships:
            if cell in sh.cells.keys():
                return True, sh
        return False, None

    def attack_ship(self, coord_to_attack: int, ship: Ship) -> bool:
        ship.hit_cell(coord_to_attack)
        self.field[coord_to_attack] = bited_cell
        self.field_to_enemy[coord_to_attack] = bited_cell
        if ship.dead:
            nearby_ship_cells = ship.assign_nearby_cells_to_missed(self.field)
            self.cells_attacked.update(nearby_ship_cells)
            ship.assign_nearby_cells_to_missed(self.field_to_enemy)
            return True
        else:
            self.cells_attacked.add(coord_to_attack)
            return False

    def remove_ship_assignation(self):
        self.ships = []
        self.field = empty_field()
        self.field_to_enemy = empty_field()

    def all_ships_dead(self):
        for sh in self.ships:
            if not sh.dead:
                return False
        return True

    def attack_sea(self, coord_to_attack: int):
        self.field[coord_to_attack] = missed_cell
        self.field_to_enemy[coord_to_attack] = missed_cell
        self.cells_attacked.add(coord_to_attack)

    def repeated_cell(self, coord_to_attack):
        return coord_to_attack in self.cells_attacked
