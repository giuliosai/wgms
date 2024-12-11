#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 11:54:42 2023

@author: giuliosaibene
"""

# =============================================================================
# COUNTRY PROFILES WGMS 2023
#
# Writing results of each country profile based on the html Jinja template (template.html)
# onto the output.html file.
#
# Make sure there is a folder in main working directory called "Text" and with
# the country_profiles_text.csv file in it.
# =============================================================================

import jinja2
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
from key_stats import *
from mass_balance import *
from no_of_plots import *
from glacier_area import *

# Enable matplotlib interactive mode to prevent plots from blocking the script
plt.ion()

#%%

def output_from_template(country_code, text_path):

    # Read text from file in Text folder in main working directory

    text_data = pd.read_csv(text_path)

    # take only text for given country

    country_text = text_data[text_data['country'] == country_code]

    # convert to dictionary
    country_text = country_text.set_index('key')['value'].to_dict()

    # Get country full name

    country_name = country_names.get(country_code)

    # PLOTS

    # FV combined bar and grid plot

    plot_bar_grid_fv(fronts_df, fv_reco_df, fronts_df_2015v_merge, fv_reco_df_2015v, country_code)

    # Save the plot to a BytesIO object
    buffer_obs_fv_bar_grid = BytesIO()
    plt.savefig(buffer_obs_fv_bar_grid, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_obs_fv_bar_grid.seek(0)
    plot_obs_fv_bar_grid = base64.b64encode(buffer_obs_fv_bar_grid.getvalue()).decode()

    plt.close()


    # MB combined bar and grid plot

    plot_bar_grid_mb(mb_df_overview, mb_df_overview_2015v, country_code)

    # Save the plot to a BytesIO object
    buffer_obs_mb_bar_grid = BytesIO()
    plt.savefig(buffer_obs_mb_bar_grid, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_obs_mb_bar_grid.seek(0)
    plot_obs_mb_bar_grid = base64.b64encode(buffer_obs_mb_bar_grid.getvalue()).decode()

    plt.close()

    # TC combined plot

    plot_no_of_obs_H_methods(change_df, change_df_2015v, country_code)

    # Save the plot to a BytesIO object
    buffer_obs_H = BytesIO()
    plt.savefig(buffer_obs_H, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_obs_H.seek(0)
    plot_encoded_obs_H = base64.b64encode(buffer_obs_H.getvalue()).decode()

    plt.close()


    ## Mass balance trends - warming stripes

    plot_mb_warming_stripes(mb_df, country_code)

    # Save the plot to a BytesIO object
    buffer_stripes = BytesIO()
    plt.savefig(buffer_stripes, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_stripes.seek(0)
    plot_encoded_stripes = base64.b64encode(buffer_stripes.getvalue()).decode()

    plt.close()

    # Inventory percentage GLIMS and WGI area plot

    plot_glims_area_yearly(glims_pts_countries, wgi, rgi7_countries, country_code)

    buffer_glims_area= BytesIO()
    plt.savefig(buffer_glims_area, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_glims_area.seek(0)
    plot_encoded_glims_area = base64.b64encode(buffer_glims_area.getvalue()).decode()

    plt.close()


    ## Key statistics table

    tot_area = get_national_rgi_area(rgi7_countries, country_code)

    # Area coverage between two periods

    # Area covered for 2005-2013

    perc_area_fronts_0513 = area_covered_by_x_data(fronts_df_0513, glacier_A, glaciers_df, rgi7_countries, country_code)

    if 0 < perc_area_fronts_0513 < 1:
        perc_area_fronts_0513 = round(perc_area_fronts_0513, 2)
    elif perc_area_fronts_0513 == 0:
        pass
    else:
        perc_area_fronts_0513 = int(perc_area_fronts_0513)

    perc_area_mb_0513 = area_covered_by_x_data(mb_df_overview_0513, glacier_A, glaciers_df, rgi7_countries, country_code)
    perc_area_H_0513 = area_covered_by_x_data(change_df_0513, glacier_A, glaciers_df, rgi7_countries, country_code)

    # Area covered for 2014-2022

    perc_area_fronts_1422 = area_covered_by_x_data(fronts_df_1422, glacier_A, glaciers_df, rgi7_countries, country_code)
    perc_area_mb_1422 = area_covered_by_x_data(mb_df_overview_1422, glacier_A, glaciers_df, rgi7_countries, country_code)
    perc_area_H_1422 = area_covered_by_x_data(change_df_1422, glacier_A, glaciers_df, rgi7_countries, country_code)


    # Number of series from 2005-2013

    n_series_fronts_0513 = n_of_series(fronts_df_0513, country_code)
    n_series_mb_0513 = n_of_series(mb_df_overview_0513, country_code)
    n_series_change_0513 = n_of_series(change_df_0513, country_code)

    # Number of series from 2014-2022

    n_series_fronts_1422 = n_of_series(fronts_df_1422, country_code) # for frontal variations
    n_series_mb_1422 = n_of_series(mb_df_overview_1422, country_code) # mass balance
    n_series_change_1422 = n_of_series(change_df_1422, country_code) # thickness change


    # Length of series for 2005-2013

    len_series_fronts_0513 = len_of_series_period_specific(fronts_df, fronts_df_0513, country_code)
    len_series_mb_0513 = len_of_series_period_specific(mb_df_overview, mb_df_overview_0513, country_code)
    len_series_change_0513 = len_of_series_period_specific(change_df, change_df_0513, country_code)

    # Length of series for 2014-2022

    len_series_fronts_1422 = len_of_series_period_specific(fronts_df, fronts_df_1422, country_code)
    len_series_mb_1422 = len_of_series_period_specific(mb_df_overview, mb_df_overview_1422, country_code)
    len_series_change_1422 = len_of_series_period_specific(change_df, change_df_1422, country_code)


    # Average number of observations per series for 2005-2013

    avg_obs_fronts_0513 = avg_obs_period_specific(fronts_df, fronts_df_0513, country_code)
    avg_obs_mb_0513 = avg_obs_period_specific(mb_df_overview, mb_df_overview_0513, country_code)
    avg_obs_change_0513 = avg_obs_period_specific(change_df, change_df_0513, country_code)

    # Average number of observations per series for 2014-2022

    avg_obs_fronts_1422 = avg_obs_period_specific(fronts_df, fronts_df_1422, country_code)
    avg_obs_mb_1422 = avg_obs_period_specific(mb_df_overview, mb_df_overview_1422, country_code)
    avg_obs_change_1422 = avg_obs_period_specific(change_df, change_df_1422, country_code)


    # Load the Jinja template and render the HTML
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template_country.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    # All data to render onto HTML file
    outputText = template.render(country_code = country_code,

                                 # Text

                                 overview_text = country_text.get('overview', ''),
                                 tier1_past_text = country_text.get('tier1_past', ''),
                                 tier1_present_text = country_text.get('tier1_present', ''),
                                 tier1_future_text = country_text.get('tier1_future', ''),

                                 tier2_past_text = country_text.get('tier2_past', ''),
                                 tier2_present_text = country_text.get('tier2_present', ''),
                                 tier2_future_text = country_text.get('tier2_future', ''),

                                 tier3_past_text = country_text.get('tier3_past', ''),
                                 tier3_present_text = country_text.get('tier3_present', ''),
                                 tier3_future_text = country_text.get('tier3_future', ''),

                                 tier4_past_text = country_text.get('tier4_past', ''),
                                 tier4_present_text = country_text.get('tier4_present', ''),
                                 tier4_future_text = country_text.get('tier4_future', ''),

                                 tier5_past_text = country_text.get('tier5_past', ''),
                                 tier5_present_text = country_text.get('tier5_present', ''),
                                 tier5_future_text = country_text.get('tier5_future', ''),

                                 country_name = country_name,

                                 #Plots

                                 plot_obs_fv_bar_grid = plot_obs_fv_bar_grid,
                                 plot_obs_mb_bar_grid = plot_obs_mb_bar_grid,
                                 plot_obs_H = plot_encoded_obs_H,

                                 plot_stripes = plot_encoded_stripes,

                                 plot_glims_area = plot_encoded_glims_area,

                                 #Key stats

                                 tot_area = tot_area,

                                 perc_area_fronts_0513 = perc_area_fronts_0513,
                                 perc_area_mb_0513 = round(perc_area_mb_0513, 2),
                                 perc_area_H_0513 = round(perc_area_H_0513, 2),

                                 perc_area_fronts_1422 = round(perc_area_fronts_1422, 2),
                                 perc_area_mb_1422 = round(perc_area_mb_1422, 2),
                                 perc_area_H_1422 = int(perc_area_H_1422),

                                 n_series_fronts_0513 = int(n_series_fronts_0513),
                                 n_series_mb_0513 = int(n_series_mb_0513),
                                 n_series_change_0513 = int(n_series_change_0513),

                                 n_series_fronts_1422 = int(n_series_fronts_1422),
                                 n_series_mb_1422 = int(n_series_mb_1422),
                                 n_series_change_1422 = int(n_series_change_1422),

                                 len_series_fronts_0513 = int(len_series_fronts_0513),
                                 len_series_mb_0513 = int(len_series_mb_0513),
                                 len_series_change_0513 = int(len_series_change_0513),

                                 len_series_fronts_1422 = int(len_series_fronts_1422),
                                 len_series_mb_1422 = int(len_series_mb_1422),
                                 len_series_change_1422 = int(len_series_change_1422),

                                 avg_obs_fronts_0513 = int(avg_obs_fronts_0513),
                                 avg_obs_mb_0513 = int(avg_obs_mb_0513),
                                 avg_obs_change_0513 = int(avg_obs_change_0513),

                                 avg_obs_fronts_1422 = int(avg_obs_fronts_1422),
                                 avg_obs_mb_1422 = int(avg_obs_mb_1422),
                                 avg_obs_change_1422 = int(avg_obs_change_1422),


                                 )

    # Save the rendered HTML to a file
    output_file_path = f"output_{country_code}.html"
    with open(output_file_path, "w") as file:
        file.write(outputText)

#%% Output all the countries with glacier data

country_list = list(countries['id']) # All the countries

for country_code in country_list:

    # Check if there is any data:
    glaciers_country = glaciers_df[glaciers_df['POLITICAL_UNIT'] == country_code]

    if len(glaciers_country) > 0:

        #intro_text = f"Text/{country_code}_intro.txt"
        output_from_template(country_code, "text/country_profiles_text.csv")

    # Don't make country profile sheet if there are no glaciers for that country
    else:
        pass

#%% or run an individual country

output_from_template("CH", "text/country_profiles_text.csv")
