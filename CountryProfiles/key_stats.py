#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 12:19:42 2023

@author: giuliosaibene
"""

# =============================================================================
# COUNTRY PROFILES WGMS 2023
# 
# Functions to calculate the key statistics of each country, like the total glaciated area, the
# number of series in each country, the average time length of each series, and the average 
# number of observations per series
# =============================================================================

import numpy as np
import pandas as pd
import os

#%%

# Relative file paths to repository (make sure to set working directory to repository CountryProfiles folder!!)

data_dir = "data"

glaciers_df_2015v_path = os.path.join(data_dir, "WGMS-FoG-2015-11-A-GENERAL-INFORMATION.csv")
fv_reco_df_2015v_path = os.path.join(data_dir, "WGMS-FoG-2015-11-RR-RECONSTRUCTION-FRONT-VARIATION.csv")
mb_df_overview_2015v_path = os.path.join(data_dir, "WGMS-FoG-2015-11-E-MASS-BALANCE-OVERVIEW.csv")
change_df_2015v_path = os.path.join(data_dir, "WGMS-FoG-2015-11-D-CHANGE.csv")
fronts_df_path = os.path.join(data_dir, "front_variation.csv")
fv_reco_df_path = os.path.join(data_dir, "reconstruction_front_variation.csv")
mb_df_path = os.path.join(data_dir, "mass_balance.csv")
mb_df_overview_path = os.path.join(data_dir, "mass_balance_overview.csv")
change_df_path = os.path.join(data_dir, "change.csv")
glaciers_df_path = os.path.join(data_dir, "glacier.csv")
country_names_path = os.path.join(data_dir, "country_codes.csv")
fronts_df_2015v_path = os.path.join(data_dir, "fog-2015-11-front_variation.csv")

glaciers_df_2015v = pd.read_csv(glaciers_df_2015v_path)
fv_reco_df_2015v = pd.read_csv(fv_reco_df_2015v_path)
mb_df_overview_2015v = pd.read_csv(mb_df_overview_2015v_path)
change_df_2015v = pd.read_csv(change_df_2015v_path)
fronts_df = pd.read_csv(fronts_df_path)
fv_reco_df = pd.read_csv(fv_reco_df_path)
mb_df = pd.read_csv(mb_df_path)
mb_df_overview = pd.read_csv(mb_df_overview_path)
change_df = pd.read_csv(change_df_path)
glaciers_df = pd.read_csv(glaciers_df_path)
country_names = pd.read_csv(country_names_path)
fronts_df_2015v = pd.read_csv(fronts_df_2015v_path)



#%% Shared location - file paths

# Change import file location accordingly

# =============================================================================
# country_names = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/country_codes.csv") # Shared file path
# 
# glaciers_df_2015v = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/WGMS-FoG-2015-11-A-GENERAL-INFORMATION.csv",
#                                 encoding = 'latin-1')
# 
# 
# fronts_df = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/front_variation.csv")
# 
# fronts_df_2015v = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/fog-2015-11-front_variation.csv",
#                              encoding = 'latin-1')
# 
# # the 2015 fv table doesn't have a POLITICAL UNIT column so merge
# fronts_df_2015v_merge = pd.merge(fronts_df_2015v, glaciers_df_2015v[['WGMS_ID', 'POLITICAL_UNIT']], on=['WGMS_ID'], how='inner')
# 
# fv_reco_df = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/reconstruction_front_variation.csv")
# 
# fv_reco_df_2015v = pd.read_csv('/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/WGMS-FoG-2015-11-RR-RECONSTRUCTION-FRONT-VARIATION.csv',
#                             encoding = 'latin-1')
# 
# mb_df = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/mass_balance.csv")
# 
# mb_df_overview = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/mass_balance_overview.csv")
# 
# mb_df_overview_2015v = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/WGMS-FoG-2015-11-E-MASS-BALANCE-OVERVIEW.csv",
#                                    encoding = 'latin-1')
# 
# change_df = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/change.csv")
# 
# change_df_2015v = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/WGMS-FoG-2015-11-D-CHANGE.csv",
#                               encoding = 'latin-1')
# 
# glaciers_df = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/glacier_ids.csv",
#                           dtype = {'POLITICAL_UNIT': str})
# 
# glacier_A = pd.read_csv("/Volumes/shared/group/wgms_guest/2023_GiulioSaibene/CountryProfiles24/Data/fog_glacier_area.csv")
# =============================================================================



#%% Local file paths (updated with 2024)

# Reading in the look-up table for the country full name based on its code

country_names = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/country_codes.csv")

# Convert it to a dictionary

country_names = country_names.set_index('id')['name'].to_dict()

# FV data

glaciers_df_2015v = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/fog-2015/WGMS-FoG-2015-11-A-GENERAL-INFORMATION.csv",
                                encoding = 'latin-1')


fronts_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/front_variation.csv")

fronts_df_2015v = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/fog-2015-11-front_variation.csv",
                             encoding = 'latin-1')

# the 2015 fv table doesn't have a POLITICAL UNIT column so merge
fronts_df_2015v_merge = pd.merge(fronts_df_2015v, glaciers_df_2015v[['WGMS_ID', 'POLITICAL_UNIT']], on=['WGMS_ID'], how='inner')

fv_reco_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/reconstruction_front_variation.csv")

fv_reco_df_2015v = pd.read_csv('/Users/giuliosaibene/Desktop/University/UZH/WGMS/fog-2015/WGMS-FoG-2015-11-RR-RECONSTRUCTION-FRONT-VARIATION.csv',
                            encoding = 'latin-1')

# MB data

mb_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/mass_balance.csv")

mb_df_overview = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/mass_balance_overview.csv")

mb_df_overview_2015v = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/fog-2015/WGMS-FoG-2015-11-E-MASS-BALANCE-OVERVIEW.csv",
                                   encoding = 'latin-1')

# TC data

change_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/change.csv")

change_df_2015v = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/fog-2015/WGMS-FoG-2015-11-D-CHANGE.csv",
                              encoding = 'latin-1')

# Other data

glaciers_df = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/DOI-WGMS-FoG-2024-01/data/glacier.csv",
                          dtype = {'POLITICAL_UNIT': str})

glacier_A = pd.read_csv("/Users/giuliosaibene/Desktop/University/UZH/WGMS/fog_glacier_area.csv")

glacier_A_recent = glacier_A[ glacier_A['YEAR'] >= 2000]

# filtering current database to before 2015

mb_df_overview_2015 = mb_df_overview[ mb_df_overview['YEAR'] <= 2015 ]
fronts_df_2015 = fronts_df[ fronts_df['YEAR'] <= 2015 ]
change_df_2015 = change_df[ change_df['YEAR'] <= 2015 ]

# filtering to 2005-2013 period (9 years) using old version of database

fronts_df_0513 = fronts_df_2015v_merge[ (fronts_df_2015v_merge['YEAR'] >= 2005) & (fronts_df_2015v_merge['YEAR'] <= 2013)]
mb_df_overview_0513 = mb_df_overview_2015v[ (mb_df_overview_2015v['YEAR'] >= 2005) & (mb_df_overview_2015v['YEAR'] <= 2013)]
change_df_0513 = change_df_2015v[ (change_df_2015v['YEAR'] >= 2005) & (change_df_2015v['YEAR'] <= 2013)]

# filtering to 2014-2022 period (9 years)

fronts_df_1422 = fronts_df[ (fronts_df['YEAR'] >= 2014) & (fronts_df['YEAR'] <= 2022)]
mb_df_overview_1422 = mb_df_overview[ (mb_df_overview['YEAR'] >= 2014) & (mb_df_overview['YEAR'] <= 2022)]
change_df_1422 = change_df[ (change_df['YEAR'] >= 2014) & (change_df['YEAR'] <= 2022)]


#%% Total glaciated area (not used)

# The national areas from the WGMS database

def calc_tot_area(glaciers_df, country_code):
    
    # area look up table
    single_glacier_A = glacier_A.groupby('WGMS_ID')['AREA'].mean().reset_index()
    
    df_country = glaciers_df[glaciers_df['POLITICAL_UNIT'] == country_code]
    glaciers = df_country['WGMS_ID']
    unique_glaciers = glaciers.drop_duplicates()
    
    df_country_areas = single_glacier_A[single_glacier_A['WGMS_ID'].isin(unique_glaciers)]
    
    tot_area = df_country_areas['AREA'].sum()
    
    return(tot_area)

#%% NUMBER OF GLACIERS PER COUNTRY IN WHOLE DATABASE to compare versions

def n_of_glaciers_per_country(df, country_code):
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    
    glaciers_country = df_country['WGMS_ID'].drop_duplicates()
    
    n_of_glaciers_country = len(glaciers_country)
    
    return(n_of_glaciers_country)


#%% No of series

def n_of_series(df, country_code):
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    
    # Find how many unique glaciers in each country, each glacier counts as a series
    glaciers = df_country['WGMS_ID']
    unique_glaciers = glaciers.drop_duplicates()
    
    n_of_series = len(unique_glaciers)
    
    return(n_of_series)

def n_of_series_perc_change(df15, country_code):
    
    df15_country = df15[df15['POLITICAL_UNIT'] == country_code]
    
    n_of_series_2015 = df15_country['nr. of series']
    
    #perc_n_series_change = 100 * ((n_of_series(df, country_code) - n_of_series_2015) / n_of_series_2015)
    
    return(int(n_of_series_2015.values[0]))
    
# n_of_series_perc_change(fronts_df, key_stats_2015_fv, "CA")

#%% Length of series (years)

def len_of_series_perc_change(df15, country_code):
    
    df15_country = df15[df15['POLITICAL_UNIT'] == country_code]
    
    len_of_series_2015 = df15_country['avg. length of series']
    
    return(int(len_of_series_2015.values[0]))

# Average length of series for glaciers reported between 2007 and 2014

def len_of_series_period_specific(df, df_period, country_code):
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    
    df_period_country = df_period[df_period['POLITICAL_UNIT'] == country_code]
    
    if len(df_period_country) > 0:
    
        # get list of glaciers included in this time period
        
        glaciers_in_period = df_period_country['WGMS_ID'].drop_duplicates() 
        
        # filter complete table to only include these glaciers
        
        df_country_period_glaciers = df_country[df_country['WGMS_ID'].isin(glaciers_in_period)] 
        
        # find the length of the series for these glaciers of 2007-2014
        
        series_length = df_country_period_glaciers.groupby('WGMS_ID')['YEAR'].agg(np.ptp) + 1 
    
        avg_len_of_series = series_length.mean()
        
    else:
        avg_len_of_series = 0
    
    return avg_len_of_series

# len_of_series_period_specific(mb_df, mb_df_0513, "KG")


#%% Avg number of observations per series (i.e. avg no of obs per glacier)


def avg_obs_period_specific(df, df_period, country_code):
    
    df_country = df[df['POLITICAL_UNIT'] == country_code]
    
    df_period_country = df_period[df_period['POLITICAL_UNIT'] == country_code]
    
    if len(df_period_country) > 0:
        
        # get list of glaciers included in this time period
        
        glaciers_in_period = df_period_country['WGMS_ID'].drop_duplicates() 
        
        # filter complete table to only include these glaciers
        
        df_country_period_glaciers = df_country[df_country['WGMS_ID'].isin(glaciers_in_period)] 
        
        obs_each_series = []
        
        for glacier in glaciers_in_period:
            
            # Subset df such that only series for given glacier is selected
            
            df_glacier = df_country_period_glaciers[df_country_period_glaciers['WGMS_ID'] == glacier]
            
            obs_each_series.append(len(df_glacier))
        
        obs_of_series = sum(obs_each_series) / len(obs_each_series)
        
    else:
        obs_of_series = 0
    
    return(obs_of_series)
    

def avg_obs_perc_change(df15, country_code):
    
    df15_country = df15[df15['POLITICAL_UNIT'] == country_code]
    
    avg_obs_2015 = df15_country['avg. nr. of observations']
    
    return(int(avg_obs_2015.values[0]))

