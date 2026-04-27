from lexer import tokenize
from parser import Parser
from codegen import generate_code


def main():
    user_input = input("Enter BizLang command:\n")

    try:
        tokens = tokenize(user_input)
        print("\nTOKENS:")
        print(tokens)

        parser = Parser(tokens)
        ast = parser.parse()

        print("\nAST:")
        print(ast)

        code = generate_code(ast)

        print("\nGENERATED PYTHON CODE:\n")
        print(code)

        with open("generated_program.py", "w") as f:
            f.write(code)

        print("\nGenerated code saved to generated_program.py")

    except SyntaxError as e:
        print(f"Syntax Error: {e}")


if __name__ == "__main__":
    main()