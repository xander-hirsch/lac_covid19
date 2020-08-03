import pandas as pd
import plotly.express as px
import seaborn as sns

import lac_covid19.const as const
import lac_covid19.const.lac_regions as lac_regions

CENTRAL = 'Central'
VALLEYS = 'Valleys'
OCEAN = 'Ocean'
RURAL = 'Rural'
region_geo_groups = {
    CENTRAL: (lac_regions.CENTRAL_LA, lac_regions.EASTSIDE,
              lac_regions.NORTHEAST_LA, lac_regions.SOUTH_LA,
              lac_regions.SOUTHEAST),
    VALLEYS: (lac_regions.SAN_FERNANDO_VALLEY, lac_regions.SAN_GABRIEL_VALLEY,
              lac_regions.POMONA_VALLEY, lac_regions.VERDUGOS),
    OCEAN: (lac_regions.HARBOR, lac_regions.SOUTH_BAY, lac_regions.WESTSIDE),
    RURAL: (lac_regions.ANGELES_FOREST, lac_regions.ANTELOPE_VALLEY,
            lac_regions.SANTA_MONICA_MOUNTAINS, lac_regions.NORTHWEST_COUNTY),
}
region_plot_groups = (
    (region_geo_groups[CENTRAL] + region_geo_groups[OCEAN]),
    (region_geo_groups[VALLEYS] + region_geo_groups[RURAL])
)

dash_list = ('solid', 'dash')
line_dash_map = {}
for dash_index in range(len(dash_list)):
    dash_type = dash_list[dash_index]
    for region in region_plot_groups[dash_index]:
        line_dash_map[region] = dash_type

color_list = px.colors.qualitative.Plotly
color_discrete_map = {}
for group in region_plot_groups:
    color_index = 0
    for region in group:
        color_discrete_map[region] = color_list[color_index]
        color_index += 1


def plot_region(df_region):
    """Plots a region time series as a Plotly Figure"""
    return px.line(df_region, x=const.DATE, y=const.CASE_RATE,
                   line_dash=const.REGION, line_dash_map=line_dash_map,
                   color=const.REGION, color_discrete_map=color_discrete_map,
                   hover_data=[const.CASES],
                   title='COVID-19 Case Rate by County Region')


def calc_high_outlier(values) -> float:
    """Calculates the high outlier from a pandas Series"""
    q1, q3 = [values.quantile(x, 'midpoint') for x in (0.25, 0.75)]
    return q3 + 1.5 * (q3 - q1)


def high_vals_summary(values) -> str:
    obs = values.size
    ninety, ninety_five = [values.quantile(x, 'midpoint') for x in (0.9, 0.95)]
    high_outlier = calc_high_outlier(values)
    return 'n={}, 90%={}, 95%={}, outlier={}'.format(obs, ninety, ninety_five,
                                                     high_outlier)


def csa_distribution(ax, df_csa, variable=const.CASE_RATE, selections=None,
                     bin_width=400):
    """Plots a histogram of CSA-specific statistics.

    Args:
        ax: The matplotlib axes to use
        df_csa: The dataframe with the current CSA data
        variable: The variable to plot distribution for, defaulting to case rate
        selections: A subset of data to plot.
        bin_width: The size of histogram bins
    """
    if selections is not None:
        df_csa = df_csa[df_csa[const.AREA].isin(selections)]
    counts = df_csa[variable]

    bin_edges = tuple(range(0, counts.max()+bin_width, bin_width))
    out = sns.distplot(counts, bin_edges, kde=False, ax=ax)

    ax.set_xlim(left=0)

    return out

    # outlier_value = calc_high_outlier(counts)
    # outlier_csa = df_csa.loc[df_csa[variable] > outlier_value,
    #                          (const.AREA, variable, const.CF_OUTBREAK)]
    # outlier_csa.sort_values(variable, ascending=False, inplace=True)

    # print('n={}, High outlier: {}'.format(len(selections), outlier_value))
    # print(outlier_csa)

def plot_time_series(ax, df_ts, dep_var=const.CASES):
    """Plots a time series using the Date as the independent variable and the
        parameter dep_var as the dependent variable.
    """
    out = sns.scatterplot(const.DATE, dep_var, data=df_ts, ax=ax)

    x_pad = pd.Timedelta(1, 'day')
    min_date = df_ts[const.DATE].min() - x_pad
    max_date = df_ts[const.DATE].max() + x_pad

    ax.set_xlim(min_date, max_date)
    ax.tick_params('x', which='both', labelrotation=45)

    return out


def csa_ts(ax, df_csa, area, dep_var=const.CASES):
    """Plots the cases over time for an area"""
    df_csa = df_csa[df_csa[const.AREA] == area]
    out = plot_time_series(ax, df_csa, dep_var)
    ax.set_title('COVID-19 {} in {}'.format(dep_var, area))
    return out

    # df_csa = df_csa.loc[(df_csa[const.AREA] == area)
    #                     & df_csa[const.CASES].notna(),
    #                     (const.DATE, const.CASES)]

    # df_csa.plot.scatter(const.DATE, const.CASES, c='b')
    # plt.xticks(rotation='45')
    # plt.title(area)
    # plt.show()

    # return px.scatter(df_csa, x=const.DATE, y=const.CASES, title=area)
