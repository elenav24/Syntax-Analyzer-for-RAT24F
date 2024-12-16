"""Assignment 2 - Compilers CPSC 323
Team Members: Elena Marquez
Date: 11/5/2024
Description: This assignment involves creating a syntax analyzer using a top-down parser, 
and it;s structured into several steps to ensure that you can parse an input program 
according to a specified grammar (Rat24F) while handling errors and generating detailed outputs
"""

import Assignment1 as lexical
import re

class Parser: 
    def __init__(self, tokens, output_file): # Constructor
        self.tokens = tokens # List of tokens
        self.current_index = 0
        self.current_token = self.tokens[self.current_index]
        self.output_file = output_file

    def write_output(self, message): # Write output to the file
        self.output_file.write(message + '\n')

    def advance(self): # Move to the next token
        self.current_index += 1 # Increment the index
        if self.current_index < len(self.tokens):  # Check if the index is within the bounds
            self.current_token = self.tokens[self.current_index]

    def match(self, expected_type): # Match the current token with the expected token
        if self.current_token.token_type == expected_type:
            self.write_output(f"Token: {str(self.current_token.token_type):<15} Lexeme: {str(self.current_token.lexeme):<20}")
            self.advance()
        else: # Raise an error if the token types do not match
            raise SyntaxError(f"Unexpected token {self.current_token.token_type}, expected {expected_type}, lexeme: {self.current_token.lexeme}")

    def parse(self): # Start parsing the input program
        self.rat24f()

    def rat24f(self): # Define the Rat24F grammar
        self.write_output("\t<Rat24F> -> <Opt Function Definitions> @ <Opt Declaration List> <Statement List> @")
        self.opt_function_definitions()
        self.match("separator")  # Match '@'
        self.opt_declaration_list()
        self.statement_list()
        self.match("separator")  # Match '@'

    def opt_function_definitions(self):
        if self.current_token.lexeme == "function":
            self.write_output("\t<Opt Function Definitions> -> <Function Definitions> | ε")
            self.function_definitions()

    def function_definitions(self):
        self.write_output("\t<Function Definitions> -> <Function> | <Function> <Function Definitions>")
        self.function()
        while self.current_token.lexeme == "function":
            self.function()

    def function(self):
        self.write_output("\t<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        self.match("keyword")  # Match 'function'
        self.match("identifier")
        self.match("separator")  # Match '('
        self.opt_parameter_list()
        self.match("separator")  # Match ')'
        self.opt_declaration_list()
        self.body()

    def opt_parameter_list(self): # Optional parameter list
        if self.current_token.token_type == "identifier":
            self.write_output("\t<Opt Parameter List> -> <Parameter List> | ε")
            self.parameter_list()
        
    def parameter_list(self): # Parameter list
        self.write_output("\t<Parameter List> -> <Parameter> | <Parameter>, <Parameter List>")
        self.parameter()
        while self.current_token.lexeme != ")": # Continue parsing parameters until the closing parenthesis
            self.match("separator")  # Match ','
            self.parameter()

    def parameter(self): # Parameter
        self.write_output("\t<Parameter> -> <IDs> <Qualifier>")
        self.ids()
        self.qualifier()

    def qualifier(self): # Qualifier
        if self.current_token.lexeme in ["integer", "real", "boolean"]: # Check if the token is a qualifier
            self.write_output(f"\t<Qualifier> -> {self.current_token.lexeme}")
            self.match("keyword")
        else:
            raise SyntaxError("Expected a qualifier, but got: " + str(self.current_token.lexeme))

    def ids(self): # IDs
        self.write_output("\t<IDs> -> <Identifier> | <Identifier>, <IDs>")
        self.match("identifier")
        while self.current_token.lexeme == ",": # Continue parsing IDs until there are no more commas
            self.match("separator")
            self.match("identifier")

    def opt_declaration_list(self): # Optional declaration list
        if self.current_token.token_type == "keyword" and self.current_token.lexeme in ["integer", "real", "boolean"]:
            self.write_output("\t<Opt Declaration List> -> <Declaration List> | ε")
            self.declaration_list()

    def declaration_list(self): # Declaration list
        self.write_output("\t<Declaration List> -> <Declaration>; | <Declaration>;<Declaration List>")
        self.declaration()
        self.match("separator")  # Match ';'
        while self.current_token.token_type == "keyword" and self.current_token.lexeme in ["integer", "boolean", "real"]:
            self.declaration()
            self.match("separator")  # Match ';'

    def declaration(self): # Declaration
        self.write_output("\t<Declaration> -> <Qualifier> <IDs>")
        self.qualifier()
        self.ids()

    def body(self): # Body
        self.write_output("\t<Body> -> { <Statement List> }")
        self.match("separator")  # Match '{'
        self.statement_list()  # Handle the list of statements inside the body
        self.match("separator")  # Match '}'

    def statement_list(self): # Statement list
        self.write_output("\t<Statement List> -> <Statement> | <Statement> <Statement List>")
        self.statement()
        while self.current_token.token_type in ["identifier", "keyword"]:
            self.statement()

    def statement(self): # Statement
        if self.current_token.token_type == "identifier":
            self.write_output("\t<Statement> -> <Assign>")
            self.assign()
        elif self.current_token.lexeme == "if":
            self.write_output("\t<Statement> -> <If>")
            self.if_statement()
        elif self.current_token.lexeme == "return":
            self.write_output("\t<Statement> -> <Return>")
            self.return_statement()
        elif self.current_token.lexeme == "put":
            self.write_output("\t<Statement> -> <Print>")
            self.print_statement()
        elif self.current_token.lexeme == "get":
            self.write_output("\t<Statement> -> <Scan>")
            self.scan_statement()
        elif self.current_token.lexeme == "while":
            self.write_output("\t<Statement> -> <While>")
            self.while_statement()
        elif self.current_token.token_type == "separator" and self.current_token.lexeme == "{":
            self.write_output("\t<Statement> -> <Compound>")
            self.compound_statement()
        else:
            raise SyntaxError(f"Unexpected statement: {self.current_token.lexeme}")

    def if_statement(self): # If statement
        self.write_output("\t<If> -> if ( <Condition> ) <Statement> fi | if ( <Condition> ) <Statement> else <Statement> fi")
        self.match("keyword")  # Match "if"
        self.match("separator")  # Match '('
        self.condition()  # Handle condition expression
        self.match("separator")  # Match ')'
        self.statement()  # Handle the body of the if statement
        if self.current_token.lexeme == "else":
            self.match("keyword") # Match "else"
            self.statement()  # Handle the else statement   
        self.match("keyword")  # Match "fi"

    def return_statement(self): # Return statement
        self.write_output("\t<Return> -> return ; | return <Expression>;")
        self.match("keyword")  # Match "return"
        if self.current_token.lexeme != ";":
            self.expression()  # Handle the expression in the return statement
        self.match("separator")  # Match ';'

    def print_statement(self): # Print statement
        self.write_output("\t<Print> -> put (<Expression>);")
        self.match("keyword")  # Match "print"
        self.match("separator")
        self.expression()  # Handle the expression to print
        self.match("separator")  # Match ')'
        self.match("separator")  # Match ';'

    def scan_statement(self): # Scan statement
        self.write_output("\t<Scan> -> get ( <IDs> );")
        self.match("keyword")  # Match "scan"
        self.match("separator")  # Match '('
        self.ids()  # Handle the IDs to scan
        self.match("separator")  # Match ')'
        self.match("separator")  # Match ';'

    def while_statement(self): # While statement
        self.write_output("\t<While> -> while ( <Condition> ) <Statement>")
        self.match("keyword")  # Match 'while'
        self.match("separator")  # Match '('
        self.condition()  # Handle the condition (Expression Relop Expression)
        self.match("separator")  # Match ')'
        self.statement()  # Handle the body of the loop

    def compound_statement(self): # Compound statement
        self.write_output("\t<Compound> -> { <Statement List> }")
        self.match("separator")  # Match '{'
        self.statement_list()  # Handle the list of statements inside the compound
        self.match("separator")  # Match '}'

    def condition(self): # Condition
        self.write_output("\t<Condition> -> <Expression> <Relop> <Expression>")
        self.expression()  # Parse the first expression
        self.relop()       # Match the relational operator
        self.expression()  # Parse the second expression

    def assign(self): # Assignment
        self.write_output("\t<Assign> -> <Identifier> = <Expression>;")
        self.match("identifier")
        self.match("operator")  # Match '='
        self.expression()
        self.match("separator")  # Match ';'

    def expression(self): # Expression
        self.write_output("\t<Expression> -> <Term> <Expression Prime>")
        self.term()  # Parse the first term
        self.expression_prime()  # Handle the remaining expression (e.g., + or -)

    def expression_prime(self): # Expression prime
        if self.current_token.lexeme in ["+", "-"]:
            self.write_output(f"\t<Expression Prime> -> {self.current_token.lexeme} <Term> <Expression Prime>")
            self.match("operator") # Match '+' or '-'
            self.term()
            self.expression_prime()
        else:
            self.write_output("\t<Expression Prime> -> ε")

    def term(self): # Term
        self.write_output("\t<Term> -> <Factor> <Term Prime>")
        self.factor()
        self.term_prime()

    def term_prime(self): # Term prime
        if self.current_token.lexeme in ["*", "/"]:
            self.write_output(f"\t<Term Prime> -> {self.current_token.lexeme} <Factor> <Term Prime>")
            self.match("operator") # Match '*' or '/'
            self.factor()
            self.term_prime()
        else:
            self.write_output("\t<Term Prime> -> ε")

    def factor(self): # Factor
        if self.current_token.token_type == "identifier":
            self.write_output("\t<Factor> -> <Identifier>")
            self.match("identifier")
            # Check if it's followed by '(' indicating a function call (R28: <Identifier> ( <IDs> ))
            if self.current_token.lexeme == "(":
                self.write_output("\t<Factor> -> <Identifier> ( <IDs> )")
                self.match("separator")  # Match '('
                self.ids()  # Parse the function arguments (IDs)
                self.match("separator")  # Match ')'
        elif self.current_token.token_type == "integer":
            self.write_output("\t<Factor> -> <Integer>")
            self.match("integer")
        elif self.current_token.token_type == "real":  # Handle <Real>
            self.write_output("\t<Factor> -> <Real>")
            self.match("real")
        elif self.current_token.lexeme == "true" or self.current_token.lexeme == "false":  # Handle <Boolean>
            self.write_output("\t<Factor> -> <Boolean>")
            self.match("keyword")
        elif self.current_token.token_type == "separator" and self.current_token.lexeme == "(":  # Handle parentheses (R28: ( <Expression> ))
            self.write_output("\t<Factor> -> ( <Expression> )")
            self.match("separator")  # Match '('
            self.expression()  # Parse the expression inside parentheses
            self.match("separator")  # Match ')'
        else:
            raise SyntaxError("Invalid factor: " + str(self.current_token.lexeme))

    def relop(self): # Relational operator
        if self.current_token.lexeme in ["==", "!=", ">", "<", "<=", ">="]:
            self.match("operator") # Match the relational operator
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.lexeme}, expected a relational operator")

#main function
def main():
    tokens = [] # List of tokens
    input_filename = input("Enter the input file name: ")
    output_filename = input_filename.rsplit('.', 1)[0] + '_syntax_output.txt'

    try:
        # Open files with the correct encoding
        with open(input_filename, 'r') as file, open(output_filename, 'w', encoding='utf-8') as output_file:

            comment_buffer = ""
            inside_comment = False
            # Tokenize input file line by line
            for line in file:

                if inside_comment:
                    comment_buffer += line  # Continue adding to the comment buffer
                    if "*]" in line:  # End of multi-line comment
                        line = comment_buffer
                        inside_comment = False
                        comment_buffer = ""  # Reset the comment buffer after processing
                    continue  # Skip adding this line to the token list
                
                # Check if line starts a comment
                if "[*" in line:
                    inside_comment = True
                    comment_buffer = line  # Start accumulating the comment
                    if "*]" in line:  # If the comment is on one line
                        inside_comment = False
                        comment_buffer = ""  # Reset the comment buffer after processing
                    continue  # Skip adding this line to the token list
                # Remove comments and other unnecessary parts here
                line = re.sub(r'\[\*\s*.*?\s*\*\]', '', line, flags=re.DOTALL)
                line_tokens = lexical.lexer(line)
                if line_tokens:
                    tokens.extend(line_tokens)

            # Reset the index and start parsing
            parser = Parser(tokens, output_file)
            parser.parse()

    except Exception as e: # Catch any exceptions
        print(f"Error: {e}")

if __name__ == "__main__": # Run the main function
    main()