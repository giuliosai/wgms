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
import cartopy.crs as ccrs
import plotly.graph_objects as go
import plotly.io as pio
import contextily as ctx
from PIL import Image
from matplotlib.patches import Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
import os
from datetime import datetime

# Enable matplotlib interactive mode to prevent plots from blocking the script
plt.ion()

# Relative file paths to repository (make sure to set working directory to repository GlacierProfiles folder!!)

data_dir = "data"

glacier_path = os.path.join(data_dir, "glacier.csv")
glacier_name_path = os.path.join(data_dir, "glacier_name.csv")
glacier_photo_path = os.path.join(data_dir, "glacier_photo.csv")
glacier_country_path = os.path.join(data_dir, "glacier_country.csv")
country_codes_path = os.path.join(data_dir, "country_codes.csv")
mb_path = os.path.join(data_dir, "mass_balance.csv")
fv_path = os.path.join(data_dir, "front_variation.csv")
team_member_path = os.path.join(data_dir, "team_member.csv")
state_path = os.path.join(data_dir, "state.csv")
wgms_outlines_path = os.path.join(data_dir, "wgms_outlines.shp")
glacier_outline_all_path = os.path.join(data_dir, "glacier_outline_all.csv")
bibliography_path = os.path.join(data_dir, "bibliography.csv")

glaciers_df = pd.read_csv(glacier_path, dtype = {'POLITICAL_UNIT': str}, low_memory = False)
glacier_names = pd.read_csv(glacier_name_path)
glacier_photos = pd.read_csv(glacier_photo_path)
glacier_country = pd.read_csv(glacier_country_path)
country_codes = pd.read_csv(country_codes_path)
mb_df_dbgate = pd.read_csv(mb_path)
fv_df_db = pd.read_csv(fv_path)
team_members = pd.read_csv(team_member_path)
wgms_outlines = gpd.read_file(wgms_outlines_path)
glacier_id_outline = pd.read_csv(glacier_outline_all_path)
state_df = pd.read_csv(state_path)
bibliography = pd.read_csv(bibliography_path)

#%% functions

# Get glacier name

def get_glacier_name(glacier_id):

    glacier_df = glacier_names[glacier_names['glacier_id'] == glacier_id]

    # Check if there are any preferred names in which case only take those
    if glacier_df['preferred'].any():

        glacier_df = glacier_df[glacier_df['preferred'] == True]

    glacier_name = glacier_df['name']

    if len(glacier_name) > 3:  # Too many names, limit to 3

        names_list = glacier_name.astype(str).iloc[:3].tolist()
        full_name = ' · '.join(names_list)

    elif len(glacier_name) > 1:

        names_list = glacier_name.astype(str).tolist()
        full_name = ' · '.join(names_list)

    else:
        full_name = glacier_name.astype(str).iloc[0]

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

test_name = get_glacier_name(817)


# Get glacier country

def get_glacier_country(glacier_id):

    glacier_country_code = glacier_country[glacier_country['glacier_id'] == glacier_id]['country_id'].values[0]

    glacier_country_name = country_codes[country_codes['id'] == glacier_country_code]['name'].values[0]

    return glacier_country_name

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

    glacier_length = '—'
    max_year = '—'

    if not glacier_state.empty:

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

    lower_elev = "—"
    upper_elev = "—"
    year = "—"

    if not glacier_state.empty:
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


def get_investigators(glacier_id):

    # From FV

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

        fv_investigators = ''


    # From MB

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

        mb_investigators = ''

    # Combine all of them

    if fv_investigators == '' and mb_investigators != '': # when there is only MB investigators

        mb_investigators_list = mb_investigators.split(', ')

        investigators_unique = mb_investigators_list

    elif mb_investigators == '' and fv_investigators != '': # when there is only FV investigators

        fv_investigators_list = fv_investigators.split(', ')

        investigators_unique = fv_investigators_list

    else: # When both are available
        fv_investigators_list = fv_investigators.split(', ')
        mb_investigators_list = mb_investigators.split(', ')

        investigators_unique = set(fv_investigators_list) | set(mb_investigators_list)

    if len(investigators_unique) > 0:

        investigators = ', '.join(sorted(investigators_unique))

    else:

        investigators = 'not reported'

    return investigators

#get_investigators(218)


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

        initial_area = glacier_state.loc[min_year_index, 'AREA']
        final_area = glacier_state.loc[max_year_index, 'AREA']

        if initial_area < 0.1:
            initial_area = round(initial_area, 2)

        else:
            initial_area = round(initial_area, 1)

        if final_area < 0.1:
            final_area = round(final_area, 2)

        else:
            final_area = round(final_area, 1)

        if initial_area - final_area == 0: # if there is only one area entry

            initial_area = round(initial_area, 1)
            final_area = "—"
            max_year = "—"

    return [min_year, max_year, max_year_change, initial_area, final_area]

#min_year, max_year, max_year_change, initial_area_Test, final_area_Test = get_area_change(897)

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

# Plot

def interactive_plot_cum_mb(glacier_id):

    # Filter the DataFrame for the specific glacier ID
    mb_df_glacier = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id]

    # Drop any rows with NaN for MB
    mb_df_glacier = mb_df_glacier.dropna(subset=['annual_balance'])

    # Create an interactive plot with Plotly even if it is empty
    fig = go.Figure()

    fig.update_layout(

        title=dict(
            text="Cumulative mass balance (m w.e.)",
            x=0.5,
            xanchor='center',
            font=dict(size=20, family = "Arial", color = 'black')
                ),
        width = 600,
        height = 300,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white')

    if mb_df_glacier.empty:
        print(f"No MB data available for glacier_id: {glacier_id}")
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    if not mb_df_glacier.empty:

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
        max_cum_mb = cum_mb_glacier.max()

        if min_cum_mb < 1:
            min_cum_mb = round(min_cum_mb, 2)
        else:
            min_cum_mb = int(min_cum_mb)

        if max_cum_mb < 1:
            max_cum_mb = round(max_cum_mb, 2)
        else:
            max_cum_mb = int(max_cum_mb)

        # To detect if glacier is retreating or advancing
        if max_year != min_year: # only do this if the years differ
            change_mb = (abs(max_cum_mb) - abs(min_cum_mb)) / (max_year - min_year)

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

        # Account for cases with only one MB measurement

        if len(years) == 1:

            fig.update_layout(

                title=dict(
                    text="Cumulative mass balance (m w.e.)",
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
                    tickvals=[med_year],
                    ticktext=[str(med_year)],
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
                    ticktext=[str(min_cum_mb), 0],
                    tickfont=dict(size=20,  family = "Arial", color = 'black'),
                    tickformat=',',
                    showline=True,
                    linecolor='black',
                    linewidth = 2
                    #minor=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.2)
                )

            )

        elif change_mb < 0:

            # layout for retreating glaciers
            fig.update_layout(

                title=dict(
                    text="Cumulative mass balance (m w.e.)",
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
                    ticktext=[str(min_cum_mb), 0],
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
                    text="Cumulative mass balance (m w.e.)",
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
                    ticktext = [0, str(max_cum_mb) ],
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

#interactive_plot_cum_mb(1673)

def plot_cum_mb(glacier_id):
    # Filter the DataFrame for the specific glacier ID
    mb_df_glacier = mb_df_dbgate[mb_df_dbgate['glacier_id'] == glacier_id]

    # Drop any rows with NaN for MB
    mb_df_glacier = mb_df_glacier.dropna(subset=['annual_balance'])

    if mb_df_glacier.empty:
        print(f"No MB data available for glacier_id: {glacier_id}")
        return None  # No plot if data is empty

    # Insert missing years as NaN for MB to break the line
    full_years = pd.Series(range(mb_df_glacier['year'].min(), mb_df_glacier['year'].max() + 1))

    # Set index to years to merge with the full_years
    mb_df_glacier.set_index('year', inplace=True)

    # Reindex with full years and insert NaNs where necessary
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
    max_cum_mb = cum_mb_glacier.max()

    if abs(min_cum_mb) < 1:
        min_cum_mb = round(min_cum_mb, 2)
    else:
        min_cum_mb = int(min_cum_mb)

    if abs(max_cum_mb) < 1:
        max_cum_mb = round(max_cum_mb, 2)
    else:
        max_cum_mb = int(max_cum_mb)

    # To detect if glacier is retreating or advancing
    if max_year != min_year:  # only do this if the years differ
        change_mb = (abs(max_cum_mb) - abs(min_cum_mb)) / (max_year - min_year)

    # Create the Matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(7, 3))

    # Plot the cumulative mass balance as a line plot
    ax.plot(years, cum_mb_glacier, color='black', label='Cumulative MB')

    # Plot scatter points on top of the line
    ax.scatter(years, cum_mb_glacier, color='black', s=10, zorder=5)

    # Add horizontal line at y=0
    ax.axhline(0, color='gray', linewidth=1)

    # Set the x and y axis labels
    ax.set_xlabel("Year", fontsize=14, family="Arial")

    # Consider when there is only one MB data point

    if len(years) == 1:

        ax.set_yticks([min_cum_mb, 0])
        ax.set_yticklabels([str(min_cum_mb), "0"], fontsize=14, family="Arial")

        ax.set_xticks([med_year])
        ax.set_xticklabels([str(med_year)], fontsize=14, family="Arial")


    # Consider shrinking vs growning glaciers

    elif change_mb < 0:

        # Set y-axis ticks
        ax.set_yticks([min_cum_mb, 0])
        ax.set_yticklabels([str(min_cum_mb), "0"], fontsize=14, family="Arial")

        ax.set_xticks([min_year, med_year, max_year])
        ax.set_xticklabels([str(min_year), str(med_year), str(max_year)], fontsize=14, family="Arial")

    else:

        # Set y-axis ticks
        ax.set_yticks([0, max_cum_mb])
        ax.set_yticklabels(["0", str(max_cum_mb)], fontsize=14, family="Arial")

        ax.set_xticks([min_year, med_year, max_year])
        ax.set_xticklabels([str(min_year), str(med_year), str(max_year)], fontsize=14, family="Arial")

    ax.set_xlim(min_year - 1, max_year + 1)

    # Remove plot outlines
    ax.spines[['right', 'top']].set_visible(False)

    # Add a title
    ax.set_title("Cumulative mass balance (m w.e.)", fontsize=16, family="Arial", color="black")

    # Adjust margins for aesthetics
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # Show the plot
    plt.show()

#plot_cum_mb(124)
#%% Plot 3D Earth sphere

def plot_earth_glacier(glacier_id):

    def plot_earth_with_texture(ax):
        # Load the Earth texture image
        img = Image.open(os.path.join(data_dir, 'land_shallow_topo_2048.jpg'))
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

# Order by country alphabetical order
glacier_ids_complete_sorted = sorted(common_ids, key=get_glacier_country)

# Remove some special troublesome glaciers

glacier_ids_complete_sorted.remove(1673) # For MB it only has years and not actual MB data

glacier_ids_complete_sorted.remove(322) # Remove Hansebreen with broken photo url

glacier_ids_complete_sorted.remove(1314) # Remove Glacier de Tre-la-Tete for rotated photo

glacier_ids_complete_sorted.remove(897) # Remove Japan glacier which has disappeared and was too small to be considered a glacier in the first place

#%% Render a glacier profile

def output_from_template(glacier_id):

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


    # ANNUAL MEAN MB

    min_mb_year, max_mb_year, mean_mb = get_annual_mean_mb(glacier_id)


    # INVESTIGATORS

    investigators = get_investigators(glacier_id)


    # AREA CHANGE

    min_area_year, max_area_year, max_area_year_change, initial_area, final_area= get_area_change(glacier_id)

    # PHOTO

    photo_url = get_glacier_photo(glacier_id)
    photo_credit, photographer, photo_year = get_photo_credit(glacier_id)

    # PLOTS

    # cumulative MB

    plot_cum_mb(glacier_id)

    # Save the plot to a BytesIO object
    mb_plot = BytesIO()
    plt.savefig(mb_plot, format='png', bbox_inches = 'tight', dpi = 300)
    mb_plot.seek(0)
    mb_plot_encoded = base64.b64encode(mb_plot.getvalue()).decode()

    plt.close()

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

    # Determine previous and next glacier IDs
    current_index = glacier_ids_complete_sorted.index(glacier_id)

    # Calculate prev_id and next_id, handle edge cases for first and last indices
    prev_id = glacier_ids_complete_sorted[current_index - 1] if current_index > 0 else glacier_ids_complete_sorted[-1] # Loops back to the final one in the list
    next_id = glacier_ids_complete_sorted[current_index + 1] if current_index < len(glacier_ids_complete_sorted) - 1 else glacier_ids_complete_sorted[0] # Goes back to the start of the list

    # Load the Jinja template and render the HTML
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template_glacier.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    # All data to render onto HTML file
    outputText = template.render(glacier_id = glacier_id,

                                 ids = glacier_ids_complete_sorted,

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

                                 mean_mb = mean_mb,
                                 min_mb_year = min_mb_year,
                                 max_mb_year = max_mb_year,

                                 investigators = investigators,

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

                                 plot_cum_mb = mb_plot_encoded,

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
# output_from_template(1107)
# =============================================================================

# =============================================================================
# # Output multiple glacier profiles
#
# for glacier_id in generated_glacier_ids:
#     output_from_template(glacier_id)
# =============================================================================

#%% Render both a glacier profile and the index home page

def generate_glacier_profiles(glacier_ids):

    glacier_index_data = []  # Store glacier info for index

    for idx, glacier_id in enumerate(glacier_ids):
        print("Glacier ID:", glacier_id)

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
        # ANNUAL MEAN MB
        min_mb_year, max_mb_year, mean_mb = get_annual_mean_mb(glacier_id)

        # INVESTIGATORS

        investigators = get_investigators(glacier_id)

        # AREA CHANGE
        min_area_year, max_area_year, max_area_year_change, initial_area, final_area = get_area_change(glacier_id)

        # PHOTO
        photo_url = get_glacier_photo(glacier_id)
        photo_credit, photographer, photo_year = get_photo_credit(glacier_id)

        # PLOTS
        #cum_mb_html = interactive_plot_cum_mb(glacier_id)

        # cumulative MB

        plot_cum_mb(glacier_id)

        # Save the plot to a BytesIO object
        mb_plot = BytesIO()
        plt.savefig(mb_plot, format='png', bbox_inches = 'tight', dpi = 300)
        mb_plot.seek(0)
        mb_plot_encoded = base64.b64encode(mb_plot.getvalue()).decode()

        plt.close()

        plot_all_outlines(glacier_id)

        outline_reference_max, outline_reference_min = get_outline_reference(glacier_id)

        buffer_outline = BytesIO()
        plt.savefig(buffer_outline, format='png', bbox_inches='tight', dpi=300)
        buffer_outline.seek(0)
        plot_outline_encoded = base64.b64encode(buffer_outline.getvalue()).decode()
        plt.close()

        plot_earth_glacier(glacier_id)
        buffer_earth_sphere = BytesIO()
        plt.savefig(buffer_earth_sphere, format='png', bbox_inches='tight', dpi=300)
        buffer_earth_sphere.seek(0)
        plot_earth_sphere_encoded = base64.b64encode(buffer_earth_sphere.getvalue()).decode()
        plt.close()

        current_index = glacier_ids.index(glacier_id)
        prev_id = glacier_ids[current_index - 1] if current_index > 0 else glacier_ids[-1]
        next_id = glacier_ids[current_index + 1] if current_index < len(glacier_ids) - 1 else glacier_ids[0]

        glacier_index_data.append({
            "id": glacier_id,
            "name": name,
            "name_eng": name_eng,
            "country": country,
            "photo_url": photo_url,
        })

        # Load and render individual glacier template
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "template_glacier.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        outputText = template.render(
            glacier_id=glacier_id,
            ids=glacier_ids,
            prev_id=prev_id,
            next_id=next_id,
            name=name,
            country=country,
            lower_elev=lower_elev,
            upper_elev=upper_elev,
            elev_year=elev_year,
            glacier_length=glacier_length,
            length_year=length_year,
            mean_fv=mean_fv,
            min_fv_year=min_fv_year,
            max_fv_year=max_fv_year,
            mean_mb=mean_mb,
            min_mb_year=min_mb_year,
            max_mb_year=max_mb_year,
            investigators = investigators,
            min_area_year=min_area_year,
            max_area_year=max_area_year,
            max_area_year_change=max_area_year_change,
            final_area=final_area,
            initial_area=initial_area,
            photo_url=photo_url,
            photo_credit=photo_credit,
            photographer=photographer,
            photo_year=photo_year,
            outline_reference_max=outline_reference_max,
            outline_reference_min=outline_reference_min,
            plot_cum_mb = mb_plot_encoded,
            glacier_outline=plot_outline_encoded,
            earth_sphere=plot_earth_sphere_encoded,
        )

        output_file_path = f"{glacier_id}.html"
        with open(output_file_path, "w") as file:
            file.write(outputText)

    return glacier_index_data


# Generate index

def generate_glacier_index(glacier_index_data):
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    index_template_file = "template_index.html"
    index_template = templateEnv.get_template(index_template_file)

    outputTextIndex = index_template.render(glacier_data=glacier_index_data)

    index_output_file = "index.html"
    with open(index_output_file, "w") as file:
        file.write(outputTextIndex)


# Create glacier profiles and store the glacier index data
glacier_index_vars = generate_glacier_profiles(glacier_ids_complete_sorted)

# Create the glacier index
generate_glacier_index(glacier_index_vars)
