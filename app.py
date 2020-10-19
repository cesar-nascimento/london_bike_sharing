import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

app = dash.Dash(__name__)
server = app.server

url = "https://raw.githubusercontent.com/cesar-nascimento/london_bike_sharing/master/london_bike_sharing_dataset.csv"

df = pd.read_csv(
    url,
    parse_dates=['timestamp'],
    dtype={
        'is_holiday': 'bool',
        'is_weekend': 'bool',
        'season': 'category',
    },
    index_col='timestamp'
)

app.layout = html.Div(
    [
        html.H1("London Bike Sharing Data", style={'text-align': 'center'}),
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Filter by year."),
                        dcc.RangeSlider(
                            id='year_select_slider',
                            min=df.index.min().year,
                            max=df.index.max().year,
                            step=None,
                            marks={
                                year: str(year)
                                for year in df.index.year.unique()
                            },
                            value=[df.index.min().year,
                                   df.index.max().year],
                            allowCross=False,
                            className="card"
                        ),
                        html.H4("Filter by weekend / workday."),
                        dcc.Dropdown(
                            id='weekend_select_dropdown',
                            options=[
                                {
                                    'label': 'Only Weekends',
                                    'value': 1
                                }, {
                                    'label': 'Only Weekdays',
                                    'value': 0
                                }
                            ],
                            placeholder="Filter weekends",
                            className="card"
                        ),
                        html.H4("Filter by holiday / workday."),
                        dcc.Dropdown(
                            id='holiday_select_dropdown',
                            options=[
                                {
                                    'label': 'Only Holidays',
                                    'value': 1
                                }, {
                                    'label': 'Only Non Holidays',
                                    'value': 0
                                }
                            ],
                            placeholder="Filter holidays",
                            className="card"
                        ),
                    ],
                    className="col-sm-4 pretty_container"
                ),
                dcc.Graph(
                    id='grouped_days_plot',
                    className="col-sm-8 pretty_container"
                )
            ],
            className="row"
        ),
        html.Div(
            dcc.Graph(id='grouped_weather_code_plot', className="col-sm-6 pretty_container"),
            className="row"
        ),

        # Source Link
        html.H5(
            [
                "Source: ",
                html.A(
                    "https://www.kaggle.com/hmavrodiev/london-bike-sharing-dataset",
                    href=
                    "https://www.kaggle.com/hmavrodiev/london-bike-sharing-dataset",
                    target="_blank"
                )
            ]
        ),
    ]
)


@app.callback(
    [
        Output('grouped_days_plot', 'figure'),
        Output('grouped_weather_code_plot', 'figure'),
    ], [
        Input('year_select_slider', 'value'),
        Input('weekend_select_dropdown', 'value'),
        Input('holiday_select_dropdown', 'value')
    ]
)
def update_graph(year_selected, is_weekend, is_holiday):

    # Filter is_weekend selection

    dff = df.copy()

    if is_weekend is not None:
        weekend_query = dff['is_weekend'] == is_weekend
        dff = dff[weekend_query]

    # Filter is_holiday selection
    if is_holiday is not None:
        holiday_query = dff['is_holiday'] == is_holiday
        dff = dff[holiday_query]

    min_date = f"{year_selected[0]}"
    max_date = f"{year_selected[1]}"

    # Filter year selected
    dff = dff.loc[min_date:max_date]
    query = dff.groupby(dff.index.hour).agg({
        'cnt': 'mean',
        't1': 'mean',
    }).round(0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=query.index,
            y=query['cnt'],
            mode="lines+markers",
            name="Avg. nº of bikes shared"
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=query.index,
            y=query['t1'],
            mode="lines+markers",
            marker_symbol="triangle-up",
            name='Avg. temperature (Cº)',
            line={'dash': 'dash'}
        ),
        secondary_y=True,
    )

    fig.update_layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        height=400,
        margin=dict(l=20, r=100, t=20, b=20),
        font_size=15
    )
    fig.update_xaxes(title_text="Hour of the day")
    fig.update_traces(textposition='top center')
    fig.update_yaxes(
        title_text="Avg. bikes shared hourly",
        secondary_y=False
    )
    fig.update_yaxes(
        title_text="Average temperature", range=[0, 40], secondary_y=True
    )

    def mode_(s):
        try:
            return s.value_counts().index[0]
        except IndexError:
            return 0

    def get_weather_code(n: int):
        code = {
            1:
                "Clear / mostly clear but have some values with haze/fog/patches of fog / fog in vicinity.",
            2:
                "Scattered clouds / few clouds.",
            3:
                "Broken clouds.",
            4:
                "Cloudy.",
            7:
                "Rain/ light Rain shower/ Light rain.",
            10:
                "Rain with thunderstorm.",
            26:
                "Snowfall.",
            94:
                "Freezing Fog.",
        }
        if n not in code.keys():
            return ("Invalid Weather Code!")
        else:
            return code[n]

    query2 = dff.resample('D').agg({
        'cnt': 'sum',
        'weather_code': mode_,
    }).round(0)

    fig2 = go.Figure()
    for weather_code, group in query2.groupby('weather_code'):
        if weather_code not in (1, 2, 3, 4, 7, 10, 26, 94):
            continue
        fig2.add_trace(go.Box(y=group["cnt"], name=f"Code: {weather_code}"))
    fig2.update_layout(
        legend_title_text="Weather Code:<br>\
        1 = Clear / mostly clear but have some values with<br>\
            haze/fog/patches of fog / fog in vicinity.<br>\
        2 = Scattered clouds / few clouds.<br>\
        3 = Broken clouds.<br>\
        4 = Cloudy.<br>\
        7 = Rain/ light Rain shower/ Light rain.<br>\
        10 = Rain with thunderstorm.<br>\
        26 = Snowfall.<br>\
        94 = Freezing Fog.<br>\
            ",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        height=400,
        margin=dict(l=20, r=100, t=20, b=20),
        font_size=10
    )
    fig2.update_xaxes(title_text="Weather Code")
    fig2.update_yaxes(title_text="Total number of bikes shared in a single day")
    return fig, fig2


if __name__ == '__main__':
    app.run_server(debug=True)
