#!/usr/bin/env python
# coding: utf-8

# In[12]:


import os
import win32com.client
import pythoncom
import datetime, time
import sys

from init_test import *

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
                File_Name = "D:\\Python\\Log\\Login_History.txt"
                output = open(File_Name, "a")
                output.write("로그인 에러 ---> %s \n" % (datetime.datetime.today().strftime("%Y%m%d %H%M")))
                output.close() # ---> close 가 되어야 write 처리가 완료된다

    instXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)

    instXASession.ConnectServer(Server_Name, 20001)
    instXASession.Login(id, passwd, cert_passwd, 0, 0)

    while XASessionEventHandler.login_state == 0:
        pythoncom.PumpWaitingMessages()

    num_account = instXASession.GetAccountListCount()
    for i in range(num_account):
        account = instXASession.GetAccountList(i)
        print("계좌번호 : %s" % (account))
        
##################################################
def __Check_Account() :

    # 주식잔고 조회2
    class XAQueryEventHandlerT0424:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerT0424.query_state = 1

    instXAQueryT0424 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0424)
    instXAQueryT0424.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0424.res"

    instXAQueryT0424.SetFieldData("t0424InBlock", "accno", 0, Account_No) # XAQuery 인스턴스를 통해 SetFieldData라는 메서드를 호출한 후 적절한 인자 값을 지정
    instXAQueryT0424.SetFieldData("t0424InBlock", "passwd", 0, Account_PWD)
    instXAQueryT0424.Request(0) # Request 메서드를 호출해서 입력 데이터를 서버로 전송

    while XAQueryEventHandlerT0424.query_state == 0: # 서버에 TR 요청을 했다면 해당 작업이 완료됐다는 이벤트를 받을 때까지 프로그램이 종료되지 않고 대기
        pythoncom.PumpWaitingMessages()
        # 이베스트투자증권의 서버는 TR 처리가 완료되면 OnReceiveData 메서드를 콜백합니다.
        # 이로 인해 XAQueryEventHandlerT1102.query_state 값이 1로 변경되어 이벤트 대기 루프에서 exit

    count1 = instXAQueryT0424.GetBlockCount("t0424OutBlock1")
    print(count1)

    File_Name = "D:\\Python\\Log\\My_Account_Stock_History.txt"
    output = open(File_Name, "a")
    for i in range(count1):
        expcode = instXAQueryT0424.GetFieldData("t0424OutBlock1", "expcode", i)
        hname = instXAQueryT0424.GetFieldData("t0424OutBlock1", "hname", i) # 종목명
        janqty = instXAQueryT0424.GetFieldData("t0424OutBlock1", "janqty", i) # 잔고수량
        mdposqt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mdposqt", i) # 매도 가능수량
        pamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "pamt", i) # 평균단가
        mamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mamt", i) # 매입금액
        appamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "appamt", i) # 평가금액
        dtsunik = instXAQueryT0424.GetFieldData("t0424OutBlock1", "dtsunik", i) # 평가손익
        sunikrt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "sunikrt", i) # 수익율
        print("종목번호 : %s, 종목명 : %s, 잔고수량 : %s, 평단 : %s, 매입액 : %s, 손액 : %s, 손익 : %s" % (expcode, hname, janqty, pamt, mamt, dtsunik, sunikrt))
        output.write("종목번호 : %s, 종목명 : %s, 잔고수량 : %s, 평단 : %s, 매입액 : %s, 손액 : %s, 손익 : %s\n" % (expcode, hname, janqty, pamt, mamt, dtsunik, sunikrt))
        output.write("\n")
    output.close()

################################################## 
# 주문 내역이 있는지 확인하는 Function : 없으면 CallNothing 0를 return
def __Call_Check_Day() :
    print("# Call_Check Start : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    time.sleep(1) # 자주 호출하면 먹통이 되는 거 같아서 sleep 추가, CPU Full 도 이것때문 (2020.07.16)
    ##################################################
    File_Name = "D:\\Python\\Log\\My_Account_Stock_History.txt"
    
    # 주식체결 조회2
    class XAQueryEventHandlerT0425:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerT0425.query_state = 1

    instXAQueryT0425 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0425)
    instXAQueryT0425.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0425.res"
    instXAQueryT0425.SetFieldData("t0425InBlock", "accno", 0, Account_No) # XAQuery 인스턴스를 통해 SetFieldData라는 메서드를 호출한 후 적절한 인자 값을 지정
    instXAQueryT0425.SetFieldData("t0425InBlock", "passwd", 0, Account_PWD)
#     instXAQueryT0425.SetFieldData("t0425InBlock", "expcode", 0, Target_Expcode)
    instXAQueryT0425.SetFieldData("t0425InBlock", "sortgb", 0, 1) # sorting, 매매구분 정보를 넣어야 for문으로 전체 리스트 가져온다
    instXAQueryT0425.SetFieldData("t0425InBlock", "medosu", 0, 0) # sorting, 매매구분 정보를 넣어야 for문으로 전체 리스트 가져온다, 0 : 전체, 1 : 매도, 2 : 매수
    
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
    output = open(File_Name, "a")
    output.write("총 주문수량 : %s, 총 체결수량 : %s, 총 주문금액 : %s, 총 매수액 : %s, 총 매도액 : %s\n" % (tqty, tcheqty, tamt, tmsamt, tmdamt))
    output.write("\n")
    output.close()

    count1 = instXAQueryT0425.GetBlockCount("t0425OutBlock1")
    print("Block Count : %s" % (count1))
    account_expcode, order_group_list, order_status_list = [], [], []
    output = open(File_Name, "a")
    for i in range(count1):
        ordno = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordno", i) # 주문번호
        expcode = instXAQueryT0425.GetFieldData("t0425OutBlock1", "expcode", i) # 종목번호
        medosu = instXAQueryT0425.GetFieldData("t0425OutBlock1", "medosu", i) # 구분 0 : 전체, 1 : 매도, 2 : 매수
        qty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "qty", i) # 주문수량
        price = instXAQueryT0425.GetFieldData("t0425OutBlock1", "price", i) # 주문가격
        cheqty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cheqty", i) # 체결수량
        cheprice = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cheprice", i) # 체결가격
        ordrem = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordrem", i) # 미체결 잔량
        cfmqty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cfmqty", i) # 확인 수량
        status = instXAQueryT0425.GetFieldData("t0425OutBlock1", "status", i) # 상태
        ordtime = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordtime", i) # 상태
        print("주문번호 : %s, 종목번호 : %s, 구분 : %s, 주문수량 : %s, 가격 : %s, 체결수량 : %s, 잔량 : %s, 상태 : %s, 시간 : %s" % (ordno, expcode, medosu, qty, price, cheqty, ordrem, status, ordtime))
        output.write("주문번호 : %s, 종목번호 : %s, 구분 : %s, 주문수량 : %s, 가격 : %s, 체결수량 : %s, 잔량 : %s, 상태 : %s, 시간 : %s\n" % (ordno, expcode, medosu, qty, price, cheqty, ordrem, status, ordtime))
    print("# Call_Check End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    output.close()
    
    instXAQueryT0425.close()

def __History_Write() :
    original_1 = "D:\\Python\\Log\\My_Account_Stock_History.txt"
    output_1 = "D:\\Python\\Log\\OLD\\My_Account_Stock_History"
    if os.path.isfile(original_1) :
        t_date = datetime.datetime.today().strftime("%Y%m%d%H%M")
        os.rename(original_1, output_1+'_'+t_date+'.txt')
        
# if __name__ == '__main__' :
#     __History_Write()
#     print("# Init Connection")
#     __Init_Conn()
#     print("# Check Account")
#     __Check_Account()
#     print("# Check Trade")
#     __Call_Check()
#     print("# END")