import sys
from PyQt5.QtWidgets import *
from pkg.lec03_MyKiwoomAPI import MyKiwoomAPI
from pkg.lec03_MyConfig import *


class MyKiwoonClass:
    def __init__(self):
        self.kiwoom = MyKiwoomAPI()
        self.kiwoom.CommConnect()

    def OPT10001(self):
        self.kiwoom.output_list = output_list['OPT10001']
        #-------------------------------------------------------------------------------KOA Studio SA 카피부분---------
        self.kiwoom.SetInputValue("종목코드", "005930")
        self.kiwoom.CommRqData("OPT10001", "OPT10001", 0, "0101")
        # ------------------------------------------------------------------------------------------------------------
        return self.kiwoom.ret_data['OPT10001']

    def GetLoginInfo(self):
        # 로그인 상태
        # self.kiwoom.GetConnectState()
        # 로그인 정보
        self.kiwoom.GetLoginInfo("ACCOUNT_CNT")
        self.kiwoom.GetLoginInfo("USER_ID")
        self.kiwoom.GetLoginInfo("USER_NAME")
        # self.kiwoom.GetLoginInfo("ACCLIST")
        # self.kiwoom.GetLoginInfo("KEY_BSECGB")
        # self.kiwoom.GetLoginInfo("FIREW_SECGB")
        # self.kiwoom.GetLoginInfo("GetServerGubun")

app = QApplication(sys.argv)
my = MyKiwoonClass()
my.GetLoginInfo()

res = my.OPT10001()
print(res)  # {'Data': [{'종목코드': '005930', '종목명': '삼성전자', '결산월': '12', '액면가': '100', '자본금': '7780', '상장주식': '5969783', ...
print(res['Data'][0]['종목명'])

