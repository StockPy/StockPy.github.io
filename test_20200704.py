# -*- coding: CP949 -*-

import os
import win32com.client
import pythoncom
import datetime, time

# %load init_Stock.py
from init_Stock import *

##################################################
# Argument Inform

##################################################
def __StandbyCall():
    start_time = "09:00"
    print("# Standby Start : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    while datetime.datetime.today().strftime("%H:%M") < start_time : # ---> start_time보다 크면 while문 빠져나감, 시작 Call
        now_time = datetime.datetime.today().strftime("%H:%M:%S")
        print("# Ready to Start ..... now %s" % (now_time))
        time.sleep(10)
    print("\n# Standby End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))

##################################################
def __Init_Conn() :

    class XASessionEventHandler:
        login_state = 0

        def OnLogin(self, code, msg):
            if code == "0000":
                print("로그인 성공")
                XASessionEventHandler.login_state = 1
            else:
                print("로그인 실패")

    instXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)

#     id, passwd, cert_passwd = "cchoi", "1234a", ""
#     id, passwd, cert_passwd = "cchoi", "dlfdl12", "dlftka13!#"

    # 접속할 서버의 기본 주소는 'hts.ebestsec.co.kr'인데 모의 투자인 경우에는 'demo.ebestsec.co.kr'을 사용
    #instXASession.ConnectServer("demo.ebestsec.co.kr", 20001)
    instXASession.ConnectServer("hts.ebestsec.co.kr", 20001)
    #instXASession.ConnectServer("211.216.52.140", 20001) # 211.216.52.129 (dev-center), 211.216.52.140 (XingACE), 211.216.52.135 (???)
    #instXASession.ConnectServer("211.216.52.129", 20001) # 211.216.52.129 (dev-center), 211.216.52.140 (XingACE), 211.216.52.135 (???)
    instXASession.Login(id, passwd, cert_passwd, 0, 0)

    while XASessionEventHandler.login_state == 0:
        pythoncom.PumpWaitingMessages()

    num_account = instXASession.GetAccountListCount()
    for i in range(num_account):
        account = instXASession.GetAccountList(i)
        print("계좌번호 : %s" % (account))

##################################################
# 주문 : 종목번호, 매수2호가

def __Stock_Order(Target_Expcode, Order_type, Price) :
    
    print("# __Stock_Order Start : %s, hcode : %s, Price : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode, Price))
    ##################################################
    # 현물 정상주문
    class XAQueryEventHandlerCSPAT00600:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerCSPAT00600.query_state = 1
            
        def OnReceiveMessage(self, error, code, message):
            print("OnreceiveMessage", error, code, message)
            
    ##################################################
    # print(type(Price_Check_HIDHO2)) # <class 'str'>
    # print(type(OneTime_Price)) # <class 'int'>
    Buy_Qty = OneTime_Price/int(Price) # ValueError: invalid literal for int() with base 10: ''
    Buy_Qty = int(float(Buy_Qty))# <class 'float'> ---> <class 'int'>
    print("Check ARG : %s, %s, %s" % (Buy_Qty, Price, OneTime_Price))
#     print(type(Buy_Qty)) # <class 'int'>
#     print(type(Price)) # <class 'str'>
#     print(type(OneTime_Price)) # <class 'int'>
    
    instXAQueryCSPAT00600 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerCSPAT00600)
    instXAQueryCSPAT00600.ResFileName = "C:\\eBEST\\xingAPI\\Res\\CSPAT00600.res"
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "AcntNo", 0, Account_No)
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "InptPwd", 0, Account_PWD)
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "IsuNo", 0, Target_Expcode)
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdQty", 0, Buy_Qty) # 매수 수량
    if Order_type == 1 :
        print("매도")
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdPrc", 0, Price) # 매수 가격
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "BnsTpCode", 0, 2) # 1 : 매도, 2 : 매수
    elif Order_type == 2 :
        print("매수")
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdPrc", 0, Price) # 매수 가격
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "BnsTpCode", 0, 2) # 1 : 매도, 2 : 매수
    else :
        print("---> 매수도 매도도 아닌 상황???")
        return None
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdprcPtnCode", 0, "00") # 00 : 지정가, 03 : 시장가
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "MgntrnCode", 0, "000") # 신용거래코드 : 000 보통
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdCndiTpCode", 0, "00") # 주문조건구분 : 0 그냥 0

    instXAQueryCSPAT00600.Request(0) # Request 메서드를 호출해서 입력 데이터를 서버로 전송

    while XAQueryEventHandlerCSPAT00600.query_state == 0: # 서버에 TR 요청을 했다면 해당 작업이 완료됐다는 이벤트를 받을 때까지 프로그램이 종료되지 않고 대기
        pythoncom.PumpWaitingMessages()

#     ReceiveMessage = instXAQueryCSPAT00600.GetFieldData(ReceiveMessage() # AttributeError: '<win32com.client.COMEventClass instance at 0x80428624>' object has no attribute 'ReceiveMessage'
#     print(ReceiveMessage)
    
    instXAQueryCSPAT00600_count1 = instXAQueryCSPAT00600.GetBlockCount("CSPAT00600InBlock1")
    instXAQueryCSPAT00600_count2 = instXAQueryCSPAT00600.GetBlockCount("CSPAT00600InBlock2")
    print("instXAQueryCSPAT00600_count1 : %s" % (instXAQueryCSPAT00600_count1))
    print("instXAQueryCSPAT00600_count2 : %s" % (instXAQueryCSPAT00600_count2))
    
    RecCnt = instXAQueryCSPAT00600.GetFieldData("CSPAT00600InBlock1", "RecCnt", 0)
    print("# 레코드 카운트 RecCnt : %s" % (RecCnt))
#     hname = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "hname", 0)
#     price = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "price", 0)
#     bidho22 = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "bidho22", 0)
#     offerho2 = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "offerho2", 0)
#     print("종목 : %s, 가격 : %s, 매수호가2 : %s, 매도호가2 : %s" % (hname, price, bidho2, offerho2))
#     retrun bidho2
    
    print("# __Stock_Order End : %s, hcode : %s, Price : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode, Price))
        
    instXAQueryCSPAT00600.close()

##################################################
# Target_Expcode 현재 가격을 조회 (매수2호가)
def __Price_Check(Target_Expcode) :
    print("# Price_Check Start : %s, hcode : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode))
    ##################################################
    # 주식 현재가 호가 조회
    class XAQueryEventHandlerT1101:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerT1101.query_state = 1
    ##################################################
    instXAQueryT1101 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT1101)
    instXAQueryT1101.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1101.res"
    instXAQueryT1101.SetFieldData("t1101InBlock", "shcode", 0, Target_Expcode)
    
    instXAQueryT1101.Request(0) # Request 메서드를 호출해서 입력 데이터를 서버로 전송

    while XAQueryEventHandlerT1101.query_state == 0: # 서버에 TR 요청을 했다면 해당 작업이 완료됐다는 이벤트를 받을 때까지 프로그램이 종료되지 않고 대기
        pythoncom.PumpWaitingMessages()

    hname = instXAQueryT1101.GetFieldData("t1101OutBlock", "hname", 0)
    price = instXAQueryT1101.GetFieldData("t1101OutBlock", "price", 0)
    bidho2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho2", 0)
    offerho2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho2", 0)
    print("종목 : %s, 가격 : %s, 매수호가2 : %s, 매도호가2 : %s" % (hname, price, bidho2, offerho2))
    
    print("# Price_Check End : %s, hcode : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode))

    return price, bidho2
    
    instXAQueryT1101.close()
    
################################################## 
# 주문 내역이 있는지 확인하는 Function : 없으면 CallNothing 0를 return
def __Call_Check(Target_Expcode) :
    print("# Call_Check Start : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    ##################################################
    # 주식체결 조회2
    class XAQueryEventHandlerT0425:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerT0425.query_state = 1
    ##################################################
    
    print("Call Check about Target_Expcode : %s" % (Target_Expcode))
    
    instXAQueryT0425 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0425)
    instXAQueryT0425.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0425.res"
    instXAQueryT0425.SetFieldData("t0425InBlock", "accno", 0, Account_No) # XAQuery 인스턴스를 통해 SetFieldData라는 메서드를 호출한 후 적절한 인자 값을 지정
    instXAQueryT0425.SetFieldData("t0425InBlock", "passwd", 0, Account_PWD)
    instXAQueryT0425.SetFieldData("t0425InBlock", "sortgb", 0, 1) # sorting, 매매구분 정보를 넣어야 for문으로 전체 리스트 가져온다
    instXAQueryT0425.SetFieldData("t0425InBlock", "medosu", 0, 0) # sorting, 매매구분 정보를 넣어야 for문으로 전체 리스트 가져온다
    
    instXAQueryT0425.Request(0) # Request 메서드를 호출해서 입력 데이터를 서버로 전송

    while XAQueryEventHandlerT0425.query_state == 0: # 서버에 TR 요청을 했다면 해당 작업이 완료됐다는 이벤트를 받을 때까지 프로그램이 종료되지 않고 대기
        pythoncom.PumpWaitingMessages()
        # 이베스트투자증권의 서버는 TR 처리가 완료되면 OnReceiveData 메서드를 콜백합니다.
        # 이로 인해 XAQueryEventHandlerT1102.query_state 값이 1로 변경되어 이벤트 대기 루프에서 exit

    count = instXAQueryT0425.GetBlockCount("t0425OutBlock")
#     print("Block Count : %s" % (count)) # ---> 여기서 0 체크해도 될듯
    tqty = instXAQueryT0425.GetFieldData("t0425OutBlock", "tqty", 0) # 총 주문수량
    tcheqty = instXAQueryT0425.GetFieldData("t0425OutBlock", "tcheqty", 0) # 총 체결수량
    tamt = instXAQueryT0425.GetFieldData("t0425OutBlock", "tamt", 0) # 총 주문금액
    tmsamt = instXAQueryT0425.GetFieldData("t0425OutBlock", "tmsamt", 0) # 총 매수체결액
    tmdamt = instXAQueryT0425.GetFieldData("t0425OutBlock", "tmdamt", 0) # 총 매도체결액
    print("총 주문수량 : %s, 총 체결수량 : %s, 총 주문금액 : %s, 총 매수액 : %s, 총 매도액 : %s" % (tqty, tcheqty, tamt, tmsamt, tmdamt))
    if tqty == "" or tqty == "0":
#         print("# No All Call ---> Need Call Expcode")
        CallNothing = 0
        print("# Call_Check End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
        return CallNothing # 주문값이 전혀 없으면 바로 call 하고 아래로 넘어가지 않기 위해서...되나?

    count1 = instXAQueryT0425.GetBlockCount("t0425OutBlock1")
#     print("Block Count : %s" % (count1))
    account_expcode = []
    for i in range(count1):
        ordno = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordno", i) # 주문번호
        expcode = instXAQueryT0425.GetFieldData("t0425OutBlock1", "expcode", i) # 종목번호
        medosu = instXAQueryT0425.GetFieldData("t0425OutBlock1", "medosu", i) # 구분
        qty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "qty", i) # 주문수량
        price = instXAQueryT0425.GetFieldData("t0425OutBlock1", "price", i) # 주문가격
        cheqty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cheqty", i) # 체결수량
        cheprice = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cheprice", i) # 체결가격
        ordrem = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordrem", i) # 미체결 잔량
        cfmqty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cfmqty", i) # 확인 수량
        status = instXAQueryT0425.GetFieldData("t0425OutBlock1", "status", i) # 상태
        print("주문번호 : %s, 종목번호 : %s, 구분 : %s, 주문수량 : %s, 주문가격 : %s, 체결수량 : %s, 체결가격 : %s, 미체결잔량 : %s, 확인수량 : %s, 상태 : %s" % (ordno, expcode, medosu, qty, price, cheqty, cheprice, ordrem, cfmqty, status))
        print("Call Check TEST 2")
        account_expcode.append(expcode)

    #if Call_Expcode not in account_expcode : # ---> Argu로 종목번호를 받자
    if Target_Expcode not in account_expcode : # ---> Argu로 종목번호를 받자
#         print("# Call Expcode : %s" % Target_Expcode)
#         print("# No in any Call Order---> Need Call Expcode")
        CallNothing = 0
#         print("CallNothing : %s" % (CallNothing))
#         print("Call Check TEST 3 ---> End")
        return CallNothing
        
    print("# Call_Check End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    print("\n\n\n")
    
    instXAQueryT0425.close()

##################################################
def __Start_Service() :
    stop_time = "23:50"
    print("# Start_Service Start : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    ##################################################
    # 주식잔고 조회2
    class XAQueryEventHandlerT0424:
        query_state = 0
        
        def OnReceiveData(self, code):
            XAQueryEventHandlerT0424.query_state = 1
    ##################################################
    
    instXAQueryT0424 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0424)
    instXAQueryT0424.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0424.res"
    instXAQueryT0424.SetFieldData("t0424InBlock", "accno", 0, Account_No) # XAQuery 인스턴스를 통해 SetFieldData라는 메서드를 호출한 후 적절한 인자 값을 지정
    instXAQueryT0424.SetFieldData("t0424InBlock", "passwd", 0, Account_PWD)
    
    instXAQueryT0424.Request(0) # Request 메서드를 호출해서 입력 데이터를 서버로 전송

    while XAQueryEventHandlerT0424.query_state == 0: # 서버에 TR 요청을 했다면 해당 작업이 완료됐다는 이벤트를 받을 때까지 프로그램이 종료되지 않고 대기
        pythoncom.PumpWaitingMessages()
        # 이베스트투자증권의 서버는 TR 처리가 완료되면 OnReceiveData 메서드를 콜백합니다.
        # 이로 인해 XAQueryEventHandlerT1102.query_state 값이 1로 변경되어 이벤트 대기 루프에서 exit
    
    t0424_count1 = instXAQueryT0424.GetBlockCount("t0424OutBlock1")
    print("t0424 Call : %s" % (t0424_count1))
    
    while datetime.datetime.today().strftime("%H:%M") < stop_time :
        print("# Time Check : %s " % (datetime.datetime.today().strftime("%H:%M:%S")))
        today_sum = 0
        Account_Expcode = []
        for i in range(t0424_count1):
            expcode = instXAQueryT0424.GetFieldData("t0424OutBlock1", "expcode", i)
            hname = instXAQueryT0424.GetFieldData("t0424OutBlock1", "hname", i) # 종목명
            janqty = instXAQueryT0424.GetFieldData("t0424OutBlock1", "janqty", i) # 잔고수량
            mdposqt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mdposqt", i) # 매도 가능수량
            pamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "pamt", i) # 평균단가
            sunikrt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "sunikrt", i) # 수익율
            mamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mamt", i) # 매입금액
            appamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "appamt", i) # 평가금액
            dtsunik = instXAQueryT0424.GetFieldData("t0424OutBlock1", "dtsunik", i) # 평가손익
            print("종목번호 : %s, 종목명 : %s, 잔고수량 : %s, 평단 : %s, 수익 : %s, 매입액 : %s, 평가금 : %s, 손익 : %s" % (expcode, hname, janqty, pamt, sunikrt, mamt, appamt, dtsunik))
#             print(type(sunikrt)) #  ---> int로 했으나 안되고 float에서 됨 (if문)
            sunikrt = float(sunikrt) # <class 'str'> ---> <class 'float'>
            appamt = int(appamt) # <class 'str'> ---> <class 'int'>
#             print(type(Limited_Amount)) # <class 'int'>
            
            # 수익률에 따라 매수, 매도 조건
            if (expcode == Target_Expcode) and (sunikrt < Buy_Condition) : # 수익이 Buy보다 작다
                print("비교1 : 수익 %s 대 조건 %s" % (sunikrt, Buy_Condition))
                print("---> Buy 매수 조건 만족 : 물타기")
                if appamt > Limited_Amount :
                    print("Limited_Amount 초과 : %s" % Limited_Amount)
                    return None
                Call_Check_Value = __Call_Check(Target_Expcode) # 일단 오늘 주문 내역이 있는지 확인 (CallNothing 0를 받았는지 체크)
#                 print("Call_Check_Value : %s" % Call_Check_Value)# <class 'int'>
                if Call_Check_Value == 0 :
                    Stock_Price, Price_Check_HIDHO2 = __Price_Check(Target_Expcode) # Target_Expcode의 현재 가격을 조회 (매수2호가)
#                     print(Stock_Price, Price_Check_HIDHO2)
                    __Stock_Order(Target_Expcode, 2, Price_Check_HIDHO2) # 주문 : 종목번호, 매수2호가, # 1 : 매도, 2 : 매수
                    File_Name = "D:\\Python\\Order_History.txt"
                    output = open(File_Name, "a")
                    output.write("매수 ---> %s : 종목 %s, %s " % (datetime.datetime.today().strftime("%Y%m%d"), Target_Expcode, Price_Check_HIDHO2))
                    output.write("\n")
                    output.close() # ---> close 가 되어야 write 처리가 완료된다
            elif (expcode == Target_Expcode) and (sunikrt > Sell_Condition) : # 수익이 Sell보다 크다
                print("비교2 : 수익 %s 대 조건 %s" % (sunikrt, Buy_condition))
                if appamt > Limited_Amount : # 수익실현 단계에서는 없어도 되지만 추가
                    print("Limited_Amount 초과 : %s" % Limited_Amount)
                    return None
                print("---> Sell 매도 조건 만족 : 수익실현")
                Call_Check_Value = __Call_Check(Target_Expcode) # 일단 오늘 주문 내역이 있는지 확인 (CallNothing 0를 받았는지 체크)
#                 print("Call_Check_Value : %s" % Call_Check_Value)# <class 'int'>
                if Call_Check_Value == 0 :
                    Stock_Price, Price_Check_HIDHO2 = __Price_Check(Target_Expcode) # Target_Expcode의 현재 가격을 조회 (매수2호가)
#                     print(Stock_Price, Price_Check_HIDHO2)
                    __Stock_Order(Target_Expcode, 1, Stock_Price) # 주문 : 종목번호, 매수2호가, # 1 : 매도, 2 : 매수
                    File_Name = "D:\\Python\\Order_History.txt"
                    output = open(File_Name, "a")
                    output.write("매도 ---> %s : 종목 %s, %s " % (datetime.datetime.today().strftime("%Y%m%d"), Target_Expcode, Stock_Price))
                    output.write("\n")
                    output.close() # ---> close 가 되어야 write 처리가 완료된다
            else :
                print("만족하는 조건 없음")

            today_sum += int(appamt)
            Account_Expcode.append(expcode)
#         print(Account_Expcode) # 계좌에 있는 종목 리스트
        
        # 현재 계좌에 코스닥 레버리지가 있는지 찾는다, 없으면 매수
        #if '233160' not in account_expcode :
        if Target_Expcode not in Account_Expcode :
            print("---> 자산 내 대상 종목 없음")
#             print(Target_Expcode)
            Call_Check_Value = __Call_Check(Target_Expcode) # 일단 오늘 주문 내역이 있는지 확인 (CallNothing 0를 받았는지 체크)
            print("Call_Check_Value : %s" % Call_Check_Value)# <class 'int'>
            if Call_Check_Value == 0 :
                Stock_Price, Price_Check_HIDHO2 = __Price_Check(Target_Expcode) # Target_Expcode의 현재 가격을 조회 (매수2호가)
                print(Stock_Price, Price_Check_HIDHO2)
                __Stock_Order(Target_Expcode, 2, Price_Check_HIDHO2) # 주문 : 종목번호, 매수2호가, # 1 : 매도, 2 : 매수
                File_Name = "D:\\Python\\Order_History.txt"
                output = open(File_Name, "a")
                output.write("매수 ---> %s : 종목 %s, %s " % (datetime.datetime.today().strftime("%Y%m%d"), Target_Expcode, Price_Check_HIDHO2))
                output.write("\n")
                output.close() # ---> close 가 되어야 write 처리가 완료된다
        
        print("")
        time.sleep(60) # ---> 체결량 조회 등 60초 미만일 경우 처리 안되는 듯
        
    File_Name = "D:\\Python\\Account_History.txt"
    output = open(File_Name, "a")
    output.write("%s : %s " % (datetime.datetime.today().strftime("%Y%m%d"), today_sum))
    output.write("\n")
    output.close() # ---> close 가 되어야 write 처리가 완료된다
    
    print("\n# Start_Service End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    
##################################################
# class 를 먼저 등록한다.
# 다시 실행하려고 해도 class를 우선 수행한뒤에 XAQuery 를 실행시켜야 한다. (2020.06.20)
# SetFieldData의 1번째 파라미터는 블록명이고
# 2번째 파라미터는 필드명입니다.
# 3번째 파라미터에는 단일 데이터를 조회할 때는 0을 지정하면 되고
# 4번째 파라미터는 필드에 해당하는 입력값

if __name__ == '__main__' :
    print("Buy_Condition : %s" % Buy_Condition)
    print("Sell_Condition : %s" % Sell_Condition)
    print("# Main Start_0")
    __StandbyCall()
    print("# Init Connection")
    __Init_Conn()
    print("# Main Start_1")
    __Start_Service()
    print("# Main Start_2")
