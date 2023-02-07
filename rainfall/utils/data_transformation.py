import pandas as pd
from typing import (
    List,
    Dict
)



def limits_to_slices(
    limits: List[int]
) -> List[slice]:

    """Converts a list of indices at which another list will be split into
    slices.

    Args:
        limits: It is an int list limits of the form [a_0, a_1, a_2,...a_n].

    Returns:
        Returns a list of slices, formed from the list of the form 
            [slice(0,a_0), slice(a_0,a_1), slice(a_1,a_2), ... , 
             slice(a_(n-1),a_n)]
    """  
    limits = list(limits)

    # Add start.
    limits.insert(0,0)

    # First slice.
    slices = [slice(limits[0], limits[0]+limits[1])]

    # Next slices

    for i in range(2,len(limits)):
        current = slices[i-2].stop
        slices.append(slice(current, current + limits[i]))

    return slices


def split_data(
    data_frame: pd.DataFrame, 
    independent_vars: List[str], 
    split_values: Dict[str, int]
) -> Dict[str, Dict[str, dict]]:  
    """Splits DataFrames into independent and dependent variables into three or more training, testing, and validation sets for data science.

    Args:
        data_frame: The source of the data to separate.

        independent_vars: List of column names considered as independent 
            variables. The other columns will be considered as dependent 
            variables.

        split_values: Dict of the size of each set, has the form 
            {'set_0': n_(set_0), 'set_1':n_(set1), ...},  where set_i can be    
            changed to whatever name is preferred. The dataframe rows are 
            separated in the given order not randomly.

    Returns:
        Returns three nested dictionaries, with the following structure: 
            keys dict_values[independent_var_name][type_of_vars][set_name], 
            where `independent_var_name` is one of the `independent_vars` 
            provided, `type_of_vars` is `x` for dependent variables and `y` for 
            dependent ones and `set_name` are the keys of the `split_values`.

    """  

    # To slice.
    slices = limits_to_slices(split_values.values())

    # Definition of dict of data frames with keys: `train`, `test` and `validation.`
    dict_data_frames = {}

    for key, sli in zip(split_values.keys(), slices):
        dict_data_frames[key] = data_frame[sli]


    # Normalization 
    first_key = list(split_values.keys())[0]

    train_mean = dict_data_frames[first_key].mean(numeric_only=True)
    train_std = dict_data_frames[first_key].std(numeric_only=True)

    for key, value in dict_data_frames.items():
        if pd.core.dtypes.common.is_numeric_dtype(dict_data_frames[key]):
            dict_data_frames[key] = (value - train_mean) / train_std


    # Separating dependent variables.
    columns = data_frame.columns.to_list()
    dependet_vars = [column for column in columns if column not in independent_vars]


    # Separating independent variables.
    dict_vars = {}
    for var_name in independent_vars:
        dic_aux_y = {}
        dic_aux_x = {}
        for key, value in dict_data_frames.items():
            dic_aux_y[key] = value[var_name]
            dic_aux_x[key] = value[dependet_vars]

        dict_vars[var_name] = {'x':dic_aux_x, 'y': dic_aux_y}

    return dict_vars