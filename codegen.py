from ast_nodes import FilterNode, AggregateNode, PlotNode, ExportNode


def generate_code(command_node):
    lines = [
        "import pandas as pd",
        "import matplotlib.pyplot as plt",
        "",
        f'df = pd.read_csv("{command_node.load.filename}")'
    ]

    result_name = "df"
    aggregated = False
    agg_column = None
    group_by = None

    for action in command_node.actions:
        if isinstance(action, FilterNode):
            op = "==" if action.operator == "=" else action.operator
            value = f'"{action.value}"' if isinstance(action.value, str) else action.value
            lines.append(f'{result_name} = {result_name}[{result_name}["{action.column}"] {op} {value}]')

        elif isinstance(action, AggregateNode):
            aggregated = True
            agg_column = action.column
            group_by = action.group_by

            if action.function == "COUNT":
                if group_by:
                    lines.append(
                        f'result = {result_name}.groupby("{group_by}", as_index=False).size()'
                    )
                else:
                    lines.append(f'result = pd.DataFrame({{"count": [{result_name}.shape[0]]}})')
            else:
                func = action.function.lower()
                if group_by:
                    lines.append(
                        f'result = {result_name}.groupby("{group_by}", as_index=False)["{agg_column}"].{func}()'
                    )
                else:
                    lines.append(
                        f'result = pd.DataFrame({{{{"{action.function.lower()}_{agg_column}": [{result_name}["{agg_column}"].{func}()]}}}})'
                    )
            result_name = "result"

        elif isinstance(action, PlotNode):
            if action.plot_type == "BAR":
                if aggregated and group_by and agg_column:
                    lines.append(f'{result_name}.plot(kind="bar", x="{group_by}", y="{agg_column}")')
                    lines.append("plt.tight_layout()")
                    lines.append("plt.show()")
                else:
                    lines.append(f'{result_name}.plot(kind="bar")')
                    lines.append("plt.tight_layout()")
                    lines.append("plt.show()")

            elif action.plot_type == "LINE":
                if aggregated and group_by and agg_column:
                    lines.append(f'{result_name}.plot(kind="line", x="{group_by}", y="{agg_column}")')
                    lines.append("plt.tight_layout()")
                    lines.append("plt.show()")
                else:
                    lines.append(f'{result_name}.plot(kind="line")')
                    lines.append("plt.tight_layout()")
                    lines.append("plt.show()")

        elif isinstance(action, ExportNode):
            lines.append(f'{result_name}.to_csv("{action.filename}", index=False)')

    lines.append("")
    lines.append(f'print({result_name})')

    return "\n".join(lines)