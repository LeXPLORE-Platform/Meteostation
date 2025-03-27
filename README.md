# LéXPLORE Meteostation


## Project Information / Abstract

[LéXPLORE](https://lexplore.info) is research platform on Lake Geneva for a broad range of limnological research. The platform results from a collaboration between five partner institutions ([Eawag](https://www.eawag.ch/en/), [EPFL](https://www.epfl.ch/en/), [INRAE](https://www6.lyon-grenoble.inrae.fr/carrtel/), [UNIGE](https://unige.ch), [UNIL](https://www.unil.ch/index.html)). The LéXPLORE platform is anchored since February 2019 at a position reaching 110 m depth off the lake's north-shore.
The data presented here is part of the core dataset maintained by the technical team of LéXPLORE.
The data is used and displayed on the [Datalakes website](https://www.datalakes-eawag.ch/). related data or products can be visualised and downloaded on the [Datalakes website](https://www.datalakes-eawag.ch/).


### References

Wüest, A., Bouffard, D., Guillard, J., Ibelings, B. W., Lavanchy, S., Perga, M. ‐E., & Pasche, N. (2021). LéXPLORE: a floating laboratory on Lake Geneva offering unique lake research opportunities. Wiley Interdisciplinary Reviews: Water, 8(5), e1544 (15 pp.). https://doi.org/10.1002/wat2.1544

See also the [360° virtual tour](https://www.eawag.ch/repository/lexplore/index.htm)

### Citation
Bouffard, D., Ballu, A., Cunillera, G., Fillion, R., Gios, M., Guillard, J., Ibelings, B., Lavanchy, S., Miesen, F., Pasche, N., Perga, M-E., Plüss, M., Quetin, P., Runnalls, J., Wüest, A. (2022). Data and products from LéXPLORE Meteorological station, 2019 - 2022. DOI

DOI attribution pending.


### Time Frame
- Begin date: 29-07-2019
- End data: continuous data set - live

### Geographic coverage
Lake Geneva [46.50, 6.66]


## Sensors

The meteostation is a weather station collecting a wide range of meteorological data. Every 10 minutes it measures wind speed, wind direction, amount of rainfall, air pressure, temperature and solar irradiance. The meteorological mast is located above the LéXPLORE platform at 5 m height from the platform (46°30’0.819″ N, 6°39’39.007″ E) 

### Air temperature
- **Brand, Model & SN**: Rotronics, HC2S3-L, SN 0020073077
- **System integration**: Campbell Scientific CR1000X SN 25713
- **Accuracy**: ±0.1 °C @ 23°C
- **Setup** height above lake: 5 m, sampling period: 10 min

### Relative humidity
- **Brand, Model & SN**: Rotronics, HC2S3-L, SN 0020073077
- **System integration**: Campbell Scientific CR1000X SN 25713
- **Accuracy**: ±0.8% RH @ 23°C 
- **Setup** height above lake: 5 m, sampling period: 10 min

### Wind speed & direction
- **Brand, Model & SN**: RM Young, 05103, SN WM150350
- **System integration**: Campbell Scientific CR1000X SN 25713
- **Accuracy**: Wind speed: ± 0.3 m/s (0.6 mph) or 1% of reading, Wind direction: ± 3°
- **Setup** height above lake: 5 m, sampling period: 10 min

### Barometric pressure
- **Brand, Model & SN**: Sestra, CS100-278, SN 
- **System integration**: Campbell Scientific CR1000X SN 25713
- **Accuracy**: ±0.5 hPa (@ +20°C), ±1.0 hPa (@ 0° to 40°C) 
- **Setup** height above lake: 5 m, sampling period: 10 min

### Rainfall
- **Brand, Model & SN**: EML, ARG100, SN 164110, or EML, ARG314, SN 222319(see `sensor_history`)
- **System integration**: Campbell Scientific CR1000X SN 25713
- **Accuracy**: +/- 3% up to 120mm/hr 
- **Setup** height above lake: 5 m, sampling period: 10 min

### Solar radiation
- **Brand, Model & SN**: Apogee, SP-110, SN 54369
- **System integration**: Campbell Scientific CR1000X SN 25713
- **Accuracy**: ±5% for daily total radiation
- **Setup** height above lake: 5 m, sampling period: 10 min


## Code

[![License: MIT][mit-by-shield]][mit-by]

**You need to have [git](https://git-scm.com/downloads) installed in order to successfully clone the repository.**

- Clone the repository to your local machine using the command: 

 `git clone https://renkulab.io/gitlab/lexplore/meteostation.git`
 
 Note that the repository will be copied to your current working directory.

- Use Python 3 and install the requirements with:

 `pip install -r requirements.txt`

 The python version can be checked by running the command `python --version`. In case python is not installed or only an older version of it, it is recommend to install python through the anaconda distribution which can be downloaded [here](https://www.anaconda.com/products/individual). 

## Usage

### Credentials

In order to download live data `creds_example.json` should be renamed to `creds.json` and completed.

### Operation

To run the pipeline: `python scripts/main.py`

The python script `scripts/main.py` defines the different processing steps while the python script `scripts/meteostation.py` contains the python class meteostation with all the corresponding class methods to process the data. To add a new processing or visualization step, a new class method can be created in the `meteostation.py` file and the step can be added in `main.py` file. Both above mentioned python scripts are independent of the local file system.

### Arguments

Run `scripts/main.py -h` for details on the input arguments available

## Data

### Access

Data for this repository is stored in a remote object store. In order to work with the data you need 
to run `scripts/download_remote_data.py`, this will syncronise the local `data` folder with the remote 
data folder on the server. 

### License

[![CC BY 4.0][cc-by-shield]][cc-by] 

This data is released under the Creative Commons license - Attribution - CC BY (https://creativecommons.org/licenses/by/4.0/). This license states that consumers ("Data Users" herein) may distribute, adapt, reuse, remix, and build upon this work, as long as they give appropriate credit, provide a link to the license, and indicate if changes were made.
 
The Data User has an ethical obligation to cite the data source (see the DOI number) in any publication or product that results from its use. Communication, collaboration, or co-authorship (as appropriate) with the creators of this data package is encouraged. 
 
Extensive efforts are made to ensure that online data are accurate and up to date, but the authors will not take responsibility for any errors that may exist in data provided online. Furthermore, the Data User assumes all responsibility for errors in analysis or judgment resulting from use of the data. The Data User is urged to contact the authors of the data if any questions about methodology or results occur. 



### Data Structure

The data can be found in the folder `data`. The data is structured as follows:

- **Level 0**: Raw data collected from the different sensors.
- **Level 1**: Data is converted to NetCDF and quality assurance is applied. Quality flag "1" indicates that the data point didn't pass the 
quality checks and further investigation is needed, quality flag "0" indicates that the data has passed the quality assurance check. Do not forget to apply the quality check mask when analysing the data.

## Quality assurance

Quality checks include but are not limited to range validation, data type checking and flagging missing data.
The automatic quality check is controlled by the package [Envass](https://pypi.org/project/envass/). The specific methods implemented for this dataset are listed in `notes/quality_assurance.json`. 

###  Events 

Maintenance dates, interesting or surprising events, non identified by the quality assurance outliers are listed in the folder `notes/events.csv`.
Check also the `notes/sensor_history.csv` (if existing)

## Collaborators

- **Concept, finances, project management** Damien Bouffard, Jean Guillard, Bas Ibelings, Natacha Pasche, Marie-Elodie Perga, Alfred Wüest   
- **Installation, maintenance, data collection** Aurélien Ballu, Guillaume Cunillera, Roxane Fillion, Matteo Gios, Sébastien Lavanchy, Floreana Miesen, Michael Plüss, Philippe Quetin 
- **Data pipeline** James Runnalls
- **Data review** Damien Bouffard
- **Contact tech** Sébastien Lavanchy, sebastien.lavanchy@epfl.ch 
- **Contact science** Damien Bouffard. damien.bouffard@eawag.ch

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-g.svg?label=Data%20License
[mit-by]: https://opensource.org/licenses/MIT
[mit-by-shield]: https://img.shields.io/badge/License-MIT-g.svg?label=Code%20License
