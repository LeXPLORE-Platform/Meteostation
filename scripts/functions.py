# -*- coding: utf-8 -*-
import os
import copy
import json
import ftplib
import netCDF4
import numpy as np
import pandas as pd
from shutil import move
from scipy.interpolate import griddata
from datetime import datetime, timedelta
from math import sin, cos, sqrt, atan2, radians
from dateutil.relativedelta import relativedelta
from envass import qualityassurance
from general.functions import logger


def retrieve_new_files(folder, creds, server_location="data", filetype=".csv", remove=False, overwrite=False, log=logger()):
    files = []
    log.info("Connecting to {}.".format(creds["ftp"]), indent=1)
    ftp = ftplib.FTP(creds["ftp"], timeout=100)
    ftp.login(creds["user"], creds["password"])
    server_files = ftp.nlst(server_location)
    local_files = os.listdir(folder)
    for file in server_files:
        file_name = os.path.basename(file)
        if file.endswith(filetype) and (overwrite or file_name not in local_files):
            log.info("Downloading file {}".format(file), indent=2)
            download_file(file, os.path.join(folder, file_name), ftp)
            if remove:
                ftp.delete(file)
            files.append(os.path.join(folder, file_name))
    files.sort()
    return files


def download_file(server, local, ftp):
    with open(local, "wb") as f:
        ftp.retrbinary("RETR " + server, f.write)


def merge_files(output_folder, new_files):
    files = []
    for file in new_files:
        try:
            file_name = os.path.basename(file)
            day_name = file_name[:29] + file_name[29:39].replace("_", "-") + ".dat"
            day_file = os.path.join(output_folder, day_name)
            if os.path.isfile(day_file):
                df1 = pd.read_csv(day_file, header=None)
                df2 = pd.read_csv(file, header=None)
                df = pd.concat([df1, df2], ignore_index=True)
                df = df.drop_duplicates(subset=df.columns[0], keep='last')
                df = df.sort_values(by=df.columns[0])
                df.to_csv(day_file, index=False, header=False)
                os.remove(file)
            else:
                os.rename(file, day_file)
            if day_file not in files:
                files.append(day_file)
        except:
            print("Failed to merge: {}".format(file))
    files.sort()
    return files


def interp_nan_grid(time, depth, temp, method='linear'):
    temp_qual = np.ma.masked_invalid(temp).mask
    time_index = np.arange(0, len(time), 1)
    depth_index = np.arange(0, len(depth), 1)

    time_grid, depth_grid = np.meshgrid(time_index, depth_index)

    tempval = temp[~temp_qual]
    timeval = time_grid[~temp_qual]
    depthval = depth_grid[~temp_qual]

    temp_interp = griddata((timeval, depthval), tempval, (time_grid, depth_grid), method=method)
    return temp_interp


def interp_rescale(time, depth, time_grid, depth_grid, temp, method='linear'):
    time_index = np.arange(0, len(time), 1)
    time_mesh, depth_mesh = np.meshgrid(time_index, depth)
    time_grid_index = np.arange(0, len(time_grid), 1)
    time_mesh_grid, depth_mesh_grid = np.meshgrid(time_grid_index, depth_grid)

    temp_rescaled = griddata((time_mesh.ravel(), depth_mesh.ravel()), temp.ravel(), (time_mesh_grid, depth_mesh_grid),
                             method=method)
    return temp_rescaled


def find_closest_index(arr, value):
    return min(range(len(arr)), key=lambda i: abs(arr[i] - value))


def is_number(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True


def isnt_number(n):
    try:
        float(n)
    except ValueError:
        return True
    else:
        return False
