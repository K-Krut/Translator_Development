from lab2 import lex
from lab2 import tableOfSymb, tableOfLabel, tableOfVar, tableOfConst
lex()
print('\n')

numRow = 1

len_tableOfSymb = len(tableOfSymb)


postfixCode = []
viewTranslation = True
viewSyntax = True

def parseProgram():
    print('\n' + '=' * 60 + '\n')
    try:
        parseToken('start', 'keyword', '')
        parseToken('', 'ident', '')
        parseStatementList()
        print('\nParser: Синтаксичний аналіз і трансляція завершені успішно')
        return True
    except SystemExit as e:
        print('\nParser: Аварійне завершення програми з кодом {0}'.format(e))
        exit()

def parseToken(lexeme, token, indent):
    global numRow
    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))
    numLine, lex, tok = getSymb()
    numRow += 1
    if lexeme == '':
        if tok == token:
            if viewSyntax:
                print(indent + 'parseToken():\n' + indent + '[{0}]: {1}'.format(numLine, (lex, tok)))
            return True
        else:
            failParse('невідповідність токенів', (numLine, lex, tok))
            return False
    if (lex, tok) == (lexeme, token):
        if viewSyntax:
            print(indent + 'parseToken():\n' + indent + '[{0}]: {1}'.format(numLine, (lex, tok)))
        return True
    else:
        failParse('невідповідність лексем', (numLine, lex, tok, lexeme, token))
        return False

def getSymb():
    if numRow > len_tableOfSymb:
        return False
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token

def parseStatementList(specInstr=''):
    print('\t parseStatementList():')
    while parseStatement(specInstr):
        pass
    return True

def parseStatement(specInstr=''):
    global numRow
    if getSymb():
        numLine, lex, tok = getSymb()
    else:
        return False
    if (lex, tok) == ('end', 'keyword'):
        return False
    if viewSyntax:
        print('\t\t parseStatement():')
    if tok == 'ident':
        parseAssign()
        parseToken(';', 'punct', '\t' * 5)
        return True
    elif (lex, tok) == ('read', 'keyword'):
        parseRead()
        parseToken(';', 'punct', '\t' * 5)
        return True
    elif (lex, tok) == ('print', 'keyword'):
        parsePrint()
        parseToken(';', 'punct', '\t' * 5)
        return True
    # elif (lex, tok) == ('integer', 'keyword') or (lex, tok) == ('real', 'keyword') or (lex, tok) == ('boolean', 'keyword'):
    #     parseInit()
    #     parseToken(';', 'punct', '\t' * 5)
        return True
    elif (lex, tok) == ('if', 'keyword'):
        parseIf()
        return True
    elif (lex, tok) == ('for', 'keyword'):
        parseFor()
        return True
    elif specInstr == 'IF':
        if (lex, tok) == ('}', 'brackets_op'):
            return False
        else:
            failParse('невідповідність інструкцій', (numLine, lex, tok, ''))
            return False
    elif specInstr == 'FOR':
        if (lex, tok) == ('}', 'brackets_op'):
            return False
        else:
            failParse('невідповідність інструкцій', (numLine, lex, tok, ''))
            return False
    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, ''))
        return False

def parseAssign():
    global numRow
    if viewSyntax:
        print('\t' * 4 + 'parseAssign():')
    numLine, lex, tok = getSymb()
    postfixCode.append((lex, tok))     # Трансляція
    if viewTranslation:
        configToPrint(lex, numRow)
    numRow += 1
    if viewSyntax:
        print('\t' * 5 + '[{0}]: {1}'.format(numLine, (lex, tok)))
    if parseToken('=', 'assign_op', '\t\t\t\t\t'):
        numRowCopy = numRow - 1
        parseExpression()
        postfixCode.append(('=', 'assign_op'))  # Трансляція
        # Бінарний оператор  '=' додається після своїх операндів
        if viewTranslation:
            configToPrint('=', numRowCopy)
        return True
    else:
        return False

def parseIdentList():
    if viewSyntax:
        print('\t' * 5 + 'parseIdentList():')
    while parseIdent():
        if getSymb():
            numLine, lex, tok = getSymb()
        else:
            return True
        if lex == ',':
            parseToken(',', 'punct', '\t\t\t\t\t')
            postfixCode.append(('IN', 'in'))  # Трансляція
        else:
            return True
    numLine, lex, tok = getSymb()
    failParse('невідповідність токенів', (numLine, lex, tok))

def parseIdent():
    if viewSyntax:
        print('\t' * 6 + 'parseIdent():')
    global numRow
    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', ('', 'ident', numRow))
    numLine, lex, tok = getSymb()
    if tok == 'ident':
        numRow += 1
        postfixCode.append((lex, tok))
        if viewSyntax:
            print('\t' * 6 + 'parseToken():\n' + '\t' * 6 + '[{0}]: {1}'.format(numLine, (lex, tok)))
        return True
    else:
        return False

def parseExpressionList():
    if viewSyntax:
        print('\t' * 5 + 'parseExpressionList():')
    while parseExpression():
        if getSymb():
            numLine, lex, tok = getSymb()
        else:
            return True
        if lex == ')':
            break
        parseToken(',', 'punct', '\t\t\t\t\t')
        postfixCode.append(('OUT', 'out'))
    return True

def parseExpression():
    global numRow, postfixCode

    if viewSyntax:
        print('\t' * 5 + 'parseExpression():')
    parseTerm()
    F = True
    while F:
        if getSymb():
            numLine, lex, tok = getSymb()
        else:
            return True
        if tok in 'add_op':
            numRowCopy = numRow
            numRow += 1
            if viewSyntax:
                print('\t' * 6 + '[{0}]: {1}'.format(numLine, (lex, tok)))
            parseTerm()

            postfixCode.append((lex, tok))  # трансляція
            # lex - бінарний оператор  '+' чи '-' додається після своїх операндів

            if viewTranslation:
                configToPrint(lex, numRowCopy)
        else:
            F = False
    return True

def parseTerm():
    global numRow, postfixCode
    if viewSyntax:
        print('\t' * 6 + 'parseTerm():')
    parseFactor()
    F = True
    while F:
        if getSymb():
            numLine, lex, tok = getSymb()
        else:
            return True
        if tok in 'mult_op':
            numRowCopy = numRow
            numRow += 1
            if viewSyntax:
                print('\t' * 6 + '[{0}]: {1}'.format(numLine, (lex, tok)))
            parseFactor()
            postfixCode.append((lex, tok))
            if viewTranslation:
                configToPrint(lex, numRowCopy)
        else:
            F = False
    return True

def parseFactor():
    global numRow, postfixCode
    if viewSyntax:
        print('\t' * 7 + 'parseFactor():')
    if getSymb():
        numLine, lex, tok = getSymb()
    else:
        return True
    if viewSyntax:
        print('\t' * 7 + '[{0}]: {1}'.format(numLine, (lex, tok)))
    if tok in ('integer', 'real', 'ident'):
        postfixCode.append((lex, tok))
        if viewTranslation:
            configToPrint(lex, numRow)
        numRow += 1
        if getSymb():
            numLine, lex, tok = getSymb()
        else:
            return True
        if lex == '^':
            numRowCopy = numRow
            numRow += 1
            if viewSyntax:
                print('\t' * 6 + '[{0}]: {1}'.format(numLine, (lex, tok)))
            parseFactor()
            postfixCode.append((lex, tok))
            if viewTranslation:
                configToPrint(lex, numRowCopy)
    elif lex == '(':
        numRow += 1
        parseExpression()
        parseToken(')', 'brackets_op', '\t' * 7)
    elif lex == '-':
        numRowCopy = numRow
        numRow += 1
        parseExpression()
        postfixCode.append(('NEG', tok))
        if viewTranslation:
            configToPrint(lex, numRowCopy)

    else:
        failParse('невідповідність у Expression.Factor',
                  (numLine, lex, tok, 'integer, real, ident або \'(\' Expression \')\''))
    return True

def parseRead():
    global numRow
    if viewSyntax:
        print('\t' * 4 + 'parseRead():')
    _, lex, tok = getSymb()
    if lex == 'read' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'brackets_op', '\t' * 5)
        parseIdentList()
        parseToken(')', 'brackets_op', '\t' * 5)
        return True
    else:
        return False

def parsePrint():
    global numRow
    if viewSyntax:
        print('\t' * 4 + 'parsePrint():')
    _, lex, tok = getSymb()
    if lex == 'print' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'brackets_op', '\t' * 5)
        parseExpressionList()
        parseToken(')', 'brackets_op', '\t' * 5)
        return True
    else:
        return False

def parseIf():
    global numRow
    if viewSyntax:
        print('\t' * 4 + 'parseIf():')
    _, lex, tok = getSymb()
    if lex == 'if' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'brackets_op', '\t' * 5)
        parseBoolExpr()
        parseToken(')', 'brackets_op', '\t' * 5)
        parseToken('{', 'brackets_op', '\t' * 5)
        parseStatementList('IF')
        parseToken('}', 'brackets_op', '\t' * 5)
        return True
    else:
        return False

def createLabel():
    global tableOfLabel
    nmb = len(tableOfLabel) + 1
    lexeme = "m" + str(nmb)
    val = tableOfLabel.get(lexeme)
    if val is None:
        tableOfLabel[lexeme] = 'val_undef'
        tok = 'label'  # # #
    else:
        failParse('конфлікт міток')
    return (lexeme, tok)

def setValLabel(lbl):
    global tableOfLabel
    lex, _tok = lbl
    tableOfLabel[lex] = len(postfixCode)
    return True

def parseFor():
    global numRow
    if viewSyntax:
        print('\t' * 4 + 'parseFor():')
    _, lex, tok = getSymb()
    if lex == 'for' and tok == 'keyword':
        numRow += 1
        numLine, lex, tok = getSymb()
        parseToken('(', 'brackets_op', '\t' * 5)
        parseIdent()
        parseToken('=', 'assign_op', '\t' * 5)
        parseExpression()
        parseToken(')', 'brackets_op', '\t' * 5)
        parseToken('by', 'keyword', '\t' * 5)
        parseToken('(', 'brackets_op', '\t' * 5)
        parseIdent()
        parseToken('=', 'assign_op', '\t' * 5)
        parseExpression()
        parseToken(')', 'brackets_op', '\t' * 5)
        parseToken('while', 'keyword', '\t' * 5)
        parseToken('(', 'brackets_op', '\t' * 5)
        parseBoolExpr()
        parseToken(')', 'brackets_op', '\t' * 5)
        parseToken('do', 'keyword', '\t' * 5)
        parseToken('{', 'brackets_op', '\t' * 5)
        parseStatementList('FOR')
        parseToken('}', 'brackets_op', '\t' * 5)
        return True
    else:
        return False

def parseBoolExpr():
    global numRow
    if viewSyntax:
        print('\t' * 5 + 'parseBoolExpression():')
    parseExpression()
    if getSymb():
        numLine, lex, tok = getSymb()
    else:
        return True
    numRow += 1
    parseExpression()
    if tok in ('rel_op'):
        postfixCode.append((lex, tok))  # Трансляція
        if viewSyntax:
            print('\t' * 5 + '[{0}]: {1}'.format(numLine, (lex, tok)))
    else:
        failParse('невідповідність у BoolExpr', (numLine, lex, tok, '== != <= >= < >'))
    return True

def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numRow) = tuple
        print(
            '\nParser ERROR: \n\tНеочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {1}.'
            '\n\tОчікувалось - {0}'.format((lexeme, token), numRow))
        exit(106)
    elif str == 'невідповідність лексем':
        (numLine, lexeme, token, lex, tok) = tuple
        print('\nParser ERROR: \n\t[{0}]: Неочікуваний елемент (\'{1}\', {2}).'
              '\n\tОчікувався - (\'{3}\', {4}).'.format(numLine, lexeme, token, lex, tok))
        exit(107)
    elif str == 'невідповідність інструкцій':
        (numLine, lex, tok, expected) = tuple
        print(
            '\nParser ERROR: \n\t[{0}]: Неочікуваний елемент (\'{1}\', {2}).'
            '\n\tОчікувалася інструкція.'.format(numLine, lex, tok, expected))
        exit(108)
    elif str == 'невідповідність у Expression.Factor':
        (numLine, lex, tok, expected) = tuple
        print(
            '\nParser ERROR: \n\t[{0}]: Неочікуваний елемент (\'{1}\', {2}).'
            '\n\tОчікувався - \'{3}\'.'.format(numLine, lex, tok, expected))
        exit(109)
    elif str == 'невідповідність у BoolExpr':
        (numLine, lex, tok, expected) = tuple
        print(
            '\nParser ERROR: \n\t[{0}]: Неочікуваний елемент (\'{1}\', {2}).'
            '\n\tОчікувався оператор порівняння - \'{3}\'.'.format(numLine, lex, tok, expected))
        exit(110)
    elif str == 'невідповідність токенів':
        (numLine, lex, tok) = tuple
        print('\nParser ERROR: \n\t[{0}]: Неочікуваний елемент (\'{1}\', {2}).'
              '\n\tОчікувався ідентифікатор'.format(numLine, lex, tok))
        exit(111)

def configToPrint(lex,numRow):
    stage = '\nКрок трансляції\n'
    stage += 'лексема: \'{0}\'\n'
    stage += 'tableOfSymb[{1}] = {2}\n'
    stage += 'postfixCode = {3}\n'
    print(stage.format(lex, numRow, str(tableOfSymb[numRow]), str(postfixCode)))

# parseProgram()
