import json
import numpy as np
import pandas as pd
from flask import Flask, make_response, jsonify, request, render_template
from datetime import  datetime, date,timedelta
import requests
import yfinance as yf
from code_cr import *
from pykrx import stock
import yfinance
import re
import pandas as pd
import numpy as np
import pandas as pd
from flask import Flask, make_response, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from datetime import datetime , date
from bs4 import BeautifulSoup
import requests   #웹통신
import sqlalchemy as sa
import json



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
import yfinance
import re
import pandas as pd
import numpy as np
import pandas as pd
from flask import Flask, make_response, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from datetime import datetime , timedelta
from bs4 import BeautifulSoup
import requests   #웹통신
import FinanceDataReader as fdr
import json

#                   ==============
#                      업종 분류
#                   ==============
# -------- 동일 업종 기업 출력
# TODO(미완성) 동일 업종 선택
def select_same_industry(corp_name):
    indus=com_df[com_df['nm']==corp_name]['industry'].values[0] # TODO(df 확인)

    # print(com_df.groupby(by='industry')['nm'].nunique().max()) # 동종업계 최대 151개 -> 151개 재무제표 크롤링?

    list_com=com_df[com_df['industry']==indus]['corp_name'].values.tolist()
    return list_com



#  -------- 네이버증권 연관기업 코드(hjh)
def relate_code_crawl(co):
    #연관 종목코드 있는 페이지 불러오기
    url='https://finance.naver.com/item/main.naver?code='+str(co)
    page=pd.read_html(url,encoding='CP949')
    #연관 종목명과 종목코드 뽑아내기(code_list[0]은 '종목명'이어서 제외)
    code_list=page[4].columns.tolist()
    code_list=code_list[1:]
    #종목코드 리스트 반환
    codes=[]
    for word in (code_list):
        codes.append(word[-6:])
    #print(codes)
    return codes

#relate_code_crawl('000660')



#                   ==============
#                  기업 이름 코드 변환
#                   ==============

# -------- 네이버 재무제표 크롤링 용 gicode로 변환
def nm_to_bs_gicode(corp_name):
    gi=com_df[com_df['nm']==corp_name]['cd']
    gi=gi.values[0]
    return gi



def stc_code_to_bs_gicode(stock_code):
    gi = com_df[com_df['stock_code'] == stock_code]['cd']
    gi = gi.values[0]
    return gi



def yh_code_to_bs_gicode(yh_code):
    gi = com_df[com_df['yh_code'] == yhcode]['cd']
    gi = gi.values[0]
    return gi



# -------- 네이버 금융 크롤링 용 gicode로 변환
def nm_to_fn_gicode(corp_name):
    gi=com_df[com_df['nm']==corp_name]['stock_code']
    gi=gi.values[0]
    return gi



def yh_code_to_fn_gicode(yh_code):
    gi=com_df[com_df['yh_code']==yh_code]['stock_code']
    gi=gi.values[0]
    return gi



# -------- 코드를 기업이름으로 변환
def stc_code_to_nm(stock_code):
    gi = com_df[com_df['stock_code'] == stock_code]['nm']
    gi = gi.values[0]
    return gi



def yh_code_to_nm(yh_code):
    gi = com_df[com_df['yh_code'] == yh_code]['nm']
    gi = gi.values[0]
    return gi



#                   ==============
#                     데이터 수집
#                   ==============


# -------- Balance Sheets API call
# def bs_api(corp_name=None, yh_code=None, stock_code=None):
#     print('haha')




# -------- Balance Sheets Crawling(재무제표 크롤링)
# 220220 수정
# 1) 매개변수 stock_code로 축약
# 2) kind로 특정 테이블 지정하는 대신 데이터프레임 리스트 전체 반환
# 3) '~계산에 참여한 계정 펼치기' 제거는 선택사항으로 둠

def bs_craw(stock_code, clear_name=False):  # ------- 검색과 연동해서 입력 변수 설정
    """
    # kind
        : 0 (연간 포괄손익계산서),  1 (분기별 포괄손익계산서)
          2 (연간 재무상태표),     3 (분기별 재무상태표)
          4 (연간 현금흐름표),     5 (분기별 현금프름표)
    """

    # ------- 검색과 연동해서 입력되는 변수 따라 gicode(네이버에서 분류하는 기업 코드)로 변환
    gcode = stc_code_to_bs_gicode(stock_code)

    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?NewMenuID=103&gicode={gcode}"

    table_list = pd.read_html(url, encoding='UTF-8')

    # 항목에서 불필요한 부분 제거('계산에 참여한 계정 펼치기')
    if clear_name == False:
        return table_list

    else:
        new_table_list = []
        for tbl in table_list:
            for i, idx in enumerate(tbl.iloc[:, 0]):
                m = idx.replace('계산에 참여한 계정 펼치기', '')
                tbl.iloc[i, 0] = m
            new_table_list.append(tbl)
        return new_table_list


# ------- 네이버 금융
# 220220 수정
# 1) 매개변수 stock_code로 축약
# 2) kind로 특정 테이블 지정하는 대신 데이터프레임 리스트 전체 반환
def fn_craw(stock_code):
    """
       # kind
           : 0 (전일&당일 상한가, 하한가, 거래량 등) #TODO 가공 필요
             1 (증권사 별 매도 매수 정보) #TODO 가공 필요(컬럼이름)
             2 (외국인, 기관 거래 정보) #TODO 가공 필요
             3 (기업실적분석(연도별 분기별 주요재무 정보)) #TODO 가공 필요?
             4 (동일업종비교) #TODO 가공 필요?
             5 (시가총액, 주식수, 액면가 정보) #TODO 가공 필요
             6 (외국인 주식 한도, 보유 정보)
             7 (목표주가 정보) #TODO 가공 필요
             8 (PER, PBR 배당수익률 정보) (주가 따라 변동) #TODO 가공 필요
             9 (동일업종 PER, 등락률 정보) #TODO 가공 필요
             10 (호가 10단계)
             11 (인기 검색 종목: 코스피) #TODO 가공 필요
             12 (인기 검색 종목: 코스닥) #TODO 가공 필요
       """

    gcode = str(stock_code)

    url = f"https://finance.naver.com/item/main.naver?code={gcode}"
    table_list = pd.read_html(url, encoding='euc-kr')

    return table_list


#                   ==============
#                      지표 선정
#                   ==============

# -------- 지표 선정
# 220220 수정
# 1) 매개변수 stock_code로 축약
# 2) 데이터프레임 하나가 아닌 리스트로 받아오기때문에 kind 제거하고 직접 선택해줌
# 3) sli_df_y, sil_df_q 에서 '-' 가공 시 if 조건에 따라 처리하는 대신 lambda와 re.sub 이용
# 4) dict 대신 array로 반환, 기업 이름(nm도 반환)
def idv_radar_data(stock_code):
    """
    # <지표 설명>
    # 1. 배당 분석                      -> 배당성향(배당 커버리지의 역수.)
    # 2. 유동성 분석(단기채무지급능력)    -> 당좌비율(당좌자산 / 유동부채)
    # 3. 재무건전성 분석(레버리지 비율)   -> 부채비율(총부채 / 자기자본)의 역수
    # 4. 수익성분석                      -> 매출수익성(당기순이익/매출액))
    # 5. 성장성분석                      -> 순이익성장률
    """

    gcode = stock_code
    nm = stc_code_to_nm(stock_code)

    sil_df = fn_craw(gcode)[3]  # 3: 기업실적정보 재무제표 (220220 수정)

    if (sil_df.iloc[0:8, 3].isna().sum()) > 0:  # 표 안 가르고 계산하는 건 신규 상장 기업은 정보가 아예 없기 때문
        pass
    elif (sil_df.iloc[0:8, 9].isna().sum()) > 0:  # 표 안 가르고 계산하는 건 신규 상장 기업은 정보가 아예 없기 때문
        pass


    else:
        # 0. 재무정보는 최신 분기 실공시 기준
        # 0. 단, 배당은 1년에 한 번 이루어지기 때문에 최신 년도 공시 기준임
        sil_df_y = sil_df['최근 연간 실적'].iloc[:, 2]  # 느리지만 .iloc으로 하는 이유는 공시 날짜가 다른 기업이 있기 때문
        sil_df_q = sil_df['최근 분기 실적'].iloc[:, 4]

        sil_df_y = sil_df_y.fillna(0)
        sil_df_q = sil_df_q.fillna(0)

        if sil_df_y.dtype == 'O':
            sil_df_y = sil_df_y.apply(lambda x: re.sub('^-$', '0', '{}'.format(x)))
            sil_df_y = sil_df_y.astype('float')

        if sil_df_q.dtype == 'O':
            sil_df_q = sil_df_q.apply(lambda x: re.sub('^-$', '0', '{}'.format(x)))
            sil_df_q = sil_df_q.astype('float')

        # 1. 배당성향(bd_tend)
        bd_tend = sil_df_y[15]  # 실제 배당 성향

        # 2. 유동성 분석 - 당좌비율(당좌자산/유동부채)
        #                       당좌자산 = (유동자산 - 재고자산)
        dj_rate = sil_df_q[7]  # 당좌비율

        # 3. 재무건전성 분석 - 부채비율(총부채/자기자본)의 역수
        bch_rate = sil_df_q[6] / 100  # 부채비율
        bch_rate = round((1 / bch_rate) * 100, 2)

        # 4. 수익성 분석 - 매출수익성(당기순이익/매출액) # TODO 매출액 0인 애들은?

        dg_bene = sil_df_q[2]
        mch = sil_df_q[0]

        suyk = round((dg_bene / mch) * 100, 2)

        # 5. 성장성 분석 - 순이익성장률(지속성장 가능률)
        # (1-배당성향)*자기자본순이익률(ROE)
        #    유보율

        roe = sil_df_y[5] / 100
        ubo = (100 - bd_tend) / 100
        grth = round(roe * ubo * 100, 2)

        data_arr = np.array([bd_tend, dj_rate, bch_rate, suyk, grth])

        return data_arr, nm


# -------- 관련 기업 지표 선정(상대적 비율 기준)
# 220220 수정
# 1) 매개변수 stock_code로 축약
# 2) dict 대신 array로 반환, 기업 이름(nm도 반환)
def relate_radar_data(stock_code):
    label_list = ['배당성향', '유동성', '건전성', '수익성', '성장성']
    arr_list = []

    # 주식 코드,이름으로 변환

    gcode = stock_code

    relate_corp = relate_code_crawl(co=gcode)

    arr_list = [idv_radar_data(stock_code=stcd) for stcd in relate_corp]
    nm_list = [x[1] for x in arr_list if x is not None]
    arr_list = [x[0] for x in arr_list if x is not None]

    arr_list = np.array(arr_list)

    arr_list[:, 0] = (arr_list[:, 0] / arr_list[:, 0].mean()) * 100
    arr_list[:, 1] = (arr_list[:, 1] / arr_list[:, 1].mean()) * 100
    arr_list[:, 2] = (arr_list[:, 2] / arr_list[:, 2].mean()) * 100
    arr_list[:, 3] = (arr_list[:, 3] / arr_list[:, 3].mean()) * 100
    arr_list[:, 4] = (arr_list[:, 4] / arr_list[:, 4].mean()) * 100

    dict_list = []

    for i, nm in enumerate(nm_list):
        dic = {}
        dic[nm] = arr_list[i, :].tolist()
        dict_list.append(dic)

    return label_list, dict_list


# -------- 관련 기업 지표 선정(원본)

# def relate_radar_data(yh_code=None, corp_name=None, stock_code=None):
#     label_list=['배당성향', '유동성', '건전성', '수익성', '성장성']
#     dict_list = []
#
#     # 주식 코드로 변환
#     gcode = 0
#     if yh_code != None:
#         gcode = yh_code_to_fn_gicode(yh_code)
#     elif corp_name != None:
#         gcode = nm_to_fn_gicode(corp_name)
#     elif stock_code != None:
#         gcode = stock_code
#
#     relate_corp = relate_code_crawl(co=gcode)
#
#     dict_list = [idv_radar_data(stock_code=stcd) for stcd in relate_corp]
#
#     dict_list = [x for x in dict_list if x is not None]
#
#
#     return label_list, dict_list


#                   ==============
#                       시각화
#                   ==============

# -------- 매출, 당기순이익 추이 그래프
# 220220 수정
# 1) 매개변수 stock_code로 축약
# 2) 크롤링한 데이터는 list로 받아오므로 kind 없애고 직접 인덱스 처리

def mch_dg(stock_code):
    gcode = stock_code
    nm = stc_code_to_nm(stock_code)

    bs_df = bs_craw(stock_code=gcode)[0]
    label_list = bs_df.columns[1:6].tolist()  # 네 분기 + 전년동기
    mch_list = bs_df.loc[0, label_list].tolist()  # 매출액
    dg_list = bs_df.loc[15, label_list].tolist()  # 당기순이익

    return label_list, mch_list, dg_list


# -------- BS TABLE (재무상태표 필요 없다 ^^)
# def bs_table(corp_name=None, yh_code=None, stock_code=None):
#     df=bs_craw(corp_name=cor_name, yh_code=yh_code, stock_code=stock_code, kind=1)
#     df
#     """
#     # kind
#         : 0 (연간 포괄손익계산서),  1 (분기별 포괄손익계산서)
#           2 (연간 재무상태표),     3 (분기별 재무상태표)
#           4 (연간 현금흐름표),     5 (분기별 현금프름표)
#     """


# tot_list = []
# print(box_list)
#
# for box in box_list:
#     print(box)
#     for item in box:
#         title = box.select_one('th > div').text
#         print(item)
# list=[]
# price1 = box.select_one("th > div").text
# price2 = box.select_one("").text
#
# list.append(price1)
# list.append(price2)
#
# tot_list.append(list)

# 프레임 만드는 게 주 목적이면 df=pd.DataFrame(data=tot_list) 하고 return df
# df = pd.DataFrame(data=tot_list)
# return tot_list  # [[],[],[]]




# ====================================================
#                      데이터
# ====================================================

# -------- 병합 파일 불러오기
com_df=pd.read_csv('com_df.csv',
                   dtype={'stock_code': 'str', '표준코드': 'str', '단축코드': 'str', 'stock_code_ori':'str'},
                   parse_dates=['listed_date', '상장일'])




def news_crawl(gi):


    tot_list = []

    for p in range(1):
        # 뉴스 기사 모인 페이지
        url = 'https://m.stock.naver.com/domestic/stock/' + str(gi) + '/news/title'  # https://m.stock.naver.com/domestic/stock/003550/total
        #F12누르면 나오는 네트워크상에서 찾아온 경로
        #https://m.stock.naver.com/api/news/stock/005930?pageSize=20&page=1&searchMethod=title_entity_id.basic
        url = "https://m.stock.naver.com/api/news/stock/"+str(gi)+"?pageSize=5&searchMethod=title_entity_id.basic&page=1"
        res = requests.get(url)

        news_list = json.loads(res.text)
        #페이지에서 가져온 전체 뉴스기사를 for문으로 분리
        #print(news_list[0])
        for i, news in enumerate(news_list) :
            #신문사 id
            a=news['items'][0]['officeId']
            #기사 id
            b=news['items'][0]['articleId']
            list = []
            list.append(news['items'][0]['officeName']) #신문사
            list.append(news['items'][0]['datetime'][:8]) #날짜
            list.append(news['items'][0]['title'].replace('&quot;','\"')) #제목
            list.append(news['items'][0]['imageOriginLink']) #이미지
            list.append(news['items'][0]['body'].replace('&quot;','\"')) # 기사 내용
            list.append('https://m.stock.naver.com/domestic/stock/005930/news/view/'+str(a)+'/'+str(b)) #기사 url
            tot_list.append(list)

    news_df = pd.DataFrame(data=tot_list, columns=['offname','rdate','title','imgsrc','content','url'])
    news_df['title'] = news_df['title'].str.replace('&amp;', '&')
    news_df['content'] = news_df['content'].str.replace('&amp;', '&')

    #news_df['title'] = [re.sub('[^A-Za-z0-9가-힣]', '' ,s) for s in news_df['title']]


    #news_df.to_csv('css.csv',index=False)
    return news_df

#co-종목코드
def relate_code_crawl(co):
    #연관 종목코드 있는 페이지 불러오기
    url='https://finance.naver.com/item/main.naver?code='+str(co)
    page=pd.read_html(url,encoding='CP949')
    #연관 종목명과 종목코드 뽑아내기(code_list[0]은 '종목명'이어서 제외)
    code_list=page[4].columns.tolist()
    code_list=code_list[1:]
    #종목코드 리스트 반환
    codes=[]
    for word in (code_list):
        codes.append(word[-6:])
    #print(codes)
    return codes


# def before_1w_kospi(date):
#     before1w=date-timedelta(days=7)
#     return fdr.DataReader('KS11',before1w)[['Close']]#, fdr.DataReader('KQ11',before1w)

def invest_opinion(gcode):
    url='https://finance.naver.com/item/coinfo.naver?code='+str(gcode)
    page=pd.read_html(url,encoding='CP949')
    try:
        a,b=page[3][1].tolist()[0][:4].split('.')
        return ((int(a)+int(b)/100)/5)*100 #의견 점수 구한 후 백분율로 다시 변환
    except ValueError:
        return 0.1
#최상현 함수
def crawl_ifrs(gcode):
    url = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A" + gcode + "&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=701"
    table_list = pd.read_html(url, encoding='UTF-8')

    ifrs = table_list[10]

    ifrs = ifrs.fillna('9999999999')
    for i in range(1, 9):
        ifrs.iloc[:, i] = ifrs.iloc[:, i].apply(lambda x: format(float(x), ','))
    ifrs = ifrs.astype(str)
    for i in range(1, 9):
        ifrs.iloc[:12, i] = ifrs.iloc[:12, i].apply(lambda x: x[:-2])
        ifrs.iloc[18:21, i] = ifrs.iloc[18:21, i].apply(lambda x: x[:-2])
        ifrs.iloc[23:24, i] = ifrs.iloc[23:24, i].apply(lambda x: x[:-2])
    ifrs = ifrs.replace(['9,999,999,999', '9,999,999,999.0', '99999999', '9999999999'], ['-', '-', '-', '-'])
    ifrs = ifrs.to_html(justify="right", index=False, classes="table")
    ifrs = ifrs.replace('border="1"', 'border="0"')
    pd.options.display.float_format = '{:,.0f}'.format
    ifrs = ifrs.replace('<td>', '<td align="right">')
    ifrs = ifrs.replace('<th>', '<th style="text-align: right;">')
    ifrs = ifrs.replace('halign="left"', 'style="text-align: center;"')
    ifrs = ifrs.replace('class ="dataframe table"', 'class ="dataframe table" style = "table-layout:fixed;word-break:break-all;"')


    return (ifrs)

def ori_code(yh_code):
    origin_stock=com_df[com_df['yh_code']==yh_code]['stock_code_ori'].values[0]
    return origin_stock












if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8088, threaded=True)