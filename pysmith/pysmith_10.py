from hypothesis import strategies as st


@st.composite
def NAME(draw):
    return draw(st.sampled_from('xyz'))


@st.composite
def NUMBER(draw):
    return draw(st.one_of(
        st.integers(),
        st.floats()
    ))


@st.composite
def STRING(draw):
    return draw(st.text(st.characters(min_codepoint=1, max_codepoint=128)))


# single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
# file_input: (NEWLINE | stmt)* ENDMARKER
# eval_input: testlist NEWLINE* ENDMARKER
# funcdef: 'def' NAME parameters ':' suite
# parameters: '(' [varargslist] ')'


@st.composite
def varargslist(draw):
    """
    varargslist: (fpdef ',')* '*' NAME | fpdef (',' fpdef)* [',']
    """
    #return (fpdef ',')* '*' NAME | fpdef (',' fpdef)* [',']


@st.composite
def fpdef(draw):
    """
    fpdef: NAME | '(' fplist ')'
    """
    #return NAME | '(' fplist ')'


@st.composite
def fplist(draw):
    """
    fplist: fpdef (',' fpdef)* [',']
    """
    #fpdef (',' fpdef)* [',']

# stmt: simple_stmt | compound_stmt
# simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
# small_stmt: expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | access_stmt | exec_stmt
# expr_stmt: (testlist '=')* testlist
# print_stmt: 'print' (test ',')* [test]
# del_stmt: 'del' exprlist
# pass_stmt: 'pass'
# flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt
# break_stmt: 'break'
# continue_stmt: 'continue'
# return_stmt: 'return' [testlist]
# raise_stmt: 'raise' test [',' test]
# import_stmt: 'import' NAME (',' NAME)* | 'from' NAME 'import' ('*' | NAME (',' NAME)*)
# global_stmt: 'global' NAME (',' NAME)*
# access_stmt: 'access' ('*' | NAME (',' NAME)*) ':' accesstype (',' accesstype)*
# accesstype: NAME+
# exec_stmt: 'exec' expr ['in' test [',' test]]
# compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef
# if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
# while_stmt: 'while' test ':' suite ['else' ':' suite]
# for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
# try_stmt: 'try' ':' suite (except_clause ':' suite)+ | 'try' ':' suite 'finally' ':' suite
# except_clause: 'except' [test [',' test]]
# suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT


def _expr_builder(draw, expr_part_strategy, delimiters):
    """
    Build a expression by drawing multiple parts of the expression and
    joining on one of the specified delimiters.

    :param draw: Let hypothesis draw examples for us.
    :param expr_part_strategy: Strategy used to make up parts of the expression.
    :param delimiters: The list of delimiters to choose from.

    :return: The built expression.
    """
    result = [draw(expr_part_strategy())]
    count = draw(st.integers(1, 5))
    for i in range(1, count):
        result.append(draw(st.sampled_from(delimiters)))
        result.append(draw(expr_part_strategy()))
    return ''.join(result)


@st.composite
def test(draw):
    """
    test: and_test ('or' and_test)* | lambdef
    """
    # TODO : lambda
    return _expr_builder(draw, and_test, 'or')  # | lambdef


def comparison():
    """
    comparison: expr (comp_op expr)*
    """
    @st.composite
    def _comparison(draw, sub_expr):
        return _expr_builder(draw, not_test, 'and')

    return st.recursive(STRING(), _comparison)


def not_test():
    """
    not_test: 'not' not_test | comparison
    """
    @st.composite
    def _not_test(draw, other_not_test):
        return 'not ' + draw(st.one_of(comparison(), other_not_test))

    return st.recursive(STRING(), _not_test)


@st.composite
def and_test(draw):
    """
    and_test: not_test ('and' not_test)*
    """
    return _expr_builder(draw, not_test, 'and')


@st.composite
def comp_op(draw):
    """
    comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    """
    ops = ('<', '>', '==', '>=', '<=', '<>', '!=',
           'in', 'not in', 'is', 'is not')
    return draw(st.sampled_from(draw, ops))


@st.composite
def expr(draw):
    """
    expr: xor_expr ('|' xor_expr)*
    """
    return _expr_builder(draw, xor_expr, '|')


@st.composite
def xor_expr(draw):
    """
    xor_expr: and_expr ('^' and_expr)*
    """
    return _expr_builder(draw, and_expr, '^')


@st.composite
def and_expr(draw):
    """
    and_expr: shift_expr ('&' shift_expr)*
    """
    return _expr_builder(draw, shift_expr, '&')


@st.composite
def shift_expr(draw):
    """
    shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    """
    return _expr_builder(draw, arith_expr, ('<<', '>>'))


@st.composite
def arith_expr(draw):
    """
    arith_expr: term (('+'|'-') term)*
    """
    return _expr_builder(draw, term, '+-')


@st.composite
def term(draw):
    """
    term: factor (('*'|'/'|'%') factor)*
    """
    return _expr_builder(draw, factor, '*/%')


def factor():
    """
    factor: ('+'|'-'|'~') factor | atom trailer*
    """
    @st.composite
    def _multi_atom_trailer(draw):
        result = [draw(atom())]
        iter_count = range(draw(st.integers(1, 5)))
        result += [draw(trailer()) for _ in iter_count]
        return ' '.join(result)

    @st.composite
    def _factor(draw, other_factor):
        unary = st.sampled_from('+-~ ')
        strategy = st.one_of(other_factor, _multi_atom_trailer())
        return unary + draw(strategy)

    return st.recursive(st.just(''), _factor)


@st.composite
def atom(draw):
    """
    atom: '(' [testlist] ')' | '[' [testlist] ']' | '{' [dictmaker] '}' | '`' testlist '`' | NAME | NUMBER | STRING
    """
    #'(' [testlist] ')' | '[' [testlist] ']' | '{' [dictmaker] '}' | '`' testlist '`' | NAME | NUMBER | STRING
    return ''


@st.composite
def lambdef(draw):
    """
    lambdef: 'lambda' [varargslist] ':' test
    """
    #'lambda' [varargslist] ':' test


@st.composite
def trailer(draw):
    """
    trailer: '(' [testlist] ')' | '[' subscript ']' | '.' NAME
    """
    #'(' [testlist] ')' | '[' subscript ']' | '.' NAME
    return ''

@st.composite
def subscript(draws):
    """
    subscript: test | [test] ':' [test]
    """
    #test | [test] ':' [test]


# exprlist: expr (',' expr)* [',']


@st.composite
def testlist(draw):
    """
    testlist: test (',' test)* [',']
    """
    #test (',' test)* [',']


@st.composite
def dictmaker(draw):
    """
    dictmaker: test ':' test (',' test ':' test)* [',']
    """
    #test ':' test (',' test ':' test)* [',']


# classdef: 'class' NAME ['(' testlist ')'] ':' suite