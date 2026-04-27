import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from lexer import tokenize
from parser import Parser
from ast_nodes import FilterNode, AggregateNode, PlotNode, ExportNode

FILE_NAME = "nba_25_26_stats.csv"

st.set_page_config(page_title="CourtVisionLang", layout="wide")

st.title("CourtVisionLang: NBA Analytics Extension")
st.write(
    "CourtVisionLang extends BizLang into basketball analytics using NBA player statistics. "
    "It uses the same lexer, parser, and AST pipeline to analyze basketball data."
)

st.subheader("Example Commands")
st.code(
    f'''LOAD {FILE_NAME} AND SUM PpG BY TEAM AND PLOT BAR
LOAD {FILE_NAME} AND SUM RpG BY TEAM AND PLOT BAR
LOAD {FILE_NAME} AND AVG PpG BY TEAM AND PLOT BAR
LOAD {FILE_NAME} AND MAX RpG BY TEAM
LOAD {FILE_NAME} AND FILTER TEAM = "Bos" AND AVG PpG BY NAME
LOAD {FILE_NAME} AND COUNT BY POS'''
)

command = st.text_input(
    "Enter Command:",
    f"LOAD {FILE_NAME} AND SUM RpG BY TEAM AND PLOT BAR"
)


def execute_ast(command_node):
    df = pd.read_csv(command_node.load.filename)
    result = df.copy()

    plot_type = None
    group_by = None
    column = None
    export_file = None

    for action in command_node.actions:

        if isinstance(action, FilterNode):
            col = action.column
            value = action.value

            if col not in result.columns:
                raise ValueError(f"Column '{col}' not found in dataset.")

            if action.operator == "=":
                result = result[result[col].astype(str) == str(value)]

            elif action.operator == ">":
                result[col] = pd.to_numeric(result[col], errors="coerce")
                result = result[result[col] > float(value)]

            elif action.operator == "<":
                result[col] = pd.to_numeric(result[col], errors="coerce")
                result = result[result[col] < float(value)]

        elif isinstance(action, AggregateNode):
            group_by = action.group_by
            column = action.column

            if group_by and group_by not in result.columns:
                raise ValueError(f"Group-by column '{group_by}' not found in dataset.")

            if action.function == "COUNT":
                if group_by:
                    result = result.groupby(group_by, as_index=False).size()
                    result = result.sort_values(by="size", ascending=False).reset_index(drop=True)
                else:
                    result = pd.DataFrame({"count": [len(result)]})

            else:
                if column not in result.columns:
                    raise ValueError(f"Metric column '{column}' not found in dataset.")

                result[column] = pd.to_numeric(result[column], errors="coerce")

                if action.function == "AVG":
                    func = "mean"
                elif action.function == "SUM":
                    func = "sum"
                elif action.function == "MAX":
                    func = "max"
                elif action.function == "MIN":
                    func = "min"
                else:
                    raise ValueError(f"Unsupported aggregate function: {action.function}")

                if group_by:
                    result = result.groupby(group_by, as_index=False)[column].agg(func)
                    result = result.sort_values(by=column, ascending=False).reset_index(drop=True)
                else:
                    result = pd.DataFrame({
                        f"{func}_{column}": [getattr(result[column], func)()]
                    })

        elif isinstance(action, PlotNode):
            plot_type = action.plot_type

        elif isinstance(action, ExportNode):
            export_file = action.filename
            result.to_csv(export_file, index=False)

    return result, plot_type, group_by, column, export_file


if st.button("Run NBA Analysis"):
    try:
        tokens = tokenize(command)
        parser = Parser(tokens)
        ast = parser.parse()

        st.success("Command parsed successfully.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Tokens")
            st.code(str(tokens))

        with col2:
            st.subheader("AST")
            st.code(str(ast))

        result, plot_type, group_by, column, export_file = execute_ast(ast)

        st.subheader("NBA Results")
        st.dataframe(result, use_container_width=True)

        if export_file:
            st.info(f"Result exported to {export_file}")

        if plot_type:
            st.subheader("Chart Output")

            chart_data = result.copy()

            if len(chart_data) > 15:
                chart_data = chart_data.head(15)

            fig, ax = plt.subplots(figsize=(12, 6))

            if plot_type == "BAR":
                if group_by and column:
                    chart_data.plot(kind="bar", x=group_by, y=column, ax=ax, legend=False)
                    ax.set_xlabel(group_by)
                    ax.set_ylabel(column)
                else:
                    chart_data.plot(kind="bar", ax=ax)

            elif plot_type == "LINE":
                if group_by and column:
                    chart_data.plot(kind="line", x=group_by, y=column, ax=ax, marker="o", legend=False)
                    ax.set_xlabel(group_by)
                    ax.set_ylabel(column)
                else:
                    chart_data.plot(kind="line", ax=ax)

            ax.set_title("CourtVisionLang NBA Analytics Output")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)

    except Exception as e:
        st.error(str(e))