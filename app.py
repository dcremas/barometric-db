from pathlib import Path

import pandas as pd
import numpy as np

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Div, Select, RangeTool, HoverTool
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme

from models import airports, data, headers

df = pd.DataFrame(data, columns=headers)
df['time'] = np.array(df['time'], dtype=np.datetime64)
dates = np.array(df['time'], dtype=np.datetime64)
source = ColumnDataSource(data=dict(date=df[df['station_name'] == airports[0]]['time'],
                                    pressure=df[df['station_name'] == airports[0]]['pressure_in']))

plot = figure(tools="xpan", x_axis_type="datetime", x_axis_location="above",
              x_range=(dates[0], dates[479]), y_range=(29.0, 31.0),
              sizing_mode="stretch_width")
plot.add_tools(HoverTool(tooltips=[('Date', '@date{%F}'), ('Time', '@date{%I:%M %p}'), ('Pressure', '@pressure{0.2f}')],
                         formatters={'@date': 'datetime'}, mode='vline'))
plot.line('date', 'pressure', source=source)
plot.circle('date', 'pressure', source=source, fill_color="white", size=2)
plot.yaxis.axis_label = 'Barometric Pressure'

desc = Div(text=(Path(__file__).parent / "description.html").read_text("utf8"), sizing_mode="stretch_width",
           margin=(2, 2, 2, 15))

def callback(attr, old, new):
    if new == 0:
        data = dict(date=df[df['station_name'] == old]['time'],
                    pressure=df[df['station_name'] == old]['pressure_in'])
    else:
        data = dict(date=df[df['station_name'] == new]['time'],
                    pressure=df[df['station_name'] == new]['pressure_in'])
    source.data = data

select = figure(title="Drag the middle and edges of the selection box to change the range above",
                height=130, width=800, y_range=plot.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef",
                sizing_mode="stretch_width")

range_tool = RangeTool(x_range=plot.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line('date', 'pressure', source=source)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)

select_airport = Select(title="Select Airport:", value="", options=airports)
select_airport.on_change('value', callback)

curdoc().add_root(column(desc, select_airport, plot, select, sizing_mode="stretch_width"))
curdoc().theme = Theme(filename="theme.yaml")
curdoc().title = 'Seven Day Historical & Forecasted Barometric Pressure'
