import re

INTEGER = 'INTEGER'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
DOT = 'DOT'
OPEN_BRACE = '('
CLOSE_BRACE = ')'
ID = 'ID'
ASSIGN = 'ASSIGN'
SEMI = 'SEMI'
EOF = 'EOF'


class Token(object):
    """
     Each syntax submitted is broken down to Token
     Token is the basic unit of the syntax.

     :type represents the type of Token: Each token is classified to one of the following
     'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DOT', 'DIV', '(', ')', 'ID', 'ASSIGN',
    'SEMI', 'EOF'
    """

    def __init__(self, type, value):
        self.type = type
        self.value = value


class Lexer(object):
    """
        Lexer break downs syntax into tokens.
        This also traverses the syntax, and returns current token.
    """

    def __init__(self, text):
        # syntax
        self.syntax = text
        # self.pos is an index into self.syntax
        self.pos = 0
        # current char
        self.current_char = self.syntax[self.pos]

    def error(self):
        """
        Raises error.
        :return: Exception
        """
        raise Exception('Error')

    def advance(self):
        """
        Advance to next token.
        :return: new syntax
        """
        self.pos += 1
        if self.pos > len(self.syntax) - 1:
            self.current_char = None
        else:
            self.current_char = self.syntax[self.pos]

    def skip_whitespace(self):
        """
        skip whitespace
        """
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """
        Returns number, could be multi-digit
        :return: INTEGER
        """
        literal = re.compile(r'(0){1}|([1-9])\d*')
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if literal.fullmatch(result) is not None:
            return int(result)
        else:
            self.error()

    def _id(self):
        """
            Handle identifiers and reserved keywords
        """
        result = ''
        while self.current_char is not None and self.current_char.isalnum() or self.current_char == '_':
            result += self.current_char
            self.advance()

        return Token(ID, result)

    def get_next_token(self):
        """
            Returns next token of syntax
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == '=':
                self.advance()
                return Token(ASSIGN, '=')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '(':
                self.advance()
                return Token(OPEN_BRACE, '(')

            if self.current_char == ')':
                self.advance()
                return Token(CLOSE_BRACE, ')')

            self.error()

        return Token(EOF, None)


class Operation(object):
    pass


class Binary(Operation):
    """
    Represents binary operation.
    left represents left portion of operation and right represents right one.
    op represents the operator.
    """

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Numeric(Operation):
    """
    Represents the numeric value
    """

    def __init__(self, token):
        self.token = token
        self.value = token.value


class Unary(Operation):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Assign(Operation):
    def __init__(self, left, op, right, semi):
        self.left = left
        self.token = self.op = op
        self.right = right
        self.semi = semi


class Variable(Operation):

    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(Operation):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def consume(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def execute(self):
        node = self.assignment_statement()
        while self.current_token.type in ASSIGN:
            token = self.current_token
            if token.type == ASSIGN:
                self.consume(DOT)

            node = Binary(left=node, op=token, right=self.assignment_statement())

        return node

    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.consume(ASSIGN)
        right = self.expr()
        semi = self.current_token
        self.consume(SEMI)
        node = Assign(left, token, right, semi)
        return node

    def variable(self):
        node = Variable(self.current_token)
        self.consume(ID)
        return node

    def empty(self):
        return NoOp()

    def expr(self):

        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.consume(PLUS)
            elif token.type == MINUS:
                self.consume(MINUS)

            node = Binary(left=node, op=token, right=self.term())

        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL):
            token = self.current_token
            if token.type == MUL:
                self.consume(MUL)
            node = Binary(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        token = self.current_token
        if token.type == PLUS:
            self.consume(PLUS)
            node = Unary(token, self.factor())
            return node
        elif token.type == MINUS:
            self.consume(MINUS)
            node = Unary(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.consume(INTEGER)
            return Numeric(token)
        elif token.type == OPEN_BRACE:
            self.consume(OPEN_BRACE)
            node = self.expr()
            self.consume(CLOSE_BRACE)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        node = self.execute()
        if self.current_token.type != EOF:
            self.error()

        return node


class NodeVisitor(object):
    """
    Visitor to traverse in expression.
    """

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    # dictionary to hold the variable and their value
    VARIABLES = {}

    def __init__(self, text):
        """
        Constructor
        :param text: input syntax to be interpreted.
        @:return Interpreters
        """
        self.parser = Parser(Lexer(text))

    def visit_Binary(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Numeric(self, node):
        """
        Returns value of numeirc token.
        :param node:
        :return:
        """
        return node.value

    def visit_Unary(self, node):
        """
        Handles unary operations eg. +,-,*,/
        """
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        """
        further breaks down compound visit
        """
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        """
        Assigns the value to variable,
        Also caches the key and value of variable in VARIABLES
        :param node:
        :return:
        """
        var_name = node.left.value
        self.VARIABLES[var_name] = self.visit(node.right)

    def visit_Variable(self, node):
        """
        Used to look up value of variable from VARIABLES dictionary.
        :param node:
        :return:
        """
        var_name = node.value
        val = self.VARIABLES.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_NoOp(self, node):
        pass

    def interpret(self):
        """
        Start interpreting the provided text.
        :return:
        """
        tree = self.parser.parse()
        if tree is None:
            return ''
        return self.visit(tree)


def main():
    """
    Main program, waits for the syntax input infinitely until the program is killed.
    Interprets every syntax, and keeps the variable in the global scope,  so that same variables can be used for later
    syntax.
    :return:
    """
    try:
        while True:
            try:
                text = input(' enter expression > ')
            except EOFError:
                break
            if not text:
                continue

            # instantiate interpreter
            interpreter = Interpreter(text)
            interpreter.interpret()

            # print the value of variable in scope after interpreting every syntax.
            print("\n".join("{} = {}".format(key, value) for key, value in interpreter.VARIABLES.items()))
    except:
        print("error")


if __name__ == '__main__':
    main()
