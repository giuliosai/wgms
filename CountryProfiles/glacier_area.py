#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 09:23:43 2023

@author: giuliosaibene
"""

# =============================================================================
# COUNTRY PROFILES WGMS 2023
# 
# Importing and joining glacier and country outlines
# Calculating national glacier area from RGI7
# Plotting how much out of the total national glacier area is covered by
# each different type of measurement
# =============================================================================

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Change import file location accordingly

#%% importing spatial data from shared file locations

# =============================================================================
# glims_points = gpd.read_file("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/glims_point.gpkg")
# 
# countries = gpd.read_file("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/country.gpkg")
# 
# rgi7 = gpd.read_file("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/rgi7.gpkg")
# 
# # Transform the geometries to the chosen projection and calculate areas
# rgi7['area'] = rgi7.geometry.to_crs({'proj': 'cea'}).area
# 
# # intersect rgi6 representative points of each outline by country outline
# # output table should have each glacier ID and country code
# 
# # get area of each glacier outline
# 
# # get representitve point of each glacier RGI outline
# rgi7['rep_point'] = rgi7.geometry.representative_point() 
# 
# # set these points as the geometry to use them to join
# rgi7.set_geometry('rep_point', inplace = True)
# 
# # intersect points with countries
# rgi7_countries = gpd.sjoin(rgi7, countries, how="left", op = "within")
# 
# wgi = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/wgi.csv")
# =============================================================================

#%% importing spatial data from local file locations

glims_points = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/glims_point.gpkg")

countries = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/country.gpkg")

rgi7 = gpd.read_file("/Users/giuliosaibene/Desktop/University/UZH/WGMS/rgi7.gpkg")

# Transform the geometries to the chosen projection and calculate areas
rgi7['area'] = rgi7.geometry.to_crs({'proj': 'cea'}).area

# intersect rgi6 representative points of each outline by country outline
# output table should have each glacier ID and country code

# get area of each glacier outline

# get representitve point of each glacier RGI outline
rgi7['rep_point'] = rgi7.geometry.representative_point() 

# set these points as the geometry to use them to join
rgi7.set_geometry('rep_point', inplace = True)

# intersect points with countries
rgi7_countries = gpd.sjoin(rgi7, countries, how="left", op = "within")

wgi = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/wgi.csv")


#%% GET NATIONAL RGI TOTAL AREA

def get_national_rgi_area(rgi_countries, country_code):
    
    # First get national glaciated area from RGI6
    gpd_country = rgi_countries[rgi_countries['id'] == country_code]
    
    national_glacier_area = (gpd_country['area'].sum()) / 1e6 # convert to km^2
    
    return(int(national_glacier_area))

#get_national_rgi_area(rgi7_countries, "CH")

#%% AREA COVERAGE FOR EACH DATA TYPE

def area_covered_by_x_data(df, glacier_A, glaciers_df, rgi_outlines, country_code):
    
    # area look up table
    single_glacier_A = glacier_A.groupby('WGMS_ID')['AREA'].mean().reset_index()
    
    df_country = glaciers_df[glaciers_df['POLITICAL_UNIT'] == country_code]
    glaciers = df_country['WGMS_ID']
    unique_glaciers = glaciers.drop_duplicates()
    
    tot_area = get_national_rgi_area(rgi_outlines, country_code) # in a given country
    
    if len(unique_glaciers) > 0 and tot_area > 0: # only do this calculation if the country has glaciers and has an RGI area
    
        # list of individual glacier areas per country
        df_country_areas = single_glacier_A[single_glacier_A['WGMS_ID'].isin(unique_glaciers)]
        
        # getting list of ids per country per data type
        
        df_country_data = df[df['POLITICAL_UNIT'] == country_code]
        glaciers_data = df_country_data['WGMS_ID']
        unique_glaciers_datatype = glaciers_data.drop_duplicates()
        
        df_country_area_x_datatype = df_country_areas[df_country_areas['WGMS_ID'].isin(unique_glaciers_datatype)]
        
        tot_area_datatype = df_country_area_x_datatype['AREA'].sum()
        
        perc_coverage_datatype = 100*(tot_area_datatype / tot_area)
    
    else:
        perc_coverage_datatype = 0
    
    return(perc_coverage_datatype)

#area_covered_by_x_data(fronts_df_0513, glacier_A, glaciers_df, rgi7_countries, "AL") 

#%% Plot % coverage of each GLIMS inventory with respect to total RGI7 area

# spatial join glacier points and country outlines 

glims_pts_countries = gpd.sjoin(glims_points, countries, how="left", op = "within")

def plot_glims_area_yearly(glims_points, wgi, area_gpd, country_code ):
    
    # First get national glaciated area from RGI7
    
    national_glacier_area = get_national_rgi_area(area_gpd, country_code)
    
    # Select country's GLIMS points
    
    glims_pts_country = glims_points[glims_points['id'] == country_code]
    
    # Get total national area per year from GLIMS inventory
    
    glims_pts_country['src_date'] = pd.to_datetime(glims_pts_country['src_date'])
    
    glims_annual_area = glims_pts_country.groupby(glims_pts_country['src_date'].dt.year)["db_area"].sum().reset_index()
    # The GLIMS area is in km^2
    
    if national_glacier_area > 0: # Only calculate if there is an RGI area for given country
    
        # Get percentage of GLIMS area relative to RGI6 area
        
        glims_annual_area['perc_annual_glims_area'] = (glims_annual_area["db_area"] / national_glacier_area) * 100
        
        year = glims_annual_area['src_date']
        perc_area = glims_annual_area['perc_annual_glims_area']
        
        # Do the same for WGI
        
        wgi_country = wgi[wgi['political_unit'] == country_code ]
        
        wgi_country['photo_year'] = pd.to_datetime(wgi['photo_year'])
        
        wgi_country['topo_year'] = pd.to_datetime(wgi['topo_year']) # some cases when inventoried glacier has
        # topo_year but no photo_year
        
        wgi_annual_area = wgi_country.groupby(wgi_country['photo_year'].dt.year)["total_area"].sum().reset_index()
        
        wgi_annual_area_2 = wgi_country.groupby(wgi_country['topo_year'].dt.year)["total_area"].sum().reset_index()
        
        year_wgi = wgi_annual_area['photo_year']
        year_wgi_2 = wgi_annual_area_2['topo_year']
        perc_area_wgi = (wgi_annual_area["total_area"] / national_glacier_area) * 100
        perc_area_wgi_2 = (wgi_annual_area_2["total_area"] / national_glacier_area) * 100
        
    else:
        
        year = []
        perc_area = []
        year_wgi = []
        perc_area_wgi = []
        year_wgi_2 = []
        perc_area_wgi_2 = []
    
    
    # plotting
    plt.figure(figsize = (9,2))
    
    plt.bar(year, perc_area, color = "#8d3b3b", label = "GLIMS", 
            zorder = 0)
    plt.bar(year_wgi, perc_area_wgi, color = "#f37359", label = "WGI", 
            zorder = 0)
    plt.bar(year_wgi_2, perc_area_wgi_2, color = "#f37359", label = "WGI", 
            zorder = 0)
    plt.grid()
    plt.gca().set_axisbelow(True)
    plt.xlim(1900, 2025)
    plt.tick_params(axis = 'x', labelsize = 10)
    plt.tick_params(axis = 'y', labelrotation = 90)
    plt.legend(handles=[plt.Rectangle((0, 0), 1, 1, color="#f37359"), plt.Rectangle((0, 0), 1, 1, color="#8d3b3b")], 
           labels=["WGI", "GLIMS"])
    
    # Set ylim if there is no data:
    if len(year) == 0:
        plt.ylim(0, 1)


#plot_glims_area_yearly(glims_pts_countries, wgi, rgi7_countries, "DE")

  
   



