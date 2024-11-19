#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 10:12:21 2023

@author: giuliosaibene
"""

# =============================================================================
# CONTRY PROFILES WGMS 2023
# 
# Plotting the time series of number of observations for each variable and
# subplot with temporal grid plot
# =============================================================================

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#import geopandas as gpd
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import matplotlib.colors as mcolors


#%% COMBINING BAR TIME SERIES WITH GRID PLOT FOR FV

# expand dates function to account for the fact that FV and TC measurements can span over many years,
# so need to count all years as individual "observations" to plot

def expand_dates(df):
    
    if 'REFERENCE_DATE' in df.columns:
    
        df.dropna(subset=['REFERENCE_DATE'], inplace=True) # removes rows when the reference date is missing
        
        # Remove date and month to only get start and end year of when measurement came from
        df['START_YEAR'] = df['REFERENCE_DATE'].astype('int64') // 10000
        df['END_YEAR'] = df['SURVEY_DATE'].astype('int64') // 10000
    
    else: # as the column names are different for the 2015 reconstructed dataframe
    
        df.dropna(subset=['REFERENCE_YEAR'], inplace=True)  # removes rows when the reference year is missing
    
        # Remove date and month to only get start and end year of when measurement came from

        df['START_YEAR'] = df['REFERENCE_YEAR'].astype('int64') // 10000
        df['END_YEAR'] = df['YEAR'].astype('int64') // 10000
        
        
    # Create a list of years between START_YEAR and END_YEAR
    def get_years(row):
        return list(range(row['START_YEAR'], row['END_YEAR'] + 1))
    
    # Check if 'START_YEAR' column has any data
    if len(df['START_YEAR']) > 0:
        
        # Apply the function to create a new column 'YEARS_ALL' which is a list of all years embedded within one row
        df['YEARS_ALL'] = df.apply(get_years, axis=1)
    
        # Explode such that there is a row for each year
        df_long = df.explode('YEARS_ALL')
        
    else:
        # Handle case where 'START_YEAR' column has no data
        df_long = df
        df_long['YEARS_ALL'] = ''
    
    return(df_long)

# combine FV table with Reconstructed FV table

# need to only merge rows with a unique combination of WGMS_ID and YEAR (will be in YEARS_ALL column)

def merge_fv_tables(df_measured, df_reconstructed):
    
    # Expand dates on just the measured dataframe, the reconstructed one doesn't have date ranges
    
    df_measured = expand_dates(df_measured)
    
    df_reconstructed["YEARS_ALL"] = df_reconstructed["YEAR"]

    merged_df = pd.merge(df_measured, df_reconstructed, on=['WGMS_ID', 'YEARS_ALL'], how='left', suffixes=('', '_right')) 
    
    # Filter rows where there is no match in the right dataframe
    complete_fv = merged_df[merged_df['POLITICAL_UNIT_right'].isnull()]

    # Drop the unnecessary columns from the result
    complete_fv = complete_fv.drop(['POLITICAL_UNIT_right'], axis=1)
    
    return(complete_fv)

# FV plot

def plot_bar_grid_fv(df, df_reconstructed, df_2015v, df_reconstructed_2015v, country_code):
    
    df = merge_fv_tables(df, df_reconstructed) # merge function already expands the dates
    
    df_2015v = merge_fv_tables(df_2015v, df_reconstructed_2015v)
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    df_country_15v = df_2015v[df_2015v['POLITICAL_UNIT'] == country_code]

    #Extracting variables
    year = df_country["YEARS_ALL"]
    unique_year = year.drop_duplicates()

    year_15v = df_country_15v["YEARS_ALL"]
    unique_year_15v = year_15v.drop_duplicates()

    # Handle cases when there is no data
    if len(unique_year) == 0:
        first_year = np.nan
        last_year = np.nan
    else:
        first_year = min(unique_year)
        last_year = max(unique_year)

    # For each year I want to get the number of observations
    
    obs_each_year = []

    obs_each_year_15v = []

    for year in unique_year:
        
        # Subset df such that only series for given year is selected
        df_year = df_country[df_country['YEARS_ALL'] == year]
        
        # Drop duplicates of WGMS_ID
        
        df_year = df_year.drop_duplicates(subset='WGMS_ID', keep='first')
        
        obs_each_year.append(len(df_year)) # inclusive
        
    for year_15v in unique_year_15v:
         
        # Subset df such that only series for given year is selected
        df_year_15v = df_country_15v[df_country_15v['YEARS_ALL'] == year_15v]
        
        # Drop duplicate glaciers in a given year
        
        df_year_15v = df_year_15v.drop_duplicates(subset='WGMS_ID', keep='first')
         
        obs_each_year_15v.append(len(df_year_15v)) # inclusive

    # Sorting such that plot goes from oldest to most recent series
    df_oldest_yr = df_country.groupby('WGMS_ID')['YEARS_ALL'].min().reset_index()
    sorted_wgms_order = df_oldest_yr.sort_values(by='YEARS_ALL', ascending=False)['WGMS_ID']
    df_country['WGMS_ID'] = pd.Categorical(df_country['WGMS_ID'], categories=sorted_wgms_order, ordered=True)

    # Create a dataframe that counts the occurrences when the WGMS_ID and YEAR match to use to build the pivot table
    count_df = df_country.groupby(['WGMS_ID', 'YEARS_ALL']).size().reset_index(name='count')

    # Create a pivot table to represent the grid
    pivot_df_country = count_df.pivot(index='WGMS_ID', columns='YEARS_ALL', values='count').fillna(0)

    # Re-add all the years even if they don't have any counts
    all_years = range(1900, 2023 + 1)
    pivot_df_country = pivot_df_country.reindex(columns=all_years, fill_value=0)

    # Create a mask for cells with measurements
    mask = pivot_df_country > 0

    ## Reapeat for 2015 version

    # Sorting such that plot goes from oldest to most recent series
    df_oldest_yr_15 = df_country_15v.groupby('WGMS_ID')['YEARS_ALL'].min().reset_index() # fnid oldest year per WGMS_ID
    sorted_wgms_order_15 = df_oldest_yr_15.sort_values(by='YEARS_ALL', ascending=False)['WGMS_ID']
    df_country_15v['WGMS_ID'] = pd.Categorical( df_country_15v['WGMS_ID'], categories = sorted_wgms_order_15, ordered=True)

    # Create a dataframe that counts the occurrences when the WGMS_ID and YEAR match to use to build the pivot table
    count_df_15 = df_country_15v.groupby(['WGMS_ID', 'YEARS_ALL']).size().reset_index(name='count')

    # Create a pivot table to represent the grid
    pivot_df_country_15 = count_df_15.pivot(index='WGMS_ID', columns='YEARS_ALL', values='count').fillna(0)

    # Re-add all the years even if they don't have any counts
    pivot_df_country_15 = pivot_df_country_15.reindex(columns=all_years, fill_value=0)

    # Mergin two pivot tables such that the 2015 contains the same number of series as 2023
    pivot_df_country_15_extended = pd.merge(pivot_df_country_15, pivot_df_country, how='right', left_index=True, right_index=True,
                                            suffixes=('', '_y'))
    pivot_df_country_15_columns = pivot_df_country_15.columns.astype(str)
    pivot_df_country_15_extended = pivot_df_country_15_extended[list(pivot_df_country_15_columns)] # merging doubles the number of columns

    # Two pivot tables should match in columns
    additional_columns = pivot_df_country.columns.difference(pivot_df_country_15.columns)

    for col in additional_columns:
        pivot_df_country_15_extended[col] = pd.Series(dtype=pivot_df_country[col].dtype) # adding missing years (2015-2022)
        
    pivot_df_country_15_extended.columns = pd.to_numeric(pivot_df_country_15_extended.columns, errors='coerce') # convert column names to integers
    pivot_df_country_15_extended = pivot_df_country_15_extended.reindex(sorted(pivot_df_country_15_extended.columns), axis=1)

    # Create a mask for cells with measurements
    mask_15 = pivot_df_country_15_extended > 0

    if pivot_df_country_15_extended.empty:
        mask_15 = np.zeros((len(unique_year), len(pivot_df_country_15_extended.columns)))

    
    # PLOTTING
    
    if len(unique_year) != 0:

        fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 2))
    
        axs[0].bar(unique_year, obs_each_year, color = "#e36d26", label = "2024", width = 1)
        
        # Handle cases when there is no 2015 data:
        if len(obs_each_year_15v) > 0:
            axs[0].bar(unique_year_15v, obs_each_year_15v, color = "#919191", label = "2015", width = 1)
        
        else:
            pass
        
        axs[0].legend(loc = 'upper left', bbox_to_anchor = (0, 1.2), ncol = 2, framealpha = 0.3)
        
        # Axes formatting
        axs[0].set_xlim(1900, 2025)
        axs[0].tick_params(axis = 'x', labelsize = 10)
        #axs[0].tick_params(axis='x', length=0, labelbottom = False)
        #axs[0].set_xticks([])
        axs[0].tick_params(axis = 'y', labelrotation = 90)
        #axs[0].set_ylabel("No. of obs.", size = 12)
        axs[0].yaxis.set_minor_locator(MultipleLocator(10))
        
        # Grid
        axs[0].grid(alpha = 0.7)
        axs[0].minorticks_on()
        axs[0].grid(which = 'minor', axis='x', alpha = 0.4)
        axs[0].set_axisbelow(True)
    
        cmap_15 = mcolors.LinearSegmentedColormap.from_list('white_to_gray', [(1, 1, 1, 0), (0.5, 0.5, 0.5)], N=256)
    
        color_points = [(1, 1, 1, 0), (0.890196, 0.427451, 0.14902, 1)]
        cmap = mcolors.LinearSegmentedColormap.from_list('white_to_orange', color_points, N=256) # for 2023
    
        axs[1].imshow(mask_15, cmap = cmap_15, extent=[1900 - 0.5, pivot_df_country.columns[-1] + 0.5, sorted_wgms_order.iloc[-1], sorted_wgms_order.iloc[0]],
                   aspect = 'auto', zorder = 1)
    
        axs[1].imshow(mask, cmap = cmap, extent=[1900 - 0.5, pivot_df_country.columns[-1] + 0.5, sorted_wgms_order.iloc[-1], sorted_wgms_order.iloc[0]],
                  aspect = 'auto', zorder = 0)
    
        #axs[1].set_ylabel('Glacier \n series', size = 12)
        
        # Axes formatting
        axs[1].set_yticks([])
        axs[1].set_xlim(1900, 2025)
        axs[1].tick_params(axis = 'x', labelsize = 10)
        
        # Grid
        axs[1].grid(axis='x', alpha = 0.7)
        axs[1].minorticks_on()
        axs[1].grid(which = 'minor', axis='x', alpha = 0.4)
        axs[1].set_axisbelow(True)
    
        # extract y_min and y_max to set text box position
        y_min, y_max = axs[1].get_ylim()
    
        axs[1].text(
            1901,  # x-coordinate
            y_min + 0.95 * (y_max - y_min),  # y-coordinate
            f'First obs. year: {first_year}\nLast obs. year: {last_year}',
            fontsize=10,
            linespacing = 1.5,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)  # Optional: Add a box around the text
        )
            
        plt.subplots_adjust(hspace=0.5) 
    
        plt.show()
    
    # Cases when there is no data = make empty plot
    else:
        
        fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 2))
        
        axs[0].set_xlim(1900, 2025)
        axs[0].grid(alpha = 0.7)
        axs[0].minorticks_on()
        axs[0].grid(which = 'minor', axis='x', alpha = 0.4)
        
        axs[1].set_xlim(1900, 2025)
        axs[1].grid(axis='x', alpha = 0.7)
        axs[1].minorticks_on()
        axs[1].grid(which = 'minor', axis='x', alpha = 0.4)
        
        plt.subplots_adjust(hspace=0.5) 
        plt.show()
    
#plot_bar_grid_fv(fronts_df, fv_reco_df, fronts_df_2015v_merge, fv_reco_df_2015v, "VE")

#%% COMBINING BAR TIME SERIES WITH GRID PLOT FOR MB

def plot_bar_grid_mb(df, df_2015v, country_code):
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    df_country_15v = df_2015v[df_2015v['POLITICAL_UNIT'] == country_code]

    #Extracting variables - get a list of years that span the record
    year = df_country["YEAR"]
    unique_year = year.drop_duplicates()

    year_15v = df_country_15v["YEAR"]
    unique_year_15v = year_15v.drop_duplicates()

    # Handle cases when there is no data
    if len(unique_year) == 0:
        first_year = np.nan
        last_year = np.nan
    else:
        first_year = min(unique_year)
        last_year = max(unique_year)

    # For each year I want to get the number of observations
    obs_each_year = []

    obs_each_year_15v = []

    for year in unique_year:
        
        # Subset df such that only series for given year is selected
        df_year = df_country[df_country['YEAR'] == year]
        
        obs_each_year.append(len(df_year)) # inclusive
        
    for year_15v in unique_year_15v:
         
        # Subset df such that only series for given year is selected
        df_year_15v = df_country_15v[df_country_15v['YEAR'] == year_15v]
         
        obs_each_year_15v.append(len(df_year_15v)) # inclusive
        
        
    ## GRID PLOT

    # Sorting such that plot goes from oldest to most recent series
    df_oldest_yr = df_country.groupby('WGMS_ID')['YEAR'].min().reset_index() # fnid oldest year per WGMS_ID
    sorted_wgms_order = df_oldest_yr.sort_values(by='YEAR', ascending=False)['WGMS_ID']
    df_country['WGMS_ID'] = pd.Categorical( df_country['WGMS_ID'], categories = sorted_wgms_order, ordered=True)

    # Create a dataframe that counts the occurrences when the WGMS_ID and YEAR match to use to build the pivot table
    count_df = df_country.groupby(['WGMS_ID', 'YEAR']).size().reset_index(name='count')

    # Create a pivot table to represent the grid
    pivot_df_country = count_df.pivot(index='WGMS_ID', columns='YEAR', values='count').fillna(0)

    # Re-add all the years even if they don't have any counts
    all_years = range(1900, 2023 + 1)
    pivot_df_country = pivot_df_country.reindex(columns=all_years, fill_value=0)

    # Create a mask for cells with measurements
    mask = pivot_df_country > 0

    ## Reapeat for 2015 version

    # Sorting such that plot goes from oldest to most recent series
    df_oldest_yr_15 = df_country_15v.groupby('WGMS_ID')['YEAR'].min().reset_index() # fnid oldest year per WGMS_ID
    sorted_wgms_order_15 = df_oldest_yr_15.sort_values(by='YEAR', ascending=False)['WGMS_ID']
    df_country_15v['WGMS_ID'] = pd.Categorical( df_country_15v['WGMS_ID'], categories = sorted_wgms_order_15, ordered=True)

    # Create a dataframe that counts the occurrences when the WGMS_ID and YEAR match to use to build the pivot table
    count_df_15 = df_country_15v.groupby(['WGMS_ID', 'YEAR']).size().reset_index(name='count')

    # Create a pivot table to represent the grid
    pivot_df_country_15 = count_df_15.pivot(index='WGMS_ID', columns='YEAR', values='count').fillna(0)

    # Re-add all the years even if they don't have any counts
    pivot_df_country_15 = pivot_df_country_15.reindex(columns=all_years, fill_value=0)

    # Mergin two pivot tables such that the 2015 contains the same number of series as 2023
    pivot_df_country_15_extended = pd.merge(pivot_df_country_15, pivot_df_country, how='right', left_index=True, right_index=True,
                                            suffixes=('', '_y'))
    pivot_df_country_15_columns = pivot_df_country_15.columns.astype(str)
    pivot_df_country_15_extended = pivot_df_country_15_extended[list(pivot_df_country_15_columns)] # merging doubles the number of columns

    # Two pivot tables should match in columns
    additional_columns = pivot_df_country.columns.difference(pivot_df_country_15.columns)

    for col in additional_columns:
        pivot_df_country_15_extended[col] = pd.Series(dtype=pivot_df_country[col].dtype) # adding missing years (2015-2022)
        
    pivot_df_country_15_extended = pivot_df_country_15_extended[sorted(pivot_df_country_15_extended.columns, key=lambda x: int(x))]

    # Create a mask for cells with measurements
    mask_15 = pivot_df_country_15_extended > 0

    # PLOTTING
    
    if len(unique_year) != 0:

        fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 2))
    
        axs[0].bar(unique_year, obs_each_year, color = "#e36d26", label = "2024", width = 1)
        
        # Handle cases when there is no 2015 data:
        if len(obs_each_year_15v) > 0:
            axs[0].bar(unique_year_15v, obs_each_year_15v, color = "#919191", label = "2015", width = 1)
        
        else:
            pass
        
        axs[0].legend(loc = 'upper left', ncol = 2, framealpha = 0.3)
        
        axs[0].set_xlim(1900, 2025)
        axs[0].tick_params(axis = 'x', labelsize = 10)
        axs[0].tick_params(axis = 'y', labelrotation = 90)
        
        axs[0].yaxis.set_minor_locator(MultipleLocator(1))
        #axs[0].set_ylabel("No. of obs.", size = 12)
        
        axs[0].grid(alpha = 0.7)
        axs[0].minorticks_on()
        axs[0].grid(which = 'minor', axis='x', alpha = 0.4)
        axs[0].set_axisbelow(True)
    
        cmap_15 = mcolors.LinearSegmentedColormap.from_list('white_to_gray', [(1, 1, 1, 0), (0.5, 0.5, 0.5, 1 )], N=256) # for 2015, last of four numbers represents alpha
    
        color_points = [(1, 1, 1, 0), (0.890196, 0.427451, 0.14902, 1)]
        cmap = mcolors.LinearSegmentedColormap.from_list('white_to_orange', color_points, N=256) # for 2023
    
        axs[1].imshow(mask_15, cmap = cmap_15, extent=[1900 - 0.5, pivot_df_country.columns[-1] + 0.5, sorted_wgms_order.iloc[-1], sorted_wgms_order.iloc[0]],
                   aspect = 'auto', zorder = 1)
    
        axs[1].imshow(mask, cmap = cmap, extent=[1900 - 0.5, pivot_df_country.columns[-1] + 0.5, sorted_wgms_order.iloc[-1], sorted_wgms_order.iloc[0]],
                  aspect = 'auto', zorder = 0)
    
        #axs[1].set_ylabel('Glacier \n series', size = 12)
        axs[1].set_yticks([])
        
        axs[1].set_xlim(1900, 2025)
        axs[1].tick_params(axis = 'x', labelsize = 10)
        
        axs[1].grid(axis='x', alpha = 0.7)
        axs[1].minorticks_on()
        axs[1].grid(which = 'minor', axis='x', alpha = 0.4)
        axs[1].set_axisbelow(True)
    
        # extract y_min and y_max to set text box position
        y_min, y_max = axs[1].get_ylim()
    
        axs[1].text(
            1901,  # x-coordinate
            y_min + 0.95 * (y_max - y_min),  # y-coordinate
            f'First obs. year: {first_year}\nLast obs. year: {last_year}',
            fontsize=10,
            linespacing = 1.5,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)  # Optional: Add a box around the text
        )
            
        plt.subplots_adjust(hspace=0.5) 
    
        plt.show()
    
    # Cases when there is no data = make empty plot
    else:
        
        fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 2))
        
        axs[0].set_xlim(1900, 2025)
        axs[0].grid(alpha = 0.7)
        axs[0].minorticks_on()
        axs[0].grid(which = 'minor', axis='x', alpha = 0.4)
        
        axs[1].set_xlim(1900, 2025)
        axs[1].grid(axis='x', alpha = 0.7)
        axs[1].minorticks_on()
        axs[1].grid(which = 'minor', axis='x', alpha = 0.4)
        
        plt.subplots_adjust(hspace=0.5) 
        plt.show()

#plot_bar_grid_mb(mb_df_overview, mb_df_overview_2015v, "VE")

#%% No of obs for elevation changes (updates methods version) using expand_dates functioin and subplot complete

def plot_no_of_obs_H_methods(df, df_2015v, country_code):
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    
    df_country_15v = df_2015v[df_2015v['POLITICAL_UNIT'] == country_code]
    
    # Order by year
    df_country = df_country.sort_values('YEAR')
    
    # Remove missing values
    df_country.dropna(subset=['REFERENCE_DATE'], inplace=True)
    
    # Grouping diff methods together
    
    # Methods
    methods = {
    't': ['tR', 'tM', 'tG', 'tP', 'tL', 'tZ', 'tC', 'tX'],
    'a': ['aR', 'aM', 'aG', 'aP', 'aL', 'aZ', 'aC', 'aX'],
    's': ['sR', 'sM', 'sG', 'sP', 'sL', 'sZ', 'sC', 'sX'],
    'x': ['cR', 'cM', 'cG', 'cP', 'cL', 'cZ', 'cC', 'cX', 'xR', 'xM', 'xG', 
          'xP', 'xL', 'xZ', 'xC', 'xX', np.nan]
    }
    
    df_country['METHOD'] = df_country['SD_PLATFORM_METHOD'].apply(
        lambda x: next((k for k, v in methods.items() if x in v), x))
    
    # expanding dates
    
    df_country_long = expand_dates(df_country)
    df_country_long_15v = expand_dates(df_country_15v)
    
    #Extracting variables - get a list of years that span the record
    year = df_country_long["YEARS_ALL"]
    unique_year = year.drop_duplicates()

    year_15v = df_country_long_15v["YEARS_ALL"]
    unique_year_15v = year_15v.drop_duplicates()
    
    # Handle cases when there is no data
    if len(unique_year) == 0:
        first_year = np.nan
        last_year = np.nan
    else:
        first_year = min(unique_year)
        last_year = max(unique_year)
    
    # Setting up bottom methods plot
    
    obs_each_year = []
    obs_each_year_t = []
    obs_each_year_a = []
    obs_each_year_s = []
    obs_each_year_x = []

    for year in unique_year:
        
        # Subset df such that only series for the given year is selected
        df_year = df_country_long[df_country_long['YEARS_ALL'] == year]
        
        obs_each_year.append(len(df_year))
        
        # Number of obs for each different method
        obs_each_year_t.append(len(df_year[df_year['METHOD'] == 't']))
        obs_each_year_a.append(len(df_year[df_year['METHOD'] == 'a']))
        obs_each_year_s.append(len(df_year[df_year['METHOD'] == 's']))
        obs_each_year_x.append(len(df_year[df_year['METHOD'] == 'x']))
    
    # Setting up for top simple bar plot
    
    # For each year I want to get the number of observations
    obs_each_year = []

    obs_each_year_15v = []

    for year in unique_year:
        
        # Subset df such that only series for given year is selected
        df_year = df_country_long[df_country_long['YEARS_ALL'] == year]
        
        obs_each_year.append(len(df_year)) # inclusive
        
    for year_15v in unique_year_15v:
         
        # Subset df such that only series for given year is selected
        df_year_15v = df_country_long_15v[df_country_long_15v['YEARS_ALL'] == year_15v]
         
        obs_each_year_15v.append(len(df_year_15v)) # inclusive
        
        
    # PLOTTING  
    
    if len(unique_year) != 0:
        
        fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 3))
    
        axs[0].bar(unique_year, obs_each_year, color = "#e36d26", label = "2024", width = 1)
        
        # Handle cases when there is no 2015 data:
        if len(obs_each_year_15v) > 0:
            axs[0].bar(unique_year_15v, obs_each_year_15v, color = "#919191", label = "2015", width = 1)
        
        else:
            pass
    
        axs[0].legend(loc = 'upper left', bbox_to_anchor=(0.01, 1), ncol = 2, framealpha = 0.3)
    
        axs[0].set_xlim(1900, 2025)
        axs[0].tick_params(axis = 'x', labelsize = 12)
        axs[0].tick_params(axis = 'y', labelrotation = 90)
        axs[0].set_yscale('log')
        axs[0].set_ylim(0.1, max(obs_each_year)) # specify ylim to ensure bars of value of 1 are shown in both plots 
    
        axs[0].grid(alpha = 0.7)
        axs[0].set_axisbelow(True)
        axs[0].minorticks_on()
        axs[0].grid(which = 'minor', axis='x', alpha = 0.4)
    
        axs[1].bar(unique_year, obs_each_year_x, color="#80B2C7", label="Unknown/combined")
        axs[1].bar(unique_year, obs_each_year_t, color="#DB504A", label="Terrestrial",
                 bottom=obs_each_year_x)
        axs[1].bar(unique_year, obs_each_year_a, color="#E3B505", label="Aerial",
                 bottom=np.array(obs_each_year_x) + np.array(obs_each_year_t))
        axs[1].bar(unique_year, obs_each_year_s, color="#084C61", label="Space",
                 bottom=np.array(obs_each_year_x) + np.array(obs_each_year_t) + np.array(obs_each_year_a))
    
        axs[1].legend(bbox_to_anchor=(0.5, -0.5), loc = 'center', ncol=4)
    
        axs[1].set_xlim(1900, 2025)
        axs[1].tick_params(axis = 'x', labelsize = 12)
        axs[1].tick_params(axis = 'y', labelrotation = 90)
        axs[1].set_yscale('log')
        axs[1].set_ylim(0.1, max(obs_each_year))
    
        axs[1].grid(alpha = 0.7)
        axs[1].set_axisbelow(True) # puts grid in background
        axs[1].minorticks_on()
        axs[1].grid(which = 'minor', axis='x', alpha = 0.4)
    
        #axs[1].set_yticks(axs[1].get_yticks(minor=False))
    
        # Remove first y-axis tick label
        def y_tick_formatter(value, pos):
            if value == 0.1:  # Hide the first tick label (10^-1)
                return ''
            else:
                return r"$10^{{{}}}$".format(int(np.log10(value))) # Had to specify the exponent format like 10^2
            
        axs[0].yaxis.set_major_formatter(FuncFormatter(y_tick_formatter))
        axs[1].yaxis.set_major_formatter(FuncFormatter(y_tick_formatter))
            
        axs[1].text(
            1901,  # x-coordinate
            max(obs_each_year) - (max(obs_each_year)/2.5),  # y-coordinate
            f'First obs. year: {first_year}\nLast obs. year: {last_year}',
            fontsize=10,
            linespacing = 1.5,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)  # Optional: Add a box around the text
        )
        
        #fig.text(-0.05, 0.5, 'No. of obs.', va='center', rotation='vertical', fontsize=12)
        
        fig.tight_layout()
        
        fig.subplots_adjust(hspace=0.4)
    
    # Cases when there is no data = make empty plot
    else:
        
        fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 3))
        
        axs[0].set_xlim(1900, 2025)
        axs[0].grid(alpha = 0.7)
        axs[0].minorticks_on()
        axs[0].grid(which = 'minor', axis='x', alpha = 0.4)
        
        axs[1].set_xlim(1900, 2025)
        axs[1].grid(axis='x', alpha = 0.7)
        axs[1].minorticks_on()
        axs[1].grid(which = 'minor', axis='x', alpha = 0.4)
        
        plt.subplots_adjust(hspace=0.5) 
        plt.show()
    
    
#plot_no_of_obs_H_methods(change_df, change_df_2015v, "IT")

