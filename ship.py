import enum

from cells import bited_cell, missed_cell


class Ship:

    def __init__(self, cells: list):
        self.cells: dict = {}
        self.cells_to_map(cells)
        self.dead: bool = False
        self.count_of_decks = len(self.cells)

    def cells_to_map(self, cells: list):
        for c in cells:
            self.cells[c] = True

    def assign_nearby_cells_to_missed(self, field) -> set:
        missed_cells = set()
        # заполнить все соседние ячейки и ячейки корабля
        for c in self.cells.keys():
            append_nearby_cells(missed_cells, c)

        # все ячейки корабля будут помечены как "ранен"
        for c in self.cells.keys():
            field[c] = bited_cell
            missed_cells.remove(c)

        # все соседние ячейки будут помечены как "мимо"
        for c in missed_cells:
            field[c] = missed_cell
        return missed_cells.union(self.cells.keys())

    def check_if_dead(self):
        for v in self.cells.values():
            if v:
                return
        self.dead = True

    def hit_cell(self, cell):
        self.cells[cell] = False
        self.check_if_dead()


class Deck(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4


def append_nearby_cells(busy_cells: set[int], coord: int) -> None:
    busy_cells.add(coord)
    if coord == 1:
        busy_cells.add(coord + 1)
        busy_cells.add(coord + 10)
        busy_cells.add(coord + 10 + 1)
    elif coord == 10:
        busy_cells.add(coord - 1)
        busy_cells.add(coord + 10)
        busy_cells.add(coord + 10 - 1)
    elif coord == 91:
        busy_cells.add(coord + 1)
        busy_cells.add(coord - 10)
        busy_cells.add(coord - 10 + 1)
    elif coord == 100:
        busy_cells.add(coord - 1)
        busy_cells.add(coord - 10)
        busy_cells.add(coord - 10 - 1)
    elif coord < 10:
        busy_cells.add(coord - 1)
        busy_cells.add(coord + 1)
        busy_cells.add(coord + 10)
        busy_cells.add(coord + 10 + 1)
        busy_cells.add(coord + 10 - 1)
    elif coord > 91:
        busy_cells.add(coord - 1)
        busy_cells.add(coord + 1)
        busy_cells.add(coord - 10)
        busy_cells.add(coord - 10 + 1)
        busy_cells.add(coord - 10 - 1)
    elif coord % 10 == 1:
        busy_cells.add(coord + 1)
        busy_cells.add(coord + 10)
        busy_cells.add(coord - 10)
        busy_cells.add(coord + 10 + 1)
        busy_cells.add(coord - 10 + 1)
    elif coord % 10 == 0:
        busy_cells.add(coord - 1)
        busy_cells.add(coord + 10)
        busy_cells.add(coord - 10)
        busy_cells.add(coord + 10 - 1)
        busy_cells.add(coord - 10 - 1)
    else:
        busy_cells.add(coord + 1)
        busy_cells.add(coord - 1)
        busy_cells.add(coord + 10)
        busy_cells.add(coord - 10)
        busy_cells.add(coord + 10 + 1)
        busy_cells.add(coord + 10 - 1)
        busy_cells.add(coord - 10 + 1)
        busy_cells.add(coord - 10 - 1)
