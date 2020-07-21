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
import lac_covid19.covid_plots as covid_plots

sns.set()

df_csa_curr = pd.read_pickle(paths.CSA_CURRENT_PICKLE)


# ## Choropleth Values

# In[2]:


covid_plots.csa_distribution(df_csa_curr, lac_regions.ALL_CSA, const.CASE_RATE)


# In[3]:


covid_plots.csa_distribution(df_csa_curr, lac_regions.ALL_CSA, const.DEATH_RATE, 20)


# ## Region

# In[4]:


print(tuple(lac_regions.REGIONS.keys()))


# In[5]:


bin_width = {
    lac_regions.ANTELOPE_VALLEY: 200,
    lac_regions.CENTRAL_LA: 200,
    lac_regions.HARBOR: 400,
    lac_regions.SAN_FERNANDO_VALLEY: 250,
    lac_regions.SAN_GABRIEL_VALLEY: 300,
    lac_regions.SOUTH_BAY: 250,
    lac_regions.WESTSIDE: 200,
    
}
region = lac_regions.WESTSIDE
covid_plots.csa_distribution(df_csa_curr, lac_regions.REGIONS[region], const.CASE_RATE, bin_width.get(region, 300))


# In[6]:


df_csa_ts = pd.read_pickle(paths.CSA_TS_PICKLE)


# In[7]:


area = lac_regions.ALL_CSA[25]
covid_plots.csa_ts(df_csa_ts, area)


# ## Rolling Average

# In[8]:


df_summary = pd.read_pickle(paths.MAIN_STATS_PICKLE)

df_summary['Avg New Cases'] = df_summary[const.NEW_CASES].rolling(3).mean()
df_summary['New Cases Predictor'] = df_summary['Avg New Cases'].transform(np.log)

df_summary['Total Cases Predictor'] = df_summary[const.CASES].dropna().transform(np.log)

sns.scatterplot(x=const.DATE, y=const.NEW_CASES, data=df_summary)
plt.xlim((pd.Timestamp(2020, 3, 29), pd.Timestamp(2020, 7, 17)))
plt.xticks(rotation='45')
plt.title('New COVID-19 Cases in LA County over Time')
plt.show()

ax = sns.scatterplot(x=const.DATE, y='Avg New Cases', data=df_summary)
plt.xlim((pd.Timestamp(2020, 3, 29), pd.Timestamp(2020, 7, 17)))
plt.xticks(rotation='45')
plt.title('New COVID-19 Cases in LA County over Time')
plt.ylabel('3 Day Rolling Average')
plt.show()

ax = sns.scatterplot(x=const.DATE, y='New Cases Predictor', data=df_summary)
plt.xlim((pd.Timestamp(2020, 3, 29), pd.Timestamp(2020, 7, 17)))
plt.xticks(rotation='45')
plt.title('New COVID-19 Cases in LA County over Time')
plt.ylabel('ln(3 Day Rolling Average)')
plt.show()


# In[ ]:




