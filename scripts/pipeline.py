# -*- coding: utf-8 -*-
import os
import sys
import yaml
import json
import time
import argparse
import requests
from download_remote_data import download_remote_data
from upload_remote_data import upload_files
from main import main

def pipeline(reprocess=False, initialize=False, download=False, upload=False, datalakes=False, logs=False):
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    directories = {f: os.path.join(repo, "data", f) for f in ["Level0", "Level1", "failed"]}
    if download:
        print("Download sync with remote bucket")
        download_remote_data(warning=False, delete=True)
    elif initialize:
        if not os.path.exists(directories["Level0"]):
            print("No local data syncing with remote bucket")
            download_remote_data(warning=False, delete=True)
            for directory in directories:
                if not os.path.exists(directories[directory]):
                    os.makedirs(directories[directory])

    edited_files = main(~reprocess, logs)

    if reprocess and upload:
        print("Upload sync with remote bucket")
        upload_remote_data(warning=False, delete=True)
    elif upload:
        print("Uploading edited files to remote bucket")
        upload_files(edited_files)

    if datalakes:
        for index, datalakes_id in enumerate(datalakes):
            requests.get("https://api.datalakes-eawag.ch/update/{}".format(datalakes_id))
            time.sleep(30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--reprocess', '-r', help="Reprocess complete dataset", action='store_true')
    parser.add_argument('--initialize', '-i', help="Try to download data from remote bucket if no Level0 folder", action='store_true')
    parser.add_argument('--logs', '-l', help="Write logs to file", action='store_true')
    parser.add_argument('--download', '-d', help="Download sync with remote bucket", action='store_true')
    parser.add_argument('--upload', '-u', help="Upload sync with remote bucket", action='store_true')
    parser.add_argument('--datalakes', '-dl', type=lambda s: list(map(int, s.split(','))) if s else False, nargs="?", const=False, default=False, help="Datalakes ID's to update, or False if not provided.")
    args = vars(parser.parse_args())
    pipeline(reprocess=args["reprocess"], initialize=args["initialize"], download=args["download"], upload=args["upload"], datalakes=args["datalakes"], logs=args["logs"])