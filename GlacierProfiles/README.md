# Glacier Profiles

I created individual glacier profiles describing the current state and historical changes for glaciers with available mass balance data, complete names, and a photo. The aim is to display these on the monitor outisde of the WGMS office at UZH. An index page is also created to provide an overview of all the available glaciers with profile sheets with the option of clicking on the desired glacier to arrive at its profile sheet. From each profile sheet it's possible to navigate to the previous and next glacier profile (alphabetically ordered by country) or to go back to the index page.

## Data

The data used to generate the country profiles comes from the [2024 version](https://doi.org/10.5904/wgms-fog-2024-01) of the WGMS database. Additional data such as glacier names, countries and investigators is downloaded directly from the DBGate access of the WGMS database. The WGMS outlines are downloaded through the PostgreSQL GIS access of the database. The *country_codes.csv* file is already provided in the data folder for this project. Please download each file and name it as named in the following lists.

### Data needed from WGMS database zip file
- glacier.csv
- state.csv

### Data to download from DBGate tables as CSV files
- glacier.csv
- glacier_name.csv
- glacier_photo.csv
- glacier_country.csv
- mass_balance.csv
- front_variation.csv
- team_member.csv
- glacier_outline_all.csv

### Data to download from GIS access to database
- wgms_outlines.shp

## Scripts

The script used to generate the glacier profiles is:
- *glacier_profiles.py*

The Python script uses Jinja to output the plots, variables and any other parameter onto the HTML template.

Make sure to have the following templates in the The HTML templates used are:
- *template_glacier.html*
- *template_index.html*

## Instructions
1. Install all packages that are used in *glacier_profiles.py*
2. Download all required data files and name them as in the lists above. Place the files under the /data/ folder in this subfolder of the repository
3. Open the *glacier_profiles.py* script in the preferred IDE application
4. Set the working directory to the GlacierProfiles folder in this repository
5. Load the required data files directly from the data subfolder in this repository (where you placed all the downloaded files in previous steps under *Data* section)
6. The first cells are to run the functions used to build the visuals and extract statistics for a given glacier
7. Before the rendering jinja template cells I find the list of glacier IDs which have the required data (photo, complete name and MB data) which is then used to output all these glacier profiles
8. The cell *Render a glacier profile* function takes a single glacier ID as input and outputs a single glacier profile for testing (no index page)
9. The cell *Render both a glacier profile and the index home page* creates glacier profiles for a given list of glacier IDs and outputs the *glacier_index_data* which then acts as an input to the *generate_glacier_index* function to create the index.html home page

## Contact
Giulio Saibene - saibene.giulio@gmail.com - [Linkedin](www.linkedin.com/in/giulio-saibene-b3a858261)
