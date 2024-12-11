#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 09:27:57 2023

@author: giuliosaibene
"""

# =============================================================================
# COUNTRY PROFILES WGMS 2023
#
# Functions to generate plot of warming stripes based on the glaciological mass balance
# =============================================================================

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap


#%% WARMING STRIPES

def plot_mb_warming_stripes(mb_df, country_code):

    mb_df_country = mb_df[mb_df['POLITICAL_UNIT'] == country_code]
    mb_df_country.dropna(subset=['ANNUAL_BALANCE'], inplace=True)

    # Take only glacier-wide measurements
    mb_df_country = mb_df_country[mb_df_country['UPPER_BOUND'] == 9999]

    # Sort the DataFrame by year
    mb_df_country = mb_df_country.sort_values('YEAR')

    # Extracting variables
    years = mb_df_country["YEAR"]

    # Removing years with multiple measurements
    unique_years = years.drop_duplicates()

    # Defining plot

    fig = plt.figure(figsize=(10, 1))

    ax = fig.add_axes([0, 0, 1, 1])

    # Only plot if there is data for given country

    if len(unique_years) > 0:

        # Create a DataFrame with all years to add
        all_years_df = pd.DataFrame({'YEAR': range(unique_years.min(), unique_years.max() + 1)})

        mb_df_country['YEAR'] = mb_df_country['YEAR'].astype(int)

        # Merge the existing DataFrame with the one containing all years
        mb_df_country = pd.merge(all_years_df, mb_df_country, on='YEAR', how='left')

        # Calculate the annual mean for each year
        annual_mb = mb_df_country.groupby('YEAR')['ANNUAL_BALANCE'].mean()

        # Finding range of mb
        min_mb = min(annual_mb)
        max_mb = max(annual_mb)

        FIRST = unique_years.iloc[0]
        LAST = unique_years.iloc[-1]

        # Creating the input data for the warming strips
        # Reset index to combine data properly
        annual_mb_reset = annual_mb.reset_index()

        stripes_data = pd.DataFrame({'year': annual_mb_reset['YEAR'],
                                     'mb': annual_mb_reset['ANNUAL_BALANCE']})

        stripes_data['mb'].fillna(-9999, inplace=True)

        # Filling plot

        # Create a collection with a stripe for each year

        rectangles = [Rectangle((y, 0), 1, 1) for y in range(FIRST, LAST + 1)]

        # Create a custom colormap with red for negative values, blue for positive values, and gray for -9999

        cmap_colors = [(0.0, '#bf1600'), (0.25, "#ff6652"), (0.5, 'white'), (0.75, "#649bed"), (1.0, '#002d70')]
        cmap_custom = LinearSegmentedColormap.from_list('custom_cmap', cmap_colors, N=256)
        cmap_custom.set_under(color='gray')  # Assign black to values below the colormap range

        # set data, colormap and color limits

        max_abs_mb = max(abs(min_mb), abs(max_mb)) # maximum absolute value to scale color limits and ensure 0 is white

        col = PatchCollection(rectangles)
        col.set_array(stripes_data['mb'])
        col.set_cmap(cmap_custom)
        col.set_clim(-max_abs_mb, max_abs_mb)
        ax.add_collection(col)

        ax.set_ylim(0, 1)
        ax.set_xlim(FIRST, LAST + 1)

        # Adding years to the x-axis
        ax.set_xticks(stripes_data['year'][::5])
        ax.set_xticklabels(stripes_data['year'][::5], rotation=90)

        # Removing the y-axis
        ax.set_yticks([])

        # Add color bar
        cax = fig.add_axes([0.3, 1.35, 0.4, 0.05])  # location of color bar (-0.65 good for bottom)
        cbar = plt.colorbar(col, cax=cax, orientation='horizontal')

        # Add min_mb and max_mb as text on the top left

        if LAST - FIRST > 10: # case when there are enough years
            ax.text(FIRST, 1.2, f'Max MB: {max_mb:.0f} mm/a', fontsize=12, ha='left', va='center')
            ax.text(LAST - (LAST - FIRST)/6, 1.2, f'Min MB: {min_mb:.0f} mm/a', fontsize=12, ha='left', va='center')

        elif LAST - FIRST == 0: # case when there is only one year of measurements
            ax.text(FIRST, 1.2, f'MB: {max_mb:.0f} mm/a', fontsize=12, ha='left', va='center')

        else:
            ax.text(FIRST, 1.2, f'Max MB: {max_mb:.0f} mm/a', fontsize=12, ha='left', va='center')
            ax.text(LAST, 1.2, f'Min MB: {min_mb:.0f} mm/a', fontsize=12, ha='left', va='center')

    else:

       # If unique_years is empty, create an empty plot with the same size
       ax.set_axis_off()  # Remove all axes
       ax.set_xlim(0, 1)
       ax.set_ylim(0, 1)



#plot_mb_warming_stripes(mb_df, "DE")
