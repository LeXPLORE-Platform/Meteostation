@echo off
setlocal enabledelayedexpansion

SET homedir="C:\Users\Seatronic 1147\Documents\Data_Lexplore\git\meteostation"
SET pythonenv="C:\Users\Seatronic 1147\Documents\Data_Lexplore\git\venv39\Scripts\python"
SET script="C:\Users\Seatronic 1147\Documents\Data_Lexplore\git\meteostation\scripts\main.py"
SET in="C:\Users\Seatronic 1147\Documents\Data_Lexplore\WeatherStation"
SET backup="C:\Users\Seatronic 1147\Documents\Data_Lexplore\WeatherStationBackup"
SET upload="C:\Users\Seatronic 1147\Documents\Data_Lexplore\git\meteostation\scripts\upload_remote_data.py"

:: Ensure correct location
cd %homedir%

:: Backup files
md %backup%
robocopy %in% %backup% /NFL /NDL /NJH /NJS /nc /ns /np

:: Process meteostation data
for %%a in (%in%"\*.dat") do (
	%pythonenv% %script% "%%a"
)

:: Upload new data
%pythonenv% %upload% -w

:: Send notification to Datalakes API
curl https://api.datalakes-eawag.ch/update/459
