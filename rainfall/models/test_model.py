
from sklearn.metrics import (
    mean_squared_error,
    r2_score,
    mean_absolute_error,
    explained_variance_score,
    accuracy_score,
    log_loss,
    recall_score,
    f1_score
)


import json
from ..utils.paths import make_dir_function

from pandas import DataFrame, Series
from os import makedirs

REGRESSION_METRICS ={
    'mse':mean_squared_error,
    'r2_score': r2_score,
    'mae': mean_absolute_error,
    'explained_variance_score': explained_variance_score
}

REGRESSION_METRICS_FILE_NAME = 'model_summaries_rainfall'


# *args <- y_true, y_pred, y_prob, labels

CLASSIFICATION_METRICS ={
    'accuracy_score':accuracy_score, 
    'crossentropy_loss': lambda *args : \
        log_loss(args[0], args[2], labels=args[3]),
        
    'recall_score':lambda *args : \
        recall_score(args[0], args[1],labels=args[3],
                                 average='weighted'),
                                 
    'f1_score': lambda *args : \
        f1_score(args[0], args[1], average='weighted')
}

CLASSIFICATION_METRICS_FILE_NAME = 'model_summaries_rainfall'

WORKSPACE_PATH = '..'

work_dir = make_dir_function(workspace=WORKSPACE_PATH)
metrics_destiny_file = lambda file_name, state, municipality: \
    work_dir('models', state, municipality, f'{file_name}.json')



def store_metrics_json(
    model_name: str, 
    best_parameters: dict | str, 
    y_val: list | DataFrame | Series, 
    y_predict: list | DataFrame | Series, 
    y_prob = None, 
    type_of_model = 'regression', 
    labels = None,
    state = '',
    municipality = ''
) -> dict:
    """Evaluates different prediction metrics given a predicted and actual 
    values. It stores them in json files in `data\interim`. If the function is 
    run multiple times, it concatenates this file.

    Args:
        model_name: Name of the model, thus the primary key of the json will be 
            stored.

        best_parameters: Dictionary with the best model parameters.

        y_val: Actual values that will be used to compare with the predicted values.

        y_predict: Values predicted by the model.

        y_prob: In classification, it is required to calculate the probability of each predicted value. Default is None.

        type_of_model: For now, only `classification` and `regression` are allowed values. Default is `regression`.

        labels:In classification, a list of possible categories is required.

    Returns:
        Dictionary with the different calculated metrics.
        
    """
  
    if type_of_model == 'regression':
        metrics = REGRESSION_METRICS
        file_name = REGRESSION_METRICS_FILE_NAME
    else:
        metrics = CLASSIFICATION_METRICS
        file_name = CLASSIFICATION_METRICS_FILE_NAME


    model_summary = {model_name:{
        'best_parameters': best_parameters
    }}

    for name, function in metrics.items():
        if y_prob:
            model_summary[model_name][name] = function(y_val, y_predict, 
                                                       y_prob, labels)
        else:
            model_summary[model_name][name] = function(y_val, y_predict)
        
        print(f'{name}: {model_summary[model_name][name]}')


    data = {}

    makedirs(metrics_destiny_file(file_name, state, municipality).parent,
             exist_ok=True)
    

    try:
        with open(metrics_destiny_file(file_name, state, municipality), 'r') as outfile:
            data = json.load(outfile)
            print(data)
    except:
        pass
    
        
    with open(metrics_destiny_file(file_name, state, municipality), 'w') as outfile:       
        json.dump(data | model_summary, outfile)

    return model_summary