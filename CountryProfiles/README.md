# Country profiles

I created a country profile sheet for each country with WGMS glacier data. The aim was to provide an update from the previous [publication](https://doi.org/10.1659/mrd-journal-d-19-00021.1) of national glacier states which used the country sheets made in 2015. This includes showing how the number of monitored glaciers has changed for front variation, mass balance and thickness change. 
Future work is required to complete the written evaluation which will assess whether the "Future potential/needs" described in 2015 have been met or not. 

## Data

The data used to generate the country profiles comes from the [2024 version](https://doi.org/10.5904/wgms-fog-2024-01) of the WGMS database. 
The data from the [2015 version](https://doi.org/10.5904/wgms-fog-2015-11) of the database is also used in order to compare between the two generations of country profiles. If the following files are not already in the *data* folder then download:
- *country_codes.csv*
- *glacier_info_2015.csv*
- 

## Scripts

The scripts needed are:
- *jinja_template.py*
- *key_stats.py*
- *mass_balance.py*
- *no_of_plots.py*
- *glacier_area.py*

The Python script *jinja_template.py* uses Jinja to output the plots, variables and any other parameter onto the HTML template.

The HTML template is:
- *template_country.html*

## Contact
Giulio Saibene - saibene.giulio@gmail.com - [Linkedin](www.linkedin.com/in/giulio-saibene-b3a858261)
