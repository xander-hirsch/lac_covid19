#!/usr/bin/env python
# coding: utf-8

# # COVID-19 in Los Angeles County
# 
# * Data sourced from Los Angeles County Department of Public Health's daily 2019 Novel Coronavirus news releases. The archived releases can be found [here](http://publichealth.lacounty.gov/phcommon/public/media/mediaCOVIDdisplay.cfm?unit=media&ou=ph&prog=media)
# * *Case rate* and *Death rate* are **per 100,000 people**
#  
# **Last Update:** Thursday, 6 August
#  
# ### Other Sources
# * Los Angeles County Department of Public Health [**COVID-19 Surveillance Dashboard**](http://dashboard.publichealth.lacounty.gov/covid19_surveillance_dashboard/)
# * California Department of Public Health [**COVID-19 Public Dashboard**](https://public.tableau.com/views/COVID-19PublicDashboard/Covid-19Public?:embed=y&:display_count=no&:showVizHome=no)
#  
# ### Development and Data
# * Source code is hosted on GitHub at [amhirsch/lac_covid19](https://github.com/amhirsch/lac_covid19)
# * CSV time series data can be downloaded [here](https://github.com/amhirsch/lac_covid19/tree/master/docs)

# In[1]:


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import lac_covid19.const as const
import lac_covid19.const.paths as paths
import lac_covid19.visualization.plots as covid_plots

WIDTH=600
HEIGHT=400


# ## Regions of Los Angeles
# Los Angeles County Public Health releases case count by *countywide statistical areas*.
# These areas partion the entire county into cities, City of Los Angeles sections, and unincorporated areas.
# The geographic boundaries are published at the [**County of Los Angeles GIS Portal**](https://egis-lacounty.hub.arcgis.com/datasets/countywide-statistical-areas-csa).
# 
# The regions are defined by the Los Angeles Times' [**Mapping L.A.**](http://maps.latimes.com/neighborhoods/) project.
# Their project goes beyond convenient geographical and freeway partitions.
# Rather, it attempts to define regions based on socioeconomic indicators, demographic data, and shared characteristics.
# Those definitions seem most appropriate for asking questions on how varying communities are affected by the disease.

# In[2]:


df_region = pd.read_pickle(paths.REGION_TS_PICKLE)


# ### Region List - Sorted by Case Rate

# In[3]:


(df_region.tail(16).drop(columns=const.DATE)
 .sort_values(const.CASE_RATE, ascending=False).reset_index(drop=True)
 .loc[:, [const.REGION, const.CASE_RATE, const.CASES]])


# In[4]:


fig = covid_plots.plot_region(df_region)
fig.show()


# ## Statistics by Demographic

# ### Gender

# In[5]:


by_gender = pd.read_pickle(paths.GENDER_PICKLE)

male_color, female_color = px.colors.qualitative.Plotly[:2]
color_discrete_map = {const.MALE: male_color, const.FEMALE: female_color}
fig = px.line(by_gender, x=const.DATE, y=const.CASE_RATE,
              color=const.GENDER, color_discrete_map=color_discrete_map,
              width=WIDTH, height=HEIGHT,
              hover_data=[const.CASES],
              title='Case Rate by Gender')
fig.show()


# ## Aggregate Daily Changes

# In[6]:


df_summary = pd.read_pickle(paths.MAIN_STATS_PICKLE)

fig_cases = px.bar(df_summary, x=const.DATE, y=const.NEW_CASES,
                   width=WIDTH, height=HEIGHT,
                   title='COVID-19 Cases in Los Angeles County')
fig_cases.show()

days_deaths_missing = [pd.Timestamp(2020, 7, x) for x in (3, 4, 5)]
df_deaths = df_summary[~df_summary[const.DATE].isin(days_deaths_missing)]

fig_deaths = px.bar(df_deaths, x=const.DATE, y=const.NEW_DEATHS,
                    width=WIDTH, height=HEIGHT,
                    title='COVID-19 Deaths in Los Angeles County')
fig_deaths.show()

