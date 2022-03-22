# import chart_studio.plotly as py
# import plotly

import cufflinks as cf
cf.set_config_file(offline=True)

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
dfcp = pdr.get_data_yahoo('005930.KS', '2018-01-01', '2019-12-31')

# QuantFig 매소드를 사용해서 그래프 그리기 -
# 내부적으로 컬럼 이름을  column=self._d['close'] , _d['volume']로 찾는다.
qf=cf.QuantFig(dfcp, title='Samsung', legend='top', name='삼성')
qf.add_bollinger_bands()
qf.add_volume()
qf.add_macd()
qf.
qf.iplot()