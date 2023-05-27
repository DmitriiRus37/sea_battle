from helpers import bited_cell, missed_cell
from validation import append_nearby_cells


class Ship:

    def __init__(self, cells):
        self.cells = {}
        self.cells_to_map(cells)
        self.dead = False
        self.count_of_decks = len(self.cells)

    def cells_to_map(self, cells):
        for c in cells:
            self.cells[c] = True

    def assign_nearby_cells_to_missed(self, field):
        missed_cells = []
        for c in self.cells.keys():
            append_nearby_cells(missed_cells, c)
        for c in self.cells.keys():
            field[c] = bited_cell
            missed_cells.remove(c)
        for c in missed_cells:
            field[c] = missed_cell


    def check_if_dead(self):
        for v in self.cells.values():
            if v:
                return
        self.dead = True

    def hit_cell(self, cell):
        self.cells[cell] = False
        self.check_if_dead()

