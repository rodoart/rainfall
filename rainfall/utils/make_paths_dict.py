# Load custom library


# Load custom library

from pathlib import Path

here = Path(__file__).resolve()
workspace = here.parents[2]

from sys import path
path.append(str(workspace))

from ..utils.paths import make_dir_function

local_dir = make_dir_function(workspace=workspace)

def make_dict():
    KMZ_NAME = 'weather_stations'

    # Define custom function for pathing.
    
    path_dict = {
        'kmz_url': 'https://smn.conagua.gob.mx/tools/RESOURCES/estacion/EstacionesClimatologicas.kmz',
        'kmz_path': local_dir('tmp', f'{KMZ_NAME}.kmz'),
        'kml_path': local_dir('data', 'raw', f'{KMZ_NAME}.kml'),
        'unzip_path': local_dir('tmp', 'unzipped'),
        'df_stations_path': local_dir('data','processed', 'df_stations.ftr'),
        'url_base': lambda number: f'https://smn.conagua.gob.mx/tools/RESOURCES/Diarios/{number}.txt',
        'download_dir_base': lambda state, municipality :\
            local_dir('data','raw', state, municipality),
        'interim_dir_base': lambda state, municipality : \
            local_dir('data','interim', state, municipality),
        'processed_stations_base': lambda state, municipality :\
            local_dir('data','processed', state, municipality)
        ,
        'df_region_medians_dir_base': \
            lambda \
                *args : \
            local_dir(
                'data', 
                'processed',
                name_convention('medians', *args), 
            )
        ,
        'df_interval_dir_base': \
            lambda \
                *args: \
            local_dir(
                'data',
                'processed',
                name_convention('interval', *args),
            )
    }
    return path_dict

def name_convention(*args):
    res = 'df_'
    for arg in args:
        if arg and arg is not None:
            arg_ = arg.replace(' ', '_')
            arg_ = arg_.replace('-', '_')    
            res += f'{arg_}-'

    return  res[:-1] +'.ftr'



def _run():
    p_dict = make_dict()
    print(p_dict['df_interval_dir_base']('durango','M','1991'))

if __name__ == '__main__':
    _run()