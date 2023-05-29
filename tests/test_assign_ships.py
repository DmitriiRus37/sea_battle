import re
from unittest import TestCase
from actions import assign_ships


class TestAssignShips(TestCase):
    original_phrase_list = ['ввод',
                            '1:', 'в8', 'з3', 'е7', 'в4',
                            '2:', 'д1е1', 'и6и7', 'з10и10',
                            '3:', 'а2а3а4', 'к1к2к3',
                            '4:', 'а10б10в10г10']
    original_phrase = 'ввод\n' \
                      '1: в8 з3 е7 в4\n' \
                      '2: д1е1 и6и7 з10и10\n' \
                      '3: а2а3а4 к1к2к3\n' \
                      '4: а10б10в10г10'

    def test_assign_ships_string(self):
        result = self.original_phrase.split()
        assert self.original_phrase_list == result

        phrase_to_test = '\n\n\n     ввод\n' \
                         '1: в8 з3  \n  е7      в4\n' \
                         '2: д1е1 и6и7 з10и10\n' \
                         '3: а2а3а4 \nк1к2к3\n' \
                         '4: \n\nа10б10в10г10'
        result = phrase_to_test.split()
        assert self.original_phrase_list == result

    def test_assign_ships(self):
        class msg:
            class chat:
                def __init__(self, id):
                    self.id = id

            def __init__(self, id, txt):
                self.chat(id)
                self.message = txt

        assign_ships(msg(0, self.original_phrase_list))
