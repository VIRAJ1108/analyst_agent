import os
import matplotlib.pyplot as plt
import pandas as pd


def _save_plot(title: str):
    """
    Saves the current matplotlib figure and returns the file path.
    """
    filename = title.lower().replace(" ", "_") + ".png"
    path = os.path.join("charts", filename)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def generate_bar_chart(df: pd.DataFrame, plan):

    data = (df.groupby(plan.x_column)[plan.y_column].sum().sort_values(ascending=False))

    plt.figure(figsize=(10, 5))

    plt.bar(data.index.astype(str), data.values)

    plt.title(plan.title)
    plt.xlabel(plan.x_column)
    plt.ylabel(plan.y_column)

    plt.xticks(rotation=45)

    return _save_plot(plan.title)

def generate_line_chart(df: pd.DataFrame, plan):
    temp = df.copy()
    temp[plan.x_column] = pd.to_datetime(temp[plan.x_column])

    data = (temp.groupby(plan.x_column)[plan.y_column].sum().sort_index())

    plt.figure(figsize=(10, 5))

    plt.plot(data.index, data.values, marker="o")

    plt.title(plan.title)
    plt.xlabel(plan.x_column)
    plt.ylabel(plan.y_column)

    return _save_plot(plan.title)


def generate_scatter_chart(df: pd.DataFrame, plan):

    plt.figure(figsize=(8, 6))

    plt.scatter(
        df[plan.x_column],
        df[plan.y_column]
    )

    plt.title(plan.title)
    plt.xlabel(plan.x_column)
    plt.ylabel(plan.y_column)

    return _save_plot(plan.title)


def generate_pie_chart(df: pd.DataFrame, plan):

    data = (
        df.groupby(plan.x_column)[plan.y_column].sum()
    )

    plt.figure(figsize=(8, 8))

    plt.pie(
        data.values,
        labels=data.index.astype(str),
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(plan.title)

    return _save_plot(plan.title)