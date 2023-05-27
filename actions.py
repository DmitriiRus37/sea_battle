from telebot import types
from telebot.types import Message

import re
from bot_init import bot, players, stage
from cells import ship_cell
from helpers import get_monospace_text, get_field, check_turn, get_user_by_id, \
    cells_set
from ship import Ship
from validation import validate_ship, to_coord


def assign_ships(message):
    if stage.v != 1:
        bot.send_message(message.chat.id, 'Ждите. Расставлять корабли еще рано. Ожидайте второго игрока')
        return
    current_player = get_user_by_id(message.chat.id)

    text_list_ships = message.text.lower().split()

    ships_1 = []
    ships_2 = []
    ships_3 = []
    ships_4 = []
    for i in range(len(text_list_ships)):
        if text_list_ships[i] == '1:':
            ships_1.append(text_list_ships[i + 1])
            ships_1.append(text_list_ships[i + 2])
            ships_1.append(text_list_ships[i + 3])
            ships_1.append(text_list_ships[i + 4])
            del text_list_ships[i:i + 5]
            break

    for i in range(len(text_list_ships)):
        if text_list_ships[i] == '2:':
            ships_2.append(text_list_ships[i + 1])
            ships_2.append(text_list_ships[i + 2])
            ships_2.append(text_list_ships[i + 3])
            del text_list_ships[i:i + 4]
            break
    for i in range(len(text_list_ships)):
        if text_list_ships[i] == '3:':
            ships_3.append(text_list_ships[i + 1])
            ships_3.append(text_list_ships[i + 2])
            del text_list_ships[i:i + 3]
            break
    for i in range(len(text_list_ships)):
        if text_list_ships[i] == '4:':
            ships_4.append(text_list_ships[i + 1])
            del text_list_ships[i:i + 2]
            break

    busy_c = set()
    v1 = validate_ship(busy_c, ships_1)
    v2 = validate_ship(busy_c, ships_2)
    v3 = validate_ship(busy_c, ships_3)
    v4 = validate_ship(busy_c, ships_4)
    if v1 and v2 and v3 and v4:
        validated = True
    else:
        validated = False
    f_working = current_player.field
    cells_ships = set()
    for sh in ships_1 + ships_2 + ships_3 + ships_4:
        current_player.ships.append(Ship(sh))
        if isinstance(sh, list):
            [cells_ships.add(cell) for cell in sh]
        elif isinstance(sh, int):
            cells_ships.add(sh)
        else:
            pass
    for i in range(len(f_working)):
        if i in cells_ships:
            f_working[i] = ship_cell

    if not validated:
        bot.send_message(message.chat.id, 'У вас ошибка, попробуйте расставить корабли заново\n' +
                         get_monospace_text(get_field(f_working)),
                         parse_mode='html')
        current_player.remove_ship_assignation()
        return

    keyboard = types.InlineKeyboardMarkup()
    key_commit = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='commit_ships')
    key_reassign = types.InlineKeyboardButton(text='Ввести заново 🔁', callback_data='reassign_ships')
    keyboard.add(key_commit)
    keyboard.add(key_reassign)
    bot.send_message(message.chat.id, get_monospace_text(get_field(f_working)),
                     parse_mode='html',
                     reply_markup=keyboard)


def valid_cell_to_attack(text):
    return True if 2 <= len(text) <= 3 and text.lower() in cells_set else False


def attack_cell(msg: Message) -> None:
    if stage.v != 2:
        bot.send_message(msg.chat.id, 'Игра еще не начата.')
        return
    cur_pl = get_user_by_id(msg.chat.id)
    if not check_turn(cur_pl):
        bot.send_message(msg.chat.id, 'Сейчас ходит ваш оппонент. Дождитесь своей очереди')
        return
    if not valid_cell_to_attack(msg.text):
        bot.send_message(msg.chat.id, 'Невалидная ячейка. Введите еще раз')
        return
    cur_pl.cell_to_attack = msg.text
    cur_pl = get_user_by_id(msg.chat.id)
    if not check_turn(cur_pl):
        bot.send_message(msg.chat.id, 'Сейчас ходит ваш оппонент. Дождитесь своей очереди')
        return
    letter, digit = cur_pl.cell_to_attack[0].lower(), int(cur_pl.cell_to_attack[1:])
    coord_to_attack = to_coord(letter, digit)
    cur_pl.cell_to_attack = ''
    en = cur_pl.enemy
    if en.repeated_cell(coord_to_attack):
        bot.send_message(msg.chat.id, 'В эту ячейку нельзя стрелять')
        return
    found, sh = en.find_ship_by_cell_attacked(coord_to_attack)

    bot.send_message(cur_pl.player_id, 'Вы стреляете: ' + letter + str(digit))
    bot.send_message(en.player_id, 'Противник стреляет : ' + letter + str(digit))
    if found:
        dead_ship = en.attack_ship(coord_to_attack, sh)
        if en.all_ships_dead():
            del players[:]
            stage.v = 3
            bot.send_message(cur_pl.player_id, 'Вы победили. Вы потопили все вражеские корабли')
            bot.send_message(en.player_id, 'Вы проиграли. Ваши корабли потоплены')
            # TODO
            return

        if dead_ship:
            attack_msg = 'Корабль противника потоплен!\n'
            attack_enemy_msg = 'Ваш корабль потоплен!\n'
        else:
            attack_msg = 'Попадание по врагу!\n'
            attack_enemy_msg = 'По вам попали!\n'

        bot.send_message(cur_pl.player_id, attack_msg +
                         '\nВаше поле:\n' + get_monospace_text(get_field(cur_pl.field)) +
                         '\nПоле врага:\n' + get_monospace_text(get_field(en.field_to_enemy)) +
                         '\nВыберите ячейку для атаки',
                         parse_mode='html')
        bot.send_message(en.player_id,
                         attack_enemy_msg +
                         '\nВаше поле:\n' + get_monospace_text(get_field(en.field)) +
                         '\nПоле врага:\n' + get_monospace_text(get_field(cur_pl.field_to_enemy)) +
                         '\nОжидайте хода врага',
                         parse_mode='html')
    else:
        cur_pl.turn = False
        en.turn = True
        en.attack_sea(coord_to_attack)
        bot.send_message(cur_pl.player_id, 'Вы промахнулись.\n' +
                         '\nВаше поле:\n' + get_monospace_text(get_field(cur_pl.field)) +
                         '\nПоле врага:\n' + get_monospace_text(get_field(en.field_to_enemy)) +
                         '\nОжидайте хода врага',
                         parse_mode='html'
                         )
        bot.send_message(en.player_id, 'Противник промахнулся.\n' +
                         '\nВаше поле:\n' + get_monospace_text(get_field(en.field)) +
                         '\nПоле врага:\n' + get_monospace_text(get_field(cur_pl.field_to_enemy)) +
                         '\nВыберите ячейку для атаки',
                         parse_mode='html')
