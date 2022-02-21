import json
import numpy as np
import pandas as pd
from flask import Flask, make_response, jsonify, request, render_template
from datetime import  datetime, date,timedelta
import requests
import yfinance as yf
from code_cr import *
from pykrx import stock


# ====================================================
#                      데이터
# ====================================================

# -------- 병합 파일 불러오기
com_df=pd.read_csv('com_df.csv',
                   dtype={'stock_code': 'str', '표준코드': 'str', '단축코드': 'str', 'stock_code_ori':'str'},
                   parse_dates=['listed_date', '상장일'])


app = Flask(__name__, template_folder="production", static_folder="build")


@app.route('/')
def index():

    return render_template("index.html")

#---------------- 업체이름을 타이핑할때마다 실시간 비동기로 업체 명단을 가져와서 리턴 -----------
@app.route('/com_search_ajax', methods=['post'])
def com_search_ajax():

    str = request.form.get('search_input')
    print(str)


    com_df = pd.read_csv("com_df.csv")

    #-----------웹에서 입력한 검색어와 관련된 업체만 가져오기 -----------------
    temp = com_df[(com_df['한글 종목명'].str.contains(str))|(com_df['한글 종목명'].str.contains(str.upper()))][['yh_code', '한글 종목명']].head()
    print(temp.values.tolist())
    return json.dumps(  temp.values.tolist()  )



#=============================================== form get
@app.route('/form_submit_get', methods=["get"])
def form_submit_get():

    # input = request.args.get("search_input")  # name="userid"
    # corpname= request.args.get("lec20_flask.py0_name")
    hidden_stock_code = request.args.get("hidden_stock_code")
    hidden_corp_name = request.args.get("hidden_corp_name")
    origin_code=ori_code(hidden_stock_code)



    print(hidden_corp_name)
    stock_code= hidden_stock_code[:-3]

    radar_label, radar_dict = relate_radar_data(stock_code=origin_code)

    bar_label, bar_mch_list, bar_dg_list = mch_dg(stock_code=origin_code)

    df = news_crawl(origin_code) #우선주말고 보통주로 검색
    ifrs=crawl_ifrs(origin_code) #우선주말고 보통주로 검색

    # print(df.head())
    html = df.to_html()

    json_str = df.to_json(orient="values")  # <class 'str'> [[1,2,3],[10,20,30]]
    json_obj = json.loads(json_str)


    code = invest_opinion(origin_code)
    print(code)

    # kms re 변수변경
    chart_res = chart_data(hidden_stock_code)
    f_info = finance_data(hidden_stock_code)
    # end

    print("form_submit_get.....--------------------------------....실행",hidden_stock_code,stock_code)
    #print(radar_dict,radar_label)
    return render_template("res.html", ifrs = ifrs, res_obj=chart_res,
                           hidden_corp_name=hidden_corp_name,
                           f_info=f_info,
                           RD_LABEL_LIST=radar_label,RD_DATA_DICT=radar_dict,
                           BAR_LABEL_LIST=bar_label,
                           BAR_DATA_LIST_MCH=bar_mch_list,
                           BAR_DATA_LIST_DG=bar_dg_list,MY_NEWS=json_obj, MY_CODE=code)     #render_template("index.html", MY_MSG="ok")
#=============================================== form get

# chart_data : KMS 2022.02.21
# 사용자가 선택한 날짜에 맞추어 해당 기업의 주가정보를 반영해 주는 함수.
# 날짜지정을 하지 않을경우 해당기업의 1년 주가정보를 반영.
#######kms re start
def chart_data(ent, select_date = None):
    ent = ent.split(".")[0]
    if (select_date != None):
        ent_df = stock.get_market_ohlcv_by_date(fromdate=select_date[0], todate=select_date[1], ticker=ent)

    else:
        e_date = datetime.now()
        s_date = e_date - timedelta(days=365)
        print(f"s_date .................: {s_date}")
        ent_df = stock.get_market_ohlcv_by_date(fromdate=s_date, todate=e_date, ticker=ent)
    ent_df = ent_df.reset_index()
    ent_df = ent_df.drop(['시가', '고가', '저가', '거래량'], axis=1)
    ent_df.columns = ['Date', 'Close']
    ent_df['Date'] = ent_df['Date'].astype('str')
    ent_dict = ent_df.to_dict()

    dfcp = ent_df.tail(2)
    rate_color = dfcp['Close'].values.tolist()
    ent_dict['eve'] = rate_color[0]
    ent_dict['today'] = rate_color[1]
    if (rate_color[1] - rate_color[0] < 0):
        ent_dict['rate'] = "fa fa-sort-desc"
        ent_dict['color'] = 'blue'
    else:
        ent_dict['rate'] = "fa fa-sort-asc"
        ent_dict['color'] = 'red'

    res = {'ent':ent, 'ent_dict':ent_dict}
    return res

# 비동기통신을 이용하여 사용자가 선택한 날짜를 yfinance에서 요구하는 날짜로 재가공처리해주는 함수.
@app.route('/calendar_ajax_handle', methods=["post"])
def calendar_ajax_handle():
    data = request.form.get("prm")
    ent_name = request.form.get("ent")
    splt_data = data.split(":")
    se_list = []
    for my_day in splt_data:

        se_list.append(str(datetime.strptime(my_day, "%m/%d/%Y").date()))
    print(f'ent_name............. : {ent_name}')
    res = chart_data(ent_name, se_list)
    return res

# 2022-02-21 KMS
# 기업(stock_code) ,코스피, 코스닥, 나스탁, 다우, S&p500 전날 현재 가격가져오는 함수.
# 전날 지수와 현재 지수 비교하여 html class에 뿌려줄 data ; [rate, color]
def finance_data(stock_code):
    stock_list = ['^KS11','^KQ11', '^IXIC', '^GSPC', '^DJI']
    res_list = {}
    for stock in stock_list:
        yf_df = yf.download(stock ,start = '2022-01-01')
        se_list = round(yf_df.tail(2).reset_index()['Close'].astype('float'), 2)
        if(se_list[1]-se_list[0] < 0):
            se_list['rate'] = "fa fa-sort-desc"
            se_list['color'] = 'blue'
        else:
            se_list['rate'] = "fa fa-sort-asc"
            se_list['color'] = 'red'
        res_list[stock] = se_list
    return res_list
# kms re end

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8088, threaded=True)