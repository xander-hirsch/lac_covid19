#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
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


# In[11]:


area = lac_regions.ALL_CSA[25]
covid_plots.csa_ts(df_csa_ts, area)


# In[ ]:




