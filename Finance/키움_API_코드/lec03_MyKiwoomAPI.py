from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pythoncom

class MyKiwoomAPI(QAxWidget):
    def __init__(self, login=False):
        super().__init__()
        self.set_kiwoom_api()
        self.set_event_slot()
        self.ret_data = {}
        self.output_list = []

        if login:
            self.CommConnect()

    # ---------------------------------------------------------------------------------
    def set_kiwoom_api(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    # TR/실시간 요청 콜백메서드 등록
    def set_event_slot(self):
        self.OnReceiveTrData.connect(self.callback_TrData)
        self.OnReceiveRealData.connect(self.callback_RealData)
        self.OnEventConnect.connect(self.E_OnEventConnect)

    def E_OnEventConnect(self, nErrCode):
        # print(nErrCode)
        self.event_loop_CommConnect.exit()

    ## TR 요청 ##
    # def E_OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
    def callback_TrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
        print("callback_TrData:",sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg)
        self.Call_TR(sTrCode, sRQName)
        self.event_loop_CommRqData.exit()

    ## 실시간 요청 ##
    # def E_OnReceiveRealData(self, sCode, sRealType, sRealData):
    def callback_RealData(self, sCode, sRealType, sRealData):
        # print(sCode, sRealType, sRealData)
        pass

    # ---------------------------------------------------------------------------------
    # OpenAPI+ Python 용 오버라이딩
    # ---------------------------------------------------------------------------------
    def CommConnect(self):
        self.dynamicCall('CommConnect()')
        self.event_loop_CommConnect = QEventLoop()
        self.event_loop_CommConnect.exec_()

    # 로그인 상태
    def GetConnectState(self):
        ret = self.dynamicCall('GetConnectState()')
        # print(ret)

    def GetLoginInfo(self, kind=''):
        ret = self.dynamicCall('GetLoginInfo(String)', kind)
        # print(ret)


    # 조회 요청
    def CommRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        # self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen)
        ret = self.dynamicCall('CommRqData(String, String, int, String)', sRQName, sTrCode, nPrevNext, sScreenNo)
        self.event_loop_CommRqData = QEventLoop()
        self.event_loop_CommRqData.exec_()
        # print(ret)

    # 조회 요청 시 TR의 Input 값 지정
    def SetInputValue(self, sID, sValue):
        # self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)
        ret = self.dynamicCall('SetInputValue(String, String)', sID, sValue)

    # 조회 수신한 멀티 데이터의 개수(Max : 900개)
    def GetRepeatCnt(self, sTrCode, sRecordName):
        # count = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        count = self.dynamicCall('GetRepeatCnt(String, String)', sTrCode, sRecordName)
        return count

    # TR 요청 : 결과 받아오기
    def GetCommData(self, strTrCode, strRecordName, nIndex, strItemName):
        # data = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item)
        ret = self.dynamicCall('GetCommData(String, String, int, String)', strTrCode, strRecordName, nIndex, strItemName)
        return ret.strip()

    # 실시간 요청 : 결과 받아오기
    def GetCommRealData(self, sCode, sFid):
        # data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        ret = self.ocx.dynamicCall("GetCommRealData(QString, int)", sCode, sFid)
        return ret.strip()


    # ---------------------------------------------------------------------------------
    # TR 요청
    # ---------------------------------------------------------------------------------
    # def _handler_tr(self, screen, rqname, trcode, record, next):
    def Call_TR(self, strTrCode, sRQName):
        self.ret_data[strTrCode] = {}
        self.ret_data[strTrCode]['Data'] = {}

        self.ret_data[strTrCode]['TrCode'] = strTrCode

        count = self.GetRepeatCnt(strTrCode, sRQName)
        self.ret_data[strTrCode]['Count'] = count

        if count == 0:
            temp_list = []
            temp_dict = {}

            for output in self.output_list:
                data = self.GetCommData(strTrCode, sRQName, 0, output)
                # print(data)
                temp_dict[output] = data

            temp_list.append(temp_dict)

            self.ret_data[strTrCode]['Data'] = temp_list

        if count >= 1:
            temp_list = []
            for i in range(count):
                temp_dict = {}
                for output in self.output_list:
                    data = self.GetCommData(strTrCode, sRQName, i, output)
                    temp_dict[output] = data

                temp_list.append(temp_dict)

            self.ret_data[strTrCode]['Data'] = temp_list