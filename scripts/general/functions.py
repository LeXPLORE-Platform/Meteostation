# -*- coding: utf-8 -*-
import os
import pytz
import copy
import json
import netCDF4
import traceback
import numpy as np
import pandas as pd
from envass import qualityassurance
from math import sin, cos, sqrt, atan2, radians
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt


class GenericInstrument:
    def __init__(self, log=False):
        self.general_attributes = {
            "institution": "",
            "source": "",
            "references": "",
            "history": "",
            "conventions": "CF 1.7",
            "comment": "",
            "title": ""
        }
        self.dimensions = {}
        self.variables = {}
        self.data = {}
        self.grid = {}
        if log != False:
            self.log = log
        else:
            self.log = logger()

    def quality_assurance(self, file_path='./quality_assurance.json', valid=False, time_label="time"):
        self.log.info("Applying quality assurance", indent=2)

        if not os.path.exists(file_path):
            self.log.warning("Cannot find QA file: {}, no QA applied.".format(file_path), indent=2)
            return False
        try:
            quality_assurance_dict = json_converter(json.load(open(file_path)))
            for key, values in self.variables.copy().items():
                if "_qual" not in key and key in quality_assurance_dict:
                    name = key + "_qual"
                    self.variables[name] = {'var_name': name, 'dim': values["dim"],
                                            'unit': '0 = nothing to report, 1 = more investigation',
                                            'long_name': name, }
                    if len(self.data[key]) == 1:
                        self.data[name] = [1]
                    else:
                        qa = qualityassurance(np.array(self.data[key]), np.array(self.data[time_label]),
                                              **quality_assurance_dict[key]["simple"])
                        if valid:
                            time = np.array(self.data[time_label])
                            if min(time) < valid[0] < max(time) and min(time) < valid[1] < max(time):
                                qa[time < valid[0]] = 1
                                qa[time > valid[1]] = 1
                        self.data[name] = qa
        except:
            self.log.error("Unable to apply QA file, this is likely due to bad formatting of the file.")

    def apply_events(self, events_file, time_label="time"):
        self.log.info("Applying events from {}".format(events_file), indent=2)
        if not os.path.exists(events_file):
            self.log.warning("Cannot find events file: {}, no events applied.".format(events_file), indent=2)
            return False
        events = parse_events(events_file, self.log)
        if events is None:
            return False

        time = np.array(self.data[time_label], dtype=float)
        events = events[(events["start"] <= np.nanmax(time)) & (events["stop"] >= np.nanmin(time))]
        for _, event in events.iterrows():
            variables = event_variables(event["parameter"], self.data.keys(), time_label=time_label)
            for parameter in variables["unknown"]:
                self.log.warning("Unknown parameter {} in events line {}".format(parameter, event["line"]), indent=3)
            mask = (time >= event["start"]) & (time <= event["stop"])
            for var in variables["qual"]:
                qual = np.array(self.data[var])
                qual[mask] = 1
                self.data[var] = qual
            self.log.info("{} ({}): flagged {} points for {}".format(
                event["comments"], event["parameter"], int(mask.sum()), ", ".join(variables["qual"])), indent=3)
        return True

    def mask_outside_water_and_upcast_ctd(self, rolling=3, diff=0.01, var="Cond", depth="Press", max_depth_cut=3.0):
        self.log.info("Masking data from outside water and the upcast.", 2)
        bottom_of_profile_index = np.argmax(np.array(self.data[depth]))
        df = pd.DataFrame(np.array(self.data[var]))
        df_mean = df.rolling(rolling, center=True).mean().fillna(method='bfill').fillna(method='ffill')
        df_diff = df_mean.diff()
        outliers = np.array(np.abs(df_diff) > diff).flatten()
        water_entry_index = np.where(outliers[:np.argmax(np.array(self.data[depth]) > max_depth_cut)])[0][-1]

        for key, values in self.variables.copy().items():
            if "_qual" in key and "time" not in key and "Press" not in key:
                self.data[key][bottom_of_profile_index:] = 1
                self.data[key][:water_entry_index] = 1

    def export(self, folder, title, output_period="file", time_label="time", profile_to_grid=False, overwrite=False):
        if profile_to_grid:
            variables = self.grid_variables
            dimensions = self.grid_dimensions
            data = self.grid
        else:
            variables = self.variables
            dimensions = self.dimensions
            data = self.data

        time = data[time_label]
        time_min = datetime.utcfromtimestamp(np.nanmin(time)).replace(tzinfo=pytz.utc)
        time_max = datetime.utcfromtimestamp(np.nanmax(time)).replace(tzinfo=pytz.utc)
        if output_period == "file":
            file_start = time_min
            file_period = time_max - time_min
        elif output_period == "daily":
            file_start = (time_min - timedelta(days=time_min.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            file_period = timedelta(days=1)
        elif output_period == "weekly":
            file_start = (time_min - timedelta(days=time_min.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            file_period = timedelta(weeks=1)
        elif output_period == "monthly":
            file_start = time_min.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            file_period = relativedelta(months=+1)
        elif output_period == "yearly":
            file_start = time_min.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            file_period = relativedelta(year=+1)
        else:
            self.log.warning('Output period "{}" not recognised.'.format(output_period), indent=2)
            return

        if not os.path.exists(folder):
            os.makedirs(folder)

        output_files = []
        while file_start < time_max:
            file_end = file_start + file_period
            filename = "{}_{}.nc".format(title, file_start.strftime('%Y%m%d_%H%M%S'))
            out_file = os.path.join(folder, filename)
            output_files.append(out_file)
            self.log.info(
                "Writing {} data from {} until {} to NetCDF file {}".format(title, file_start, file_end, filename),
                indent=2)

            valid_time = (time >= datetime.timestamp(file_start)) & (time < datetime.timestamp(file_end))

            if not os.path.isfile(out_file):
                self.log.info("Creating new file.", indent=3)
                with netCDF4.Dataset(out_file, mode='w', format='NETCDF4') as nc:
                    for key in self.general_attributes:
                        setattr(nc, key, self.general_attributes[key])
                    for key, values in dimensions.items():
                        nc.createDimension(values['dim_name'], values['dim_size'])
                    for key, values in variables.items():
                        var = nc.createVariable(values["var_name"], np.float64, values["dim"], fill_value=np.nan)
                        var.units = values["unit"]
                        var.long_name = values["long_name"]
                        if profile_to_grid and key == time_label:
                            var[0] = time[0]
                        elif profile_to_grid and len(values["dim"]) == 2:
                            if values["dim"][0] == time_label:
                                var[0, :] = data[key]
                            elif values["dim"][1] == time_label:
                                var[:, 0] = data[key]
                            else:
                                raise ValueError("Failed to write variable {} with dimensions: {} to file".format(key, ", ".join(values["dim"])))
                        else:
                            if len(values["dim"]) == 1:
                                if values["dim"][0] == time_label:
                                    var[:] = data[key][valid_time]
                                else:
                                    var[:] = data[key]
                            elif len(values["dim"]) == 2:
                                if values["dim"][0] == time_label:
                                    var[:] = data[key][valid_time, :]
                                elif values["dim"][1] == time_label:
                                    var[:] = data[key][:, valid_time]
                            else:
                                raise ValueError("Failed to write variable {} with dimensions: {} to file".format(key, ", ".join(values["dim"])))
            else:
                self.log.info("Editing existing file.", indent=3)
                with netCDF4.Dataset(out_file, mode='a', format='NETCDF4') as nc:
                    nc_time = np.array(nc.variables[time_label][:])
                    if profile_to_grid:
                        if time[0] in nc_time:
                            if overwrite:
                                self.log.info("Overwriting data at {}.".format(time[0]), indent=3)
                                idx = np.where(nc_time == time[0])[0][0]
                                for key, values in variables.items():
                                    if key not in dimensions:
                                        if len(values["dim"]) == 1:
                                            if hasattr(data[key], "__len__"):
                                                nc.variables[key][idx] = data[key][0]
                                            else:
                                                nc.variables[key][idx] = data[key]
                                        elif len(values["dim"]) == 2 and values["dim"][1] == time_label:
                                            nc.variables[key][:, idx] = data[key]
                                        else:
                                            self.log.warning("Unable to write {} with {} dimensions.".format(key, len(
                                                values["dim"])))

                            else:
                                self.log.info("Grid data already exists in NetCDF, skipping.", indent=3)
                        else:
                            idx = position_in_array(nc_time, time[0])
                            nc.variables[time_label][:] = np.insert(nc_time, idx, time[0])
                            for key, values in variables.items():
                                if key not in dimensions:
                                    var = nc.variables[key]
                                    if len(values["dim"]) == 1:
                                        if hasattr(data[key], "__len__"):
                                            var[idx] = data[key][0]
                                        else:
                                            var[idx] = data[key]
                                    elif len(values["dim"]) == 2 and values["dim"][1] == time_label:
                                        end = len(var[:][0]) - 1
                                        if idx != end:
                                            var[:, end] = data[key]
                                            var[:] = var[:, np.insert(np.arange(end), idx, end)]
                                        else:
                                            var[:, idx] = data[key]
                                    else:
                                        self.log.warning(
                                            "Unable to write {} with {} dimensions.".format(key, len(values["dim"])))
                    else:
                        if np.all(np.isin(time, nc_time)) and not overwrite:
                            self.log.info("Data already exists in NetCDF, skipping.", indent=3)
                        else:
                            non_duplicates = ~np.isin(time, nc_time)
                            valid = np.logical_and(valid_time, non_duplicates)
                            combined_time = np.append(nc_time, time[valid])
                            order = np.argsort(combined_time)
                            nc_copy = copy_variables(nc.variables)
                            for key, values in self.variables.items():
                                if time_label in values["dim"]:
                                    if len(values["dim"]) == 1:
                                        combined = np.append(nc_copy[key][:], np.array(data[key])[valid])
                                        if overwrite:
                                            combined[np.isin(combined_time, time)] = np.array(data[key])[
                                                np.isin(time, combined_time)]
                                        out = combined[order]
                                    elif len(values["dim"]) == 2 and values["dim"][1] == time_label:
                                        combined = np.concatenate((np.array(nc_copy[key][:]), np.array(data[key])[:, valid]), axis=1)
                                        if overwrite:
                                            combined[:, np.isin(combined_time, time)] = np.array(data[key])[:, np.isin(time, combined_time)]
                                        out = combined[:, order]
                                    else:
                                        raise ValueError(
                                            "Failed to write variable {} with dimensions: {} to file"
                                            .format(key, ", ".join(values["dim"])))
                                    nc.variables[key][:] = out
            file_start = file_start + file_period
        return output_files

    def mask_data(self):
        self.log.info("Masking L1 data.", indent=2)
        for var in self.variables:
            if var + "_qual" in self.data:
                idx = self.data[var + "_qual"][:] > 0
                self.data[var][idx] = np.nan

    def profile_to_timeseries_grid(self, time_label="time", depth_label="depth"):
        self.log.info("Resampling profile to fixed grid...", indent=2)
        try:
            self.grid[depth_label] = self.depths
        except:
            raise ValueError("self.depths must be defined as an fixed array of depths to produce timeseries grid.")
        self.grid[time_label] = np.array([self.data[time_label][0]])
        for key, values in self.grid_variables.items():
            if key not in self.grid_dimensions:
                if len(values["dim"]) == 1:
                    if "depth" in values and "source" in values:
                        mask = (~np.isnan(self.data[values["source"]])) & (~np.isnan(self.data[depth_label]))
                        pressures = self.data[depth_label][mask]
                        data = self.data[values["source"]][mask]
                        self.grid[key] = np.interp([float(values["depth"])], pressures, data, left=np.nan, right=np.nan)
                    else:
                        self.log.warning(
                            '"depth" and "source" keys must be included in self.variables["{}"].'.format(key), indent=2)
                elif len(values["dim"]) == 2:
                    mask = (~np.isnan(self.data[key])) & (~np.isnan(self.data[depth_label]))
                    pressures = self.data[depth_label][mask]
                    data = self.data[key][mask]
                    if len(data) < 5:
                        self.grid[key] = np.asarray([np.nan] * len(self.depths))
                    else:
                        self.grid[key] = np.interp(self.depths, pressures, data, left=np.nan, right=np.nan)
                else:
                    self.log.warning(
                        "Unable to process data for {} with {} dimensions.".format(key, len(values["dim"])), indent=2)

    def read_netcdf_data(self, file):
        with netCDF4.Dataset(file, 'r') as nc:
            for key in nc.variables.keys():
                self.data[key] = np.array(nc.variables[key][:])


class logger(object):
    def __init__(self, path=False, time=True):
        if path != False:
            if os.path.exists(os.path.dirname(path)):
                path.split(".")[0]
                if time:
                    self.path = "{}_{}.log".format(path.split(".")[0], datetime.now().strftime("%H%M%S.%f"))
                else:
                    self.path = "{}.log".format(path.split(".")[0])
            else:
                print("\033[93mUnable to find log folder: {}. Logs will be printed but not saved.\033[0m".format(
                    os.path.dirname(path)))
                self.path = False
        else:
            self.path = False
        self.stage = 1

    def info(self, string, indent=0):
        out = datetime.now().strftime("%H:%M:%S.%f") + (" " * 3 * (indent + 1)) + string
        print(out)
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")

    def initialise(self, string):
        out = "****** " + string + " ******"
        print('\033[1m' + out + '\033[0m')
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")

    def begin_stage(self, string):
        self.newline()
        out = datetime.now().strftime("%H:%M:%S.%f") + "   Stage {}: ".format(self.stage) + string
        self.stage = self.stage + 1
        print('\033[95m' + out + '\033[0m')
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")
        return self.stage - 1

    def end_stage(self):
        out = datetime.now().strftime("%H:%M:%S.%f") + "   Stage {}: Completed.".format(self.stage - 1)
        print('\033[92m' + out + '\033[0m')
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")

    def warning(self, string, indent=0):
        out = datetime.now().strftime("%H:%M:%S.%f") + (" " * 3 * (indent + 1)) + "WARNING: " + string
        print('\033[93m' + out + '\033[0m')
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")

    def error(self):
        out = datetime.now().strftime("%H:%M:%S.%f") + "   ERROR: Script failed on stage {}".format(self.stage - 1)
        print('\033[91m' + out + '\033[0m')
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")
                file.write("\n")
                traceback.print_exc(file=file)

    def end(self, string):
        out = "****** " + string + " ******"
        print('\033[92m' + out + '\033[0m')
        if self.path:
            with open(self.path, "a") as file:
                file.write(out + "\n")

    def subprocess(self, process, error=""):
        failed = False
        while True:
            output = process.stdout.readline()
            out = output.strip()
            print(out)
            if error != "" and error in out:
                failed = True
            if self.path:
                with open(self.path, "a") as file:
                    file.write(out + "\n")
            return_code = process.poll()
            if return_code is not None:
                for output in process.stdout.readlines():
                    out = output.strip()
                    print(out)
                    if self.path:
                        with open(self.path, "a") as file:
                            file.write(out + "\n")
                break
        return failed

    def newline(self):
        print("")
        if self.path:
            with open(self.path, "a") as file:
                file.write("\n")


def parse_events(events_file, log):
    """Read an events file (start;stop;parameter;depth;comments) and return start/stop as epoch seconds.
    An empty stop means the event is ongoing. Malformed rows are reported and skipped."""
    columns = ["start", "stop", "parameter", "depth", "comments"]
    df = pd.read_csv(events_file, sep=";", dtype=str, skipinitialspace=True, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in columns if c not in df.columns]
    if missing:
        log.warning("Events file {} missing columns: {}, no events applied.".format(events_file, ", ".join(missing)), indent=2)
        return None
    df = df.apply(lambda c: c.str.strip())
    df["line"] = df.index + 2
    start = pd.to_datetime(df["start"], format="%Y%m%d %H:%M:%S", utc=True, errors="coerce")
    stop = pd.to_datetime(df["stop"], format="%Y%m%d %H:%M:%S", utc=True, errors="coerce")
    stop[df["stop"] == ""] = pd.Timestamp.now(tz="UTC")
    valid = start.notna() & stop.notna() & (stop >= start) & (df["parameter"] != "")
    for line in df.loc[~valid, "line"]:
        log.warning("Invalid event on line {} of {}, skipped.".format(line, events_file), indent=3)
    df = df[valid].copy()
    df["start"] = start[valid].map(lambda t: t.timestamp())
    df["stop"] = stop[valid].map(lambda t: t.timestamp())
    return df


def event_variables(parameter, keys, time_label="time"):
    """Map an events parameter ("All" or comma separated variable names) to the matching _qual variables."""
    qual = [k for k in keys if k.endswith("_qual") and k != time_label + "_qual"]
    if parameter.strip().lower() == "all":
        return {"qual": qual, "unknown": []}
    names = [p.strip() for p in parameter.split(",") if p.strip()]
    return {"qual": [n + "_qual" for n in names if n + "_qual" in qual],
            "unknown": [n for n in names if n + "_qual" not in qual]}


def json_converter(qa):
    for keys in qa.keys():
        try:
            if qa[keys]["simple"]["bounds"][0] == "-inf":
                qa[keys]["simple"]["bounds"][0] = -np.inf
            if qa[keys]["simple"]["bounds"][1] == "inf":
                qa[keys]["simple"]["bounds"][1] = np.inf
        except:
            pass
    try:
        if qa["time"]["simple"]["bounds"][1] == "now":
            qa["time"]["simple"]["bounds"][1] = datetime.now().timestamp()
        return qa
    except:
        return qa


def geographic_distance(latlng1, latlng2):
    lat1 = radians(latlng1[0])
    lon1 = radians(latlng1[1])
    lat2 = radians(latlng2[0])
    lon2 = radians(latlng2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return 6373000.0 * c


def copy_variables(variables_dict):
    var_dict = dict()
    for var in variables_dict:
        var_dict[var] = variables_dict[var][:]
    nc_copy = copy.deepcopy(var_dict)
    return nc_copy


def position_in_array(arr, value):
    for i in range(len(arr)):
        if value < arr[i]:
            return i
    return len(arr)


def files_in_directory(root):
    f = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            f.append(os.path.join(path, name))
    return f


def latlng_to_ch1903(lat, lng):
    lat = lat * 3600
    lng = lng * 3600
    lat_aux = (lat - 169028.66) / 10000
    lng_aux = (lng - 26782.5) / 10000
    x = 2600072.37 + 211455.93 * lng_aux - 10938.51 * lng_aux * lat_aux - 0.36 * lng_aux * lat_aux ** 2 - 44.54 * lng_aux ** 3 - 2000000
    y = 1200147.07 + 308807.95 * lat_aux + 3745.25 * lng_aux ** 2 + 76.63 * lat_aux ** 2 - 194.56 * lng_aux ** 2 * lat_aux + 119.79 * lat_aux ** 3 - 1000000
    return x, y


def ch1903_to_latlng(x, y):
    x_aux = (x - 600000) / 1000000
    y_aux = (y - 200000) / 1000000
    lat = 16.9023892 + 3.238272 * y_aux - 0.270978 * x_aux ** 2 - 0.002528 * y_aux ** 2 - 0.0447 * x_aux ** 2 * y_aux - 0.014 * y_aux ** 3
    lng = 2.6779094 + 4.728982 * x_aux + 0.791484 * x_aux * y_aux + 0.1306 * x_aux * y_aux ** 2 - 0.0436 * x_aux ** 3
    lat = (lat * 100) / 36
    lng = (lng * 100) / 36
    return lat, lng


def latlng_to_ch1903plus(lat, lng):
    lat = lat * 3600
    lng = lng * 3600
    lat_aux = (lat - 169028.66) / 10000
    lng_aux = (lng - 26782.5) / 10000
    x = 2600072.37 + 211455.93 * lng_aux - 10938.51 * lng_aux * lat_aux - 0.36 * lng_aux * lat_aux ** 2 - 44.54 * lng_aux ** 3 - 2000000
    y = 1200147.07 + 308807.95 * lat_aux + 3745.25 * lng_aux ** 2 + 76.63 * lat_aux ** 2 - 194.56 * lng_aux ** 2 * lat_aux + 119.79 * lat_aux ** 3 - 1000000
    x = x + 2000000
    y = y + 1000000
    return x, y


def ch1903plus_to_latlng(x, y):
    x = x - 2000000
    y = y - 1000000
    x_aux = (x - 600000) / 1000000
    y_aux = (y - 200000) / 1000000
    lat = 16.9023892 + 3.238272 * y_aux - 0.270978 * x_aux ** 2 - 0.002528 * y_aux ** 2 - 0.0447 * x_aux ** 2 * y_aux - 0.014 * y_aux ** 3
    lng = 2.6779094 + 4.728982 * x_aux + 0.791484 * x_aux * y_aux + 0.1306 * x_aux * y_aux ** 2 - 0.0436 * x_aux ** 3
    lat = (lat * 100) / 36
    lng = (lng * 100) / 36
    return lat, lng


def first_centered_differences(x, y, fill=False):
    if x.size != y.size:
        raise ValueError("First-centered differences: vectors do not have the same size")
    dy = np.full(x.size, np.nan)
    iif = np.where((np.isfinite(x)) & (np.isfinite(y)))[0]
    if iif.size == 0:
        return dy
    x0 = x[iif]
    y0 = y[iif]
    dy0 = np.full(x0.size, np.nan)
    # calculates differences
    dy0[0] = (y0[1] - y0[0]) / (x0[1] - x0[0])
    dy0[-1] = (y0[-1] - y0[-2]) / (x0[-1] - x0[-2])
    dy0[1:-1] = (y0[2:] - y0[0:-2]) / (x0[2:] - x0[0:-2])

    dy[iif] = dy0

    if fill:
        dy[0:iif[0]] = dy[iif[0]]
        dy[iif[-1] + 1:] = dy[iif[-1]]
    return dy
