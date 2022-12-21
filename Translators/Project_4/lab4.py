from lab2 import tableOfSymb, tableToPrint, tableOfVar, tableOfConst, tableOfLabel,tableOfSymbolsToPrint,tableOfIdToPrint,tableOfConstToPrint,tableOfLabelToPrint
from lab3 import parseProgram, postfixCode
from stack import Stack


stack = Stack()
commandTrack = []
toView = True
import re

def interpret():
    if parseProgram():
        if toView:
            print('\n' + '=' * 60 + '\n')

        global stack, postfixCode, commandTrack, nextInstr
        cyclesNumb = 0
        instrNum = 0
        maxNumb = len(postfixCode)

        try:
            while instrNum < maxNumb:
                cyclesNumb += 1
                lex, tok = postfixCode[instrNum]
                commandTrack.append((instrNum, lex, tok))

                if tok in ('integer', 'real', 'ident', 'label'):
                    stack.push((lex, tok))
                    nextInstr = instrNum + 1
                else:
                    doIt(lex, tok)
                    nextInstr = instrNum + 1
                if toView:
                    configToPrint(instrNum, lex, tok, maxNumb)
                instrNum = nextInstr

            # print('Загальна кiлькiсть крокiв: {0}'.format(cyclesNumb))
            if toView:
                tableOfSymbolsToPrint()
                tableOfIdToPrint()
                tableOfConstToPrint()
                tableOfLabelToPrint()
            print("\033[36m{}".format(""), end="")
            print('\n\nInterpretor: Інтерпретація завершена успішно!')
            print("\033[0m{}".format(""), end="")
            return commandTrack
        except SystemExit as e:
            # Повідомити про факт виявлення помилки
            print('\nInterpreter: Аварійне завершення програми з кодом {0}'.format(e))
        return True





def configToPrint(step, lex, tok, maxN):
    if step == 1:
        print('\n' + '=' * 60)
        tableOfSymbolsToPrint()
        tableOfIdToPrint()
        tableOfConstToPrint()
        tableOfLabelToPrint()
    print('\nКрок інтерпретації: {0}'.format(step))
    if tok in ('int', 'float'):
        print('Лексема: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in ('ident'):
        print('Лексема: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfVar[lex])))
    else:
        print('Лексема: {0}'.format((lex, tok)))
    print('postfixCode={0}'.format(postfixCode))
    stack.print()
    if step == maxN:
        for table in ('Id', 'Const', 'Label'):
            tableToPrint(table)
    return True

def doIt(lex, tok):
    global stack, postfixCode, tableOfVar, tableOfConst, tableOfLabel
    if (lex, tok) == ('=', 'assign_op'):
        (lexL, tokL) = stack.pop()
        (lexR, tokR) = stack.pop()
        print(tokR)
        tableOfVar[lexR] = (tableOfVar[lexR][0], tableOfConst[lexL][1], tableOfConst[lexL][2])
    elif lex == 'NEG':
        # зняти з вершини стека запис
        (lexx, tokk) = stack.pop()

        processingNEG((lexx, tokk))
    elif tok in ('add_op', 'mult_op', 'nelt_op', 'rel_op'):
        # зняти з вершини стека запис (правий операнд)
        (lexR, tokR) = stack.pop()
        # зняти з вершини стека запис (лівий операнд)
        (lexL, tokL) = stack.pop()
        processingAddMultDeg((lexL, tokL), lex, (lexR, tokR))
    elif tok == 'out':
        print("\033[31m{}".format(""), end="")
        (lex, tok) = stack.pop()

        if tok == 'ident':
            if tableOfVar[lex][1] == 'type_undef':
                failRunTime('неініціалізована змінна', (lex, tableOfVar[lex]))
            else:
                val = tableOfVar[lex][2]
                print('\nPRINT ' + lex + ' >>> ', end="")
                print(str(val), end="")
        else:
            print('\nPRINT >>> ', end="")
            print(str(tableOfConst[lex][2]), end="")

        print("\033[0m{}".format(""), end="")
        print()

    elif tok == 'in':
        print("\033[35m{}".format(""), end="")
        (lex, tok) = stack.pop()

        inp = input('READ ' + lex + ' <<< ')

        if inp.isdigit():
            inpType = 'integer'
            inpVal = int(inp)
        elif re.match('^[-+]?([0-9]+[.,])?[0-9]+(?:[e][-+]?[0-9]+)?$', inp):
            inpType = 'real'
            inpVal = float(inp)
        else:
            failRunTime('неправильний тип', (lex, type(inp)))

        tableOfVar[lex] = (tableOfVar[lex][0], inpType, inpVal)
        print("\033[0m{}".format(""), end="")
        print()
    return True

def processingNEG(lt):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lex, tok = lt

    if tok == 'ident':
        if tableOfVar[lex][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lex, tableOfVar[lex]))
        else:
            val, tok = (tableOfVar[lex][2], tableOfVar[lex][1])
    else:
        val = tableOfConst[lex][2]

    value = -val
    stack.push((str(value), tok))
    toTableOfConst(value, tok)

def processingAddMultDeg(ltL, lex, ltR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lexL, tokL = ltL
    lexR, tokR = ltR

    if tokL == 'ident':
        if tableOfVar[lexL][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfVar[lexL]))
        else:
            valL, tokL = (tableOfVar[lexL][2], tableOfVar[lexL][1])
    else:
        valL = tableOfConst[lexL][2]

    if tokR == 'ident':
        if tableOfVar[lexR][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexR, tableOfVar[lexR]))
        else:
            valR, tokR = (tableOfVar[lexR][2], tableOfVar[lexR][1])
    else:
        valR = tableOfConst[lexR][2]

    getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))

def getValue(vtL, lex, vtR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    valL, lexL, tokL = vtL
    valR, lexR, tokR = vtR
    if lex == '+':
        value = valL + valR
    elif lex == '-':
        value = valL - valR
    elif lex == '*':
        value = valL * valR
    elif lex == '/' and valR == 0:
        failRunTime('ділення на нуль', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '/':
        value = valL / valR
    elif lex == '^':
        value = pow(valL, valR)
    elif lex == '<':
        value = valL < valR
    elif lex == '<=':
        value = valL <= valR
    elif lex == '>':
        value = valL > valR
    elif lex == '>=':
        value = valL >= valR
    elif lex == '==':
        value = valL == valR
    elif lex == '!=':
        value = valL != valR
    else:
        pass

    if isinstance(value, float):
        stack.push((str(value), "real"))
        toTableOfConst(value, "real")
    elif isinstance(value, bool):
        stack.push((str(value), "boolean"))
        toTableOfConst(value, "boolean")
    elif isinstance(value, int):
        stack.push((str(value), "integer"))
        toTableOfConst(value, "integer")

def toTableOfConst(val, tok):
    lexeme = str(val)
    indx1 = tableOfConst.get(lexeme)
    if indx1 is None:
        indx = len(tableOfConst) + 1
        tableOfConst[lexeme] = (indx, tok, val)

def failRunTime(str, tuple):
    if str == 'неініціалізована змінна':
        (lx, rec) = tuple
        print('\nRunTime ERROR: \n\t Значення змінної {0}:{1} не визначене'.format(lx, rec))
        exit(112)
    elif str == 'ділення на нуль':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('\nRunTime ERROR: \n\t Ділення на нуль у {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR)))
        exit(113)
    elif str == 'неправильний тип':
        (lex, inpType) = tuple
        print('\n\nRunTime ERROR: \n\tДаний формат змінної не підтримується.'
              '\n\tЗмінна {0} повинна бути цілим або дійсним числом.'
              '\n\tОтримано {1}'.format(lex, inpType))
        exit(114)

def tableToPrint(step, lex, tok, maxN):
    print('\nКрок інтерпретації: {0}'.format(step))
    if tok in ('int', 'float'):
        print('Лексема: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in ('ident'):
        print('Лексема: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfVar[lex])))
    else:
        print('Лексема: {0}'.format((lex, tok)))

    print('postfixCode={0}'.format(postfixCode))
    stack.print()

    if step == maxN:
        for table in ('Id', 'Const', 'Label'):
            tableToPrint(table)
    return True

def tableOfSymbolsToPrint():
    print("\n Таблиця символів")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} '
    s2 = '{0:<10d} {1:<10d} {2:<10s} {3:<10s} {4:<5s} '
    print(s1.format("numRec", "numLine", "lexeme", "token", "index"))
    for numRec in tableOfSymb:
        numLine, lexeme, token, index = tableOfSymb[numRec]
        print(s2.format(numRec, numLine, lexeme, token, str(index) ))

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

interpret()
