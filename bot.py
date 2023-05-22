from telebot.types import CallbackQuery, Message

from actions import assign_ships, get_user_by_id, attack_cell
from bot_init import bot, players, stage
from helpers import get_field, get_monospace_text, cells_set
from player_profile import PlayerProfile


def send_start_to_play_message(message: Message):
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
        player_2.player_number = 'second'
        bot.send_message(message.chat.id, 'Вы второй.')
        stage.insert(0, 1)

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


@bot.message_handler(commands=['start'])  # handle the command "start"
def start_welcome(message):
    msg = "Привет, " + message.from_user.first_name + "!\n" + \
          "Это бот для игры в морской бой\n" + \
          "Ты можешь послать мне следующие команды:\n" + \
          "1) /info, чтобы узнать информацию о боте\n" + \
          "2) /play, чтобы поиграть с соперником"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['info'])  # handle the command "info"
def send_info_message(message):
    msg = "Я был создан [этим](tg://user?id={416544613}) пользователем.\n" \
          "[VK](vk.com/id46566190)\n" \
          "[Instagram](instagram.com/dmitrygurylev/)"
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')


@bot.message_handler(commands=['rules'])  # handle the command "rules"
def send_rules_message(message):
    msg = "Правила"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['play'])  # handle the command "play"
def start_welcome(message):
    send_start_to_play_message(message)


@bot.message_handler(content_types=['text'])  # handle with text
def handle_text(message):
    message_text_array = message.text.split('\n')

    # match message_text_array[0]:
    if message_text_array[0] == "ввод":
        assign_ships(message)
    elif message_text_array[0].lower() in cells_set:
        attack_cell(message)
    else:
        "ЗАГЛУШКА"


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: CallbackQuery):
    if call.data == "commit_ships":
        current_player = get_user_by_id(call.from_user.id)
        current_player.ready_to_play = True
        current_player.turn = True

        enemy = current_player.enemy

        first_player = current_player if current_player.player_number == 'first' else enemy

        if enemy.ready_to_play:
            stage.insert(0, 2)
            bot.send_message(current_player.player_id, 'Принято')
            if current_player == first_player:
                bot.send_message(current_player.player_id,
                                 'Игра начинается.\n'
                                 'Вы ходите первым.'
                                 '\nВаше поле:\n' +
                                 get_monospace_text(get_field(current_player.field)) +
                                 '\nПоле врага:\n' +
                                 get_monospace_text(get_field(enemy.field_to_enemy)) +
                                 'Выберите ячейку для атаки',
                                 parse_mode='html')
                bot.send_message(enemy.player_id, 'Игра начинается.\n'
                                                  'Ожидайте хода первого игрока'
                                                  '\nВаше поле:\n' +
                                 get_monospace_text(get_field(enemy.field)) +
                                 '\nПоле врага:\n' + get_monospace_text(get_field(current_player.field_to_enemy)),
                                 parse_mode='html')
            else:
                bot.send_message(enemy.player_id,
                                 'Игра начинается.\n'
                                 'Вы ходите первым.'
                                 '\nВаше поле:\n' + get_monospace_text(get_field(enemy.field)) +
                                 '\nПоле врага:\n' + get_monospace_text(get_field(current_player.field_to_enemy)) +
                                 'Выберите ячейку для атаки',
                                 parse_mode='html')
                bot.send_message(current_player.player_id, 'Игра начинается.\n'
                                                           'Ожидайте хода первого игрока.'
                                                           '\nВаше поле:\n' +
                                 get_monospace_text(get_field(current_player.field)) +
                                 '\nПоле врага:\n' + get_monospace_text(get_field(enemy.field_to_enemy)),
                                 parse_mode='html',
                                 )

        else:
            if current_player == first_player:
                bot.send_message(current_player.player_id, 'Принято. Дождитесь второго игрока')
            else:
                bot.send_message(current_player.player_id, 'Принято. Дождитесь первого игрока')

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


bot.polling(non_stop=True)
