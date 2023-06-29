from bot_init import parties
from party import Party
from player_profile import PlayerProfile


def get_user_by_id(p_id: int) -> PlayerProfile:
    players = set()
    for party in parties:
        for pl in party.players:
            players.add(pl)

    for pl in players:
        if pl.player_id == p_id:
            return pl
    return None


cells_set: frozenset[str] = frozenset([
    'а1', 'а2', 'а3', 'а4', 'а5', 'а6', 'а7', 'а8', 'а9', 'а10',
    'б1', 'б2', 'б3', 'б4', 'б5', 'б6', 'б7', 'б8', 'б9', 'б10',
    'в1', 'в2', 'в3', 'в4', 'в5', 'в6', 'в7', 'в8', 'в9', 'в10',
    'г1', 'г2', 'г3', 'г4', 'г5', 'г6', 'г7', 'г8', 'г9', 'г10',
    'д1', 'д2', 'д3', 'д4', 'д5', 'д6', 'д7', 'д8', 'д9', 'д10',
    'е1', 'е2', 'е3', 'е4', 'е5', 'е6', 'е7', 'е8', 'е9', 'е10',
    'ж1', 'ж2', 'ж3', 'ж4', 'ж5', 'ж6', 'ж7', 'ж8', 'ж9', 'ж10',
    'з1', 'з2', 'з3', 'з4', 'з5', 'з6', 'з7', 'з8', 'з9', 'з10',
    'и1', 'и2', 'и3', 'и4', 'и5', 'и6', 'и7', 'и8', 'и9', 'и10',
    'к1', 'к2', 'к3', 'к4', 'к5', 'к6', 'к7', 'к8', 'к9', 'к10'])


def get_field(field: list[str]) -> str:
    return '. 1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟\n' \
           'A {f[1]}{f[2]}{f[3]}{f[4]}{f[5]}{f[6]}{f[7]}{f[8]}{f[9]}{f[10]}\n' \
           'Б {f[11]}{f[12]}{f[13]}{f[14]}{f[15]}{f[16]}{f[17]}{f[18]}{f[19]}{f[20]}\n' \
           'В {f[21]}{f[22]}{f[23]}{f[24]}{f[25]}{f[26]}{f[27]}{f[28]}{f[29]}{f[30]}\n' \
           'Г {f[31]}{f[32]}{f[33]}{f[34]}{f[35]}{f[36]}{f[37]}{f[38]}{f[39]}{f[40]}\n' \
           'Д {f[41]}{f[42]}{f[43]}{f[44]}{f[45]}{f[46]}{f[47]}{f[48]}{f[49]}{f[50]}\n' \
           'Е {f[51]}{f[52]}{f[53]}{f[54]}{f[55]}{f[56]}{f[57]}{f[58]}{f[59]}{f[60]}\n' \
           'Ж {f[61]}{f[62]}{f[63]}{f[64]}{f[65]}{f[66]}{f[67]}{f[68]}{f[69]}{f[70]}\n' \
           'З {f[71]}{f[72]}{f[73]}{f[74]}{f[75]}{f[76]}{f[77]}{f[78]}{f[79]}{f[80]}\n' \
           'И {f[81]}{f[82]}{f[83]}{f[84]}{f[85]}{f[86]}{f[87]}{f[88]}{f[89]}{f[90]}\n' \
           'К {f[91]}{f[92]}{f[93]}{f[94]}{f[95]}{f[96]}{f[97]}{f[98]}{f[99]}{f[100]}\n' \
        .format(f=field)


def get_monospace_text(text: str) -> str:
    return '<code>{0}</code>'.format(text)


def check_turn(pl: PlayerProfile) -> bool:
    if pl.turn:
        return True
    return False


def get_stage_ship_decks_1_text(pl: PlayerProfile):
    return get_monospace_text(get_field(pl.field)) + \
        '\nПоставьте однопалубные корабли на свое поле. Ввод осуществляется следующим образом:\n' \
        'а1 б3 в5 г7'


def get_stage_ship_decks_2_text(pl: PlayerProfile):
    return get_monospace_text(get_field(pl.field)) + \
        '\nПоставьте двухпалубные корабли на свое поле. Ввод осуществляется следующим образом:\n' \
        'д1д2 г1г2 a1б1'


def get_stage_ship_decks_3_text(pl: PlayerProfile):
    return get_monospace_text(get_field(pl.field)) + \
        '\nПоставьте трехпалубные корабли на свое поле. Ввод осуществляется следующим образом:\n' \
        'ж1ж2ж3 е1е2е3'


def get_stage_ship_decks_4_text(pl: PlayerProfile):
    return get_monospace_text(get_field(pl.field)) + \
        '\nПоставьте четырехпалубный корабль на свое поле. Ввод осуществляется следующим образом:\n' \
        'а1а2а3а4'


def stage_2_pl_1_text(pl: PlayerProfile):
    return 'Игра начинается.\nВы ходите первым.\nВаше поле:\n' + \
        get_monospace_text(get_field(pl.field)) + \
        '\nПоле врага:\n' + \
        get_monospace_text(get_field(pl.enemy.field_to_enemy)) + \
        'Выберите ячейку для атаки'


def stage_2_pl_2_text(pl: PlayerProfile):
    return 'Игра начинается.\nОжидайте хода первого игрока.\nВаше поле:\n' + \
        get_monospace_text(get_field(pl.field)) + \
        '\nПоле врага:\n' + get_monospace_text(get_field(pl.enemy.field_to_enemy))


def assign_enemies(current_party: Party) -> None:
    current_party.players[0].enemy = current_party.players[1]
    current_party.players[1].enemy = current_party.players[0]