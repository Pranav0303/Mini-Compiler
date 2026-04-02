#include <iostream>
#include <sstream>
#include <vector>
#include <unordered_map>
using namespace std;

// ---------------- TOKEN ----------------
class Token {
public:
    string type, value;
    Token(string t, string v) : type(t), value(v) {}
};

// ---------------- LEXER ----------------
unordered_map<string, string> KEYWORDS = {
    {"agar","IF"}, {"warna","ELSE"}, {"printKaro","PRINT"},
    {"lo","DECLARE"}, {"barabar","ASSIGN"}
};

class Lexer {
public:
    string code;
    Lexer(string c) : code(c) {}

    vector<Token> tokenize() {
        vector<Token> tokens;
        stringstream ss(code);
        string word;

        while (ss >> word) {
            if (KEYWORDS.count(word))
                tokens.push_back(Token(KEYWORDS[word], word));
            else if (isdigit(word[0]))
                tokens.push_back(Token("NUMBER", word));
            else
                tokens.push_back(Token("IDENTIFIER", word));
        }
        return tokens;
    }
};

// ---------------- AST ----------------
class Node {
public:
    virtual ~Node() {}
};

class Assignment : public Node {
public:
    string var, value;
    Assignment(string v, string val) : var(v), value(val) {}
};

class Print : public Node {
public:
    string value;
    Print(string v) : value(v) {}
};

class IfElse : public Node {
public:
    string condition;
    vector<Node*> if_body, else_body;

    IfElse(string cond) : condition(cond) {}
};

// ---------------- PARSER ----------------
class Parser {
public:
    vector<Token> tokens;
    int pos = 0;

    Parser(vector<Token> t) : tokens(t) {}

    Token current() {
        if (pos < tokens.size()) return tokens[pos];
        return Token("EOF", "");
    }

    Token eat(string type) {
        Token tok = current();
        if (tok.type == type) {
            pos++;
            return tok;
        }
        throw runtime_error("Syntax Error");
    }

    Node* statement() {
        Token tok = current();

        if (tok.type == "DECLARE") return assignment();
        if (tok.type == "PRINT") return print_stmt();
        if (tok.type == "IF") return if_stmt();

        throw runtime_error("Invalid statement");
    }

    Node* assignment() {
        eat("DECLARE");
        string var = eat("IDENTIFIER").value;
        eat("ASSIGN");
        string val = eat("NUMBER").value;
        return new Assignment(var, val);
    }

    Node* print_stmt() {
        eat("PRINT");
        string val = eat("IDENTIFIER").value;
        return new Print(val);
    }

    Node* if_stmt() {
        eat("IF");
        string cond = eat("IDENTIFIER").value;

        IfElse* node = new IfElse(cond);

        // skip {
        pos++;

        while (current().value != "}") {
            node->if_body.push_back(statement());
        }
        pos++; // skip }

        if (current().type == "ELSE") {
            eat("ELSE");
            pos++; // skip {

            while (current().value != "}") {
                node->else_body.push_back(statement());
            }
            pos++; // skip }
        }

        return node;
    }

    vector<Node*> parse() {
        vector<Node*> stmts;
        while (pos < tokens.size()) {
            stmts.push_back(statement());
        }
        return stmts;
    }
};

// ---------------- SEMANTIC ----------------
class Semantic {
public:
    unordered_map<string, int> table;

    void visit(Node* node) {
        if (auto a = dynamic_cast<Assignment*>(node)) {
            table[a->var] = stoi(a->value);
        }
        else if (auto p = dynamic_cast<Print*>(node)) {
            if (!table.count(p->value))
                throw runtime_error("Semantic Error: Undeclared variable " + p->value);
        }
        else if (auto i = dynamic_cast<IfElse*>(node)) {
            if (!table.count(i->condition))
                throw runtime_error("Semantic Error: Condition variable not declared");

            for (auto stmt : i->if_body) visit(stmt);
            for (auto stmt : i->else_body) visit(stmt);
        }
    }
};

// ---------------- TAC ----------------
class TAC {
public:
    vector<string> code;

    void visit(Node* node) {
        if (auto a = dynamic_cast<Assignment*>(node)) {
            code.push_back(a->var + " = " + a->value);
        }
        else if (auto p = dynamic_cast<Print*>(node)) {
            code.push_back("print " + p->value);
        }
        else if (auto i = dynamic_cast<IfElse*>(node)) {
            code.push_back("if " + i->condition + " goto L1");

            for (auto stmt : i->else_body) visit(stmt);

            code.push_back("goto L2");
            code.push_back("L1:");

            for (auto stmt : i->if_body) visit(stmt);

            code.push_back("L2:");
        }
    }
};

// ---------------- MAIN ----------------
int main() {
    string input, line;

    while (getline(cin, line)) {
        input += line + " ";
    }

    try {
        Lexer lex(input);
        auto tokens = lex.tokenize();

        cout << "TOKENS:\n";
        for (auto &t : tokens)
            cout << t.type << ":" << t.value << "\n";

        Parser parser(tokens);
        auto ast = parser.parse();

        Semantic sem;
        for (auto stmt : ast) sem.visit(stmt);

        cout << "\nSYMBOL TABLE:\n";
        for (auto &p : sem.table)
            cout << p.first << " = " << p.second << "\n";

        TAC tac;
        for (auto stmt : ast) tac.visit(stmt);

        cout << "\nTAC:\n";
        for (auto &line : tac.code)
            cout << line << "\n";
    }
    catch (exception &e) {
        cout << e.what() << endl;
    }

    return 0;
}
