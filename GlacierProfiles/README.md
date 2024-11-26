# Glacier Profiles

I created individual glacier profiles describing the current state and historical changes for glaciers with available mass balance data, complete names, and a photo. The aim is to display these on the monitor outisde of the WGMS office at UZH. An index page is also created to provide an overview of all the available glaciers with profile sheets with the option of clicking on the desired glacier to arrive at its profile sheet. From each profile sheet it's possible to navigate to the previous and next glacier profile (alphabetically ordered by country) or to go back to the index page.

## Data

The data used to generate the country profiles comes from the [2024 version](https://doi.org/10.5904/wgms-fog-2024-01) of the WGMS database. Additional data such as glacier names, countries and investigators is downloaded directly from the DBGate access of the WGMS database. The WGMS outlines are downloaded through the PostgreSQL GIS access of the database. 

### Data needed from WGMS database zip file
- glacier

### Data to download from DBGate tables as CSV files
- glacier
- glacier_name
- glacier_photo
- glacier_country
- mass_balance
- front_variation
- team_member

### Data to download from GIS access to database
- wgms_outlines

## Scripts

The script used to generate the glacier profiles is:
- *glacier_profiles.py*

The Python script uses Jinja to output the plots, variables and any other parameter onto the HTML template.

The HTML template used is:
- *template_glacier.html*
- *index.html*

## Environment
Refer to wgms.yml file in GlacierProfiles folder of this repository for environment details including versions of Python and packages.

## Instructions
1. Install all packages that are used in *glacier_profiles.py*
2. Check data file paths and then import all needed data

## Contact
Giulio Saibene - saibene.giulio@gmail.com - [Linkedin](www.linkedin.com/in/giulio-saibene-b3a858261)
