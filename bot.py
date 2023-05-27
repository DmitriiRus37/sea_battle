from telebot import types
from telebot.types import CallbackQuery

from bot_init import bot
from helpers import get_field, ship_cell
from player_profile import PlayerProfile
from ship import Ship
from validation import valid_sh, to_coord

players: list[PlayerProfile] = []

stages = {
    0: 'game_not_started',
    1: 'assign_ships',
    2: 'game_started',
    3: 'game_finished'
}

stage: int = 0


def get_monospace_text(text: str) -> str:
    return '<code>{0}</code>'.format(text)


def send_start_message(message):
    if len(players) == 0:
        player_1 = PlayerProfile(message.chat.id)
        players.append(player_1)
        player_1.player_number = 'first'
        bot.send_message(message.chat.id, 'Вы первый. Ожидайте второго игрока')
    elif len(players) == 1:
        player_2 = PlayerProfile(message.chat.id)
        player_2.enemy = players[0]
        players[0].enemy = player_2
        players.append(player_2)
        player_2.player_number = 'first'
        bot.send_message(message.chat.id, 'Вы второй.')
        stage = 1

        bot.send_message(players[0].player_id,
                         get_monospace_text(get_field(players[0].field)) +
                         '\nПоставьте корабли на свое поле. Ввод осуществить следующим образом:\n\n'
                         'ввод\n'
                         '1: а1 б3 в5 г7\n'
                         '2: д1д2 г1г2 a1б1\n'
                         '3: ж1ж2ж3 е1е2е3\n'
                         '4: а1а2а3а4', parse_mode='html')

        bot.send_message(message.chat.id,
                         get_monospace_text(get_field(players[0].field)) +
                         '\nПоставьте корабли на свое поле. Ввод осуществить следующим образом:\n\n'
                         'ввод\n'
                         '1: а1 б3 в5 г7\n'
                         '2: д1д2 г1г2 a1б1\n'
                         '3: ж1ж2ж3 е1е2е3\n'
                         '4: а1а2а3а4', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Уже идет игра. Подождите')


def assign_ships(message):
    current_player = get_user_by_id(message.chat.id)
    text_list = message.text.split('\n')
    text_list_working = []
    for el in text_list:
        l = el.split(' ')
        for e in l:
            text_list_working.append(e)
    text_list_working = [el for el in text_list_working if el.strip()]

    sh_1 = []
    for i in range(len(text_list_working)):
        if text_list_working[i] == '1:':
            sh_1.append(text_list_working[i + 1])
            sh_1.append(text_list_working[i + 2])
            sh_1.append(text_list_working[i + 3])
            sh_1.append(text_list_working[i + 4])
            break

    sh_2 = []
    for i in range(len(text_list_working)):
        if text_list_working[i] == '2:':
            sh_2.append(text_list_working[i + 1])
            sh_2.append(text_list_working[i + 2])
            sh_2.append(text_list_working[i + 3])
            break

    sh_3 = []
    for i in range(len(text_list_working)):
        if text_list_working[i] == '3:':
            sh_3.append(text_list_working[i + 1])
            sh_3.append(text_list_working[i + 2])
            break

    sh_4 = []
    for i in range(len(text_list_working)):
        if text_list_working[i] == '4:':
            sh_4.append(text_list_working[i + 1])
            break

    busy_c = []
    if valid_sh(busy_c, sh_1) and valid_sh(busy_c, sh_2) and valid_sh(busy_c, sh_3) and valid_sh(busy_c, sh_4):
        validated = True
    else:
        validated = False
    if not validated:
        bot.send_message(message.chat.id, 'У вас ошибка, попробуйте расставить корабли заново')
    else:
        f_working = current_player.field
        cells_ships = []
        for sh in sh_1 + sh_2 + sh_3 + sh_4:
            current_player.ships.append(Ship(sh))
            if isinstance(sh, list):
                [cells_ships.append(cell) for cell in sh]
            elif isinstance(sh, int):
                cells_ships.append(sh)
        for i in range(len(f_working)):
            if i in cells_ships:
                f_working[i] = ship_cell
        keyboard = types.InlineKeyboardMarkup()
        key_commit = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='commit_ships')
        key_reassign = types.InlineKeyboardButton(text='Ввести заново 🔁', callback_data='reassign_ships')
        keyboard.add(key_commit)
        keyboard.add(key_reassign)
        bot.send_message(message.chat.id, get_monospace_text(get_field(f_working)), parse_mode='html',
                         reply_markup=keyboard)


@bot.message_handler(commands=['start'])  # handle the command "Start"
def start_welcome(message):
    send_start_message(message)


@bot.message_handler(content_types=['text'])  # handle with text
def handle_text(message):
    message_text_array = message.text.split('\n')

    match message_text_array[0]:
        case "ввод":
            assign_ships(message)
        case _:
            "ЗАГЛУШКА"


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: CallbackQuery):
    if call.data == "commit_ships":
        current_player = get_user_by_id(call.from_user.id)
        current_player.ready_to_play = True
        current_player.turn = True
        bot.send_message(call.message.chat.id, 'Принято')
        bot.send_message(call.message.chat.id, 'Игра начинается.\n'
                                               'Вы ходите первым.\n'
                                               'Выберите букву', reply_markup=letter_keyboard())
    elif call.data == "reassign_ships":
        current_player = get_user_by_id(call.from_user.id)
        current_player.remove_ship_assignation()
        bot.send_message(call.from_user.id,
                         'Поставьте корабли на свое поле. Ввод осуществить следующим образом:\n\n'
                         'ввод\n'
                         '1: а1 б3 в5 г7\n'
                         '2: д1д2 г1г2 a1б1\n'
                         '3: ж1ж2ж3 е1е2е3\n'
                         '4: а1а2а3а4')
    elif call.data == 'letter_1':
        handle_letter(call)
    elif call.data == 'letter_2':
        handle_letter(call)
    elif call.data == 'letter_3':
        handle_letter(call)
    elif call.data == 'letter_4':
        handle_letter(call)
    elif call.data == 'letter_5':
        handle_letter(call)
    elif call.data == 'letter_6':
        handle_letter(call)
    elif call.data == 'letter_7':
        handle_letter(call)
    elif call.data == 'letter_8':
        handle_letter(call)
    elif call.data == 'letter_9':
        handle_letter(call)
    elif call.data == 'letter_10':
        handle_letter(call)
    elif call.data == 'digit_1':
        handle_digit(call)
    elif call.data == 'digit_2':
        handle_digit(call)
    elif call.data == 'digit_3':
        handle_digit(call)
    elif call.data == 'digit_4':
        handle_digit(call)
    elif call.data == 'digit_5':
        handle_digit(call)
    elif call.data == 'digit_6':
        handle_digit(call)
    elif call.data == 'digit_7':
        handle_digit(call)
    elif call.data == 'digit_8':
        handle_digit(call)
    elif call.data == 'digit_9':
        handle_digit(call)
    elif call.data == 'digit_10':
        handle_digit(call)


def handle_letter(call):
    current_player = get_user_by_id(call.from_user.id)
    if not check_turn(current_player):
        bot.send_message(call.message.chat.id, 'Сейчас ходит ваш оппонент. Дождитесь своей очереди')
        return
    current_player.cell_to_attack = 'а'
    bot.send_message(call.message.chat.id, 'Выберите число', reply_markup=digit_keyboard())


def handle_digit(call):
    current_player = get_user_by_id(call.from_user.id)
    if not check_turn(current_player):
        bot.send_message(call.message.chat.id, 'Сейчас ходит ваш оппонент. Дождитесь своей очереди')
        return
    letter = current_player.cell_to_attack
    current_player.cell_to_attack = ''
    digit = 1
    coord_to_attack = to_coord(letter, digit)
    enemy = current_player.enemy
    res, sh = enemy.find_ship_by_cell_attacked(coord_to_attack)
    if res:
        enemy.attack_ship(coord_to_attack, sh)
        bot.send_message(call.message.chat.id, 'Есть попадание!')
        current_player.turn = False
        enemy.turn = True
        bot.send_message(call.message.chat.id, get_monospace_text(get_field(enemy.field)), parse_mode='html')


def get_user_by_id(p_id: int) -> PlayerProfile:
    for p in players:
        if p.player_id == p_id:
            return p
    return None


def digit_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_1 = types.InlineKeyboardButton(text='1', callback_data='digit_1')
    btn_2 = types.InlineKeyboardButton(text='2', callback_data='digit_2')
    btn_3 = types.InlineKeyboardButton(text='3', callback_data='digit_3')
    btn_4 = types.InlineKeyboardButton(text='4', callback_data='digit_4')
    btn_5 = types.InlineKeyboardButton(text='5', callback_data='digit_5')
    btn_6 = types.InlineKeyboardButton(text='6', callback_data='digit_6')
    btn_7 = types.InlineKeyboardButton(text='7', callback_data='digit_7')
    btn_8 = types.InlineKeyboardButton(text='8', callback_data='digit_8')
    btn_9 = types.InlineKeyboardButton(text='9', callback_data='digit_9')
    btn_10 = types.InlineKeyboardButton(text='10', callback_data='digit_10')
    keyboard.add(btn_1)
    keyboard.add(btn_2)
    keyboard.add(btn_3)
    keyboard.add(btn_4)
    keyboard.add(btn_5)
    keyboard.add(btn_6)
    keyboard.add(btn_7)
    keyboard.add(btn_8)
    keyboard.add(btn_9)
    keyboard.add(btn_10)
    return keyboard


def letter_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_1 = types.InlineKeyboardButton(text='А', callback_data='letter_1')
    btn_2 = types.InlineKeyboardButton(text='Б', callback_data='letter_2')
    btn_3 = types.InlineKeyboardButton(text='В', callback_data='letter_3')
    btn_4 = types.InlineKeyboardButton(text='Г', callback_data='letter_4')
    btn_5 = types.InlineKeyboardButton(text='Д', callback_data='letter_5')
    btn_6 = types.InlineKeyboardButton(text='Е', callback_data='letter_6')
    btn_7 = types.InlineKeyboardButton(text='Ж', callback_data='letter_7')
    btn_8 = types.InlineKeyboardButton(text='З', callback_data='letter_8')
    btn_9 = types.InlineKeyboardButton(text='И', callback_data='letter_9')
    btn_10 = types.InlineKeyboardButton(text='К', callback_data='letter_10')
    keyboard.add(btn_1)
    keyboard.add(btn_2)
    keyboard.add(btn_3)
    keyboard.add(btn_4)
    keyboard.add(btn_5)
    keyboard.add(btn_6)
    keyboard.add(btn_7)
    keyboard.add(btn_8)
    keyboard.add(btn_9)
    keyboard.add(btn_10)
    return keyboard


def check_turn(player: PlayerProfile) -> bool:
    if player.turn:
        return True
    return False


bot.polling(non_stop=True)
