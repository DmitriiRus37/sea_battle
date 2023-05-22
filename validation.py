import math


def validate_ship_cells(cur_ship_cells: list[int]) -> bool:
    cur_ship_cells.sort()
    if len(cur_ship_cells) == 1:
        return True
    direction_hor = True if math.fabs(cur_ship_cells[0] - cur_ship_cells[1]) == 1 else False

    for i in range(len(cur_ship_cells) - 1):
        cur_cell = cur_ship_cells[0]
        next_cell = cur_ship_cells[1]
        if direction_hor:
            if math.fabs(cur_cell - next_cell) != 1:
                return False
        else:
            if math.fabs(cur_cell - next_cell) != 10:
                return False
    return True


def validate_ship(busy_cells: set[int], ships: list[str]) -> bool:
    res = True
    for i in range(len(ships)):
        sh = ships[i]
        cur_ship_cells = []
        for c in parse_ship_cells(sh):
            valid, coord = get_int_coord(busy_cells, c)
            if not valid:
                res = False
            cur_ship_cells.append(coord)
        if not validate_ship_cells(cur_ship_cells):
            res = False
        ships[i] = cur_ship_cells
        for cell in cur_ship_cells:
            append_nearby_cells(busy_cells, cell)
    return res


def parse_ship_cells(sh: str):
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


def get_int_coord(busy_cells: set[int], cell: str) -> tuple[bool, int]:
    letter = cell[:1].lower()
    digit = int(cell[1:])
    coord = to_coord(letter, digit)
    if coord < 1 or coord > 100:
        return False, 101
    if coord in busy_cells:
        return False, coord
    return True, coord


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
