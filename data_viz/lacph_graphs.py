#!/usr/bin/env python
# coding: utf-8

# # COVID-19 in Los Angeles County

# * Data sourced from Los Angeles County Department of Public Health's daily 2019 Novel Coronavirus news releases. The archived releases can be found [here](http://publichealth.lacounty.gov/phcommon/public/media/mediaCOVIDdisplay.cfm?unit=media&ou=ph&prog=media)
# * *Case rate* and *Death rate* are **per 100,000 people**
# 
# **Last Update:** Friday, 17 July
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
import lac_covid19.covid_plots as covid_plots

WIDTH=600
HEIGHT=400


# ## Region
# Los Angeles County Public Health releases case count by *countywide statistical areas*.
# These areas partion the entire county into cities, City of Los Angeles sections, and unincorporated areas.
# The geographic boundaries are published at the [**County of Los Angeles GIS Portal**](https://egis-lacounty.hub.arcgis.com/datasets/countywide-statistical-areas-csa).
# 
# 
# The regions are defined by the Los Angeles Times' [**Mapping L.A.**](http://maps.latimes.com/neighborhoods/) project.
# Their project goes beyond convenient geographical and freeway partitions.
# Rather, it attempts to define regions based on socioeconomic indicators, demographic data, and shared characteristics.
# Those definitions seem most appropriate for asking questions on how varying communities are affected by the disease.

# In[2]:


df_region = pd.read_pickle(paths.REGION_TS_PICKLE)


# ### Region Ranking by Current COVID-19 Case Rate

# In[3]:


(df_region.tail(16).drop(columns=const.DATE)
 .sort_values(const.CASE_RATE, ascending=False).reset_index(drop=True)
 .loc[:, [const.REGION, const.CASE_RATE, const.CASES]])


# In[4]:


fig = covid_plots.plot_region(df_region)
fig.show()


# ## Statistics by Demographic

# ### Age Group

# In[5]:


by_age = pd.read_pickle(paths.AGE_PICKLE)
# Remove seemingly extraneous data point
by_age = by_age[(by_age[const.AGE_GROUP] != const.AGE_OVER_65)
                | (by_age[const.DATE] != pd.Timestamp('2020-04-13'))]

fig = px.line(by_age, x=const.DATE, y=const.CASE_RATE,
              color=const.AGE_GROUP, width=WIDTH, height=HEIGHT,
              hover_data=[const.CASES],
              title='Case Rate by Age Group')
fig.show()


# ### Gender

# In[6]:


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

# In[7]:


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


# ## Further Investigation

# ## Young Adults in New COVID-19 Cases

# In[8]:


NC_YA = '{} (Young Adults)'.format(const.NEW_CASES)
NC_ALL = '{} (All)'.format(const.NEW_CASES)
NC_NOT_YA = ' - '.join((NC_ALL, NC_YA))

df_young_adults = by_age.loc[
    by_age[const.AGE_GROUP] == const.AGE_18_40, [const.DATE, const.CASES]]
df_young_adults[NC_YA] = df_young_adults[const.CASES].diff()

df_young_adults = df_young_adults.merge(
    df_summary[[const.DATE, const.NEW_CASES]], on=const.DATE)

df_young_adults[NC_NOT_YA] = df_young_adults[const.NEW_CASES] - df_young_adults[NC_YA]

# Filter first day and backlog day
df_young_adults = df_young_adults.iloc[1:]
df_young_adults = df_young_adults[df_young_adults[const.DATE] != pd.Timestamp(2020, 7, 6)]

df_young_adults[const.NEW_CASES] = df_young_adults[const.NEW_CASES].convert_dtypes()


# In[9]:


fig = make_subplots(rows=2, cols=1)

fig.add_trace(go.Bar(name='Young Adults',
                     x=df_young_adults[const.DATE], y=df_young_adults[NC_YA]),
              row=1, col=1)
fig.add_trace(go.Bar(name='Everyone Else',
                     x=df_young_adults[const.DATE], y=df_young_adults[NC_NOT_YA]),
              row=1, col=1)
fig.update_layout(barmode='stack')

fig.add_trace(go.Scatter(x=df_young_adults[const.DATE],
              y=df_young_adults[NC_YA] / df_young_adults[const.NEW_CASES],
              mode='markers',
              name='% Young Adult'),
             row=2, col=1)

fig.update_yaxes(rangemode='tozero')
fig.update_layout(title='Composition of Young Adults in Los Angeles County New COVID-19 Cases',
                  width=WIDTH*1.5, height=HEIGHT*2)
fig.show()

