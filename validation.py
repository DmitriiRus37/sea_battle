import math
from aiogram import types

from ship import Deck, append_nearby_cells


def validate_ship_cells(cur_ship_cells: list[int]) -> bool:
    cur_ship_cells.sort()
    if len(cur_ship_cells) == 1:
        return True
    direction_hor = True if math.fabs(cur_ship_cells[0] - cur_ship_cells[1]) == 1 else False

    for i in range(len(cur_ship_cells) - 1):
        cur_cell = cur_ship_cells[i]
        next_cell = cur_ship_cells[i + 1]
        if direction_hor:
            if math.fabs(cur_cell - next_cell) != 1:
                return False
        else:
            if math.fabs(cur_cell - next_cell) != 10:
                return False
    return True


async def validate_ships(busy_cells: set[int], ships: list[str], decks: Deck, message: types.Message) -> bool:
    res = True
    ships_count = len(ships)
    ships_count_required = 0

    match decks:
        case Deck.one: ships_count_required = 4
        case Deck.two: ships_count_required = 3
        case Deck.three: ships_count_required = 2
        case Deck.four: ships_count_required = 1

    if ships_count != ships_count_required:
        await message.answer('Введенное количество кораблей: ' + str(ships_count) + ', а необходимо: ' + str(ships_count_required))
        return False
    for i in range(len(ships)):
        sh = ships[i]
        cur_ship_cells = []
        for c in parse_ship_cells(sh):
            coord = get_int_coord(c)
            if coord < 1 or coord > 100:
                coord = 101
                res = False
            if coord in busy_cells:
                res = False
            cur_ship_cells.append(coord)
        if not validate_ship_cells(cur_ship_cells):
            res = False
        ships[i] = cur_ship_cells
        for cell in cur_ship_cells:
            append_nearby_cells(busy_cells, cell)
    return res


def parse_ship_cells(sh: str) -> list[str]:
    cells_list = []
    cur_cell = ''
    for ch in sh:
        if ch.isalpha():
            if cur_cell != '':
                cells_list.append(cur_cell)
            cur_cell = ch
        else:
            cur_cell += ch
    cells_list.append(cur_cell)
    return cells_list


def get_int_coord(cell: str) -> int:
    letter = cell[:1].lower()
    digit = int(cell[1:])
    return to_coord(letter, digit)


def to_coord(letter: str, digit: int) -> int:
    if digit < 1 or digit > 10:
        return 101
    match letter:
        case 'а':
            coord = digit
        case 'б':
            coord = 10 + digit
        case 'в':
            coord = 20 + digit
        case 'г':
            coord = 30 + digit
        case 'д':
            coord = 40 + digit
        case 'е':
            coord = 50 + digit
        case 'ж':
            coord = 60 + digit
        case 'з':
            coord = 70 + digit
        case 'и':
            coord = 80 + digit
        case 'к':
            coord = 90 + digit
        case _:
            coord = 101
    return coord
