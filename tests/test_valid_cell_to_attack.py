from unittest import TestCase
from actions import valid_cell_to_attack


class TestValidCellToAttack(TestCase):

    def test_valid_cell_to_attack(self):
        cell_to_test = 'а1'
        assert valid_cell_to_attack(cell_to_test)

        cell_to_test = ' а1'
        assert valid_cell_to_attack(cell_to_test)

        cell_to_test = '  а1'
        assert valid_cell_to_attack(cell_to_test)

        cell_to_test = '\nа1'
        assert valid_cell_to_attack(cell_to_test)
