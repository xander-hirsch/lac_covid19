#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import lac_covid19.const as const
import lac_covid19.const.lac_regions as lac_regions
import lac_covid19.const.paths as paths
import lac_covid19.visualization.plots as covid_plots

sns.set()


# In[2]:


# sns.palplot(sns.color_palette())


# In[3]:


df_csa_curr = pd.read_pickle(paths.CSA_CURRENT_PICKLE)


# ## Choropleth Values

# ### Case Rate

# In[4]:


print(covid_plots.high_vals_summary(df_csa_curr[const.CASE_RATE]))

fig, ax = plt.subplots(figsize=(12,4))
covid_plots.csa_distribution(ax, df_csa_curr, bin_width=250)
ax.set_xlim(right=5500)
fig.show()


# In[5]:


print(' Bottom 5% {}'.format(df_csa_curr[const.CASE_RATE].quantile(.05, 'midpoint')))
print('Bottom 10% {}'.format(df_csa_curr[const.CASE_RATE].quantile(.10, 'midpoint')))

fig, ax = plt.subplots(figsize=(12, 4))
covid_plots.csa_distribution(ax, df_csa_curr, bin_width=50)
ax.set_xlim(0, 1000)
fig.show()


# ### Death Rate

# In[7]:


print(covid_plots.high_vals_summary(df_csa_curr[const.DEATH_RATE], (30, 90)))

fig, ax = plt.subplots()
covid_plots.csa_distribution(ax, df_csa_curr, const.DEATH_RATE, bin_width=10)
ax.set_xlim(right=150)
fig.show()


# In[8]:


fig, ax = plt.subplots()
covid_plots.csa_distribution(ax, df_csa_curr, const.DEATH_RATE, bin_width=5)
ax.set_xlim(0, 30)
fig.show()


# ## Region

# In[9]:


print(tuple(lac_regions.REGIONS.keys()))


# In[10]:


bin_width = {
    lac_regions.ANTELOPE_VALLEY: 200,
    lac_regions.CENTRAL_LA: 200,
    lac_regions.HARBOR: 400,
    lac_regions.SAN_FERNANDO_VALLEY: 400,
    lac_regions.SAN_GABRIEL_VALLEY: 300,
    lac_regions.SOUTH_BAY: 250,
    lac_regions.WESTSIDE: 200,
}
region = lac_regions.SAN_FERNANDO_VALLEY

fig, ax = plt.subplots()
covid_plots.csa_distribution(ax, df_csa_curr, selections=lac_regions.REGIONS[region],
                             bin_width=bin_width.get(region, 300))
fig.show()


# ## Countywide Statistical Area

# In[11]:


df_csa_ts = pd.read_pickle(paths.CSA_TS_PICKLE)


# In[17]:


fig, ax = plt.subplots(figsize=(12,6))

city_industry = 'City of Industry'
city_vernon = 'City of Vernon'
unic_rosewood_w_rancho = 'Unincorporated - Rosewood/West Rancho Dominguez'
unic_val_verde = 'Unincorporated - Val Verde'

# area = lac_regions.ALL_CSA[16]
area = city_vernon

lower_date, upper_date = '2020-07-25', '2020-08-01'

covid_plots.csa_ts(ax, df_csa_ts, area)
# ax.set_xlim(pd.Timestamp(lower_date), pd.Timestamp(upper_date))
fig.show()


# In[ ]:


# Batch inspection of CSA time series

# start = 345
# for i in range(start, start+5):
#     fig, ax = plt.subplots(figsize=(12,5))
#     area = lac_regions.ALL_CSA[i]
#     covid_plots.csa_ts(ax, df_csa_ts, area)


# ## Rolling Average

# In[10]:


df_summary = pd.read_pickle(paths.MAIN_STATS_PICKLE)


# In[11]:


df_summary['Avg New Cases'] = df_summary[const.NEW_CASES].rolling(3).mean()
df_summary['New Cases Predictor'] = df_summary['Avg New Cases'].transform(np.log)

df_summary['Total Cases Predictor'] = df_summary[const.CASES].dropna().transform(np.log)

fig, ax = plt.subplots()
covid_plots.plot_time_series(ax, df_summary, const.NEW_CASES)
fig.show()

fig, ax = plt.subplots()
covid_plots.plot_time_series(ax, df_summary, 'Avg New Cases')
fig.show()

fig, ax = plt.subplots()
covid_plots.plot_time_series(ax, df_summary, 'New Cases Predictor')
fig.show()

