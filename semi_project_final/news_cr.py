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

app = Flask(__name__,template_folder="production", static_folder="build") #, template_folder="", static_folder="")
CORS(app)


def get_code():
    # ---------------------------------------------
    # 네이버금융 : 시황 업체 목록 가져오기
    # ---------------------------------------------
    # 네이버 증권사 : ISO-8859-1
    url = "http://comp.fnguide.com/XML/Market/CompanyList.txt"
    com_res = requests.get(url)

    com_res.encoding = "utf-8-sig"
    com_json = json.loads(com_res.text)  # {"Co" : [ {},{},{}] }

    com_df = pd.DataFrame(data=com_json["Co"])  # [ {},{},{}]

    return com_df


def news_crawl(gi):
    #gi는 종목 이름
    dd = get_code()
    # 종목 코드 뽑아내기
    gi=str(dd.loc[dd['nm'][dd['nm']==gi].index,'cd'].tolist()[0])[1:]


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

    #news_df['title'] = [re.sub('[^A-Za-z0-9가-힣]', '' ,s) for s in news_df['title']]


    #news_df.to_csv('css.csv',index=False)
    return news_df










# {'total': 1,
#  'items': [{'id': '0090004922779',
#             'officeId': '009',
#             'articleId': '0004922779',
#             'officeName': '매일경제',
#             'datetime': '202202161618',
#             'type': 1,
#             'title': '&quot;노동3권 보장은 거짓, 직접 만나자&quot;…삼성 노조, 경영진에 대화 요청',
#             'body': '임금협상을 두고 회사와 대립하고 있는 삼성전자 노조가 이재용 부회장 등 최고경영진과의 직접 대화를 요청했다. 16일 전국삼성전자노조 등 삼성전자 내 4개 노조가 결성한 공동교섭단에 따르면 이들은 이날 오전 서울 서초구 삼성전자... ',
#             'photoType': 1,
#             'imageOriginLink': 'https://imgnews.pstatic.net/image/origin/009/2022/02/16/4922779.jpg?type=nf220_150',
#             'titleFull': '&quot;노동3권 보장은 거짓, 직접 만나자&quot;…삼성 노조, 경영진에 대화 요청'}
#            ]
#  }
#<img src="https://imgnews.pstatic.net/image/origin/009/2022/02/16/4922939.jpg?type=nf220_150" class="img" width="103" height="70" data-src="https://imgnews.pstatic.net/image/origin/009/2022/02/16/4922939.jpg?type=nf220_150" alt="LG엔솔 &amp;quot;배터리 성장의 핵심은 상생과 협력&amp;quot;">