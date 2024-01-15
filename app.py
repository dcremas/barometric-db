from pathlib import Path

import pandas as pd
import numpy as np

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Div, Select, RangeTool, HoverTool, Paragraph
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme

from models import airports, data, headers, update

df = pd.DataFrame(data, columns=headers)
df['time'] = np.array(df['time'], dtype=np.datetime64)
dates = np.array(df['time'], dtype=np.datetime64)
source = ColumnDataSource(data=dict(date=df[df['station_name'] == airports[0]]['time'],
                                    pressure=df[df['station_name'] == airports[0]]['pressure_in']))

plot = figure(tools="xpan", x_axis_type="datetime", x_axis_location="above",
              x_range=(dates[0], dates[479]), y_range=(28.5, 31.5), margin=(10, 10, 10, 15),
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
                margin=(10, 10, 10, 15), 
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef",
                sizing_mode="stretch_width")

range_tool = RangeTool(x_range=plot.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line('date', 'pressure', source=source)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)

select_airport = Select(title="Select Airport:", value="", options=airports, margin=(10, 10, 10, 15))
select_airport.on_change('value', callback)

update_text_1 = f'The Postgresql AWS Cloud Database that feeds the visuals was last updated:'
update_text_2 = f'Date: {update.strftime("%d %B, %Y")}'
update_text_3 = f'Time: {update.strftime("%I:%M:%S %p")}'

p1 = Paragraph(text=update_text_1, width=800, height=10, margin=(25, 25, 5, 15))
p2 = Paragraph(text=update_text_2, width=800, height=10, margin=(5, 25, 5, 15))
p3 = Paragraph(text=update_text_3, width=800, height=10, margin=(5, 25, 25, 15))

hyperlink_div = Div(
    text="""<a href="https://dataviz.dustincremascoli.com">Go back to Data Visualizations Main Page</a>""",
    width=400, height=100, margin=(10, 10, 10, 15)
    )

curdoc().add_root(column(desc, select_airport, plot, select, p1, p2, p3, hyperlink_div, sizing_mode="stretch_width"))
curdoc().theme = Theme(filename="theme.yaml")
curdoc().title = '10 Day Historical & Forecasted Hourly Barometric Pressure'
