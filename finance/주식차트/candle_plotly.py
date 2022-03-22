import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
df = pdr.get_data_yahoo('005930.KS', '2018-01-01', '2019-12-31')
print(df.head())

fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.show()