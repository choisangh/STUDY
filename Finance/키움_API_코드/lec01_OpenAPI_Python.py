from pykiwoom.kiwoom import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *



kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)
print("블록킹 로그인 완료")

state = kiwoom.GetConnectState()
if state == 0:
    print("미연결")
elif state == 1:
    print("연결완료")

print("==================== 이런 식으로는 호출 불가 ===============")

# @ 오버라이딩
def _handler_tr(screen, rqname, trcode, record, next) :
    print("call back..........................")
    if rqname == "opt10001_req":
        print(kiwoom.GetCommData( "opt10001", "opt10001_req", 0, "종목명"))


kiwoom.SetInputValue("종목코드"	,  "005930");
kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")
kiwoom._set_signals_slots()

kiwoom.ocx.OnReceiveTrData.connect(_handler_tr)
print("=======================================================")

"""
ACCOUNT_CNT	전체 계좌 개수를 반환합니다.
ACCNO	전체 계좌를 반환합니다.
USER_ID	사용자 ID를 반환합니다.
USER_NAME	사용자명을 반환합니다.
KEY_BSECGB	키보드보안 해지여부를 반환합니다. 0: 정상, 1: 해지
FIREW_SECGB	방화벽 설정 여부를 반환합니다. 0: 미설정, 1: 설정, 2: 해지
"""

account_num = kiwoom.GetLoginInfo("ACCOUNT_CNT")        # 전체 계좌수
accounts = kiwoom.GetLoginInfo("ACCNO")                 # 전체 계좌 리스트
user_id = kiwoom.GetLoginInfo("USER_ID")                # 사용자 ID
user_name = kiwoom.GetLoginInfo("USER_NAME")            # 사용자명
keyboard = kiwoom.GetLoginInfo("KEY_BSECGB")            # 키보드보안 해지여부
firewall = kiwoom.GetLoginInfo("FIREW_SECGB")           # 방화벽 설정 여부
print(account_num)
print(accounts)
print(user_id)
print(user_name)
print(keyboard)
print(firewall)

#
# """
# 파라미터	시장
# "0"	코스피
# "3"	ELW
# "4"	뮤추얼펀드
# "5"	신주인수권
# "6"	리츠
# "8"	ETF
# "9"	하이얼펀드
# "10"	코스닥
# "30"	K-OTC
# "50"	코넥스
# """
# kospi = kiwoom.GetCodeListByMarket('0')
# kosdaq = kiwoom.GetCodeListByMarket('10')
# etf = kiwoom.GetCodeListByMarket('8')
# print(len(kospi), kospi)
# print(len(kosdaq), kosdaq)
# print(len(etf), etf)
#
#
#
# name = kiwoom.GetMasterCodeName("005930")
# print(name)
#
# stock_cnt = kiwoom.GetMasterListedStockCnt("005930")
# print("삼성전자 상장주식수: ", stock_cnt)
#
# 상장일 = kiwoom.GetMasterListedStockDate("005930")
# print(상장일)
#
# 전일가 = kiwoom.GetMasterLastPrice("005930")
# print(int(전일가))
#
#
# #----------------------------------------------------------- 1987??년 ~ 현재까지 삼성의 모든 주가 정보 엑셀 저장 ---> 상당시간 걸림
# ref : https://jackerlab.com/kiwoom-api-tr-opt10006/
# TR 요청 (연속조회)
# dfs = []
df = kiwoom.block_request("opt10081",
                          종목코드="005930",
                          기준일자="20200424",
                          수정주가구분=1,
                          output="주식일봉차트조회",
                          next=0)
print(df.head())
df.to_excel("005930.xlsx")
#








# dfs.append(df)
# 
# while kiwoom.tr_remained:
#     df = kiwoom.block_request("OPT10011",
#                               종목코드="005930",
#                               기준일자="20200424",
#                               수정주가구분=1,
#                               output="주식일봉차트조회",
#                               next=2)
#     dfs.append(df)
#     time.sleep(1)
# 
# df = pd.concat(dfs)
# #종목코드	현재가	거래량	거래대금	일자	시가	고가	저가
# df.to_excel("005930.xlsx")