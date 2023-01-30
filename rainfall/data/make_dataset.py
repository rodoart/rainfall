# Load custom library

from datetime import date
from pathlib import Path
from xmlrpc.client import Boolean
from ..utils.make_paths_dict import make_dict
from ..utils.paths import is_valid


# Define custom function for pathing.
paths_dict = make_dict()

import pandas as pd
import numpy as np
import regex as re

from datetime import date
from typing import List, Literal, Tuple
from numpy import unique
from shutil import rmtree
from os import makedirs
from ..utils.web import asyncronous_download_from_urls

class StationsDataFrame(pd.DataFrame):
    """A subclass of DataFrame with the data of the climatic stations of the Mexican Republic, obtained from:
    
    <https://smn.conagua.gob.mx/tools/RESOURCES/estacion/EstacionesClimatologicas.kmz> 

    
    Attributes:

        path: Location where the feather version of the dataframe with the 
            station data is located (or will be found).


    Methods:

        station(number=int): Generates a Station object with the dataframe
            of each station, that contains the climate data collected at that 
            station. 

        region_median(state=str, municipality=str): Generates a RegionMedian
            object with a data frame that contains the temporal median of all stations of selected region.  
    """

    _kmz_url = paths_dict['kmz_url']
    _kmz_path =  paths_dict['kmz_path'] 
    _kml_path = paths_dict['kml_path']  
    path =  paths_dict['df_stations_path']

    def __init__(
        self, 
        re_download: bool = False
    ): 
             
        # Verify if the data frame is already created:
        if not self.path.is_file() or re_download:
            # Verify if the kml file exists.
            if not self._kml_path.is_file() or re_download:
                # Verify if kmz file exits.
                if not self._kmz_path.is_file() or re_download:
                    _download_kmz(self._kmz_url, self._kmz_path)
                _kmz_to_kml(self._kmz_path, self._kml_path)
        
            kml_file = open(self._kml_path, "r", encoding='utf-8')
            lines = kml_file.readlines() 

            # Regular expression to extract description tag.
            r_stations = '^\s*<description><!\[CDATA\[<h3>' +\
                        "(.*) - ([A-Z]{8,10})</h3><font color='red'><p><b>Estado : </b>"+ \
                        '(.*)</p><p><b>Municipio : </b>' +\
                        '(.*)</p><p><b>Organismo : </b>' +\
                        '(.*)</p><p><b>Cuenca : </b>'+\
                        '(.*)</p><p><a href=https://smn.conagua.gob.mx/tools/RESOURCES/Diarios/'+\
                        '(.*).txt>Climatología diaria</a></p>.*</a></p>\]\]></description>$'

            rs = re.compile(r_stations) 

            # Regular expression to extract coordinates tag.
            r_coordinates = '^\s*<coordinates>(.*),(.*),(.*)</coordinates>$'
            rc = re.compile(r_coordinates) 

            # Search with both regular expresions line by line:

            rows = []
            for k, line in enumerate(lines):
                if rs.match(line):
                    rows.append(rs.search(line).groups() 
                                + rc.search(lines[k+3]).groups())


            # Creating the data frame.
            cols = ['name', 'status', 'state', 'municipality', 'organization', 'basin', 
                    'number', 'longitude', 'latitude', 'altitude']
        
        
            df_stations = pd.DataFrame(rows, columns=cols)

            # Change names and types
            df_stations = df_stations.astype({
                'number':'int64','status':'category', 'longitude':'float64', 
                'latitude':'float64', 'altitude':'float64'
                })
        
            df_stations['status'] = df_stations['status']\
                .cat\
                .rename_categories({'OPERANDO':'working', 'SUSPENDIDA':'stopped'})
        

            # Change index
            df_stations = df_stations.set_index('number')
            df_stations.sort_index()

            # Export the data frame.
            df_stations.reset_index().to_feather(self.path)

        # Load file.
        df_stations = pd.read_feather(self.path)
        df_stations = df_stations.set_index('number')
    
        super().__init__(df_stations)


    def _download_url_base(self, number:int):
        return paths_dict['url_base'](number)


    def _numbers_by_region(
        self,
        state: str,
        municipality: str = ""
    ) -> list:

        # Query string
        new_query = f"state == '{state.upper()}'"
        if municipality:
            new_query += f" and municipality == '{municipality.upper()}'"
        
        # Doing the query. 
        return  self.query(new_query).index.to_list()

    def _download_files_by_numbers(
        self,
        number_list: List[int],
        re_download: bool = False
    ):
        assert len(number_list) > 0,  (
            f"The list of stations is empty, verify that you are making a query with valid names of states and/or municipalities within the Mexican Republic."
        ) 

        download_dirs = [
            self.station(number, define_empty=True).raw_path.parent for number in number_list
        ]

        # Remove dirs
        if re_download:
            for dir in unique(download_dirs):
                if dir.is_dir():
                    rmtree(dir)

        # Verify if dirs exists:
        dirs_already_exist = []
        for dir in unique(download_dirs):
            if dir.is_dir():
                dirs_already_exist.append(dir)
            else:
                makedirs(dir, exist_ok=True)

        # Removing already downloaded files from list.        
        if re_download == False:
            to_pop = []
            for k, download_dir in enumerate(download_dirs):
                for already_downloaded_dir in dirs_already_exist:
                    if download_dir == already_downloaded_dir:
                        to_pop.append(k)
            
            number_list = [
                number_list[k] for k in range(len(number_list)) if k not in to_pop
            ]
            download_dirs = [
                download_dirs[k] for k in range(len(download_dirs)) 
                if k not in to_pop
            ]
        
        # Url List
        urls = [self._download_url_base(number) for number in number_list]

        #  Download files: 
        asyncronous_download_from_urls(urls, download_dirs, encoding='cp1252')

    def Station(
        self, 
        number:int, 
        define_empty:bool=False
    ):
        """Create a Station object, downloading and sorting the data from <https://smn.conagua.gob.mx/tools/RESOURCES/Diarios/{number}.txt>.


        Attributes:

            number(int): Is the station number, corresponding to the StationsDataFrame object.

            state(str): Is the state where the station is located.

            municipality(str): The municipality where the station is located.

            raw_path(Path): This is the location of the raw data on the hard drive, used to create the object. (If the file does not exist, it will be downloaded)

            df(pandas,DataFrame): Here the information of each station is stored. Contains the columns 
                - `rainfall`: total daily rain in mm
                - `evaporation`: total daily evaporation in mm.
                - `min_t`: minimal temperature in °C.
                - `max_t` maximal temperature in °C.

        Methods:

        """
        return station(self, number, define_empty)


    def DailyMedians(self, state, municipality=''):
        """Calculates the median of the day of each column with the data from all the stations in the given `state` and `municipality`.
        
        Attributes:
            
            path(Path): The path where the dataframe generated by this object is stored. If the file already exists, it just loads it.

            state(str): Is the state where the station is located.

            municipality(str): The municipality where the station is located.

            df(pandas.DataFrame):  Here the data is stored. Columns:
                - `rainfall`: total daily rain in mm
                - `evaporation`: total daily evaporation in mm.
                - `min_t`: minimal temperature in °C.
                - `max_t` maximal temperature in °C.

        Methods:
            
            add_is_rainy_col: Generates a column of boolean values in the df. True when it is a rainy day and False when it is not.

            add_month_number_col: Generates a column with the month number.

            add_day_of_year: Genarates a column with the day of the year (1-366).

            interpolate: Fills empty one-day gaps with linear interpolation.

            time_interval_trim: Generates a new DataFrame only with values between a time interval.

            PeriodicMedians: Generates an new object with weekly or monthly median values.
        """
        return daily_medians(self, state, municipality)

def station(outer_self, number:int, define_empty=False):
    class Station():
        def __init__(self, number:int, define_empty = False):
            """            
            Parameters:
            
                number(int): It's the station number. You can look up this number on the object StationsDataFrame.
                define_empty(bool)
            """
            # Region:
            assert len(outer_self.index == number)!=0, "The station doesn't exists."                 
            
            self.number = number
            self.state = str(outer_self['state'][
                outer_self.index == number
            ].to_list()[0].lower())
            
            self.municipality = str(outer_self['municipality'][
                outer_self.index == number
            ].to_list()[0].lower())              
            
            # Raw path:
            def _raw_dir_base(state:str, municipality:str):    
                return paths_dict['download_dir_base'](
                    state, municipality
                ) 
            
            def _interim_dir_base(state:str, municipality:str):    
                return paths_dict['interim_dir_base'](
                    state, municipality
                ) 
            
            state = self.state.replace(" ", "_")
            municipality = self.municipality.replace(" ", "_")        

            self.raw_path = _raw_dir_base(state, municipality)\
                .joinpath(f"{number}.txt")
            self.interim_path = _interim_dir_base(state, municipality)\
                .joinpath(f"{number}.txt")

            if define_empty == False:
                # Download files if requiered.        
                if not self.raw_path.is_file():
                    stations_in_same_region = \
                        outer_self._numbers_by_region(
                            self.state, self.municipality
                        )
                    outer_self._download_files_by_numbers(
                        stations_in_same_region
                    )

                
                pattern = \
                    "([\d]{2,2}/[\d]{2,2}/[\d]{4,4})\s+"\
                    + "([\d.Nulo]+)\s+"\
                    + "([\d.Nulo]+)\s+"\
                    + "([\d.Nulo]+)\s+"\
                    + "([\d.Nulo]+)\s+"
                r_pattern = re.compile(pattern) 
    
                rows = []
                with open(self.raw_path, 'r') as raw_file:
                    for line in raw_file:
                        if r_pattern.match(line):
                            rows.append(r_pattern.search(line).groups())
                    
                
                df_station = pd.DataFrame(
                    rows, 
                    columns=['date', 'rainfall','evaporation','max_t',
                                'min_t'],
                    )
                
                # Date as index.
                df_station['date'] = pd.to_datetime(df_station['date'],
                                                    format='%d/%m/%Y')
                df_station = df_station.set_index('date')
                
                # Change al data frame to float.
                df_station = df_station.replace('Nulo', np.nan)
                df_station = df_station.astype(float)

            else:
                df_station = pd.DataFrame()
                
            self.df =  df_station

    return Station(number, define_empty)

# Functions for interior classes:

def daily_medians(outer_self, state, municipality=''):
    class DailyMedians():
        def __init__(self, state, municipality):
            self.state = state
            self.municipality = municipality

            # Path:
            def _path_base(state:str, municipality:str):    
                return paths_dict['df_region_medians_dir_base'](
                    state, municipality
                ) 
            
            state_ = self.state.replace(" ", "_")
            municipality_ = self.municipality.replace(" ", "_")        

            self.path = _path_base(state_, municipality_)

            if not self.path.is_file():

                
                # Find all stations in same region.
                stations_in_region = \
                    outer_self._numbers_by_region(
                        self.state, self.municipality
                    )

                df_all = None 
                
                # Join al stations in the region
                for number in stations_in_region:
                    df_station = outer_self.Station(number).df

                    if df_all is None: 
                        df_all = df_station.copy(deep=True)
                    else:
                        df_all = pd.concat([df_all, df_station], axis=0)                

                # Calculate median.
                df_all = df_all.groupby('date').median().reset_index()
                
                # Set index  
                df_all = df_all.set_index('date')

                # Remove empty values by interpolation.
                df_all = df_all.interpolate(method='time')

                # Export
                df_all.reset_index().to_feather(self.path)

            else:
                df_all = pd.read_feather(self.path)
                df_all = df_all.set_index('date')

            self.df = df_all
        
        def add_is_rainy_col(self):
            '''Generates in-place `is_rainy` column with boolean values in the df. True when it is a rainy day and False when it is not.            
            '''
            # Empty col.
            self.df['is_rainy'] = False
            # True values
            self.df.loc[self.df['rainfall'] >= 2.5, 'is_rainy'] = True

        def add_month_number_col(self):
            '''Generates in-place `month` with month numbers.          
            '''
            self.df['month'] = self.df.index.month.tolist()
        
        def add_day_of_year_col(self):
            '''Generates in-place `day_of_year` with the number of the day of the year (1-366).          
            '''

            self.df['day_of_year'] = self.df.index.dayofyear

        def interpolate(self):
            self.df = self.df.interpolate(method='time')

        def time_interval_trim(self, date_interval:Tuple[date,date]):
            
            if date_interval[0]:                 
                mask = (self.df.index>=str(date_interval[0]))
            else:
                mask = (self.df.index == self.df.index)

            if date_interval[1]:
                mask &= (self.df.index<=str(date_interval[1]))

            return self.df[mask]
            

        def PeriodicMedians(
            self, 
            frequency: Literal["W", "M"], 
            date_interval: Tuple[date,date] = None
        ): 

            return interval_medians(self, frequency, date_interval)
    
    return DailyMedians(state, municipality)



from datetime import timedelta
def interval_medians(outer_self, 
    frequency: Literal["W", "M"], 
    date_interval: Tuple[date,date] = None
):

    class PeriodicMedians():
        def __init__(
            self, 
            frequency: Literal["W", "M"], 
            date_interval: Tuple[date,date] = None
        ) -> None:
            path_base = paths_dict['df_interval_dir_base']

            self.frequency = frequency
            self.date_interval = date_interval
        
            self.path = path_base(outer_self.state, 
                                outer_self.municipality, frequency,
                                str(self.date_interval[0]), 
                                str(self.date_interval[1]))

            if not self.path.is_file():
                outer_self.interpolate()

                outer_self.add_is_rainy_col()
                
                if self.frequency == 'W': # Weekly
                    outer_self.add_day_of_year_col()
                    key = 'day_of_year'
                else: # 'Monthly
                    outer_self.add_month_number_col()
                    key = 'month'

                if self.date_interval:
                    df_trimmed = outer_self.time_interval_trim(self.date_interval)
                else:
                    df_trimmed = outer_self.df.copy()
                
                data_dict = {}
                
                for col in df_trimmed.columns:
                    if col == 'is_rainy': # Sum of total rainfall in the 
                                        # interval
                        data_dict[col] = df_trimmed[col]\
                            .groupby(pd.PeriodIndex(
                                df_trimmed[col].index,freq=self.frequency))\
                            .sum()
                    else: # median for every else.
                        data_dict[col] =df_trimmed[col]\
                            .groupby(pd.PeriodIndex(
                                df_trimmed[col].index,freq=self.frequency))\
                            .median()

                # Creation of data frame.
                df_interval = pd.DataFrame(data_dict)

                # Types.
                df_interval[key] = df_interval[key].astype(int)
                df_interval.index = df_interval.index.to_timestamp()

                # Change one column name.
                names = df_interval.columns.tolist()
                names[names.index('is_rainy')] = 'rainy_days'
                df_interval.columns = names

                df_interval.reset_index().to_feather(self.path)

            else:
                df_interval = pd.read_feather(self.path)
                df_interval = df_interval.set_index('date')

            self.df = df_interval

        def _gaps(self):
            deltas = self.df.index.to_series().diff()[1:]
            gaps = deltas[deltas > timedelta(days=31)]

            gaps = gaps.index.to_list()
            gaps.insert(0,self.df.index.to_list()[0])
            gaps.append(self.df.index.to_list()[-1])

            return gaps

       

        def skip_with_gaps(self, independent_vars=['rainfall', 'rainy_days'], n=1):
            df_skipped = None
            gaps = self._gaps()
            for k in range(len(gaps)-1):

                mask = (self.df.index >= gaps[k]) & (self.df.index < gaps[k+1])

                df_interval = self.df[mask]
                df_interval = skip(df_interval, independent_vars, n)

                if df_skipped is None:
                    df_skipped = df_interval.copy()
                else:
                    df_skipped = pd.concat([df_skipped, df_interval], axis=0)

            return df_skipped


                
    return PeriodicMedians(frequency, date_interval)
                  
      



# Download kmz file.
import requests
def _download_kmz(
    kmz_url = paths_dict['kmz_url'],
    kmz_path =  paths_dict['kmz_path']
) -> None:
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.3'}
    
    response = requests.get(kmz_url, verify=False, headers=headers )
    
    response.raise_for_status()
    open(kmz_path, "wb").write(response.content)    
    print(f'{kmz_url} has been downloaded.')


from zipfile import ZipFile
from shutil import copy, rmtree

def _kmz_to_kml(
    kmz_path = paths_dict['kmz_path'],
    kml_path = paths_dict['kml_path']
) -> None:

    unzip_path = paths_dict['unzip_path']
    # Unzip 
    with ZipFile(kmz_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    
    # Copy only the kml file.
    kml_origin = unzip_path.joinpath('doc.kml')
    copy(kml_origin, kml_path)

    # Delete irrelevant files.
    rmtree(unzip_path)

    print('The kmz file has been converted to kml')



def skip(df, independent_vars=['rainfall', 'rainy_days'], n=1):
    """
    function to skip one column on the dataframe
    """
        # Copy independent columns.
    for column in independent_vars:
       df.insert(0, f'{column}_copy',df[column].copy(), True)

    # Finding  dependant variables.
    columns = df.columns.to_list()
    dependet_vars = [column for column in columns if column not in independent_vars]

    # Skiping dependant vars.
    df_x = df[dependet_vars].iloc[:-n]
    df_x.index =df[dependet_vars].index[n:]  

    # Skiping independent vars.
    df_y = df[independent_vars].iloc[n:]
    
    return pd.concat([df_x, df_y], axis=1)


def run():
   state = 'distrito federal'
   municipality = ''

   sdf  = StationsDataFrame()

   rm = sdf.DailyMedians(state, municipality)



   date_interval = (date(1970,1,1), '')

   pm_montly = rm.PeriodicMedians('M', date_interval)

   print(pm_montly.skip_with_gaps())

if __name__=='__main__':
    run()
