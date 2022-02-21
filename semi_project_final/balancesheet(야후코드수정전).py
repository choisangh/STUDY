# ====================================================
#                       패키지
# ====================================================
# -------- data
import pandas as pd
import numpy as np

# -------- str
import re
# -------- date
from datetime import datetime, date
# -------- float
import math

# -------- craw
from bs4 import BeautifulSoup # 클래스라 생성자 만들어야 함
import requests

# -------- flask
from flask import Flask, make_response, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import json

# -------- API
# import yfinance


# --------
# ====================================================
#                      기본 설정
# ====================================================

# ====================================================
#                       함  수
# ====================================================

"""
# 변수 설명
# 크롤링 데이터 : nm(회사명), cd(네이버에서 사용하는 회사 코드)
# 상장 기업 리스트 : corp_name(회사명), stock_code(종목코드), industry(업종), main_product(주요제품), listed_date(상장일), settle_mont(	결산월), pres(대표자명), hpage(홈페이지), region(지역)
# 야후 파이낸스 : yh_code(TODO 변경 필요)
"""

#                   ==============
#                      업종 분류
#                   ==============
# -------- 동일 업종 기업 출력
# TODO(미완성) 동일 업종 선택
def select_same_industry(corp_name):
    indus=com_df[com_df['nm']==corp_name]['industry'].values[0] # TODO(df 확인)

    # print(com_df.groupby(by='industry')['nm'].nunique().max()) # 동종업계 최대 151개 -> 151개 재무제표 크롤링?

    list_com=com_df[com_df['industry']==indus]['corp_name'].values.tolist() # TODO(리스트로???)
    print(list_com) # TODO(print 없앨 예정)
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
# TODO(미완성)
def nm_to_bs_gicode(corp_name):
    gi=com_df[com_df['nm']==corp_name]['cd'] # TODO(데이터 프레임에서 직접 꺼내오지 않게(직접 여기서 크롤링 하는 것보다는 DB에서 꺼내오는 게 나을듯))
    gi=gi.values[0]
    return gi



def stc_code_to_bs_gicode(stock_code):
    gi = com_df[com_df['stock_code'] == stock_code]['cd']  # TODO(데이터 프레임에서 직접 꺼내오지 않게(직접 여기서 크롤링 하는 것보다는 DB에서 꺼내오는 게 나을듯))
    gi = gi.values[0]
    return gi
    # ----------- 검색 용
    # Series.str.contains 외에도 start_with, end_with 등등 있다
    # print(com_df[com_df['nm'].str.contains('카카오')][['cd', 'nm']])
    # print(com_df[com_df['nm'].str.contains('카카오')]['cd'].tolist())



# TODO(미완성)
def yh_code_to_bs_gicode(yh_code):
    print('haha')



# -------- 네이버 금융 크롤링 용 gicode로 변환
def nm_to_fn_gicode(corp_name):
    gi=com_df[com_df['nm']==corp_name]['stock_code'] # TODO(데이터 프레임에서 직접 꺼내오지 않게(직접 여기서 크롤링 하는 것보다는 DB에서 꺼내오는 게 나을듯))
    gi=gi.values[0]
    return gi



# -------- 코드를 기업이름으로 변환
def stc_code_to_nm(stock_code):
    gi = com_df[com_df['stock_code'] == stock_code]['nm']  # TODO(데이터 프레임에서 직접 꺼내오지 않게(직접 여기서 크롤링 하는 것보다는 DB에서 꺼내오는 게 나을듯))
    gi = gi.values[0]
    return gi



#                   ==============
#                     데이터 수집
#                   ==============

# TODO(크롤링 할 건지 API 호출할 건지 & 미완성)
# -------- Balance Sheets API call
def bs_api(corp_name=None, yh_code=None, stock_code=None):
    print('haha')
    # 공공데이터포털 자료



# -------- Balance Sheets Crawling(재무제표 크롤링)
def bs_craw(corp_name=None, yh_code=None, stock_code=None, kind=0): # ------- 검색과 연동해서 입력 변수 설정
    """
    # kind
        : 0 (연간 포괄손익계산서),  1 (분기별 포괄손익계산서)
          2 (연간 재무상태표),     3 (분기별 재무상태표)
          4 (연간 현금흐름표),     5 (분기별 현금프름표)
    """

    # ------- 검색과 연동해서 입력되는 변수 따라 gicode(네이버에서 분류하는 기업 코드)로 변환
    gcode=0
    if corp_name!=None:
        gcode=nm_to_bs_gicode(corp_name)
    elif yh_code!=None:
        gcode=yh_code_to_bs_gicode(yh_code)
    elif stock_code!=None:
        gcode=stc_code_to_bs_gicode(stock_code)

    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?NewMenuID=103&gicode={gcode}"
    # headers = {'User-Agent': 'Mozilla'}
    #
    # res = requests.get(url, headers=headers)
    # soup = BeautifulSoup(res.text, "html.parser")

    table_list = pd.read_html(url, encoding='UTF-8')
    new_table_list = []
    # print(len(table_list))
    # print(table_list[0].head())

    # 항목에서 불필요한 부분 제거('계산에 참여한 계정 펼치기')
    for tbl in table_list:
        for i, idx in enumerate(tbl.iloc[:,0]):
            m = idx.replace('계산에 참여한 계정 펼치기','')
            tbl.iloc[i, 0] = m
        new_table_list.append(tbl)

    return new_table_list[kind]


# ------- 네이버 금융
def fn_craw(corp_name=None, yh_code=None, stock_code=None, kind=0):
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

    gcode = 0
    if corp_name != None:
        gcode = nm_to_fn_gicode(corp_name)
    elif stock_code != None:
        gcode = str(stock_code)

    url = f"https://finance.naver.com/item/main.naver?code={gcode}"
    table_list = pd.read_html(url, encoding='euc-kr')

    return table_list[kind]






#                   ==============
#                      지표 선정
#                   ==============

# -------- 지표 선정
def idv_radar_data(corp_name=None, yh_code=None, stock_code=None):  # TODO(연관기업리스트 for문)
    """
    # <지표 설명> #TODO (추가)
    # 1. 배당 분석                      -> 배당성향(배당 커버리지의 역수.)
    # 2. 유동성 분석(단기채무지급능력)    -> 당좌비율(당좌자산 / 유동부채)
    # 3. 재무건전성 분석(레버리지 비율)   -> 부채비율(총부채 / 자기자본)의 역수
    # 4. 수익성분석                      -> 매출수익성(당기순이익/매출액))
    # 5. 성장성분석                      -> 순이익성장률
    """

    if corp_name != None:
        gcode = nm_to_fn_gicode(corp_name)
        nm = corp_name
    elif stock_code != None:
        gcode = stock_code
        nm = stc_code_to_nm(stock_code)

    sil_df = fn_craw(stock_code=gcode, kind=3)

    if (sil_df.iloc[0:8, 3].isna().sum()) > 0:  # 표 안 가르고 계산하는 건 신규 상장 기업은 정보가 아예 없기 때문
        pass
    if (sil_df.iloc[0:8, 9].isna().sum()) > 0:  # 표 안 가르고 계산하는 건 신규 상장 기업은 정보가 아예 없기 때문
        pass

    else:
        # 0. 재무정보는 최신 분기 실공시 기준
        # 0. 단, 배당은 1년에 한 번 이루어지기 때문에 최신 년도 공시 기준임
        sil_df_y = sil_df['최근 연간 실적'].iloc[:, 3]  # 느리지만 .iloc으로 하는 이유는 공시 날짜가 다른 기업이 있기 때문
        sil_df_q = sil_df['최근 분기 실적'].iloc[:, 4]

        sil_df_y = sil_df_y.fillna(0)
        sil_df_q = sil_df_q.fillna(0)

        if sil_df_y.dtype == 'O':
            sil_df_y[(sil_df_y.str.len() == 1) & (sil_df_y.values == '-')] = 0
            sil_df_y = sil_df_y.astype('float')

        if sil_df_q.dtype == 'O':
            sil_df_q[(sil_df_q.str.len() == 1) & (sil_df_q.values == '-')] = 0
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

        data_list = [bd_tend, dj_rate, bch_rate, suyk, grth]
        data_dict = {nm: data_list}

        return(data_dict)


# -------- 관련 기업 지표 선정
def relate_radar_data(corp_name=None, yh_code=None, stock_code=None):
    label_list=['배당성향', '유동성', '건전성', '수익성', '성장성']
    dict_list = []

    # 주식 코드로 변환
    gcode = 0
    if corp_name != None:
        gcode = nm_to_fn_gicode(corp_name)
    elif stock_code != None:
        gcode = stock_code

    relate_corp = relate_code_crawl(co=gcode)

    dict_list = [idv_radar_data(stock_code=stcd) for stcd in relate_corp]

    dict_list = [x for x in dict_list if x is not None]


    return label_list, dict_list



#                   ==============
#                       시각화
#                   ==============

# -------- 매출, 당기순이익 추이 그래프
def mch_dg(corp_name=None, yh_code=None, stock_code=None):
    gcode=0

    if corp_name != None:
        gcode = nm_to_fn_gicode(corp_name)
        nm = corp_name
    elif stock_code != None:
        gcode = stock_code
        nm = stc_code_to_nm(stock_code)

    bs_df=bs_craw(stock_code=gcode, kind=1)
    label_list=bs_df.columns[1:6].tolist() # 네 분기 + 전년동기
    mch_list=bs_df.loc[0, label_list].tolist() # 매출액
    dg_list=bs_df.loc[15, label_list].tolist() # 당기순이익

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
#                      데이터            # TODO(데이터 저장 다르게)
# ====================================================

# -------- 네이버 company list : nv_com_df
url = "http://comp.fnguide.com/XML/Market/CompanyList.txt"

nv_com_res = requests.get(url)
nv_com_res.encoding = "utf-8-sig"  # # ISO-8859-1

nv_com_json = json.loads(nv_com_res.text)

nv_com_df = pd.DataFrame(data=nv_com_json["Co"])
nv_com_df['gb']=nv_com_df['gb'].astype('int')



# TODO(csv 파일 가져올 경로 설정)
# -------- 상장법인목록(산업 정보 포함) : listed company
listed_comp=pd.read_csv('상장법인목록.csv', dtype=str)
listed_comp.columns=['corp_name', 'stock_code', 'industry', 'main_product','listed_date',  'settle_month', 'presid', 'hpage', 'region']




# TODO(상대 목록에 없는 기업 어떻게 처리할 것인가)
# -------- OUTER JOIN (네이버 company list 상장법인목록(산업 정보 포함))
nv_com_df2=nv_com_df[nv_com_df['gb']==701]
# nv_com_df2.info()
com_df=pd.merge(nv_com_df2, listed_comp, how='outer', left_on= 'nm', right_on= 'corp_name')



# -------- 기업별 산업 코드





# ====================================================
#                  함수 호출(test)
# ====================================================

# df=bs_craw(corp_name='삼성전자', kind=0)
# print(df)
# select_same_industry('삼성전자')




# ====================================================
#                    라우터
# ====================================================

stc_code='005930' # 삼성전자 주식코드
# ------------------

radar_label, radar_dict=relate_radar_data(corp_name=None, yh_code=None, stock_code=stc_code) # TODO: 검색에서 기업 코드/이름 할당 받음
bar_label, bar_mch_list, bar_dg_list = mch_dg(corp_name=None, yh_code=None, stock_code=stc_code) # TODO: 데이터 없으면 0으로 처리하건 해야할듯

