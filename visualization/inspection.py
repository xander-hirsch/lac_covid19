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


sns.palplot(sns.color_palette())


# ## Choropleth Values

# In[2]:


df_csa_curr = pd.read_pickle(paths.CSA_CURRENT_PICKLE)


# In[3]:


print(covid_plots.high_vals_summary(df_csa_curr[const.CASE_RATE]))

fig, ax = plt.subplots()
covid_plots.csa_distribution(ax, df_csa_curr)
ax.set_xlim(right=5500)
fig.show()


# In[4]:


print(covid_plots.high_vals_summary(df_csa_curr[const.DEATH_RATE]))

fig, ax = plt.subplots()
covid_plots.csa_distribution(ax, df_csa_curr, const.DEATH_RATE, bin_width=10)
ax.set_xlim(right=200)
fig.show()


# ## Region

# In[5]:


print(tuple(lac_regions.REGIONS.keys()))


# In[11]:


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


# In[2]:


df_csa_ts = pd.read_pickle(paths.CSA_TS_PICKLE)


# In[16]:


fig, ax = plt.subplots(figsize=(12,6))
area = lac_regions.ALL_CSA[16]

covid_plots.csa_ts(ax, df_csa_ts, area)
fig.show()


# ## Rolling Average

# In[24]:


df_summary = pd.read_pickle(paths.MAIN_STATS_PICKLE)


# In[31]:


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


# In[ ]:




