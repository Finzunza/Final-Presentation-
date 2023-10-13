import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Calculate the min and max payload values
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Define the available launch site options
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options += [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
                                # Add the Dropdown component
                                dcc.Dropdown(id='site-dropdown',
                                             options=site_options,
                                             value='ALL',
                                             placeholder="Select a Launch Site",
                                             searchable=True),
                                # Add the RangeSlider for payload selection
                                dcc.RangeSlider(id='payload-slider',
                                               marks={i: str(i) for i in range(0, 10001, 1000)},
                                               min=0,
                                               max=10000,
                                               step=1000,
                                               value=[min_payload, max_payload]),
                                # Add the Pie chart
                                dcc.Graph(id='success-pie-chart'),
                                # Add the Scatter chart
                                dcc.Graph(id='payload-scatter-chart')
                                ])

# Define a callback to update the scatter chart
@app.callback(
    [Output('success-pie-chart', 'figure'),
     Output('payload-scatter-chart', 'figure')],
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_charts(selected_site, selected_payload_range):
    min_payload, max_payload = selected_payload_range

    if selected_site == 'ALL':
        # For all sites, show total successful launches within the payload range
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) &
                                  (spacex_df['Payload Mass (kg)'] <= max_payload)]
        success_counts = filtered_data[filtered_data['class'] == 1]['Launch Site'].value_counts()
        fig_pie = px.pie(
            values=success_counts.values,
            names=success_counts.index,
            title='Total Successful Launches for All Sites'
        )

        # Scatter chart for payload vs. launch success
        fig_scatter = px.scatter(
            filtered_data,
            x='Payload Mass (kg)',
            y='class',
            labels={'class': 'Launch Success'},
            title='Correlation between Payload Mass and Launch Success'
        )
    else:
        # For a specific site, show Success vs. Failed counts within the payload range
        site_data = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                             (spacex_df['Payload Mass (kg)'] >= min_payload) &
                             (spacex_df['Payload Mass (kg)'] <= max_payload)]
        success_counts = site_data[site_data['class'] == 1]['class'].count()
        failed_counts = site_data[site_data['class'] == 0]['class'].count()
        labels = ['Successful', 'Failed']
        values = [success_counts, failed_counts]
        fig_pie = px.pie(
            values=values,
            names=labels,
            title=f'Success vs. Failed Launches at {selected_site}'
        )

        # Scatter chart for payload vs. launch success
        fig_scatter = px.scatter(
            site_data,
            x='Payload Mass (kg)',
            y='class',
            labels={'class': 'Launch Success'},
            title=f'Correlation between Payload Mass and Launch Success at {selected_site}'
        )

    return fig_pie, fig_scatter

if __name__ == '__main__':
    app.run_server(debug=True)
