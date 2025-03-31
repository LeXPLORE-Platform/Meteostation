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
from download_remote_data import download_remote_data
from upload_remote_data import upload_files

def main(reprocess=False, initialize=False, download=False, upload=False, datalakes=False, logs=False):
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if logs:
        log = logger(os.path.join(repo, "logs/meteostation"))
    else:
        log = logger()
    log.initialise("Processing LéXPLORE meteostation data")
    directories = {f: os.path.join(repo, "data", f) for f in ["Level0", "Level1", "failed"]}
    edited_files = []
    log.begin_stage("Downloading data")
    if download:
        log.info("Download sync with remote bucket")
        download_remote_data(warning=False, delete=True)
    elif initialize:
        if not os.path.exists(directories["Level0"]):
            log.info("No local data syncing with remote bucket")
            download_remote_data(warning=False, delete=True)
            for directory in directories:
                if not os.path.exists(directories[directory]):
                    os.makedirs(directories[directory])
    log.end_stage()

    log.begin_stage("Collecting inputs")
    if reprocess:
        files = os.listdir(directories["Level0"])
        files = [os.path.join(directories["Level0"], f) for f in files]
        files.sort()
        log.info("Reprocessing complete dataset from {}".format(directories["Level0"]))
    else:
        log.info("Processing files from sftp server")
        if not os.path.exists(os.path.join(repo, "creds.json")):
            raise ValueError("Credential file required to retrieve live data from the fstp server.")
        with open(os.path.join(repo, "creds.json"), 'r') as f:
            creds = json.load(f)
        new_files = retrieve_new_files(directories["failed"], creds, server_location="data/WeatherStation", filetype=".dat", remove=upload, overwrite=True)
        files = merge_files(directories["Level0"], new_files)
        edited_files = edited_files + files
    log.end_stage()

    log.begin_stage("Processing data to L1")
    for file in files:
        if ".dat" in file:
            sensor = Meteostation(log=log)
            if sensor.read_data(file):
                sensor.quality_assurance(file_path="notes/quality_assurance.json")
                edited_files.extend(sensor.export(directories["Level1"], "L1_Meteostation", output_period="weekly"))
    log.end_stage()

    log.begin_stage("Data handling")
    if reprocess and upload:
        log.info("Upload sync with remote bucket")
        upload_remote_data(warning=False, delete=True)
    elif upload:
        log.info("Uploading edited files to remote bucket")
        upload_files(edited_files)

    if datalakes:
        log.info("Calling Datalakes API")
        for index, datalakes_id in enumerate(datalakes):
            requests.get("https://api.datalakes-eawag.ch/update/{}".format(datalakes_id))
            if index != len(datalakes) - 1:
                time.sleep(30)
    log.end_stage()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--reprocess', '-r', help="Reprocess complete dataset", action='store_true')
    parser.add_argument('--initialize', '-i', help="Try to download data from remote bucket if no Level0 folder", action='store_true')
    parser.add_argument('--logs', '-l', help="Write logs to file", action='store_true')
    parser.add_argument('--download', '-d', help="Download sync with remote bucket", action='store_true')
    parser.add_argument('--upload', '-u', help="Upload sync with remote bucket", action='store_true')
    parser.add_argument('--datalakes', '-dl', type=lambda s: list(map(int, s.split(','))) if s else False, nargs="?", const=False, default=False, help="Datalakes ID's to update, or False if not provided.")
    args = vars(parser.parse_args())
    main(reprocess=args["reprocess"], initialize=args["initialize"], download=args["download"], upload=args["upload"], datalakes=args["datalakes"], logs=args["logs"])