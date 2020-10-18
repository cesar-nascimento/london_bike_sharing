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
        dcc.RangeSlider(
            id='year_select_slider',
            min=df.index.min().year,
            max=df.index.max().year,
            step=None,
            marks={year: str(year)
                   for year in df.index.year.unique()},
            value=[df.index.min().year,
                   df.index.max().year],
            allowCross=False,
        ),
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
            placeholder="Filter weekends"
        ),
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
            placeholder="Filter holidays"
        ),
        # dcc.Dropdown(
        #     id='holiday_select_dropdown',
        #     options=[
        #         {'label': 'Spring', 'value': (1, )},
        #         {'label': 'Summer', 'value': (0, )},
        #         {'label': 'Fall', 'value': (0, )},
        #         {'label': 'Winter', 'value': (0, 1)}
        #     ],
        #     value=(0, 1)
        # ),
        # html.Div(
        #     [
        #         html.Div(
        #             dcc.DatePickerSingle(
        #                 id='date_picker_single',
        #                 min_date_allowed=df.index.min().date(),
        #                 max_date_allowed=df.index.max().date(),
        #                 initial_visible_month=df.index.min().date(),
        #                 date=df.index.min().date(),
        #                 number_of_months_shown=3,
        #             ),
        #             className="mini_container"
        #         ),
        #         html.Div(
        #             [
        #                 html.H6(id='selected_day_container'),
        #                 html.P("Selected day")
        #             ],
        #             className="mini_container"
        #         ),
        #         html.Div(
        #             [html.H6(id='is_holiday_container'),
        #              html.P("Is Holiday")],
        #             className="mini_container"
        #         ),
        #         html.Div(
        #             [html.H6(id='is_weekend_container'),
        #              html.P("Is Weekend")],
        #             className="mini_container"
        #         ),
        #     ],
        #     className="container-display"
        # ),
        dcc.Graph(id='grouped_days_plot', className="pretty_container"),
        dcc.Graph(id='grouped_weather_code_plot', className="pretty_container"),

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
        # Output(
        #     component_id='selected_day_container',
        #     component_property='children'
        # ),
        # Output(
        #     component_id='is_holiday_container', component_property='children'
        # ),
        # Output(
        #     component_id='is_weekend_container', component_property='children'
        # ),
        Output(component_id='grouped_days_plot', component_property='figure'),
        Output(component_id='grouped_weather_code_plot', component_property='figure'),

    ],
    [
        Input(component_id='year_select_slider', component_property='value'),
        Input(
            component_id='weekend_select_dropdown', component_property='value'
        ),
        Input(
            component_id='holiday_select_dropdown', component_property='value'
        )
    ]
)
def update_graph(year_selected, is_weekend, is_holiday):

    # query = df.loc[day_selected]

    # date_object = datetime.strptime(day_selected, '%Y-%m-%d')
    # selected_day_container = date_object.strftime('%B %d, %Y')

    # is_holiday_container = "Is Holiday: {}".format(
    #     query['is_holiday'].mode()[0]
    # )
    # is_weekend_container = "Is Weekend: {}".format(
    #     query['is_weekend'].mode()[0]
    # )

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
    query = dff.groupby(dff.index.hour).agg(
        {
            'cnt': 'mean',
            't1': 'mean',
        }
    ).round(0)

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
        # width=500,
        margin=dict(l=20, r=100, t=20, b=20),
        font_size=10
    )
    fig.update_xaxes(title_text="Hour of the day")
    fig.update_traces(textposition='top center')
    fig.update_yaxes(title_text="Number of Shared Bikes", secondary_y=False)
    fig.update_yaxes(title_text="Average Temperature", range=[0, 40], secondary_y=True)

    def mode_(s):
        try:
            return s.value_counts().index[0]
        except IndexError:
            return 0

    def get_weather_code(n: int):
        code = {
            1: "Clear / mostly clear but have some values with haze/fog/patches of fog / fog in vicinity.",
            2: "Scattered clouds / few clouds.",
            3: "Broken clouds.",
            4: "Cloudy.",
            7: "Rain/ light Rain shower/ Light rain.",
            10: "Rain with thunderstorm.",
            26: "Snowfall.",
            94: "Freezing Fog.",
        }
        if n not in code.keys():
            return("Invalid Weather Code!")
        else:
            return code[n]

    query2 = dff.resample('D').agg(
        {
            'cnt': 'mean',
            'weather_code': mode_,
        }
    ).round(0)

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
    fig2.update_yaxes(title_text="Number of Shared Bikes")
    return fig, fig2


if __name__ == '__main__':
    app.run_server(debug=True)

