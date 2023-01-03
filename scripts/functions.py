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
from general_functions import logger


def pre_process(file, Level0_dir, process_dir):
    for row in open(file, "r"):
        filename_l = Level0_dir+"/"+"LeXPLORE_WS_Lexplore_Weather_"+row[1:11]+".dat"
        filename_p = process_dir+"/"+"LeXPLORE_WS_Lexplore_Weather_"+row[1:11]+".dat"
        if os.path.isfile(filename_l):
            os.rename(filename_l, filename_p)
        if os.path.isfile(filename_p):
            read = open(filename_p, "r")
            if row in read.readlines():
                read.close()
            else:
                read.close()
                append = open(filename_p, "a")
                append.write(row)
                append.close()
        else:
            new = open(filename_p, "w")
            new.write(row)
            new.close()
    os.remove(file)
    return filename_p


def post_process(file, Level0_dir):
    if os.path.isfile(file):
        move(file, Level0_dir)
    else:
        log("Error, file does not exist")


def retrieve_new_files(folder, creds, server_location="data", log=logger()):
    files = []
    log.info("Connecting to {}.".format(creds["ftp"]), indent=1)
    ftp = ftplib.FTP(creds["ftp"], creds["user"], creds["password"], timeout=100)
    server_files = [os.path.join(server_location, f) for f in ftp.nlst(server_location)]
    local_files = os.listdir(folder)
    for file in server_files:
        file_name = os.path.basename(file)
        if file_name not in local_files and file.split(".")[-1] == "csv":
            log.info("Downloading file {}".format(file), indent=2)
            download_file(os.path.join(file), os.path.join(folder, file_name), ftp)
            files.append(os.path.join(folder, file_name))
    files.sort()
    log.info("{} new files found on the server.".format(len(files)), indent=1)
    return files


def download_file(server, local, ftp):
    with open(local, "wb") as f:
        ftp.retrbinary("RETR " + server, f.write)


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
