
import string

from collections import namedtuple
from lambda_ast import Variable, Application, Abstraction


PUNCTUATION = [u'λ', '@', '.', '(', ')']
WHITESPACE = list(string.whitespace)

Token = namedtuple('Token', ['type', 'value'])

#lexer

class Lexer(object):
    """An iterator that splits lambda calculus source code into Tokens.

    Attributes:
        source (str): Lambda calculus source code
        size (int): The number of characters in the source
        position (int): Current index in the source
    """

    def __init__(self, source):
        self.source = source
        self.size = len(source)
        self.position = 0

    def __iter__(self):
        return self

    def next(self):
        """Returns the next lexeme as a Token object."""
        self._clear_whitespace()
        if self.position > self.size:
            raise StopIteration()
        elif self.position == self.size:
            self.position += 1
            return Token('EOF', None)
        elif self.source[self.position] in PUNCTUATION:
            char = self.source[self.position]
            self.position += 1
            return Token(char, None)
        else:
            symbol = ''
            while (self.position < self.size and
                   not self.source[self.position] in PUNCTUATION + WHITESPACE):
                symbol += self.source[self.position]
                self.position += 1
            return Token('SYMBOL', symbol)

    def _clear_whitespace(self):
        """Advances position past any whitespace."""
        while (self.position < self.size and
               self.source[self.position] in string.whitespace):
            self.position += 1


#parser




class Parser(object):
    """An LL(1) parser that performs syntactic analysis on lambda calculus
    source code. An abstract syntax tree is provided if the given expression is
    valid.

    Attributes:
        lexer (Lexer): A tokenizer that's iteratively read
        token (Token): The current Token object
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next()

    def _error(self, expected):
        """Raises a ParserError that compares an expected token type and the
        one given by the lexer.
        """
        raise ParserError(expected, self.token.type)

    def _advance(self):
        """Moves to the next token"""
        self.token = self.lexer.next()

    def _eat(self, prediction):
        """Advances through the source but only if type of the next token
        matches an expected form
        """
        if self.token.type == prediction:
            self._advance()
        else:
            self._error(prediction)

    def _expression(self):
        """Based on the current token, this method decides if the next
        expression is an application, abstraction, or variable"""
        if self.token.type == '(':
            self._advance()
            if self.token.type in [u'λ', '@']:
                node = self._abstraction()
            else:
                node = self._application()
            self._eat(')')
            return node
        elif self.token.type in [u'λ', '@']:
            return self._abstraction()
        elif self.token.type == 'SYMBOL':
            return self._variable()
        else:
            self._error(u'(, λ, @, or SYMBOL')

    def _variable(self):
        """Returns an instance of Variable if the current token is a symbol"""
        if self.token.type == 'SYMBOL':
            name = self.token.value
            self._advance()
            return Variable(name)
        else:
            self._error('SYMBOL')

    def _application(self):
        """Returns an Application instance if the current token is a left
        parenthesis
        """
        left_expression = self._expression()
        right_expression = self._expression()
        return Application(left_expression, right_expression)
  

    def _abstraction(self):
        """Returns an instance of Abstraction if the next series of tokens
        fits the form of a lambda calculus function"""
        if self.token.type in [u'λ', '@']:
            self._advance()
            variable = self._variable()
            self._eat('.')
            return Abstraction(variable, self._expression())
        else:
            self._error(u'λ or @')

    def parse(self):
        """Returns an abstract syntax tree if the source correctly fits the
        rules of lambda calculus
        """
        return self._expression()


class ParserError(Exception):
    """Indicates a discrepancy between what a parser expects and an actual
    value.

    Attributes:
        expected (str): The type that should have existed
        found (str): The actual type discovered
    """

    def __init__(self, expected, found):
        message = u'Expected: {}, Found: {}'.format(expected, found)
        super(ParserError, self).__init__(message)
        self.expected = expected
        self.found = found