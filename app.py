import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
#need prod WSGI server settings, currently PythonAnywhere does this
#import gunicorn

#Read in new .CSV file
#df = pd.read_csv("/home/SlappyWhite/homeless/data/Homeless_Pop.csv")
df = pd.read_csv("data\Homeless_Pop.csv")
#state = df['statediv_title'].unique()


mark_values =  {2009: '2009', 2010: '2010',2011: '2011',2012: '2012',2013: '2013',2014: '2014',
				2015: '2015',2016: '2016',2017: '2017',2018: '2018'}

#external_stylesheets = [
#    {
#        "href": "https://fonts.googleapis.com/css2?"
#        "family=Lato:wght@400;700&display=swap",
#        "rel": "stylesheet",
#   },
#]
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)
server = app.server
app.title = "Homelessness"

#Trying to find a way to import a new logo
#image_logo = 'favicon.ico' # replace with your own image

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                #html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="Homeless Populations", className="header-title"
                ),
                #html.P(
                #    children="Quickly graph various regional homeless"
                #    " populations in the US by type of homelessness"
                #    " between 2011 and 2019",
                #   className="header-description",
                #),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="State", className="menu-title"),
                        dcc.Dropdown(
                            id="state",
                            options=[{'label': m, 'value': m} for m in sorted(df.state.unique())],
                            placeholder="Search for a county",
							#add placeholder value
							value="California",
                            multi=False,
                            #clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="County", className="menu-title"),
                        dcc.Dropdown(
                            id="filtered_counties",
                            options=[],
                            placeholder="Search for a county",
                            value=[],
                            multi=False,
                            #clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Population", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": pop_type, "value": pop_type}
                                for pop_type in df.pop_type.unique()
                            ],
                            value="Total Homeless",
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="PIT-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),

                html.Div(children="Date Range", className="menu-title"
                ),
					dcc.RangeSlider(
					    id='year-slider',
					    min=2009,
					    max=2018,
					    step=1.0,
					    value=[2009, 2018],
					    allowCross=False,
					    marks=mark_values,
				 	),
				],
            className="wrapper",
        ),

    ]
)

#Populate the options of counties dropdown based on state dropdown
@app.callback(
    Output('filtered_counties','options'),
    Input('state','value')
)
def set_county_options(chosen_state):
	dff = df[df.state == chosen_state]
	return [{'label': c, 'value': c} for c in sorted(dff.county_name.unique())]

# Populate initial values of counties dropdown
@app.callback(
    Output('filtered_counties','value'),
    Input('filtered_counties','options')
)
def set_counties_value(county_options):
	return [x['value'] for x in county_options]

@app.callback(
    Output('PIT-chart', 'figure'),# Output("volume-chart", "figure")],		Input('state', 'value')
	Input('state', 'value'),
	Input('filtered_counties', 'value'),
    Input('type-filter', 'value'),
	Input('year-slider',  'value')
)
def update_charts(selected_state, selected_counties, pop_type, year_range):
	if len(selected_counties) == 0:
		return dash.no_update
	else:
		dff = df[
			(df.state == selected_state)
			& (df.county_name.isin([selected_counties]))
			& (df.pop_type == pop_type)
			& (df.year >= year_range[0])
			& (df.year <= year_range[1])
		]

		PIT_count_figure = {
	        "data": [
	            {
	                "x": dff["year"],
	                "y": dff["pop_size"],
	                "type": "lines",
	                "hovertemplate": "%{y:.2f}<extra></extra>",
	            },
	        ],
	        "layout": {
	            "title": {
	                "text": "Point-in-Time Counts",
	                "x": 0.05,
	                "xanchor": "left",
	            },
	            "xaxis": {"fixedrange": True},
	            "yaxis": {"fixedrange": True},
	            "colorway": ["#17B897"],
	        }
	    }
		return PIT_count_figure #volume_chart_figure

if __name__ == "__main__":
    app.run_server(debug=True)
