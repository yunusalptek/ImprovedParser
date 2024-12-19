import ASTNodeDefs as AST

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []

    # Move to the next position in the code.
    def advance(self):
        # TODO: Students need to complete the logic to advance the position.
        self.position += 1
        # set current character to none if new position is out of bounds
        if self.position >= len(self.code):
            self.current_char = None
        # otherwise set current character to character in new position
        else:
            self.current_char = self.code[self.position]

    # Skip whitespaces.
    def skip_whitespace(self):
        # TODO: Complete logic to skip whitespaces.
        # skip character while current character exists and is a space
        while self.current_char and self.current_char.isspace():
            self.advance()

    # Tokenize an identifier.
    def identifier(self):
        result = ''
        # TODO: Complete logic for handling identifiers.
        keywords = {"if": "IF", "else": "ELSE", "while": "WHILE"}
        # return a (key, value) pair of (label, keyword) if result is a keyword
        if result in keywords:
            return (keywords[result], result)
        # keep adding characters that fit identifier criteria
        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            result += self.current_char
            self.advance()
        return ('IDENTIFIER', result)

    # Tokenize a number.
    def number(self):
        # TODO: Implement logic to tokenize numbers.
        result = ""
        # keep adding characters that are digits or decimal points
        is_float = False
        while self.current_char and (self.current_char.isdigit() or self.current_char == "."):
            if self.current_char == ".":
                is_float = True
            result += self.current_char
            self.advance()
        # handle floating-point numbers
        if is_float:
            return ('FNUMBER', float(result))
        else:
            return ('NUMBER', int(result))
    
    def token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                ident = self.identifier()
                if ident[1] == 'if':
                    return ('IF', 'if')
                elif ident[1] == 'else':
                    return ('ELSE', 'else')
                elif ident[1] == 'while':
                    return ('WHILE', 'while')
                elif ident[1] == 'int':
                    return ('INT', 'int')
                elif ident[1] == 'float':
                    return ('FLOAT', 'float')
                return ident
            if self.current_char.isdigit() or self.current_char == ".":
                return self.number()

            # TODO: Add logic for operators and punctuation tokens.
            
            tokens = {"{": "LBRACE", "}": "RBRACE", "+": "PLUS", "-": "MINUS", "*": "MULTIPLY", "/": "DIVIDE",
                      "=": "EQUAL", "!": "NOT", "<": "LESS", ">": "GREATER",
                      "(": "LPAREN", ")": "RPAREN", ",": "COMMA", ":": "COLON"}
            # if current character is a token add to token list as (label, token) pair
            if self.current_char in tokens:
                # if current character is "=" check if it's just "=" or if it's "=="
                if self.current_char == "=":
                    self.advance()
                    if self.current_char == "=":
                        self.tokens.append(("EQ", "=="))
                        self.advance()
                        continue
                    else:
                        self.tokens.append(("EQUALS", "="))
                        continue
                # if current character is "!" check if it's just "!" or if it's "!="
                elif self.current_char == "!":
                    self.advance()
                    if self.current_char == "=":
                        self.tokens.append(("NEQ", "!="))
                        self.advance()
                    continue
                else:
                    self.tokens.append((tokens[self.current_char], self.current_char))
                self.advance()
                continue

            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)

    # Collect all tokens into a list.
    def tokenize(self):
        # TODO: Implement the logic to collect tokens.
        while self.current_char:
            self.tokens.append(self.token())
        return self.tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)
        self.symbol_table = {'global': {}}
        self.scope_stack = ['global']
        self.messages = []

    def error(self, message):
        # check for duplicates with exceptions
        if message not in self.messages or message == "Type Mismatch between int and float" or message == "Type Mismatch between float and int":
            self.messages.append(message)

    def advance(self):
        # Move to the next token in the list.
        # TODO: Ensure the parser doesn't run out of tokens.
        # move to next token by popping first token
        if self.tokens:
            self.current_token = self.tokens.pop(0)

    def enter_scope(self):
        # enter new scope
        new_scope = f"scope_{len(self.scope_stack)}"
        self.symbol_table[new_scope] = {}
        self.scope_stack.append(new_scope)

    def exit_scope(self):
        # exit current scope
        self.scope_stack.pop()

    def current_scope(self):
        # return current scope
        return self.scope_stack[-1]
    
    def checkVarDeclared(self, identifier):
        # check if variable has already been declared in current scope
        scope = self.current_scope()
        if identifier in self.symbol_table[scope]:
            self.error(f"Variable {identifier} has already been declared in the current scope")

    def checkVarUse(self, identifier):
        # check if variables has not been declared in any scope
        if not self.get_variable_type(identifier):
            self.error(f"Variable {identifier} has not been declared in the current or any enclosing scopes")

    def checkTypeMatch2(self, vType, eType, var, exp):
        # return if either type is undefined
        if not vType or not eType:
            return
        # return error if type mismatch
        if vType != eType:
            self.error(f"Type Mismatch between {vType} and {eType}")

    def add_variable(self, name, var_type):
        # return error if variable already declared in current scope
        scope = self.current_scope()
        if name in self.symbol_table[scope]:
            self.error(f"Variable {name} has already been declared in the current scope")
        # otherwise add variable
        else:
            self.symbol_table[scope][name] = var_type

    def get_variable_type(self, name):
        # return variable type if declared in any scopes
        for scope in reversed(self.scope_stack):
            if name in self.symbol_table[scope]:
                return self.symbol_table[scope][name]
        # otherwise return error
        self.error(f"Variable {name} has not been declared in the current or any enclosing scopes")

    def parse(self):
        """
        Entry point for the parser. It will process the entire program.
        TODO: Implement logic to parse multiple statements and return the AST for the entire program.
        """
        return self.program()

    def program(self):
        """
        Program consists of multiple statements.
        TODO: Loop through and collect statements until EOF is reached.
        """
        statements = []
        while self.current_token[0] != 'EOF':
            # TODO: Parse each statement and append it to the list.
            statements.append(self.statement())
        # TODO: Return an AST node that represents the program.
        return statements

    def statement(self):
        """
        Determines which type of statement to parse.
        - If it's an identifier, it could be an assignment or function call.
        - If it's 'if', it parses an if-statement.
        - If it's 'while', it parses a while-statement.
        
        TODO: Dispatch to the correct parsing function based on the current token.
        """
        if self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS': # Assignment
                return self.assign_stmt() #AST of assign_stmt
            elif self.peek() == 'LPAREN': # Function call
                return self.function_call() #AST of function call
            else:
                raise ValueError(f"Unexpected token after identifier: {self.current_token}")
        elif self.current_token[0] == 'IF':
            return self.if_stmt() #AST of if stmt
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt() #AST of while stmt
        elif self.current_token[0] == 'INT' or self.current_token[0] == 'FLOAT':
            return self.decl_stmt()
        elif self.current_token[0] == 'LBRACE':
            return self.block()
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

    def decl_stmt(self):
        """
        Parses a declaration statement.
        Example:
        int x = 5
        float y = 3.5
        TODO: Implement logic to parse type, identifier, and initialization expression and also handle type checking
        """
        # parses declaration statements by capturing types, identifiers, initialization expressions, and type checking
        var_type = self.current_token[1]
        self.advance()
        var_name = self.current_token[1]
        self.checkVarDeclared(var_name)
        self.advance()
        if self.current_token[0] == 'EQUALS':
            self.advance()
            expression = self.expression()
            self.checkTypeMatch2(var_type, expression.value_type, var_name, expression)
        self.add_variable(var_name, var_type)
        return AST.Declaration(var_type, var_name, expression)

    def assign_stmt(self):
        """
        Parses assignment statements.
        Example:
        x = 5 + 3
        TODO: Implement parsing for assignments, where an identifier is followed by '=' and an expression.
        """
        # parse assignment statements by capturing identifiers and expressions
        var_name = self.current_token[1]
        self.checkVarUse(var_name)
        self.advance()
        self.expect('EQUALS')
        expression = self.expression()
        var_type = self.get_variable_type(var_name)
        self.checkTypeMatch2(var_type, expression.value_type, var_name, expression)
        return AST.Assignment(var_name, expression)

    def if_stmt(self):
        """
        Parses an if-statement, with an optional else block.
        Example:
        if condition:
            # statements
        else:
            # statements
        TODO: Implement the logic to parse the if condition and blocks of code.
        """
        # parse if-statement by capturing condition, if block, and else block
        self.advance()
        condition = self.boolean_expression()
        self.enter_scope()
        then_block = self.block()
        self.exit_scope()
        else_block = None
        # parse else block if if-statement has one
        if self.current_token[0] == "ELSE":
            self.advance()
            self.enter_scope()
            else_block = self.block()
            self.exit_scope()
        return AST.IfStatement(condition, then_block, else_block)

    def while_stmt(self):
        """
        Parses a while-statement.
        Example:
        while condition:
            # statements
        TODO: Implement the logic to parse while loops with a condition and a block of statements.
        """
        # parse while-statement by capturing condition and block
        self.advance()
        condition = self.boolean_expression()
        self.enter_scope()
        block = self.block()
        self.exit_scope()
        return AST.WhileStatement(condition, block)

    def block(self):
        """
        Parses a block of statements. A block is a collection of statements grouped by indentation.
        Example:
        if condition:
            # This is a block
            x = 5
            y = 10
        TODO: Implement logic to capture multiple statements as part of a block.
        """
        self.expect('LBRACE')
        self.enter_scope()
        statements = []
        # parses statements if token is not equal to a right brace
        while self.current_token[0] != 'RBRACE':
            statements.append(self.statement())
        self.exit_scope()
        self.expect('RBRACE')
        return AST.Block(statements)

    def expression(self):
        """
        Parses an expression. Handles operators like +, -, etc.
        Example:
        x + y - 5
        TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence.
        """
        left = self.term() # Parse the first term
        while self.current_token[0] in ['PLUS', 'MINUS']: # Handle + and -
            op = self.current_token[0] # Capture the operator
            self.advance() # Skip the operator
            right = self.term() # Parse the next term
            self.checkTypeMatch2(left.value_type, right.value_type, left, right) # check for type mismatch
            left = AST.BinaryOperation(left, op, right, left.value_type)
        return left

    def boolean_expression(self):
        """
        Parses a boolean expression. These are comparisons like ==, !=, <, >.
        Example:
        x == 5
        TODO: Implement parsing for boolean expressions.
        """
        # write your code here, for reference check expression function
        # parses a boolean expression by capturing left term, operator, and right term
        left = self.term()
        comparisons = ["EQ", "NEQ", "LESS", "GREATER"]
        while self.current_token[0] in comparisons:
            op = self.current_token[0]
            self.advance()
            right = self.term()
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BooleanExpression(left, op, right)
        return left
        
    def term(self):
        """
        Parses a term. A term consists of factors combined by * or /.
        Example:
        x * y / z
        TODO: Implement the parsing for multiplication and division.
        """
        # write your code here, for reference check expression function
        # parses a term by capturing left term, operator, and right term
        left = self.factor()
        operators = ["MULTIPLY", "DIVIDE"]
        while self.current_token[0] in operators:
            op = self.current_token[0]
            self.advance()
            right = self.factor()
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BinaryOperation(left, op, right, left.value_type)
        return left

    def factor(self):
        """
        Parses a factor. Factors are the basic building blocks of expressions.
        Example:
        - A number
        - An identifier (variable)
        - A parenthesized expression
        TODO: Handle these cases and create appropriate AST nodes.
        """
        # parses integer factors
        if self.current_token[0] == 'NUMBER':
            value = int(self.current_token[1])
            self.advance()
            return AST.Factor(value, 'int')
        # parses floating-point factors
        elif self.current_token[0] == 'FNUMBER':
            value = float(self.current_token[1])
            self.advance()
            return AST.Factor(value, 'float')
        # parses identifier factors
        elif self.current_token[0] == 'IDENTIFIER':
            var_name = self.current_token[1]
            var_type = self.get_variable_type(var_name)
            self.advance()
            return AST.Factor(var_name, var_type)
        # parses paranthesized expression factors
        elif self.current_token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        """
        Parses a function call.
        Example:
        myFunction(arg1, arg2)
        TODO: Implement parsing for function calls with arguments.
        """
        # parses a function call by capturing function name and arguments
        func_name = self.current_token[1]
        self.advance()
        self.expect('LPAREN')
        args = []
        if self.current_token[0] != "RPAREN":
            args = self.arg_list()
        self.expect('RPAREN')
        return AST.FunctionCall(func_name, args)

    def arg_list(self):
        """
        Parses a list of arguments in a function call.
        Example:
        arg1, arg2, arg3
        TODO: Implement the logic to parse comma-separated arguments.
        """
        # parses a list of arguments in a function call by capturing arguments and handling commas
        args = []
        args.append(self.expression())
        while self.current_token[0] == 'COMMA':
            self.advance()
            args.append(self.expression())
        return args

    def expect(self, token_type):
        if self.current_token[0] == token_type:
            self.advance() # Move to the next token
        else:
            raise ValueError(f"Expected token {token_type}, but got {self.current_token[0]}")

    def peek(self):
        if self.tokens:
            return self.tokens[0][0]
        else:
            return None