# Country profiles

I created a country profile sheet for each country with WGMS glacier data. The aim was to provide an update from the previous [publication](https://doi.org/10.1659/mrd-journal-d-19-00021.1) of national glacier states which used the country sheets made in 2015. This includes showing how the number of monitored glaciers has changed for front variation, mass balance and thickness change; change in area coverage of measurements, change in the average length of records. 
Future work is required to complete the written evaluation which will assess whether the "Future potential/needs" described in 2015 have been met or not. 

## Data

The data used to generate the country profiles comes from the [2024 version](https://doi.org/10.5904/wgms-fog-2024-01) of the WGMS database. 
The data from the [2015 version](https://doi.org/10.5904/wgms-fog-2015-11) of the database is also used in order to compare between the two generations of country profiles. Download the following files (if not already in *data* folder) and if needed rename them as written here in the list:

### Data from 2015 database version
- *WGMS-FoG-2015-11-A-GENERAL-INFORMATION.csv*
- *WGMS-FoG-2015-11-D-CHANGE.csv*
- *WGMS-FoG-2015-11-E-MASS-BALANCE-OVERVIEW.csv*
- *WGMS-FoG-2015-11-RR-RECONSTRUCTION-FRONT-VARIATION.csv*

### Data from 2024 database version
- *change.csv*
- *front_variation.csv*
- *glacier.csv*
- *mass_balance_overview.csv*
- *mass_balance.csv*
- *reconstruction_front_variation.csv*

### Data from other sources already uploaded to *data* folder
- *country_codes.csv*
- *fog-2015-11-front_variation.csv* (This is the version of the FV table used to generate the 2015 country profiles)

### Geospatial data
- *country.gpkg* (Country outlines to get national glacier area)
- *glims_point.gpkg* (accessed through the QGIS integration of the database)
- *rgi7.gpkg* ([source](https://nsidc.org/data/nsidc-0770/versions/7))

### Other data
- *fog_glacier_area.csv*
- *wgi.csv* ([source](https://nsidc.org/data/glacier_inventory/))

## Scripts

The scripts needed are:
- *key_stats.py*
- *glacier_area.py*
- *mass_balance.py*
- *no_of_plots.py*
- *jinja_template.py*

The Python script *jinja_template.py* uses Jinja to output the plots, variables and any other parameter onto the HTML template.

The HTML template is:
- *template_country.html*

## Instructions

1. Make sure you have created the environment from wgms.yml (file found in this repository), if not install all packages that are used in the scripts for this project.
2. Download all required data files and name them as in the lists above. Place the files under the /data/ folder in this subfolder of the repository
3. Open the *key_stats.py* script in the preferred IDE application
5. Set the working directory to the CountryProfiles folder in this repository
6. Load the required data files directly from the data subfolder in this repository (where you placed all the downloaded files in previous steps under Data section)
7. Run *key_stats.py*
8. Repeat Steps 3-7 for *glacier_area.py*, *mass_balance.py* and *no_of_plots.py*
9. Open the *jinja_template.py*
10. Make sure that you have the *template_country.html* file in the working directory folder 
11. Make sure that the /text/ subfolder exists and contains the *country_profiles_text.csv* file which should be used to fill out all the written elements which are unique for each country (this part of writing the text is yet to be completed)
12. Run the *output_from_template* function cell
13. Subsequent cell can be run to output all country profiles
14. Last cell can be run to output a single country profile by choosing a country code as the input

## Contact
Giulio Saibene - saibene.giulio@gmail.com - [Linkedin](www.linkedin.com/in/giulio-saibene-b3a858261)
