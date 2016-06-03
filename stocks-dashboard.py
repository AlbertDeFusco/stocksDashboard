import pandas as pd
import numpy as np
from pandas_datareader import data
import datetime

from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HBox, VBoxForm
from bokeh.models import BoxZoomTool, ResetTool, WheelZoomTool, PanTool, HoverTool, CrosshairTool
from bokeh.models.widgets import Slider, TextInput, Panel, Tabs
from bokeh.io import curdoc


def get_stock_data(ticker, start='1990-1-1', end=datetime.date.today()):
    return data.DataReader(ticker, 'yahoo', start, end)


def compute_moving_averages(df, short, long):
    df['mav_short'] = df['Close'].rolling(window=short).mean()
    df['mav_long'] = df['Close'].rolling(window=long).mean()


def compute_signals(df):
    if 'mav_short' not in df:
        raise ValueError('moving average columns missing')

    def cross(x):
        short = x['mav_short']
        long = x['mav_long']
        if short > long:
            return 1
        else:
            return 0

    df['position'] = 0
    df['position'] = df.apply(cross, axis=1).diff()





# input controls
ticker = TextInput(title="Ticker to plot (Yahoo name)", value='^GSPC')
start_year = Slider(title='Start Year', start=1950, end=2016, value=2000, step=1)
end_year = Slider(title='End Year',     start=1950, end=2016, value=2016, step=1)
mav_short = Slider(title='Short Average', start = 0, end=100, value=50, step=1)
mav_long = Slider(title='Long Average', start = 0, end=400, value=200, step=1)


# initialize the sources
source = ColumnDataSource(data=dict(date=[], lnprice=[], price=[], mav_short=[], mav_long=[]))
buy = ColumnDataSource(data=dict(x=[], y=[], pos=[], price=[]))
sell = ColumnDataSource(data=dict(x=[], y=[], pos=[], price=[]))

def make_plot(yscale='linear'):
    # configure the tools
    width_zoom={'dimensions':['width']}
    tools = [tool(**width_zoom) for tool in [BoxZoomTool, WheelZoomTool]]

    hover_pos = HoverTool(
            names=['buy','sell'],
            tooltips=[
              ('Position','@pos'),
              ('Date','@date'),
              ('Price','@price')
            ]
    )
    hover_pos.name = 'Postions'


    tools.extend([PanTool(), hover_pos, ResetTool(), CrosshairTool()])

    # prepare plot
    p = Figure(plot_height=600, plot_width=800, title="Moving Average Positions",
            x_axis_type='datetime', y_axis_type=yscale, tools=tools)

    p.line(x='date', y='price', alpha=0.3, color='Black', line_width=2, source=source, legend='Close', name='price')
    p.line(x='date', y='mav_short', color='DarkBlue', line_width=2, source=source, legend='Short MAV')
    p.line(x='date', y='mav_long', color='FireBrick', line_width=2, source=source, legend='Long MAV')
    p.inverted_triangle(x='x', y='y', color='Crimson', size=20, alpha=0.7, source=sell, legend='Sell', name='sell')
    p.triangle(x='x', y='y', color='ForestGreen', size=20, alpha=0.7, source=buy, legend='Buy', name='buy')

    return p



plot = make_plot()


def select_years():
    start = datetime.date(start_year.value,1,1)
    end   = datetime.date(end_year.value,12,31)
    long = mav_long.value
    short = mav_short.value
    symbol = ticker.value.strip()

    df = get_stock_data(symbol, start, end)
    compute_moving_averages(df, short, long)
    compute_signals(df)

    return df

def update(attrname, old, new):
    df = select_years()

    source.data = dict(
            date = df.index,
            price = df['Close'],
            lnprice = np.log(df['Close']),
            mav_short = df['mav_short'],
            mav_long = df['mav_long'],
            day = df.index.strftime('%b %-d')
            )

    buy_idx = df['position'] == 1
    sell_idx = df['position'] == -1
    df['pos'] = df['position'].map({1:'Buy',-1:'Sell'})

    buy.data = dict(
            x = df.loc[buy_idx].index,
            y = df.loc[buy_idx, 'mav_short'],
            price = df.loc[buy_idx, 'Close'].apply(lambda x: '%.2f' % x),
            pos = df.loc[buy_idx, 'pos'],
            date = df.loc[buy_idx].index.strftime('%b %-d'))
    sell.data = dict(
            x = df.loc[sell_idx].index,
            y = df.loc[sell_idx, 'mav_short'],
            price = df.loc[sell_idx, 'Close'].apply(lambda x: '%.2f' % x),
            pos = df.loc[sell_idx, 'pos'],
            date = df.loc[sell_idx].index.strftime('%b %-d'))


controls = [ticker, start_year, end_year, mav_short, mav_long]
for control in controls:
    control.on_change('value', update)

inputs = HBox(VBoxForm(*controls), width=300)

update(None, None, None) # initial load of the data

curdoc().add_root(HBox(inputs, plot, width=1100))
