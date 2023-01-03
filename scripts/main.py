# -*- coding: utf-8 -*-
import os
import sys
import yaml
from instruments import Meteostation
from general.functions import logger, files_in_directory

log = logger("scripts/logs/meteostation")
log.initialise("Processing LéXPLORE meteostation data")

log.begin_stage("Collecting inputs")
with open("scripts/input_python.yaml", "r") as f:
    directories = yaml.load(f, Loader=yaml.FullLoader)

for directory in directories.values():
    if not os.path.exists(directory):
        os.makedirs(directory)

if len(sys.argv) == 1:
    live = False
    files = os.listdir(directories["Level0"])
    files = [os.path.join(directories["Level0"], f) for f in files]
    files.sort()

    log.info("Reprocessing complete dataset from {}".format(directories["Level0"]))
elif len(sys.argv) == 2:
    live = True
    files = [str(sys.argv[1]).replace('\\', '/')]
    log("Live processing file {}".format(files[0]))
log.end_stage()

log.begin_stage("Processing data to L1")
for file in files:
    if ".dat" in file:
        sensor = Meteostation(log=log)
        if live:
            file = pre_process(file, directories["Level0"], directories["Process"])
        if sensor.read_data(file):
            if live:
                post_process(file, directories["Level0"])
            sensor.quality_assurance(file_path="notes/quality_assurance.json")
            sensor.export(directories["Level1"], "L1_Meteostation", output_period="weekly")
log.end_stage()
