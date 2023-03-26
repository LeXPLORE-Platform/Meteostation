# -*- coding: utf-8 -*-
import os
import math
import netCDF4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from general.functions import GenericInstrument


class Meteostation(GenericInstrument):
    def __init__(self, *args, **kwargs):
        super(Meteostation, self).__init__(*args, **kwargs)
        self.general_attributes = {
            "institution": "EPFL",
            "source": "Lexplore Weather station Campbell CR1000",
            "references": "LéXPLORE commun instruments sebastien.lavanchy@epfl.ch",
            "history": "See history on Renku",
            "conventions": "CF 1.7",
            "comment": "Data from the Meteostation on Lexplore Platform in Lake Geneva",
            "title": "Lexplore Meteostation"
        }
        self.dimensions = {
            'time': {'dim_name': 'time', 'dim_size': None}
        }
        self.variables = {
            'time': {'var_name': 'time', 'dim': ('time',), 'unit': 'seconds since 1970-01-01 00:00:00',
                     'long_name': 'time'},
            'Batt': {'var_name': 'Batt', 'dim': ('time',), 'unit': 'V', 'long_name': 'battery_level'},
            'Ptemp': {'var_name': 'Ptemp', 'dim': ('time',), 'unit': 'degC', 'long_name': 'panel_temperature'},
            'AirTC': {'var_name': 'AirTC', 'dim': ('time',), 'unit': 'degC', 'long_name': 'air_temperature'},
            'RH': {'var_name': 'RH', 'dim': ('time',), 'unit': '%', 'long_name': 'relative_humidity'},
            'Slrw': {'var_name': 'Slrw', 'dim': ('time',), 'unit': 'W m-2', 'long_name': 'solar_irradiance'},
            'Slrm': {'var_name': 'Slrm', 'dim': ('time',), 'unit': 'MJ m-2', 'long_name': 'total_solar_irradiance'},
            'WS': {'var_name': 'WS', 'dim': ('time',), 'unit': 'm s-1', 'long_name': 'wind_speed'},
            'WindDir': {'var_name': 'WindDir', 'dim': ('time',), 'unit': 'deg', 'long_name': 'wind_direction'},
            'Rain': {'var_name': 'Rain', 'dim': ('time',), 'unit': 'mm', 'long_name': 'precipitation_depth'},
            'BP': {'var_name': 'BP', 'dim': ('time',), 'unit': 'mbar', 'long_name': 'barometric_pressure'},
            'WindGust': {'var_name': 'WindGust', 'dim': ('time',), 'unit': 'm/s', 'long_name': 'wind_gust'},
        }

    def read_data(self, file):
        self.log.info("Reading data from {}".format(file), 1)
        try:
            df = pd.read_csv(file, header=None)
            if len(df.columns) == 12:
                df.columns = ["time", "Record", "Batt", "Ptemp", "AirTC", "RH", "Slrw", "Slrm", "WS", "WindDir", "Rain",
                              "BP"]
                df["WindGust"] = np.nan
            else:
                df.columns = ["time", "Record", "Batt", "Ptemp", "AirTC", "RH", "Slrw", "Slrm", "WS", "WindDir", "Rain",
                              "BP", "WindGust"]
            df["time"] = df["time"].apply(
                lambda x: datetime.timestamp(datetime.strptime(x, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)))
            df.sort_values(by=['time'])
            for variable in self.variables:
                self.data[variable] = np.array(df[variable])
        except Exception as e:
            self.log.info("Failed to read data from {}".format(file), indent=1)
            raise e
        return True
