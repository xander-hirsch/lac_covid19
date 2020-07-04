import plotly.express as px

import lac_covid19.const.columns as col

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
    return px.line(df_region, x=col.DATE, y=col.CASE_RATE,
                   line_dash=col.REGION, line_dash_map=line_dash_map,
                   color=col.REGION, color_discrete_map=color_discrete_map,
                   hover_data=[col.CASES],
                   title='COVID-19 Case Rate by County Region')
