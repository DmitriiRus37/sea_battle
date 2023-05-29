from unittest import TestCase
from actions import valid_cell_to_attack


class TestValidCellToAttack(TestCase):

    def test_valid_cell_to_attack(self):
        assert valid_cell_to_attack('а1')
        assert valid_cell_to_attack(' а1')
        assert valid_cell_to_attack('  а1  ')
        assert valid_cell_to_attack('\nа1       \n\t')
        assert not valid_cell_to_attack('а11')
        assert not valid_cell_to_attack('й10')
        assert not valid_cell_to_attack('а 1')
