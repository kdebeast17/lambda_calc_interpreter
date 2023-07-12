"""
TO DO:=
1. add multiple arguments
2. add currying
3. add assignment of functions/applications to variables using 'let' 
"""
from lexer_parser import Lexer, Parser, ParserError
from interpreter import BetaReduction


def interpret(input_string, print_reductions=False):
    """Performs normal order reduction on the given string lambda calculus
    expression. Returns the expression's normal form if it exists.
    """
    lexer = Lexer(input_string)
    try:
        ast = Parser(lexer).parse()
        #print(ast)
    except ParserError as discrepancy:
        print ('ParseError: ') + discrepancy.message
        return None
    normal_form = False
    while not normal_form:
        reducer = BetaReduction()
        reduced_ast = reducer.visit(ast)
        normal_form = not reducer.reduced
        if print_reductions:
            print (str(ast))
        ast = reduced_ast
    return str(ast)


def main():
    """Begins an interactive lambda calculus interpreter"""
    print ("Type 'quit' to exit.")
    while True:
        read = input('> ')
        if read == 'quit':
            break
        if read != '':
            interpret(read, print_reductions=True)


if __name__ == '__main__':
    main()