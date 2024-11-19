#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 13:40:11 2024

@author: giuliosaibene
"""

# =============================================================================
# GLACIER PROFILES - WGMS
# =============================================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jinja2
import base64
from io import BytesIO
import geopandas as gpd
#import contextily as cx
import folium
from folium.plugins import MiniMap
from shapely.geometry import Point
from branca.element import Figure
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import plotly.graph_objects as go
import plotly.io as pio
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.basemap import Basemap
import contextily as ctx
from PIL import Image
import pdfkit
from matplotlib.patches import FancyArrow, Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
from flask import Flask, render_template
import os
import re
from datetime import datetime
from PIL import Image




glaciers_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/glacier.csv",
                          dtype = {'POLITICAL_UNIT': str}, low_memory = False)

glaciers_ids_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/glacier_id_lut.csv")

glacier_names = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/glacier_name.csv")

glacier_photos = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/glacier_photo.csv")

glacier_country = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/glacier_country.csv")

country_codes = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/country_codes.csv")

state_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/state.csv")

mb_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/mass_balance.csv")

mb_df_dbgate = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/mass_balance.csv")

mb_df_overview = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/mass_balance_overview.csv")

fv_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/front_variation.csv")

fv_df_db = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/front_variation.csv")

bibliography = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/bibliography.csv")

investigators = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/team_investigators.csv")

team_members = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/team_member.csv")

#rgi7 = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/rgi7.gpkg")

# RGI regions

#rgi6_alaska = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/rgi60/01_rgi60_Alaska/01_rgi60_Alaska.shp")

#rgi6_west_america = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/rgi60/02_rgi60_WesternCanadaUS/02_rgi60_WesternCanadaUS.shp")

# WGMS outlines

wgms_outlines = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/wgms_outlines_v2.shp")

glacier_id_outline = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/glacier_outline_all.csv")


#%% functions

# Get glacier name

def get_glacier_name(glacier_id):
    
    glacier_df = glacier_names[glacier_names['glacier_id'] == glacier_id]
    
    # Check if there are any preferred names in which case only take those
    if glacier_df['preferred'].any():
        
        glacier_df = glacier_df[glacier_df['preferred'] == True]
    
    glacier_name = glacier_df['name']
    
    if len(glacier_name) > 1:
        
        names_list = []
        
        for i in range(len(glacier_name)):
        
            name = glacier_name.astype(str).iloc[i]
            
            names_list.append(name)
            
        full_name = ' · '.join(names_list)
        
    else:
    
        full_name = glacier_name.astype(str).iloc[0]
    
    #glacier_name = glacier_name[:1].upper() + glacier_name[1:].lower()
    
    
    # Get only English name
    
    glacier_df_eng = glacier_df[glacier_df['language'] == "english"]
    
    # If there are no English names than take other language one
    if glacier_df_eng.empty:
        
        full_name_eng = glacier_name.astype(str).iloc[0]
        
    else:
    
        # Check if there are any preferred names in which case only take those
        if glacier_df_eng['preferred'].any():
            
            glacier_df_eng = glacier_df_eng[glacier_df_eng['preferred'] == True]
        
        glacier_name_eng = glacier_df_eng['name']
        
        full_name_eng = glacier_name_eng.astype(str).iloc[0]
    
    
    return full_name, full_name_eng

#test_name = get_glacier_name(853)


# Get glacier country

def get_glacier_country(glacier_id):
    
    glacier_country_code = glacier_country[glacier_country['glacier_id'] == glacier_id]['country_id'].values[0]
    
    glacier_country_name = country_codes[country_codes['id'] == glacier_country_code]['name'].values[0]
    
    return glacier_country_name

# Get glaciere GLIMS ID

def get_rgi6_id(glacier_id):
    
    glacier_id_df = glaciers_ids_df[glaciers_ids_df['WGMS_ID'] == glacier_id]
    
    glacier_rgi6_id = glacier_id_df['RGI60_ID']
    
    glacier_rgi6_id = glacier_rgi6_id.astype(str).iloc[0]
    
    return glacier_rgi6_id

#gulkana_rgi6_id = get_rgi6_id(90)

def get_glacier_outline_id(glacier_id):
    
    glacier_outlines_df = glacier_id_outline[glacier_id_outline['glacier_id'] == glacier_id]
    
    glacier_outlines_id = glacier_outlines_df['outline_id'].unique().tolist()
    
    return glacier_outlines_id

def get_outline_reference(glacier_id):
    
    glacier_outlines_ids = get_glacier_outline_id(glacier_id)
    
    glacier_outlines_df = wgms_outlines[wgms_outlines['id'].isin(glacier_outlines_ids)]
    
    if not glacier_outlines_df.empty:
    
        # get max and min year
        
        glacier_outlines_df['date_max'] = pd.to_datetime(glacier_outlines_df['date_max'])
        
        min_year_index = glacier_outlines_df['date_max'].dt.year.idxmin()
        max_year_index = glacier_outlines_df['date_max'].dt.year.idxmax()
        
        # Get reference:
        
        reference_id_max = glacier_outlines_df.loc[max_year_index, 'bibliograp']
        reference_id_min = glacier_outlines_df.loc[min_year_index, 'bibliograp']
        
        reference_max_df = bibliography[bibliography['id'] == reference_id_max]
        reference_max = reference_max_df['original_string'].values[0]
        
        reference_min_df = bibliography[bibliography['id'] == reference_id_min]
        reference_min = reference_min_df['original_string'].values[0]
        
    else:
        
        reference_max = 'not reported'
        reference_min = 'not reported'
    
    return [reference_max, reference_min]

def get_glacier_length(glacier_id):
    
    glacier_state = state_df[state_df['WGMS_ID'] == glacier_id]
    
    # Drop rows where there is no length
    glacier_state = glacier_state.dropna(subset=['LENGTH'])
    
    max_year_index = glacier_state['YEAR'].idxmax()
    
    glacier_length = glacier_state.loc[max_year_index, 'LENGTH']
    
    glacier_length = round(glacier_length, 2)
    
    max_year = glacier_state.loc[max_year_index, 'YEAR']
    
    return [glacier_length, max_year]

# Get glacier elevation range

def get_glacier_elev_range(glacier_id):
    
    glacier_state = state_df[state_df['WGMS_ID'] == glacier_id]
    
    # Drop rows where there is no elevations
    glacier_state = glacier_state.dropna(subset=['LOWEST_ELEVATION', 'HIGHEST_ELEVATION'])

    # Find row where the year is the most recent
    max_year_index = glacier_state['YEAR'].idxmax()
    
    lower_elev = int(glacier_state.loc[max_year_index, 'LOWEST_ELEVATION'])
    upper_elev = int(glacier_state.loc[max_year_index, 'HIGHEST_ELEVATION'])
    year = int(glacier_state.loc[max_year_index, 'YEAR'])
    
    return [lower_elev, upper_elev, year]

#get_glacier_elev_range(90, state_df)

# Get glacier photo

def get_glacier_photo(glacier_id):
    
    glacier_photo_df = glacier_photos[glacier_photos['glacier_id'] == glacier_id]
    
    if glacier_photo_df.empty:
        
        photo_url = ""
    
    else:
    
        photo_url = glacier_photo_df['data_url'].values[0]
    
    return photo_url

def get_photo_credit(glacier_id):
    
    glacier_photo_df = glacier_photos[glacier_photos['glacier_id'] == glacier_id]
    
    if glacier_photo_df.empty:
        
        photo_credit = 'not reported'
        photographer = 'not reported'
        photo_year = 'not reported'
    
    else:
    
        photo_credit = glacier_photo_df['credit'].values[0]
        
        # Check if credit is NaN (not a float) or empty string
        if pd.isna(photo_credit) or photo_credit == '':
            
            photo_credit = 'not reported'
        
        photographer = glacier_photo_df['photographer'].values[0]
        
        # Check if photographer is NaN (not a float) or empty string
        if pd.isna(photographer) or photographer == '':
            
            photographer = 'not reported'
            
        # Retrieve capture year
        
        photo_year = int(glacier_photo_df['capture_year'].values[0])
        
        if pd.isna(photo_year) or photo_year == '':
            
            photo_year = 'not reported'
    
        return [photo_credit, photographer, photo_year]

#%% Annual mean FV

# Create custom datetime conversion to handle values prior to pd.datetime limit of 1677

def custom_to_datetime(date_str):
    try:
        # Try using Pandas' to_datetime for in-bound dates
        return pd.to_datetime(date_str)
    except (pd.errors.OutOfBoundsDatetime, ValueError):
        # Fall back to Python's datetime for out-of-bound dates
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # Handle any other invalid date formats
            return pd.NaT

# Chop FV measurements spanning over multiple years into yearly values

def expand_dates(df):
    
    df.dropna(subset=['begin_date_min'], inplace=True) # removes rows when the begin date is missing
    
    df['begin_date_min'] = df['begin_date_min'].apply(custom_to_datetime)
    df['end_date_min'] = df['end_date_min'].apply(custom_to_datetime)
    
    # Extract year
    df['START_YEAR'] = df['begin_date_min'].apply(lambda x: x.year)
    df['END_YEAR'] = df['end_date_min'].apply(lambda x: x.year)
        
    # For 1-year gaps increase start year by 1 to prevent expansion into two years when really the measurement is done over one hydro year
    df.loc[(df['END_YEAR'] - df['START_YEAR']) == 1, 'START_YEAR'] = df['START_YEAR'] + 1
        
    # Create a list of years between START_YEAR and END_YEAR
    def get_years(row):
        return list(range(row['START_YEAR'], row['END_YEAR'] + 1))
    
    # Check if 'START_YEAR' column has any data
    if len(df['START_YEAR']) > 0:
        
        # Apply the function to create a new column 'YEARS_ALL' which is a list of all years embedded within one row
        df['YEARS_ALL'] = df.apply(get_years, axis=1)
    
        # Explode such that there is a row for each year
        df_long = df.explode('YEARS_ALL')
        
        df_long = df_long.reset_index(drop=True)
        
        # Calculate annual average FV when there are multiple years per entry
        
        # Group by `_row_id` and calculate `length_change_annual`
        
        def calculate_length_change_annual(group):
            
            length_change_total = group['length_change'].iloc[0]  # The first value of 'length_change' in each group
            num_years = len(group)  # Number of years in the group
            group['length_change_annual'] = length_change_total / num_years
            return group
        
        df_long = df_long.groupby('_row_id').apply(calculate_length_change_annual)
        
        
    else:
        # Handle case where 'START_YEAR' column has no data
        df_long = df
        df_long['YEARS_ALL'] = ''
        
    
    return(df_long)


def get_annual_mean_fv(glacier_id):
    
    fv_glacier_df = fv_df_db[fv_df_db['glacier_id'] == glacier_id]
    
    fv_glacier_df = fv_glacier_df.dropna(subset=['length_change'])

    fv_glacier_df_long = expand_dates(fv_glacier_df)
    
    # Initialize variables:
    min_year = "—"
    max_year = "—"
    fv_annual_mean = "—"
    
    if not fv_glacier_df_long.empty:
        
        # Change back to real START_YEAR when year gap was 1 and I added 1 to START_YEAR to prevent double rows
        
        fv_glacier_df_long.loc[(fv_glacier_df_long['END_YEAR'] - fv_glacier_df_long['START_YEAR']) == 0, 'START_YEAR'] = fv_glacier_df_long['START_YEAR'] - 1

        min_year = fv_glacier_df_long['START_YEAR'].min() 
        
        max_year = fv_glacier_df_long['END_YEAR'].max()
        
        fv_annual_mean = fv_glacier_df_long['length_change_annual'].mean()
        
        fv_annual_mean = round(fv_annual_mean, 2)

    return [fv_annual_mean, min_year, max_year]



# =============================================================================
# # Cumulative FV: not used due to data gap problems
# 
# def get_cum_fv(glacier_id):
#     
#     fv_glacier_df = fv_df_db[fv_df_db['glacier_id'] == glacier_id]
#     
#     # Convert date rows to datetime
#     
# # =============================================================================
# #     fv_glacier_df['begin_date_min'] = fv_glacier_df['begin_date_min'].apply(custom_to_datetime)
# # 
# #     fv_glacier_df['end_date_min'] = fv_glacier_df['end_date_min'].apply(custom_to_datetime)
# # =============================================================================
# 
#     
#     fv_glacier_df['begin_date_min'] = pd.to_datetime(fv_glacier_df['begin_date_min'], 
#                                                      format='%Y-%m-%d', errors = 'coerce')
#     fv_glacier_df['end_date_min'] = pd.to_datetime(fv_glacier_df['end_date_min'],
#                                                    format='%Y-%m-%d', errors = 'coerce')
#     
# # =============================================================================
# #     # Drop duplicate data submissions
# #     fv_glacier_df = fv_glacier_df.drop_duplicates(subset='YEAR', keep='first')
# # =============================================================================
# 
#     # Drop rows where there is no elevations
#     fv_glacier_df = fv_glacier_df.dropna(subset=['length_change'])
#     
#     # Initialize variables:
#     min_year = "—"
#     max_year = "—"
#     cum_fv = "—"
#     
#     if not fv_glacier_df.empty:
#     
#         # Get from and to years
#         min_year = fv_glacier_df['begin_date_min'].dt.year.min()
#         
#         max_year = fv_glacier_df['end_date_min'].dt.year.max() 
#         
#         cum_fv = int(fv_glacier_df['length_change'].sum())
#     
#     return [cum_fv, min_year, max_year]
#     
# #cum_fv_test, min_year_fv_test, max_year_fv_test = get_cum_fv(899)
# 
# # =============================================================================
# # def get_fv_investigator(glacier_id):
# #     
# #     fv_glacier_df = fv_df[fv_df['WGMS_ID'] == glacier_id]
# #     
# #     fv_glacier_df = fv_glacier_df.dropna(subset=['INVESTIGATOR'])
# #     
# #     if len(fv_glacier_df) == 0:
# #         investigator = "'not reported'"
# #         
# #     else:
# #         investigator = fv_glacier_df['INVESTIGATOR'].iloc[-1]
# #     
# #     return investigator
# # =============================================================================
# =============================================================================

def get_fv_investigator(glacier_id):
    
      fv_glacier_df = fv_df_db[fv_df_db['glacier_id'] == glacier_id]
      
      fv_glacier_df = fv_glacier_df.dropna(subset = ['team_id'])
      
      if not fv_glacier_df.empty:
          
          team_ids = fv_glacier_df['team_id'].drop_duplicates()
          
          fv_team_members = team_members[team_members['team_id'].isin(team_ids)]
          
          fv_team_members = fv_team_members.dropna(subset = ['person_id.name']) # Remove rows with no person name
          
          fv_investigators = fv_team_members['person_id.name'].drop_duplicates()
          
          fv_investigators = fv_investigators.values # convert to an array
          
          fv_investigators = ', '.join(fv_investigators)
          
      else:
          
          fv_investigators = "not reported" # Handle case when there are no reported team_ids
          
      return fv_investigators

#get_fv_investigator(394)

#%% Get area change

def get_area_change(glacier_id):

    glacier_state = state_df[state_df['WGMS_ID'] == glacier_id]
    
    # Drop rows where there is no area
    
    glacier_state = glacier_state.dropna(subset = ['AREA'])
    
    # Initialize variables
    min_year = "—"
    max_year = "—"
    max_year_change = "—"
    initial_area = "—"
    final_area = "—"
    
    if not glacier_state.empty:
    
        min_year_index = glacier_state['YEAR'].idxmin()
        max_year_index = glacier_state['YEAR'].idxmax()
        
        min_year = glacier_state['YEAR'].min()
        max_year = glacier_state['YEAR'].max()
        max_year_change = max_year
        
        initial_area = round(glacier_state.loc[min_year_index, 'AREA'], 1)
        final_area = round(glacier_state.loc[max_year_index, 'AREA'], 1)
        
        if initial_area - final_area == 0: # if there is only one area entry
            
            initial_area = round(glacier_state.loc[min_year_index, 'AREA'], 1)
            final_area = "—"
            max_year = "—"
    
    return [min_year, max_year, max_year_change, initial_area, final_area]

#min_year, max_year, max_year_change, final_area, area_change = get_area_change(1367)

#%% interactive cumulative MB plot

def get_annual_mean_mb(glacier_id):
    
    mb_df_glacier = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id]
    
    if not mb_df_glacier.empty:
        
        mb_df_glacier = mb_df_glacier.dropna(subset = ['annual_balance'])
        
        min_year = mb_df_glacier['year'].min()
        
        max_year = mb_df_glacier['year'].max() 
        
        annual_mean_mb = mb_df_glacier['annual_balance'].mean()
        
        annual_mean_mb = round(annual_mean_mb, 2)
        
    else:
        
        annual_mean_mb = "—"
        
    return [min_year, max_year, annual_mean_mb]


# Cumulative MB: not used due to issue with data gaps

def get_cum_mb(glacier_id):
    
    mb_df_glacier = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id]
    
    if not mb_df_glacier.empty:
    
        cum_mb_glacier = mb_df_glacier['annual_balance'].cumsum()
        
        min_year = mb_df_glacier['year'].min()
        
        max_year = mb_df_glacier['year'].max() 
        
        total_cum_mb = round(cum_mb_glacier.iloc[-1], 1)
        
    else:
        
        min_year = "—"
        max_year = "—"
        total_cum_mb = "—"
    
    return [min_year, max_year, total_cum_mb]


# Version which only calculates the cumulative MB for the latest continuous period after any gap

def get_cum_mb_most_recent_cont_period(glacier_id):
    
    mb_df_glacier = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id].reset_index()
    
    if not mb_df_glacier.empty:
       
        mb_df_glacier = mb_df_glacier.sort_values(by='year')
        
        # Check for gaps in the year column
        mb_df_glacier['year_diff'] = mb_df_glacier['year'].diff()
        
        # Find indices where a gap exists (year_diff > 1)
        gap_indices = mb_df_glacier.index[mb_df_glacier['year_diff'] > 1]
        
        print(gap_indices)
        
        # If there are gaps, determine the last continuous segment
        if not gap_indices.empty:
            
            last_gap_start_index = gap_indices[-1]
            
            # Start from the first year before the last gap
            continuous_data_start_index = mb_df_glacier.index[last_gap_start_index]
            
            start_year = mb_df_glacier.loc[continuous_data_start_index, 'year']
            
        else:
            # No gaps, use the first year
            start_year = mb_df_glacier['year'].min()
        
        # Filter the DataFrame to include only data from the start year of the last continuous period
        continuous_data = mb_df_glacier[mb_df_glacier['year'] >= start_year]
        
        # Calculate cumulative mass balance
        cum_mb_glacier = continuous_data['annual_balance'].cumsum()
        
        # Get the min and max year of the filtered continuous data
        min_year = continuous_data['year'].min()
        max_year = continuous_data['year'].max()
        
        # Get the total cumulative mass balance
        total_cum_mb = round(cum_mb_glacier.iloc[-1], 1) if not continuous_data.empty else 0.0
        
    else:
        min_year = "—"
        max_year = "—"
        total_cum_mb = "—"
    
    return [min_year, max_year, total_cum_mb]



def get_mb_investigator(glacier_id):
    
    mb_glacier_df = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id]
    
    mb_glacier_df = mb_glacier_df.dropna(subset=['team_id'])
    
    if not mb_glacier_df.empty:
    
        team_ids = mb_glacier_df['team_id'].drop_duplicates()
        
        mb_team_members = team_members[team_members['team_id'].isin(team_ids)]
        
        mb_team_members = mb_team_members.dropna(subset = ['person_id.name'])
        
        mb_investigators = mb_team_members['person_id.name'].drop_duplicates()
                  
        mb_investigators = mb_investigators.values # convert to an array
        
        mb_investigators = ', '.join(mb_investigators)
        
    else:
        
        mb_investigators = "not reported"
    
    return mb_investigators

#get_mb_investigator(394)


# Plot

def interactive_plot_cum_mb(glacier_id):
    
    # Filter the DataFrame for the specific glacier ID
    mb_df_glacier = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id]
    
    # Insert missing years as NaN for MB to break the line

    full_years = pd.Series(range(mb_df_glacier['year'].min(), mb_df_glacier['year'].max() + 1))

    # Set index to years to merge with the full_years
    mb_df_glacier.set_index('year', inplace=True)

    mb_df_glacier = mb_df_glacier.reindex(full_years, fill_value=np.nan)

    # Reset index to get 'year' back as a column
    mb_df_glacier.reset_index(inplace=True)
    mb_df_glacier.rename(columns={'index': 'year'}, inplace=True)

    # Calculate the cumulative mass balance
    cum_mb_glacier = mb_df_glacier['annual_balance'].cumsum()
    
    # Values for custom tick labels
    
    years = mb_df_glacier['year']
    min_year = years.min()
    med_year = int(years.median())
    max_year = years.max()
    
    min_cum_mb = cum_mb_glacier.min()
    med_cum_mb = int(cum_mb_glacier.median())
    max_cum_mb = cum_mb_glacier.max()
    
    # To detect if glacier is retreating or advancing
    change_mb = (abs(max_cum_mb) - abs(min_cum_mb)) / (max_year - min_year)
    
    # Create an interactive plot with Plotly
    fig = go.Figure()

    # Add a line trace
    fig.add_trace(go.Scatter(
        x = years,
        y=cum_mb_glacier,
        mode='lines',
        line=dict(color='black'),
        hovertemplate='<b> %{y:.0f} m w.e.<extra></extra>',
        showlegend = False
    ))
    
    # Add scatter points on top of the line
    fig.add_trace(go.Scatter(
        x=years,
        y=cum_mb_glacier,
        mode='markers',  # Use 'markers' for scatter points
        marker=dict(color='black', size = 3, line=dict(color='black', width=1)),  # White points with black edges
        hoverinfo='none',
        showlegend = False
    ))
    
    # Add horizontal line at y=0
    fig.add_shape(
        type="line",
        x0 = min_year - 1,  # start of x-axis
        x1= max_year + 1,  # end of x-axis
        y0=0,  # fixed y position
        y1=0,  # fixed y position
        line=dict(color="gray", width=1)
    )

    if change_mb < 0:
        
        # layout for retreating glaciers
        fig.update_layout(
            
            title=dict(
                text="Cumulative Mass Balance (m w.e.)",  
                x=0.5,  
                xanchor='center', 
                font=dict(size=20, family = "Arial", color = 'black') 
                    ),
            width = 600,
            height = 300,
            margin=dict(l=50, r=50, t=50, b=50),
            hovermode='x unified',
            plot_bgcolor='white',  
            paper_bgcolor='white',
            
            xaxis=dict(
                title = "Year",
                ticks = 'outside',
                title_font=dict(size=24, family = "Arial", color = 'black'),
                tickvals=[min_year, med_year, max_year],  
                ticktext=[str(min_year), str(med_year), str(max_year)],  
                tickfont=dict(size = 20, family = "Arial", color = 'black'),
                showline=True,
                linecolor='black',
                linewidth = 2,
                range = [min_year - 1, max_year + 1]
                #minor=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.2)  # Minor grid lines
            ),
            
            yaxis=dict(
                tickvals=[min_cum_mb, 0], 
                ticks = 'outside',
                ticktext=[str(int(min_cum_mb)), 0], 
                tickfont=dict(size=20,  family = "Arial", color = 'black'),
                tickformat=',', 
                showline=True,
                linecolor='black',
                linewidth = 2
                #minor=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.2) 
            )
    
        )
        
    else:
        
        # layout for advancing glaciers
        fig.update_layout(
            
            title=dict(
                text="Cumulative Mass Balance (m w.e.)",  
                x=0.5,  
                xanchor='center', 
                font=dict(size=20, family = "Arial", color = 'black') 
                    ),
            width = 700,
            height = 300,
            margin=dict(l=50, r=50, t=50, b=50),
            hovermode='x unified',
            plot_bgcolor='white',  
            paper_bgcolor='white',
            
            xaxis=dict(
                title = "Year",
                ticks = 'outside',
                title_font=dict(size=24, family = "Arial", color = 'black'),
                tickvals=[min_year, med_year, max_year],  
                ticktext=[str(min_year), str(med_year), str(max_year)],
                tickfont=dict(size = 20, family = "Arial", color = 'black'),
                showline=True,
                linecolor='black',
                linewidth = 2,
                range = [min_year - 1, max_year + 1]
            ),
            
            yaxis=dict(
                tickvals = [0, max_cum_mb],  
                ticks = 'outside',
                ticktext = [0, str(int(max_cum_mb)) ],  
                tickfont=dict(size=20,  family = "Arial", color = 'black'),
                tickformat=',', 
                showline=True,
                linecolor='black',
                linewidth = 2
            )
    
        )

    html_str = pio.to_html(fig, full_html=False, include_plotlyjs='cdn',
                           config={'displayModeBar': False})
    return html_str

#interactive_plot_cum_mb(90) # Gulkana, US

#%% Plot 3D Earth sphere

def plot_earth_glacier(glacier_id):

    def plot_earth_with_texture(ax):
        # Load the Earth texture image
        img = Image.open('/Users/giuliosaibene/Desktop/University/UZH/WGMS/glacier_profiles/land_shallow_topo_2048.jpg' )
        img = np.array(img)
    
        # Generate data for a sphere
        lons = np.linspace(-180, 180, img.shape[1]) * np.pi / 180
        lats = np.linspace(-90, 90, img.shape[0])[::-1] * np.pi / 180
        lons, lats = np.meshgrid(lons, lats)
    
        x = np.cos(lats) * np.cos(lons)
        y = np.cos(lats) * np.sin(lons)
        z = np.sin(lats)
    
        # Map the texture onto the sphere
        ax.plot_surface(x, y, z, rstride=5, cstride=5, facecolors=img / 255., alpha=1.0,
                        antialiased=False, shade=False)
    
    def add_marker(ax, glacier_id):
        
        glacier_df = glaciers_df[glaciers_df['WGMS_ID'] == glacier_id]
        
        lat_glacier = glacier_df['LATITUDE'].values[0]
        lon_glacier = glacier_df['LONGITUDE'].values[0]
        
        # Convert latitude and longitude to radians
        lat = np.radians(lat_glacier)
        lon = np.radians(lon_glacier)
    
        # Calculate the Cartesian coordinates
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        
        # Adjust coordinates to ensure marker is outside of sphere
        x = x + x/10
        y = y + y/10
        z = z + z/10
        
        # Calculate elevation and azimuth angles
        elev = lat * 180 / np.pi
        azim = lon * 180 / np.pi
    
        # Set the view angle to center it on the marker
        ax.view_init(elev=elev, azim=azim)
    
        # Plot the marker
        ax.scatter(x, y, z, color='r', s=250)
    
    # Create a new figure
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.set_axis_off()
    
    ax.set_xlim([-0.7, 0.7])
    ax.set_ylim([-0.7, 0.7])
    ax.set_zlim([-0.7, 0.7])
    
    # Plot the Earth with the texture
    plot_earth_with_texture(ax)
    
    # Add a marker (example: New York City, USA)
    add_marker(ax, glacier_id)
    
    # Make background transparent
    fig.patch.set_facecolor('none') 
    ax.set_facecolor('none')
    
    plt.tight_layout()

    plt.show()

#plot_earth_glacier(90)


#%% display just outline

# This version takes outlines from WGMS and plots most recent and oldest outlines

def plot_all_outlines(glacier_id):
    
    glacier_outlines_ids = get_glacier_outline_id(glacier_id)
    
    glacier_outlines_df = wgms_outlines[wgms_outlines['id'].isin(glacier_outlines_ids)]
    
    if not glacier_outlines_df.empty:
    
        # get max and min year
        
        glacier_outlines_df['date_max'] = pd.to_datetime(glacier_outlines_df['date_max'])
        
        min_year_index = glacier_outlines_df['date_max'].dt.year.idxmin()
        max_year_index = glacier_outlines_df['date_max'].dt.year.idxmax()
        
        min_year = int(glacier_outlines_df['date_max'].dt.year.min())
        max_year = int(glacier_outlines_df['date_max'].dt.year.max())
        
        glacier_outline_min = glacier_outlines_df.loc[min_year_index, 'geometry']
        glacier_outline_max = glacier_outlines_df.loc[max_year_index, 'geometry']
    
        gdf_min = gpd.GeoDataFrame(geometry = [glacier_outline_min])
        gdf_max = gpd.GeoDataFrame(geometry = [glacier_outline_max])
        
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()})
        
        #plotting outlines
        
        gdf_max.plot(ax = ax,  transform = ccrs.PlateCarree(),  
                        facecolor='none', edgecolor='#2c8bc6', linewidth=2)
        
        ax.text(1, 0.83, f"{max_year}", color = '#2c8bc6', 
                transform = ax.transAxes, size = 20, rotation = 270)
        
        if min_year != max_year: # only plot second outline if it's a different year
            gdf_min.plot(ax = ax, transform = ccrs.PlateCarree(), 
                         facecolor='none', edgecolor='#0f9900', linewidth=2)
            
            ax.text(1, 0.57, f"{min_year}", color = '#0f9900', 
                    transform = ax.transAxes, size = 20, rotation = 270)
        
        
    # =============================================================================
    #     # Add text about source year of satellite image
    #     
    #     ax.text(0.6, 0.02, 'Basemap: 2024', color = 'black', 
    #             transform = ax.transAxes, size = 10)
    #     box = Rectangle((0.58, 0.01), 0.3, 0.05, transform=ax.transAxes,
    #                     color='white', zorder=1, alpha = 0.6)  # zorder ensures it is behind other elements
    #     ax.add_patch(box)
    # =============================================================================
        
        # Add a scale bar
        scalebar = ScaleBar(1, units="m", dimension="si-length", location="lower left", length_fraction=0.25)
        ax.add_artist(scalebar)
        
        ctx.add_basemap(ax, crs=ccrs.Mercator(), source=ctx.providers.Esri.WorldImagery)
        
        for text in ax.texts:
            if 'Source' in text.get_text():
                text.set_visible(False)
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        # Remove edge around figure
        for spine in ax.spines.values():
            spine.set_edgecolor('none')
            spine.set_linewidth(0)
            
    else:
        
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()})
                
        ctx.add_basemap(ax, crs=ccrs.Mercator(), source=ctx.providers.Esri.WorldImagery)
        
        for text in ax.texts:
            if 'Source' in text.get_text():
                text.set_visible(False)
                
        ax.text(0.25, 0.5, "No outline available", size = 14,
                transform = ax.transAxes)
        
        box = Rectangle((0.21, 0.48), 0.6, 0.08, transform=ax.transAxes,
                             color='white', zorder=1, alpha = 0.6)  # zorder ensures it is behind other elements
        ax.add_patch(box)

#plot_all_outlines(853)


#%% Get a list of ids for glaciers which have a photo, name and mb data

name_mb_common_ids = pd.merge(glacier_names[['glacier_id']], mb_df_dbgate[['glacier_id']], on='glacier_id', how='inner')

name_mb_photo_common_ids = pd.merge(name_mb_common_ids, glacier_photos[['glacier_id']], on='glacier_id', how='inner')

common_ids = name_mb_photo_common_ids['glacier_id'].unique()

# Global list to store glacier IDs
generated_glacier_ids = [57, 76, 90, 94, 124, 360, 394, 566, 635, 753, 817, 853, 1367, 
                         2867, 2921, 3334, 3987, 4630, 26615, 35232]

glacier_ids_sorted = sorted(generated_glacier_ids, key=get_glacier_country)

glacier_ids_complete_sorted = sorted(common_ids, key=get_glacier_country)


#%% jinja output

# =============================================================================
# app = Flask(__name__)
# =============================================================================

def output_from_template(glacier_id):
    
    global generated_glacier_ids
    
    # NAME
    
    name, name_eng = get_glacier_name(glacier_id)
    
    # COUNTRY
    
    country = get_glacier_country(glacier_id)
    
    # ELEVATION RANGE
    
    lower_elev, upper_elev, elev_year = get_glacier_elev_range(glacier_id)
    
    # LENGTH
    
    glacier_length, length_year = get_glacier_length(glacier_id)
    
    # CUMULATIVE FV
    
    mean_fv, min_fv_year, max_fv_year = get_annual_mean_fv(glacier_id)
    
    fv_investigator = get_fv_investigator(glacier_id)
    
    # ANNUAL MEAN MB
    
    min_mb_year, max_mb_year, mean_mb = get_annual_mean_mb(glacier_id)
    
    mb_investigator = get_mb_investigator(glacier_id)
    
    # AREA CHANGE
    
    min_area_year, max_area_year, max_area_year_change, initial_area, final_area= get_area_change(glacier_id)
    
    # PHOTO
    
    photo_url = get_glacier_photo(glacier_id)
    photo_credit, photographer, photo_year = get_photo_credit(glacier_id)
    
    # PLOTS
    
    # Interactive cumulative MB
    
    cum_mb_html = interactive_plot_cum_mb(glacier_id)
    
    # Outline
    
    #plot_outline(glacier_id, rgi_region)
    plot_all_outlines(glacier_id)
    
    # Outline references
    
    outline_reference_max, outline_reference_min = get_outline_reference(glacier_id)
    
    # Save the plot to a BytesIO object
    buffer_outline = BytesIO()
    plt.savefig(buffer_outline, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_outline.seek(0)
    plot_outline_encoded = base64.b64encode(buffer_outline.getvalue()).decode()
    
    plt.close()
    
    # Earth sphere
    
    plot_earth_glacier(glacier_id)
    
    # Save the plot to a BytesIO object
    buffer_earth_sphere = BytesIO()
    plt.savefig(buffer_earth_sphere, format='png', bbox_inches = 'tight', dpi = 300)
    buffer_earth_sphere.seek(0)
    plot_earth_sphere_encoded = base64.b64encode(buffer_earth_sphere.getvalue()).decode()
    
    plt.close()
    
    # Add glacier ID to the list
    if glacier_id not in generated_glacier_ids:
        generated_glacier_ids.append(glacier_id)
    
    # Determine previous and next glacier IDs
    current_index = glacier_ids_sorted.index(glacier_id)
    
    # Calculate prev_id and next_id, handle edge cases for first and last indices
    prev_id = glacier_ids_sorted[current_index - 1] if current_index > 0 else glacier_ids_sorted[-1] # Loops back to the final one in the list
    next_id = glacier_ids_sorted[current_index + 1] if current_index < len(glacier_ids_sorted) - 1 else glacier_ids_sorted[0] # Goes back to the start of the list
    
    # Load the Jinja template and render the HTML
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template_glacier.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    
    # All data to render onto HTML file
    outputText = template.render(glacier_id = glacier_id, 
                                 
                                 ids = glacier_ids_sorted,
                                 
                                 prev_id = prev_id,
                                 next_id = next_id,
                                 
                                 name = name,
                                 
                                 country = country,
                                 
                                 lower_elev = lower_elev,
                                 
                                 upper_elev = upper_elev,
                                 
                                 elev_year = elev_year, 
                                 
                                 glacier_length = glacier_length,
                                 length_year = length_year,
                                 
                                 mean_fv = mean_fv,
                                 min_fv_year = min_fv_year,
                                 max_fv_year = max_fv_year,
                                 fv_investigators = fv_investigator,
                                 
                                 mean_mb = mean_mb,
                                 min_mb_year = min_mb_year,
                                 max_mb_year = max_mb_year,
                                 mb_investigators = mb_investigator,
                                 
                                 min_area_year = min_area_year,
                                 max_area_year = max_area_year,
                                 max_area_year_change = max_area_year_change,
                                 final_area = final_area,
                                 initial_area = initial_area,
                                 
                                 photo_url = photo_url,
                                 photo_credit = photo_credit,
                                 photographer = photographer,
                                 photo_year = photo_year,
                                 
                                 outline_reference_max =  outline_reference_max,
                                 outline_reference_min =  outline_reference_min,
                                 
                                 # PLOTS   
                                 
                                 interactive_plot_cum_mb = cum_mb_html,
                                 
                                 glacier_outline = plot_outline_encoded,
                                 
                                 earth_sphere = plot_earth_sphere_encoded
                                 )
    
    # Save the rendered HTML to a file
    output_file_path = f"{glacier_id}.html"
    with open(output_file_path, "w") as file:
        file.write(outputText)
        
# =============================================================================
# output_from_template(90) # Gulkana
# =============================================================================

# =============================================================================
# output_from_template(94) # Wolverine
# =============================================================================

# =============================================================================
# output_from_template(76) # Columbia
# =============================================================================

# =============================================================================
# output_from_template(1367) # Easton
# =============================================================================

# =============================================================================
# output_from_template(3334) # Lemon Creek
# =============================================================================

#output_from_template(394) # Allalin

# =============================================================================
# output_from_template(753) # Golubin, KG
# 
# =============================================================================
# =============================================================================
# output_from_template(124) # Taku, US
# =============================================================================

# =============================================================================
# output_from_template(360) # Aletsch
# =============================================================================

# =============================================================================
# output_from_template(853) # Urumqi
# =============================================================================

# =============================================================================
# output_from_template(3987) # Parlung No. 94
# =============================================================================

# =============================================================================
# output_from_template(817) # Tuyuksu
# =============================================================================

# =============================================================================
# output_from_template(57) # Peyto, CA
# =============================================================================

# =============================================================================
# output_from_template(635) # Ghiacciaio del Careser, IT
# =============================================================================

# =============================================================================
# output_from_template(2921) # Chhota Shigri Glacier
# 
# =============================================================================
# =============================================================================
# output_from_template(35232) # Artesonraju, Peru
# =============================================================================

# =============================================================================
# output_from_template(26615) # Zongo, Bolivia
# =============================================================================

# =============================================================================
# output_from_template(4630) # Glacier de la Plaine Morte, CH
# =============================================================================

# =============================================================================
# output_from_template(2867) # Glacier d'Ossoue, FR
# =============================================================================

# =============================================================================
# output_from_template(566) # Pasterze, Austria
# =============================================================================


# =============================================================================
# for glacier_id in generated_glacier_ids:
#     output_from_template(glacier_id)
# =============================================================================
    

# =============================================================================
#     path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  # Adjust this if it's different
#     config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
#     
#     options = {
#     'enable-local-file-access': None,
#     'page-size': 'A4',
#     'orientation': 'Landscape'
#         }
#         
#     # Convert HTML to PDF
#     pdfkit.from_string(outputText, output_path="output.pdf", css=["template_glacier.css"],
#                        configuration = config, options = options)
# =============================================================================
    

# =============================================================================
# @app.route('/')
# def index():
#     return "Welcome to the Glacier Profiles Application!"
# 
# 
# @app.route('/output_<int:glacier_id>.html')
# def output_page(glacier_id):
#     # Assuming you have a function to check if the ID exists
#     if glacier_id in generated_glacier_ids:
#         return render_template('your_template.html', glacier_id=glacier_id)
#     else:
#         return "Glacier ID not found", 404
# 
# if __name__ == "__main__":
#     app.run(debug=False)
# =============================================================================


#%% Jinja rendering with also single index file output

generated_glacier_ids_short = [57, 76, 90, 94, 124]

def output_from_template_index(glacier_ids):
    
    global generated_glacier_ids
        
    glacier_index_data = [] # to store all glacier info to put onto the index file
        
    for idx, glacier_id in enumerate(glacier_ids):
        
    
        # NAME
        
        name, name_eng = get_glacier_name(glacier_id)
        
        # COUNTRIES
        
        country = get_glacier_country(glacier_id)
        
        # ELEVATION RANGE
        
        lower_elev, upper_elev, elev_year = get_glacier_elev_range(glacier_id)
        
        # LENGTH
        
        glacier_length, length_year = get_glacier_length(glacier_id)
        
        # CUMULATIVE FV
        
        mean_fv, min_fv_year, max_fv_year = get_annual_mean_fv(glacier_id)
        
        fv_investigator = get_fv_investigator(glacier_id)
        
        # ANNUAL MEAN MB
        
        min_mb_year, max_mb_year, mean_mb = get_annual_mean_mb(glacier_id)
        
        mb_investigator = get_mb_investigator(glacier_id)
        
        # AREA CHANGE
        
        min_area_year, max_area_year, max_area_year_change, initial_area, final_area= get_area_change(glacier_id)
        
        # PHOTO
        
        photo_url = get_glacier_photo(glacier_id)
        photo_credit, photographer, photo_year = get_photo_credit(glacier_id)
                
        # PLOTS
        
        # Interactive cumulative MB
        
        cum_mb_html = interactive_plot_cum_mb(glacier_id)
        
        # Outline
        
        #plot_outline(glacier_id, rgi_region)
        plot_all_outlines(glacier_id)
        
        # Outline references
        
        outline_reference_max, outline_reference_min = get_outline_reference(glacier_id)
        
        # Save the plot to a BytesIO object
        buffer_outline = BytesIO()
        plt.savefig(buffer_outline, format='png', bbox_inches = 'tight', dpi = 300)
        buffer_outline.seek(0)
        plot_outline_encoded = base64.b64encode(buffer_outline.getvalue()).decode()
        
        plt.close()
        
        # Earth sphere
        
        plot_earth_glacier(glacier_id)
        
        # Save the plot to a BytesIO object
        buffer_earth_sphere = BytesIO()
        plt.savefig(buffer_earth_sphere, format='png', bbox_inches = 'tight', dpi = 300)
        buffer_earth_sphere.seek(0)
        plot_earth_sphere_encoded = base64.b64encode(buffer_earth_sphere.getvalue()).decode()
        
        plt.close()
        
        # Add glacier ID to the list
        if glacier_id not in generated_glacier_ids:
            generated_glacier_ids.append(glacier_id)
        
        # Determine previous and next glacier IDs
        current_index = glacier_ids_sorted.index(glacier_id)
        
        # Calculate prev_id and next_id, handle edge cases for first and last indices
        prev_id = glacier_ids_sorted[current_index - 1] if current_index > 0 else glacier_ids_sorted[-1] # Loops back to the final one in the list
        next_id = glacier_ids_sorted[current_index + 1] if current_index < len(glacier_ids_sorted) - 1 else glacier_ids_sorted[0] # Goes back to the start of the list
        
        # Add glacier data to the dictionary for the index page
        glacier_index_data.append({
            "id": glacier_id,
            "name": name,
            "name_eng": name_eng,
            "country": country,
            "photo_url": photo_url,
        })
        
        # Load the Jinja template and render the HTML
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "template_glacier.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        
        # All data to render onto HTML file
        outputText = template.render(glacier_id = glacier_id, 
                                     
                                     ids = glacier_ids_sorted,
                                     
                                     prev_id = prev_id,
                                     next_id = next_id,
                                     
                                     name = name,
                                     
                                     country = country,
                                     
                                     lower_elev = lower_elev,
                                     
                                     upper_elev = upper_elev,
                                     
                                     elev_year = elev_year, 
                                     
                                     glacier_length = glacier_length,
                                     length_year = length_year,
                                     
                                     mean_fv = mean_fv,
                                     min_fv_year = min_fv_year,
                                     max_fv_year = max_fv_year,
                                     fv_investigators = fv_investigator,
                                     
                                     mean_mb = mean_mb,
                                     min_mb_year = min_mb_year,
                                     max_mb_year = max_mb_year,
                                     mb_investigators = mb_investigator,
                                     
                                     min_area_year = min_area_year,
                                     max_area_year = max_area_year,
                                     max_area_year_change = max_area_year_change,
                                     final_area = final_area,
                                     initial_area = initial_area,
                                     
                                     photo_url = photo_url,
                                     photo_credit = photo_credit,
                                     photographer = photographer,
                                     photo_year = photo_year,
                                     
                                     outline_reference_max =  outline_reference_max,
                                     outline_reference_min =  outline_reference_min,
                                     
                                     # PLOTS   
                                     
                                     interactive_plot_cum_mb = cum_mb_html,
                                     
                                     glacier_outline = plot_outline_encoded,
                                     
                                     earth_sphere = plot_earth_sphere_encoded
                                     )
        
        # Save the rendered HTML to a file
        output_file_path = f"{glacier_id}.html"
        with open(output_file_path, "w") as file:
            file.write(outputText)
                        
    # Render the second HTML file
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    index_template_file = "template_index.html"  # Example second template
    index_template = templateEnv.get_template(index_template_file)
    
    # All data to render onto HTML file
    outputTextIndex = index_template.render(glacier_data = glacier_index_data)
    
    # Save the second HTML file
    index_output_file = "index.html"
    with open(index_output_file, "w") as file:
        file.write(outputTextIndex)
        
output_from_template_index(generated_glacier_ids)

#output_from_template_index(glacier_ids_complete_sorted)

