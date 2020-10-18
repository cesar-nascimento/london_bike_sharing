import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date


app = dash.Dash(__name__)
server = app.server
 
df = pd.read_csv(
    "./london_bike_sharing_dataset.csv",
    parse_dates=['timestamp'],
    dtype={
        'is_holiday': 'bool',
        'is_weekend': 'bool',
        'season': 'category',
    },
    index_col='timestamp'
)

app.layout = html.Div([

    html.H1("London Bike Sharing Data", style={'text-align': 'center'}),    

    html.Div(
        [
            html.Div(
                dcc.DatePickerSingle(
                    id='date_picker_single',
                    min_date_allowed=df.index.min().date(),
                    max_date_allowed=df.index.max().date(),
                    initial_visible_month=df.index.min().date(),
                    date=df.index.min().date(),
                    number_of_months_shown=3,
                ),
                className="mini_container" 
            ),
            html.Div(
                [html.H6(id='selected_day_container'), html.P("Selected day")],
                className="mini_container"
            ),
            html.Div(
                [html.H6(id='is_holiday_container'), html.P("Is Holiday")],
                className="mini_container"
            ),
            html.Div(
                [html.H6(id='is_weekend_container'), html.P("Is Weekend")],
                className="mini_container"
            ),
            
        ],
        className="container-display"
    ),

    dcc.Graph(id='london_day_map', className="pretty_container"),
    
    
    # Source Link
    html.Div(
        html.H5([
            "Source: ",
            html.A(
                "https://www.kaggle.com/hmavrodiev/london-bike-sharing-dataset",
                href="https://www.kaggle.com/hmavrodiev/london-bike-sharing-dataset",
                target="_blank")
        ]),
    ),
])


@app.callback(
    [
        Output(component_id='selected_day_container', component_property='children'),
        Output(component_id='is_holiday_container', component_property='children'),
        Output(component_id='is_weekend_container', component_property='children'),
        Output(component_id='london_day_map', component_property='figure')
    ],
    [
        Input(component_id='date_picker_single', component_property='date')
    ]
)
def update_graph(day_selected):
    
    
    dff = df.copy()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    query = df.loc[day_selected]
    
    date_object = date.fromisoformat(day_selected)
    selected_day_container = date_object.strftime('%B %d, %Y')
    
    is_holiday_container = "Is Holiday: {}".format(query['is_holiday'].mode()[0])    
    is_weekend_container = "Is Weekend: {}".format(query['is_weekend'].mode()[0])
    
    
    fig.add_trace(
        go.Scatter(
            x=query.index,
            y=query['cnt'],
            mode="lines+markers",
            name="Bike count"
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=query.index,
            y=query['t1'],
            mode="lines+markers",
            marker_symbol="triangle-up",
            name='Temperature (Cº)',
            line={'dash': 'dash'}
        ),
        secondary_y=True,
    )

    def get_weather_code(n:int):
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

    fig.add_trace(
        go.Scatter(
        x=query.index,
        y=query['weather_code'],
        name="Weather Code:<br>\
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
        text=query['weather_code'].apply(lambda x: get_weather_code(x)),
        line_shape='hv', line={'width': 1}),
        secondary_y=True,
    )

    fig.update_layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        height=700,
        margin=dict(l=20, r=350, t=20, b=20),
        font_size=15
    )
    fig.update_traces(textposition='top center')
    fig.update_yaxes(range=([0, 8000] if query['cnt'].max() >= 5500 else [0, 6000]), secondary_y=False)
    fig.update_yaxes(range=[0, 40], secondary_y=True)
    
    return selected_day_container, is_holiday_container, is_weekend_container, fig



if __name__ == '__main__':
    app.run_server(debug=True)