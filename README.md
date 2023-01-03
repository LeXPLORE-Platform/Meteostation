# Project Name
Project Description

<span style="color:red">UPDATE THIS README WITH INFORMATION APPROPRIATE TO YOUR PROJECT!</span>

## Project Information

***
Include here a description of the project, this could include:
- Research objective
- Location
- Funding
- References
- Image of setup
***

## Citation

*** 
Include here a citation for the data such that other can use your data and cite it appropriately. 
***

## Sensors

***
Include here a description of the sensors used in your project.

This could look like the following:

The meteostation is a weather station collecting a wide range of meteorological data. Every 10 minutes it measures wind speed, wind direction, amount of rainfall, air pressure, temperature and solar irradiance. The meteorological mast is located above the LéXPLORE platform at 5 m height from the platform (46°30’0.819″ N, 6°39’39.007″ E) 

### Air temperature
- **Brand, Model & SN**: Rotronics, HC2S3-L, SN 0020073077
- **System integration**: Campbell Scientific CR1000X
- **Accuracy**: +/- 0.01degC
- **Setup**: Height above lake: 5 m, sampling period: 10 min

### Relative humidity
- **Brand, Model & SN**: Rotronics, HC2S3-L, SN 0020073077
- **System integration**: Campbell Scientific CR1000X
- **Accuracy**: +/- 0.01%
- **Setup**: Height above lake: 5 m, sampling period: 10 min

***

## Installation

**You need to have [git](https://git-scm.com/downloads) and [git-lfs](https://git-lfs.github.com/) installed in order to successfully clone the repository.**

- Clone the repository to your local machine using the command:

<span style="color:red">REPLACE WITH LINK TO YOUR REPOSITORY</span>

 `git clone --depth 1 https://renkulab.io/gitlab/lexplore/meteostation.git`
 
 Note that the repository will be copied to your current working directory.

- Use Python 3 and install the requirements with:

 `pip install -r requirements.txt`

 The python version can be checked by running the command `python --version`. In case python is not installed or only an older version of it, it is recommend to install python through the anaconda distribution which can be downloaded [here](https://www.anaconda.com/products/individual). 

## Code

[![License: MIT][mit-by-shield]][mit-by]

### Processing Data

***
Describe here how someone (maybe you in the future) could use the pipeline to process new data in the future.

This could look like:

1. Copy raw data to the `data/Level0` folder.
2. Edit `scripts/input_python.yaml` to identify directories on local machine.
3. Use requirements.txt to build a python virtual environment and activate it.
4. Run `scripts/main.py` to process all data in the `data/Level0` folder.
***

### Adapting Code

***
Provide a description on another user could edit your code to add functionality or apply it to an additional use case.
***
## Data

[![CC BY 4.0][cc-by-shield]][cc-by]

***
This data is released under the Creative Commons license - Attribution - CC BY (https://creativecommons.org/licenses/by/4.0/). This license states that consumers ("Data Users" herein) may distribute, adapt, reuse, remix, and build upon this work, as long as they give appropriate credit, provide a link to the license, and indicate if changes were made.
 
The Data User has an ethical obligation to cite the data source (see the DOI number) in any publication or product that results from its use. Communication, collaboration, or co-authorship (as appropriate) with the creators of this data package is encouraged. 
 
Extensive efforts are made to ensure that online data are accurate and up to date, but the authors will not take responsibility for any errors that may exist in data provided online. Furthermore, the Data User assumes all responsibility for errors in analysis or judgment resulting from use of the data. The Data User is urged to contact the authors of the data if any questions about methodology or results occur. 
***

The data can be found in the folder `data`. The data is structured as follows:

### Data Structure

- **Level 0**: Raw data collected from the different sensors.

- **Level 1**: Raw data stored to NetCDF file where attributes (such as sensors used, units, description of data, etc.) are added to the data. 
Quality assurance is performed on the data and QA masks are generated.

- **Level 2**: Processed data, this could include calculated parameters, transformed units, resampled or gridded data.

## Quality assurance

Quality checks include but are not limited to range validation, data type checking and flagging missing data.


###  Events 

Maintenance dates, interesting or surprising events, non identified by the quality assurance outliers are listed in the folder `notes`.

## Collaborators

***
List project collaborators
***

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-g.svg?label=Data%20License
[mit-by]: https://opensource.org/licenses/MIT
[mit-by-shield]: https://img.shields.io/badge/License-MIT-g.svg?label=Code%20License
