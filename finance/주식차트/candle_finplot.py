import finplot as fplt

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
df = pdr.get_data_yahoo('005930.KS', '2018-01-01', '2019-12-31')
print(df.head())

# import FinanceDataReader as fdr
# df = fdr.DataReader(symbol="KS11", start="2021")

fplt.candlestick_ochl(df[['Open', 'Close', 'High', 'Low']])
fplt.show()