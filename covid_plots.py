import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

import lac_covid19.const as const

region_geo_groups = {
    'Central': ('Central LA', 'Eastside', 'Northeast LA',
                'South LA', 'Southeast'),
    'Valleys': ('San Fernando Valley', 'San Gabriel Valley',
                'Pomona Valley', 'Verdugos'),
    'Ocean': ('Harbor', 'South Bay', 'Westside'),
    'Rural': ('Angeles Forest', 'Antelope Valley',
              'Santa Monica Mountains', 'Northwest County'),
}
region_plot_groups = (
    (region_geo_groups['Central'] + region_geo_groups['Ocean']),
    (region_geo_groups['Valleys'] + region_geo_groups['Rural'])
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
    return px.line(df_region, x=const.DATE, y=const.CASE_RATE,
                   line_dash=const.REGION, line_dash_map=line_dash_map,
                   color=const.REGION, color_discrete_map=color_discrete_map,
                   hover_data=[const.CASES],
                   title='COVID-19 Case Rate by County Region')


def calc_high_outlier(values):
    q1, q3 = [values.quantile(x, 'midpoint') for x in (0.25, 0.75)]
    high_outlier = q3 + 1.5 * (q3 - q1)
    return high_outlier


def csa_distribution(df_csa, selections, variable, bin_width=400):
    df_csa = df_csa[df_csa[const.AREA].isin(selections)]
    counts = df_csa[variable]

    bin_edges = tuple(range(0, counts.max()+bin_width, bin_width))
    sns.distplot(counts, bin_edges, kde=False)
    # plt.xticks(bin_edges)
    plt.show()

    outlier_value = calc_high_outlier(counts)
    outlier_csa = df_csa.loc[df_csa[variable] > outlier_value,
                             (const.AREA, variable, const.CF_OUTBREAK)]
    outlier_csa.sort_values(variable, ascending=False, inplace=True)

    print('n={}, High outlier: {}'.format(len(selections), outlier_value))
    print(outlier_csa)


def csa_ts(df_csa, area):
    df_csa = df_csa.loc[(df_csa[const.AREA] == area)
                        & df_csa[const.CASES].notna(),
                        (const.DATE, const.CASES)]
    
    df_csa.plot.scatter(const.DATE, const.CASES, c='b')
    plt.xticks(rotation='45')
    plt.title(area)
    plt.show()

    # return px.scatter(df_csa, x=const.DATE, y=const.CASES, title=area)
