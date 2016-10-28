# BEGIN
#     BEGIN
#         number := 2;
#         a := number;
#         b := 10 * a + 10 * number / 4;
#         c := a - - b
#     END;
#     x := 11;
# END.

# grammer rule
# program: compound_statement DOT
# compound_statement: BEGIN statement_list END
# statement_list: statement | statement SEMI statement_list
# statement: compound_statement | assignment_statement | empty
# assignment_statement: variable ASSIGN expr
# variable: ID
# empty:
# expr: term((PLUS | MINUS)term)*
# term: factor((MUL | DIV)factor)*
# factor: PLUS factor | MINUS factor | INTEGER | LP expr RP | variable
