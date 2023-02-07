import matplotlib.pyplot as plt
from typing import (
    Callable,
    List
)

from datetime import datetime
from pandas import DataFrame, Series

FIG_HEIGHT = 8
FIG_WIDTH = 11

def plot_function_pairs_columns(
        data_function: Callable[[str], DataFrame | Series], 
        column_pairs: list[list[str]], 
        title=None,
        ylabels=None, 
        xlabels=None, 
        xlims=None) -> None:
    
    """It is used with Dataframes, it plots a double plot in which in turn 
    there can be several plotted variables. Use with to plot time series.

    Args:
        data_function: It is a function that, given a name str in the 
            column_pairs list, returns the series or Data Frame of a column, 
            with the values to be graphed.

        column_pairs: It is a list of lists containing the names of the columns 
            to plot in each subplot.
        
        title: The title of the plot. By default it is empty.

        ylabels: A list with the str of the names of the vertical axes for each 
            subplot.

        xlabels: A list with the str of the names of the horizontal axes for    
            each subplot.

        xlims: list with the horizontal limits, following the conventions of 
            Matplotlib.

    """


    if not xlims:
        xlims = [None for _ in range(2)]

    
    fig, axs = plt.subplots(2, 1)

    fig.set_figheight(round(FIG_HEIGHT/2))
    fig.set_figwidth(FIG_WIDTH)
    
    if title:
        fig.suptitle(title)

    for ax, columns, xlabel, ylabel, xlim in zip(axs, column_pairs, xlabels, ylabels, xlims):
        
        for column in columns:
            ax.plot(data_function(column),label=column)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if xlim:
            ax.set_xlim(xlim)

        ax.legend()


def plot_model(
    y_train: Series, 
    y_test: Series, 
    y_val: Series, 
    y_predict: Series, 
    title: str, 
    metric: list, 
    xlabel = '', 
    ylabel = ''
) -> None:
        
    """For Time Series, plots the training, validation, and prediction values

    Args:
        y_train: Train values.

        y_test: Test values.
        
        y_val: Validation values.

        y_predict: Prediction values.

        title: Name of the model.

        metric: Is a list with two elements [name, value], the first one is the 
            name of the metric and the second is its value.

        xlabel: Name of the horizontal axis, default is ''.

        ylabel: Name of the vertical axis, default is ''.

    """
    
    _, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    ax.plot(y_train.append(y_test))
    ax.plot(y_val , label='truth', linestyle='--',)
    ax.plot(y_val.index, y_predict,  
            label=f"prediction ({metric[0]} = {metric[1]:0.2f})")
    
    ax.set_xlim(datetime(year=2005, month=1, day=1))
    ax.set_ylim(-1,5)

    if xlabel:
        ax.set_xlabel(xlabel)
    
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.legend()
    ax.set_title(title)