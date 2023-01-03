# Project Data

This folder contains all the data for the project.

**There are a number of example datasets included in this folder. Please replace them with your data.**

### Data Structure

- **Level 0**: Raw data collected from the different sensors.

- **Level 1**: Raw data stored to NetCDF file where attributes (such as sensors used, units, description of data, etc.) are added to the data. 
Quality assurance is performed on the data and QA masks are generated.

- **Level 2**: Processed data, this could include calculated parameters, transformed units, resampled or gridded data.
