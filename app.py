import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        'weather_code': 'int',
    },
    index_col='timestamp'
)

app.layout = html.Div(
    [
        html.H1("London Bike Sharing Data", style={'text-align': 'center'}),

        # First Row
        html.Div(
            [
                html.Div(
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
                                value=[
                                    df.index.min().year,
                                    df.index.max().year
                                ],
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
                        className="pretty_container"
                    ),
                    className="col-xl-4 col-sm-12",
                    style={'margin': '20px auto'}
                ),

                # Averaged day graph
                html.Div(
                    dcc.
                    Graph(id='grouped_days_plot', className="pretty_container"),
                    className="col-xl-8 col-sm-12",
                    style={'margin': '20px auto'}
                )
            ],
            className="row mx-md-n5",
            style={'margin': '20px auto'}
        ),

        # Second Row
        html.Div(
            [
                html.Div(
                    dcc.Graph(
                        id='grouped_weather_code_plot',
                        className="pretty_container"
                    ),
                    className="col-xl-6 col-sm-12",
                    style={'margin': '20px auto'}
                ),
                html.Div(
                    dcc.Graph(
                        id='grouped_weekdays_plot',
                        className="pretty_container"
                    ),
                    className="col-xl-6 col-sm-12",
                    style={'margin': '20px auto'}
                ),
            ],
            className="row mx-md-n5",
            style={'margin': '20px auto'}
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
    ],
    className="container-fluid"
)

layout_ax = dict(
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor='DarkGray',
    gridcolor="LightGray",
    rangemode="tozero",
)

layout_graph = dict(
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    height=500,
    font_size=15,
)


@app.callback(
    [
        Output('grouped_days_plot', 'figure'),
        Output('grouped_weather_code_plot', 'figure'),
        Output('grouped_weekdays_plot', 'figure'),
    ], [
        Input('year_select_slider', 'value'),
        Input('weekend_select_dropdown', 'value'),
        Input('holiday_select_dropdown', 'value')
    ]
)
def update_graph(year_selected, is_weekend, is_holiday):

    dff = df.copy()

    # Filter is_weekend selection
    if is_weekend is not None:
        weekend_query = dff['is_weekend'] == is_weekend
        dff = dff[weekend_query]

    # Filter is_holiday selection
    if is_holiday is not None:
        holiday_query = dff['is_holiday'] == is_holiday
        dff = dff[holiday_query]

    min_date = str(year_selected[0])
    max_date = str(year_selected[1])

    # Filter years selected

    dff = dff.loc[min_date:max_date]

    # Building first graph
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
        layout_graph,
        title="Average hourly usage",
        height=400,
        margin=dict(l=20, r=100, t=40, b=20),
    )

    fig.update_xaxes(
        layout_ax,
        title_text="Hour of the day",
    )

    fig.update_traces(textposition='top center')
    fig.update_yaxes(
        layout_ax,
        title_text="Average bikes shared",
        range=[0, 4000],
        secondary_y=False
    )
    fig.update_yaxes(
        layout_ax,
        title_text="Average temperature",
        range=[0, 40],
        secondary_y=True
    )

    # Building second graph
    def mode_(s):
        try:
            return s.value_counts().index[0]
        except IndexError:
            return 0

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
        layout_graph,
        title_text="Total bikes shared on a single day, grouped by weather code",
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
        margin=dict(l=20, r=100, t=40, b=20),
    )
    fig2.update_xaxes(title_text="Weather Code")
    fig2.update_yaxes(layout_ax, title_text="Daily total")

    # Building third graph
    by_weekday = query2.groupby(query2.index.dayofweek).mean()
    by_weekday.index = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=by_weekday.index, y=by_weekday['cnt']))
    fig3.update_layout(
        layout_graph,
        title_text="Average daily total, grouped by day of the week",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig3.update_xaxes(layout_ax)
    fig3.update_yaxes(layout_ax, title_text="Average daily total")

    return fig, fig2, fig3


if __name__ == '__main__':
    app.run_server(debug=True)
