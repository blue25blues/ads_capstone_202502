# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Task 1: Dropdown options
launch_sites = spacex_df.groupby(['Launch Site'], as_index=False).first()
dd_options = []
dd_options.append({'label': 'All Sites', 'value': 'ALL'})
for index, row in launch_sites.iterrows():
    dd_options.append({'label': row['Launch Site'], 'value': row['Launch Site']})


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=dd_options,
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True
                                ),          
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    #marks={min_payload: min_payload, max_payload: max_payload},
                                    value=[min_payload, max_payload])
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            filtered_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # 各 class の件数（成功と失敗）を取得する
        filtered_df = filtered_df.groupby('class').size().reset_index(name='counts')
        fig = px.pie(
            filtered_df,
            values='counts',
            names='class',
            title='Total Success/Failure Launches Rate for site ' + entered_site) 
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
            [Input(component_id='site-dropdown', component_property='value'), 
            Input(component_id='payload-slider', component_property='value')])

def get_scatter_plot(entered_site, slider_payload):
    #filtered_df = spacex_df.groupby()
    range_low, range_high = slider_payload
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] > range_low) & (spacex_df['Payload Mass (kg)'] <= range_high)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y="class", color="Booster Version Category", symbol="Booster Version Category")
        return fig
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & (spacex_df['Payload Mass (kg)'] > range_low) & (spacex_df['Payload Mass (kg)'] <= range_high)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y="class", color="Booster Version Category", symbol="Booster Version Category")
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
