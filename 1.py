import streamlit as st

KEYWORDS = {
    "agar": "IF",
    "warna": "ELSE",
    "jabtak": "WHILE",
    "printKaro": "PRINT",
    "lo": "DECLARE",
    "barabar": "ASSIGN"
}

OPERATORS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MUL",
    "/": "DIV",
    ">": "GT",
    "<": "LT",
    "==": "EQ"
}

SYMBOLS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE"
}

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}:{self.value}"

class Lexer:
    def __init__(self, code):
        self.code = code

    def tokenize(self):
        tokens = []
        words = self.code.replace("\n", " ").split()

        for word in words:
            if word in KEYWORDS:
                tokens.append(Token(KEYWORDS[word], word))
            elif word in OPERATORS:
                tokens.append(Token(OPERATORS[word], word))
            elif word in SYMBOLS:
                tokens.append(Token(SYMBOLS[word], word))
            elif word.isdigit():
                tokens.append(Token("NUMBER", int(word)))
            elif word.isidentifier():
                tokens.append(Token("IDENTIFIER", word))
            else:
                raise Exception(f"Lexical Error: Unknown token '{word}'")

        return tokens

class Program:
    def __init__(self, statements):
        self.statements = statements

class Assignment:
    def __init__(self, var, value):
        self.var = var
        self.value = value

    def __repr__(self):
        return f"{self.var} = {self.value}"

class Print:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"print({self.value})"

class IfElse:
    def __init__(self, condition, if_body, else_body):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

    def __repr__(self):
        return f"if {self.condition} then {self.if_body} else {self.else_body}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, type_):
        token = self.current()
        if token and token.type == type_:
            self.pos += 1
            return token
        else:
            raise Exception(f"Syntax Error: Expected {type_}, got {token}")

    def parse(self):
        statements = []
        while self.current():
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        token = self.current()

        if token.type == "DECLARE":
            return self.assignment()
        elif token.type == "PRINT":
            return self.print_stmt()
        elif token.type == "IF":
            return self.if_statement()
        else:
            raise Exception(f"Syntax Error: Invalid statement {token}")

    def assignment(self):
        self.eat("DECLARE")
        var = self.eat("IDENTIFIER").value
        self.eat("ASSIGN")
        value = self.eat("NUMBER").value
        return Assignment(var, value)

    def print_stmt(self):
        self.eat("PRINT")
        value = self.eat("IDENTIFIER").value
        return Print(value)

    def if_statement(self):
        self.eat("IF")
        condition = self.eat("IDENTIFIER").value

        self.eat("LBRACE")
        if_body = []
        while self.current() and self.current().type != "RBRACE":
            if_body.append(self.statement())
        self.eat("RBRACE")

        else_body = []
        if self.current() and self.current().type == "ELSE":
            self.eat("ELSE")
            self.eat("LBRACE")

            while self.current() and self.current().type != "RBRACE":
                else_body.append(self.statement())
            self.eat("RBRACE")

        return IfElse(condition, if_body, else_body)

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, ast):
        for stmt in ast.statements:
            self.visit(stmt)

    def visit(self, node):
        if isinstance(node, Assignment):
            self.symbol_table[node.var] = node.value

        elif isinstance(node, Print):
            if node.value not in self.symbol_table:
                raise Exception(f"Semantic Error: Variable '{node.value}' not declared")

        elif isinstance(node, IfElse):
            if node.condition not in self.symbol_table:
                raise Exception(f"Semantic Error: Variable '{node.condition}' not declared")

            for stmt in node.if_body:
                self.visit(stmt)

            for stmt in node.else_body:
                self.visit(stmt)

    def get_table(self):
        return self.symbol_table

class TACGenerator:
    def __init__(self):
        self.code = []

    def generate(self, ast):
        for stmt in ast.statements:
            self.visit(stmt)
        return self.code

    def visit(self, node):
        if isinstance(node, Assignment):
            self.code.append(f"{node.var} = {node.value}")

        elif isinstance(node, Print):
            self.code.append(f"print {node.value}")

        elif isinstance(node, IfElse):
            self.code.append(f"if {node.condition} goto L1")

            for stmt in node.else_body:
                self.visit(stmt)

            self.code.append("goto L2")
            self.code.append("L1:")

            for stmt in node.if_body:
                self.visit(stmt)

            self.code.append("L2:")

st.set_page_config(page_title="Hinglish Compiler", layout="centered")

st.title("HinglishLang Mini Compiler")
st.write("Enter Hinglish code below and run the compiler")

code = st.text_area("Hinglish Code", height=200)

if st.button("Run Compiler"):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        st.subheader("Tokens")
        st.write(tokens)

        parser = Parser(tokens)
        ast = parser.parse()

        st.subheader("AST")
        st.write(ast.statements)

        semantic = SemanticAnalyzer()
        semantic.analyze(ast)

        st.subheader("Symbol Table")
        st.write(semantic.get_table())

        tac = TACGenerator()
        code_out = tac.generate(ast)

        st.subheader("Intermediate Code")
        for line in code_out:
            st.code(line)

    except Exception as e:
        st.error(str(e))