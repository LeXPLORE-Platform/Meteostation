# -*- coding: utf-8 -*-
import os
import sys
import yaml
import json
import time
import argparse
import requests
from instruments import Meteostation
from general.functions import logger
from functions import retrieve_new_files, merge_files

def main(server=False, logs=False):
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if logs:
        log = logger(os.path.join(repo, "logs/meteostation"))
    else:
        log = logger()
    log.initialise("Processing LéXPLORE meteostation data")
    directories = {f: os.path.join(repo, "data", f) for f in ["Level0", "Level1", "failed"]}
    for directory in directories:
        if not os.path.exists(directories[directory]):
            os.makedirs(directories[directory])
    edited_files = []

    log.begin_stage("Collecting inputs")
    if server:
        log.info("Processing files from sftp server")
        if not os.path.exists(os.path.join(repo, "creds.json")):
            raise ValueError("Credential file required to retrieve live data from the fstp server.")
        with open(os.path.join(repo, "creds.json"), 'r') as f:
            creds = json.load(f)
        new_files = retrieve_new_files(directories["failed"], creds, server_location="data/WeatherStation", filetype=".dat", remove=False, overwrite=True)
        files = merge_files(directories["Level0"], new_files)
        edited_files = edited_files + files
    else:
        files = os.listdir(directories["Level0"])
        files = [os.path.join(directories["Level0"], f) for f in files]
        files.sort()
        log.info("Reprocessing complete dataset from {}".format(directories["Level0"]))
    log.end_stage()

    log.begin_stage("Processing data to L1")
    for file in files:
        if ".dat" in file:
            sensor = Meteostation(log=log)
            if sensor.read_data(file):
                sensor.quality_assurance(file_path="notes/quality_assurance.json")
                edited_files.extend(sensor.export(directories["Level1"], "L1_Meteostation", output_period="weekly"))
    log.end_stage()

    return edited_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', help="Collect and process new files from FTP server", action='store_true')
    parser.add_argument('--logs', '-l', help="Write logs to file", action='store_true')
    args = vars(parser.parse_args())
    main(server=args["server"], logs=args["logs"])