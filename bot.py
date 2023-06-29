from aiogram import executor
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from bot_init import bot, parties
from bot_init import dp
from cells import ship_cell
from helpers import cells_set, stage_2_pl_1_text, stage_2_pl_2_text, \
    check_turn, assign_enemies
from helpers import get_stage_ship_decks_1_text, get_stage_ship_decks_2_text, get_stage_ship_decks_3_text, \
    get_stage_ship_decks_4_text, get_user_by_id, get_monospace_text, get_field
from party import Party
from player_profile import PlayerProfile as Pl, PlayerNumber as Pl_num
from ship import Deck, Ship
from validation import to_coord
from validation import validate_ships


class FSMShips(StatesGroup):
    ships_1_deck = State()
    ships_2_decks = State()
    ships_3_decks = State()
    ship_4_decks = State()


@dp.message_handler(commands=['assign'])
async def assign_ships_start(message: types.Message):
    current_player = get_user_by_id(message.chat.id)
    await message.answer(text=get_stage_ship_decks_1_text(current_player), parse_mode='html')
    await FSMShips.ships_1_deck.set()


@dp.message_handler(state=FSMShips.ships_1_deck)
async def assign_ships_1_deck(message: types.Message, state: FSMContext):
    current_player = get_user_by_id(message.chat.id)
    res = await assign_s(current_player, message, Deck.one)
    if res:
        current_player.stage_assign_decks = 2
        await state.update_data(username=message.text)
        await message.answer(text=get_stage_ship_decks_2_text(current_player), parse_mode='html')
        await FSMShips.next()


@dp.message_handler(state=FSMShips.ships_2_decks)
async def assign_ships_2_deck(message: types.Message, state: FSMContext):
    current_player = get_user_by_id(message.chat.id)
    res = await assign_s(current_player, message, Deck.two)
    if res:
        current_player.stage_assign_decks = 3
        await state.update_data(username=message.text)
        await message.answer(text=get_stage_ship_decks_3_text(current_player), parse_mode='html')
        await FSMShips.next()


@dp.message_handler(state=FSMShips.ships_3_decks)
async def assign_ships_3_deck(message: types.Message, state: FSMContext):
    current_player = get_user_by_id(message.chat.id)
    res = await assign_s(current_player, message, Deck.three)
    if res:
        current_player.stage_assign_decks = 4
        await state.update_data(username=message.text)
        await message.answer(text=get_stage_ship_decks_4_text(current_player), parse_mode='html')
        await FSMShips.next()


@dp.message_handler(state=FSMShips.ship_4_decks)
async def assign_ships_finish(message: types.Message, state: FSMContext):
    current_player = get_user_by_id(message.chat.id)
    await state.update_data(username=message.text)
    res = await assign_s(current_player, message, Deck.four)
    if res:
        keyboard = InlineKeyboardMarkup()
        key_commit = InlineKeyboardButton(
            text='Подтвердить ✅',
            callback_data='commit_ships')
        key_reassign = InlineKeyboardButton(
            text='Ввести заново 🔁',
            callback_data='reassign_ships')
        keyboard.add(key_commit)
        keyboard.add(key_reassign)
        await message.answer(
            text=get_monospace_text(get_field(current_player.field)) +
                 '\nХотите продолжить или заново расставить корабли?',
            reply_markup=keyboard,
            parse_mode='html')
        await state.finish()
    else:
        await message.answer(text='Попробуйте ввести корректные координаты')


async def assign_s(current_player: Pl, message: types.Message, deck_count: Deck):
    f_working = current_player.field
    ships = message.text.lower().split()

    busy_cells = current_player.busy_cells.copy()
    if not await validate_ships(busy_cells, ships, deck_count, message):
        decks_str = None
        match deck_count:
            case Deck.one:
                decks_str = 'однопалубные корабли'
            case Deck.two:
                decks_str = 'двухпалубные корабли'
            case Deck.three:
                decks_str = 'трехпалубные корабли'
            case Deck.four:
                decks_str = 'четырехпалубный корабль'

        await message.answer('У вас ошибка, попробуйте расставить ' + decks_str + ' заново\n' +
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


@dp.message_handler(commands=['start'])  # handle the command "start"
async def start_welcome(message: types.Message):
    msg = "Привет, " + message.from_user.first_name + "!\n" + \
          "Это бот для игры в морской бой\n" + \
          "Ты можешь послать мне следующие команды:\n" + \
          "1) /info, чтобы узнать информацию о боте\n" + \
          "2) /play, чтобы поиграть с соперником"
    await message.answer(msg)


@dp.message_handler(commands=['info'])  # handle the command "info"
async def send_info_message(message: types.Message):
    msg = "Этого бота создал [этот](tg://user?id={416544613}) пользователь Telegram.\n" \
          "[VK](vk.com/id46566190)\n" \
          "[Instagram](instagram.com/dmitrygurylev/)"
    await message.answer(msg, parse_mode='Markdown')


@dp.message_handler(commands=['rules'])  # handle the command "rules"
async def send_rules_message(message: types.Message):
    msg = "Правила игры:\n" \
          "Игровое поле — квадрат 10×10.\n\n" \
          "Число кораблей:\n" \
          "1 корабль — ряд из 4 клеток («четырёхпалубный»)\n" \
          "2 корабля — ряд из 3 клеток («трёхпалубные»)\n" \
          "3 корабля — ряд из 2 клеток («двухпалубные»)\n" \
          "4 корабля — 1 клетка («однопалубные»)\n\n" \
          "Игрок, выполняющий ход, совершает выстрел — пишет координаты клетки, " \
          "в которой, по его мнению, находится корабль противника, например, «В1».\n" \
          "Если выстрел пришёлся в клетку, не занятую ни одним кораблём противника, " \
          "то следует ответ «Мимо!» и стрелявший игрок ставит на чужом квадрате в этом месте точку. " \
          "Право хода переходит к сопернику.\n" \
          "Если выстрел пришёлся в клетку, где находится многопалубный корабль (размером больше чем 1 клетка), " \
          "то следует ответ «Ранил(а)!». " \
          "Стрелявший игрок ставит на чужом поле в эту клетку крестик, " \
          "а его противник ставит крестик на своём поле также в эту клетку. " \
          "Стрелявший игрок получает право на ещё один выстрел.\n" \
          "Если выстрел пришёлся в клетку, где находится однопалубный корабль, " \
          "или последнюю непоражённую клетку многопалубного корабля, " \
          "то следует ответ «Убил(а)!». Оба игрока отмечают потопленный корабль на листе. " \
          "Стрелявший игрок получает право на ещё один выстрел.\n\n" \
          "Победителем считается тот, кто первым потопит все 10 кораблей противника"
    await message.answer(msg)


@dp.message_handler(commands=['play'])  # handle the command "play"
async def start_welcome(message: types.Message):
    if len(parties) == 0 or len(parties[len(parties) - 1].players) == 2:
        cur_party = Party()
        parties.append(cur_party)
    else:
        cur_party = parties[len(parties) - 1]

    if len(cur_party.players) == 0:
        await message.answer("Создание новой партии")
        pl_1 = Pl(message.chat.id)
        pl_1.party = cur_party
        cur_party.players.append(pl_1)
        pl_1.player_number = Pl_num.first
        await message.answer("Вы первый. Ожидайте второго игрока")
    elif len(cur_party.players) == 1:
        pl_2 = Pl(message.chat.id)
        pl_2.party = cur_party
        cur_party.players.append(pl_2)
        assign_enemies(cur_party)
        pl_2.player_number = Pl_num.second
        await message.answer("Вы второй.")
        cur_party.stage.v = 1
        for p in cur_party.players:
            p.stage_assign_decks = 1
            await bot.send_message(
                p.player_id,
                'Введите команду /assign для расстановки кораблей')
    else:
        await message.answer('Создание новой партии')


@dp.message_handler(content_types=['text'])  # handle with text
async def handle_text(message: types.Message):
    message_text_array = message.text.split()
    if message_text_array[0].lower() in cells_set:
        cur_pl = get_user_by_id(message.chat.id)
        cur_party = Party.get_current_party_by_player(cur_pl)
        if cur_party.stage.v != 2:
            await message.answer('Игра еще не начата.')
            return
        if not check_turn(cur_pl):
            await message.answer('Сейчас ходит ваш оппонент. Дождитесь своей очереди')
            return
        cell_to_attack = message.text
        cur_pl = get_user_by_id(message.chat.id)
        if not check_turn(cur_pl):
            await message.answer('Сейчас ходит ваш оппонент. Дождитесь своей очереди')
            return
        letter, digit = cell_to_attack[0].lower(), int(cell_to_attack[1:])
        coord_to_attack = to_coord(letter, digit)
        en = cur_pl.enemy
        if en.repeated_cell(coord_to_attack):
            await message.answer('В эту ячейку нельзя стрелять')
            return
        found, sh = en.find_ship_by_cell_attacked(coord_to_attack)

        bot.send_message(cur_pl.player_id, 'Вы стреляете: ' + letter + str(digit))
        bot.send_message(en.player_id, 'Противник стреляет : ' + letter + str(digit))
        if found:
            dead_ship = en.attack_ship(coord_to_attack, sh)
            if en.all_ships_dead():
                bot.send_message(cur_pl.player_id, 'Вы победили. Вы потопили все вражеские корабли')
                bot.send_message(en.player_id, 'Вы проиграли. Ваши корабли потоплены')
                parties.remove(cur_party)

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
            await bot.send_message(cur_pl.player_id, 'Вы промахнулись.\n' +
                             '\nВаше поле:\n' + get_monospace_text(get_field(cur_pl.field)) +
                             '\nПоле врага:\n' + get_monospace_text(get_field(en.field_to_enemy)) +
                             '\nОжидайте хода врага',
                             parse_mode='html'
                             )
            await bot.send_message(en.player_id, 'Противник промахнулся.\n' +
                             '\nВаше поле:\n' + get_monospace_text(get_field(en.field)) +
                             '\nПоле врага:\n' + get_monospace_text(get_field(cur_pl.field_to_enemy)) +
                             '\nВыберите ячейку для атаки',
                             parse_mode='html')
    else:
        "ЗАГЛУШКА"


@dp.callback_query_handler(lambda c: c.data == 'commit_ships')
async def callback_assign(call: types.CallbackQuery):
    cur_pl = get_user_by_id(call.from_user.id)
    cur_pl.stage_assign_decks = 0
    cur_pl.ready_to_play = True
    cur_pl.turn = True
    cur_party = Party.get_current_party_by_player(cur_pl)

    enemy = cur_pl.enemy

    first_player = cur_pl if cur_pl.player_number == Pl_num.first else enemy

    if enemy.ready_to_play:
        cur_party.stage.v = 2
        bot.send_message(cur_pl.player_id, 'Принято')
        if cur_pl == first_player:
            await bot.send_message(cur_pl.player_id, stage_2_pl_1_text(cur_pl), parse_mode='html')
            await bot.send_message(enemy.player_id, stage_2_pl_2_text(enemy), parse_mode='html')
        else:
            await bot.send_message(enemy.player_id, stage_2_pl_1_text(enemy), parse_mode='html')
            await bot.send_message(cur_pl.player_id, stage_2_pl_2_text(cur_pl), parse_mode='html')
    else:
        if cur_pl == first_player:
            await bot.send_message(cur_pl.player_id, 'Принято. Дождитесь второго игрока')
        else:
            await bot.send_message(cur_pl.player_id, 'Принято. Дождитесь первого игрока')


@dp.callback_query_handler(lambda c: c.data == 'reassign_ships')
async def process_callback_button1(call: types.CallbackQuery):
    current_player = get_user_by_id(call.from_user.id)
    current_player.stage_assign_decks = 1
    current_player.remove_ship_assignation()
    await bot.answer_callback_query(call.id)
    await bot.send_message(
        chat_id=call.from_user.id,
        text='Повторно введите команду /assign для расстановки кораблей')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
