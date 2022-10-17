from builtins import len, SystemExit, print, exit, KeyError
from io import open

f = open('test.txt', 'r')
sourceCode = f.read()
f.close()

sourceCode += ' '

FSuccess = (True, 'Lexer')

tableOfLanguageTokens = {'start': 'keyword', 'end': 'keyword', 'read': 'keyword', 'print': 'keyword',
                         'for': 'keyword', 'by': 'keyword', 'while': 'keyword', 'do': 'keyword', 'if': 'keyword',
                         '=': 'assign_op',
                         '.': 'dot',
                         '-': 'add_op', '+': 'add_op',
                         '*': 'mult_op', '/': 'mult_op',
                         '^': 'nelt_op',
                         '<': 'rel_op', '<=': 'rel_op', '>=': 'rel_op', '>': 'rel_op', '==': 'rel_op', '!=': 'rel_op',
                         '(': 'brackets_op', ')': 'brackets_op', '{': 'brackets_op', '}': 'brackets_op',
                         ',': 'punct', ';': 'punct',
                         ' ': 'ws', '\t': 'ws', '\n': 'nl'}
tableIdentFloatInt = {2: 'ident', 7: 'real', 8: 'integer'}

# δ - state-transition_function
# клас ws - для пробiльних символiв, клас nl - для символу нового рядка, клас other - для символiв, що не належать до поточної лексеми.
stf = {
    (0, 'ws'): 0,
    (0, 'nl'): 9,
    (0, 'AddOp'): 10, (0, 'MultOp'): 10, (0, '^'): 10, (0, ','): 10, (0, ';'): 10, (0, 'Brackets'): 10,
    (0, 'Letter'): 1, (0, 'E'): 1, (1, 'Letter'): 1, (1, 'E'): 1, (1, 'Digit'): 1, (1, 'other'): 2,
    (0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'E'): 5, (3, 'other'): 8, (3, 'dot'): 4, (4, 'Digit'): 4, (4, 'other'): 7,
    (4, 'E'): 5, (5, 'AddOp'): 6, (5, 'Digit'): 6, (6, 'Digit'): 6, (6, 'other'): 7,
    (0, '='): 13,
    (0, '!'): 12, (0, '<'): 14, (0, '>'): 14, (12, '='): 15, (14, '='): 15, (13, '='): 15,
    (0, 'other'): 101, (12, 'other'): 102
}

initState = 0  # q0 - стартовий стан
F = {2, 7, 8, 9, 10, 14, 15, 13, 101, 102}
Fstar = {2, 7, 8}  # зірочка
Ferror = {101, 102}  # обробка помилок

state = initState  # поточний стан
lenCode = len(sourceCode) - 1  # номер останнього символа у файлі з кодом програми
numLine = 1  # лексичний аналіз починаємо з першого рядка
numChar = -1  # з першого символа (в Python'і нумерація - з 0)

tableOfVar = {}
tableOfConst = {}  # Таблиць констант
tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)

# Таблиця символів міток програми
tableOfLabel = {}

char = ''  # ще не брали жодного символа
lexeme = ''  # ще не починали розпізнавати лексеми


def lex():
    global char, lexeme, state
    try:
        while numChar < lenCode:
            char = nextChar()
            classCh = classOfChar(char)
            state = nextState(state, classCh)
            if is_final(state):
                processing()
                if state in Ferror:
                    break
            elif state == 0:
                lexeme = ''
            else:
                lexeme += char
    except SystemExit as e:
        FSuccess = (False, 'Lexer')
        print('\nLexer: Аварійне завершення програми з кодом {0}'.format(e))
        exit()

    print('\nLexer: Лексичний аналiз завершено успішно!')
    print('\nLexer: Таблиця символів:', tableOfSymb)
    print('\nLexer: Таблиця змінних:', tableOfVar)
    print('\nLexer: Таблиця констант:', tableOfConst)


def tableToPrint(table):
    if table == "Symbol":
        tableOfSymbolsToPrint()
    elif table == "Id":
        tableOfIdToPrint()
    elif table == "Const":
        tableOfConstToPrint()
    elif table == "Label":
        tableOfLabelToPrint()
    else:
        tableOfSymbolsToPrint()
        tableOfIdToPrint()
        tableOfConstToPrint()
        tableOfLabelToPrint()
    return True


def processing():
    global state, lexeme, numLine, numChar
    if state in (2, 7, 8):
        token = getToken(state, lexeme)
        if token != 'keyword':
            index = indexIdConst(state, lexeme, token)
            print('-------------------------------------------------------------------------------------------\n\n\n\n')
            print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:  # якщо keyword
            print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = initState
    if state == 9:
        numLine += 1
        state = initState
    if state == 14:
        lexeme += char
        if nextChar() == '=':
            classCh = classOfChar('=')
            state = nextState(state, classCh)
        else:
            numChar -= 1
            token = getToken(state, lexeme)
            print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
            lexeme = ''
            state = initState
    if state == 13:
        lexeme += char
        if nextChar() == '=':
            classCh = classOfChar('=')
            state = nextState(state, classCh)
        else:
            numChar -= 1
            token = getToken(state, lexeme)
            print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
            lexeme = ''
            state = initState
    if state == 10:
        lexeme += char
        token = getToken(state, lexeme)
        print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
    if state == 15:
        lexeme += '='
        token = getToken(state, lexeme)
        print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState

    if state in Ferror:
        fail()


def fail():
    if state == 101:
        print('\nLexer ERROR:\n\t[{0}]: Неочікуваний символ \'{1}\'.'
              .format(numLine, char))
        exit(101)
    if state == 102:
        print('\nLexer ERROR:\n\t[{0}]: Неочікуваний символ \'{1}\'.'
              '\n\tОчікувався - \'=\'.'.format(numLine, char))
        exit(102)
    if state == 103:
        print('\nLexer ERROR:\n\t[{0}]: Неправильний формат числа.'
              '\n\tОчікувалася цифра після символа \'.\'.'.format(numLine, char))
        exit(103)
    if state == 104:
        print('\nLexer ERROR:\n\t[{0}]: Неправильний формат числа.'
              '\n\tОчікувалася цифра після символа \'e\'.'.format(numLine, char))
        exit(104)
    if state == 105:
        print('\nLexer ERROR:\n\t[{0}]: Неправильний формат числа.'
              '\n\tОчікувалася цифра після знаку.'.format(numLine, char))
        exit(105)


def classOfChar(char):
    if char in "!=<>^,;E":
        res = char
    elif char in '.':
        res = "dot"
    elif char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        res = "Letter"
    elif char in "0123456789":
        res = "Digit"
    elif char in " \t":
        res = "ws"
    elif char in "\n":
        res = "nl"
    elif char in "(){}":
        res = "Brackets"
    elif char in "+-":
        res = "AddOp"
    elif char in "*/":
        res = "MultOp"
    elif char in "^":
        res = "NeltOp"
    else:
        res = 'символ не належить алфавiту'
    return res


def nextChar():
    global numChar
    numChar += 1
    return sourceCode[numChar]


def putCharBack(numChar):
    return numChar - 1


def nextState(state, classCh):
    try:
        return stf[(state, classCh)]
    except KeyError:
        return stf[(state, 'other')]


def is_final(state):
    if state in F:
        return True
    else:
        return False


def getToken(state, lexeme):
    try:
        return tableOfLanguageTokens[lexeme]
    except KeyError:
        return tableIdentFloatInt[state]


def indexIdConst(state, lexeme, token):
    global val
    index1 = tableOfVar.get(lexeme)
    index = 0
    if state == 2:  # ідентифікатор
        if index1 is None:
            index = len(tableOfVar) + 1
            tableOfVar[lexeme] = (index, 'type_undef', 'val_undef')
    elif state in (7, 8):  # real, integer
        if index1 is None:
            index = len(tableOfConst) + 1
            if state == 7:
                val = float(lexeme)
                tableOfConst[lexeme] = (index, token, val)
            elif state == 8:
                val = int(lexeme)
                tableOfConst[lexeme] = (index, token, val)
    if not (index1 is None):
        if len(index1) == 2:
            index, _ = index1
        else:
            index, _, _ = index1
    return index


def tableOfSymbolsToPrint():
    print("\n Таблиця символів")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} '
    s2 = '{0:<10d} {1:<10d} {2:<10s} {3:<10s} {4:<5s} '
    print(s1.format("numRec", "numLine", "lexeme", "token", "index"))
    for numRec in tableOfSymb:
        numLine, lexeme, token, index = tableOfSymb[numRec]
        print(s2.format(numRec, numLine, lexeme, token, str(index)))


def tableOfIdToPrint():
    print("\n Таблиця ідентифікаторів")
    s1 = '{0:<10s} {1:<15s} {2:<15s} {3:<10s} '
    print(s1.format("Ident", "Type", "Value", "Index"))
    s2 = '{0:<10s} {2:<15s} {3:<15s} {1:<10d} '
    for id in tableOfVar:
        index, type, val = tableOfVar[id]
        print(s2.format(id, index, type, str(val)))


def tableOfConstToPrint():
    print("\n Таблиця констант")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} '
    print(s1.format("Const", "Type", "Value", "Index"))
    s2 = '{0:<10s} {2:<10s} {3:<10} {1:<10d} '
    for const in tableOfConst:
        index, type, val = tableOfConst[const]
        print(s2.format(str(const), index, type, val))


def tableOfLabelToPrint():
    if len(tableOfLabel) == 0:
        print("\n Таблиця міток - порожня")
    else:
        s1 = '{0:<10s} {1:<10s} '
        print("\n Таблиця міток")
        print(s1.format("Label", "Value"))
        s2 = '{0:<10s} {1:<10d} '
        for lbl in tableOfLabel:
            val = tableOfLabel[lbl]
            print(s2.format(lbl, val))


lex()
