from telebot import types
from telebot.types import Message

from bot_init import bot, players, stage
from cells import ship_cell
from helpers import get_monospace_text, get_field, check_turn, get_user_by_id, \
    cells_set, get_stage_ship_decks_2_text, get_stage_ship_decks_3_text, get_stage_ship_decks_4_text
from ship import Ship
from validation import validate_ships, to_coord


def assign_ships(message):
    if stage.v != 1:
        bot.send_message(message.chat.id, 'Расставлять корабли еще рано. Ожидайте соперника')
        return

    text_list_ships = message.text.lower().split()
    current_player = get_user_by_id(message.chat.id)

    ships_to_assign = current_player.stage_assign_decks

    match ships_to_assign:
        case 1:
            res = assign_s(current_player, text_list_ships, message, 1)
            if res:
                current_player.stage_assign_decks = 2
                bot.send_message(message.chat.id, get_stage_ship_decks_2_text(current_player), parse_mode='html')
        case 2:
            res = assign_s(current_player, text_list_ships, message, 2)
            if res:
                current_player.stage_assign_decks = 3
                bot.send_message(message.chat.id, get_stage_ship_decks_3_text(current_player), parse_mode='html')
        case 3:
            res = assign_s(current_player, text_list_ships, message, 3)
            if res:
                current_player.stage_assign_decks = 4
                bot.send_message(message.chat.id, get_stage_ship_decks_4_text(current_player), parse_mode='html')
        case 4:
            res = assign_s(current_player, text_list_ships, message, 4)
            if res:
                keyboard = types.InlineKeyboardMarkup()
                key_commit = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='commit_ships')
                key_reassign = types.InlineKeyboardButton(text='Ввести заново 🔁', callback_data='reassign_ships')
                keyboard.add(key_commit)
                keyboard.add(key_reassign)
                bot.send_message(message.chat.id,
                                 get_monospace_text(get_field(current_player.field))+
                                 '\nХотите продолжить или заново расставить корабли?',
                                 reply_markup=keyboard,
                                 parse_mode='html')


def assign_s(current_player, text_list_ships, message, decks):
    f_working = current_player.field
    ships = text_list_ships

    busy_cells = current_player.busy_cells.copy()
    if not validate_ships(busy_cells, ships, decks):
        decks_str = None
        match decks:
            case 1:
                decks_str = 'однопалубные корабли'
            case 2:
                decks_str = 'двухпалубные корабли'
            case 3:
                decks_str = 'трехпалубные корабли'
            case 4:
                decks_str = 'четырехпалубный корабль'

        bot.send_message(message.chat.id,
                         'У вас ошибка, попробуйте расставить '+decks_str+' заново\n' +
                         get_monospace_text(get_field(f_working)),
                         parse_mode='html')
        return False

    current_player.busy_cells = busy_cells
    cells_ships = set()
    for sh in ships:
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
    return True


def valid_cell_to_attack(text):
    return text.split()[0].lower() in cells_set


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
    cell_to_attack = msg.text
    cur_pl = get_user_by_id(msg.chat.id)
    if not check_turn(cur_pl):
        bot.send_message(msg.chat.id, 'Сейчас ходит ваш оппонент. Дождитесь своей очереди')
        return
    letter, digit = cell_to_attack[0].lower(), int(cell_to_attack[1:])
    coord_to_attack = to_coord(letter, digit)
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
