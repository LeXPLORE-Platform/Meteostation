# Project Data

The data for this project is stored remotely in the object store: https://eawag-data.s3.eu-central-1.amazonaws.com

In order to work with the data you need to sync the remote data folder with this "local" data folder.
You can use the script `scripts/download_remote_data.py` as follows to download the data:

```console
python scripts/download_remote_data.py -d
```

Run `python scripts/download_remote_data.py -h` for details on optional arguments.



### Data Structure

The data is structured as follows:

- **Level 0**: Raw data collected from the different sensors.
- **Level 1**: Data is converted to NetCDF and quality assurance is applied. Quality flag "1" indicates that the data point didn't pass the 
quality checks and further investigation is needed, quality flag "0" indicates that the data has passed the quality assurance check. Do not forget to apply the quality check mask when analysing the data.
