from ast_nodes import CommandNode, LoadNode, FilterNode, AggregateNode, PlotNode, ExportNode


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, expected_type):
        token = self.current_token()
        if token is None:
            raise SyntaxError(f"Expected {expected_type}, but reached end of input.")
        if token[0] == expected_type:
            self.pos += 1
            return token
        raise SyntaxError(f"Expected {expected_type}, got {token[0]}")

    def parse(self):
        load_node = self.parse_load()
        actions = []

        while self.current_token() and self.current_token()[0] == "AND":
            self.eat("AND")
            actions.append(self.parse_action())

        return CommandNode(load=load_node, actions=actions)

    def parse_load(self):
        self.eat("LOAD")
        filename = self.eat("IDENTIFIER")[1]
        return LoadNode(filename)

    def parse_action(self):
        token = self.current_token()

        if token[0] == "FILTER":
            return self.parse_filter()
        elif token[0] in ("SUM", "AVG", "COUNT", "MIN", "MAX"):
            return self.parse_aggregate()
        elif token[0] == "PLOT":
            return self.parse_plot()
        elif token[0] == "EXPORT":
            return self.parse_export()
        else:
            raise SyntaxError(f"Unexpected action token: {token}")

    def parse_filter(self):
        self.eat("FILTER")
        column = self.eat("IDENTIFIER")[1]
        operator = self.eat("OPERATOR")[1]

        token = self.current_token()
        if token[0] in ("STRING", "NUMBER", "IDENTIFIER"):
            value = self.eat(token[0])[1]
        else:
            raise SyntaxError("Expected filter value")

        return FilterNode(column, operator, value)

    def parse_aggregate(self):
        function = self.eat(self.current_token()[0])[1]

        column = None
        group_by = None

        if function != "COUNT":
            column = self.eat("IDENTIFIER")[1]

        if self.current_token() and self.current_token()[0] == "BY":
            self.eat("BY")
            group_by = self.eat("IDENTIFIER")[1]

        return AggregateNode(function=function, column=column, group_by=group_by)

    def parse_plot(self):
        self.eat("PLOT")
        plot_type = self.eat(self.current_token()[0])[1]
        return PlotNode(plot_type)

    def parse_export(self):
        self.eat("EXPORT")
        filename = self.eat("IDENTIFIER")[1]
        return ExportNode(filename)