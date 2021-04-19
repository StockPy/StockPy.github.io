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
    while datetime.datetime.today().strftime("%H:%M") < start_time : # ---> start_time���� ũ�� while�� ��������, ���� Call
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
                print("�α��� ����")
                XASessionEventHandler.login_state = 1
            else:
                print("�α��� ����")

    instXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)

#     id, passwd, cert_passwd = "cchoi", "1234a", ""
#     id, passwd, cert_passwd = "cchoi", "dlfdl12", "dlftka13!#"

    # ������ ������ �⺻ �ּҴ� 'hts.ebestsec.co.kr'�ε� ���� ������ ��쿡�� 'demo.ebestsec.co.kr'�� ���
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
        print("���¹�ȣ : %s" % (account))

##################################################
# �ֹ� : �����ȣ, �ż�2ȣ��

def __Stock_Order(Target_Expcode, Order_type, Price) :
    
    print("# __Stock_Order Start : %s, hcode : %s, Price : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode, Price))
    ##################################################
    # ���� �����ֹ�
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
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdQty", 0, Buy_Qty) # �ż� ����
    if Order_type == 1 :
        print("�ŵ�")
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdPrc", 0, Price) # �ż� ����
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "BnsTpCode", 0, 2) # 1 : �ŵ�, 2 : �ż�
    elif Order_type == 2 :
        print("�ż�")
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdPrc", 0, Price) # �ż� ����
        instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "BnsTpCode", 0, 2) # 1 : �ŵ�, 2 : �ż�
    else :
        print("---> �ż��� �ŵ��� �ƴ� ��Ȳ???")
        return None
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdprcPtnCode", 0, "00") # 00 : ������, 03 : ���尡
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "MgntrnCode", 0, "000") # �ſ�ŷ��ڵ� : 000 ����
    instXAQueryCSPAT00600.SetFieldData("CSPAT00600InBlock1", "OrdCndiTpCode", 0, "00") # �ֹ����Ǳ��� : 0 �׳� 0

    instXAQueryCSPAT00600.Request(0) # Request �޼��带 ȣ���ؼ� �Է� �����͸� ������ ����

    while XAQueryEventHandlerCSPAT00600.query_state == 0: # ������ TR ��û�� �ߴٸ� �ش� �۾��� �Ϸ�ƴٴ� �̺�Ʈ�� ���� ������ ���α׷��� ������� �ʰ� ���
        pythoncom.PumpWaitingMessages()

#     ReceiveMessage = instXAQueryCSPAT00600.GetFieldData(ReceiveMessage() # AttributeError: '<win32com.client.COMEventClass instance at 0x80428624>' object has no attribute 'ReceiveMessage'
#     print(ReceiveMessage)
    
    instXAQueryCSPAT00600_count1 = instXAQueryCSPAT00600.GetBlockCount("CSPAT00600InBlock1")
    instXAQueryCSPAT00600_count2 = instXAQueryCSPAT00600.GetBlockCount("CSPAT00600InBlock2")
    print("instXAQueryCSPAT00600_count1 : %s" % (instXAQueryCSPAT00600_count1))
    print("instXAQueryCSPAT00600_count2 : %s" % (instXAQueryCSPAT00600_count2))
    
    RecCnt = instXAQueryCSPAT00600.GetFieldData("CSPAT00600InBlock1", "RecCnt", 0)
    print("# ���ڵ� ī��Ʈ RecCnt : %s" % (RecCnt))
#     hname = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "hname", 0)
#     price = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "price", 0)
#     bidho22 = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "bidho22", 0)
#     offerho2 = instXAQueryCSPAT00600.GetFieldData("t1101OutBlock", "offerho2", 0)
#     print("���� : %s, ���� : %s, �ż�ȣ��2 : %s, �ŵ�ȣ��2 : %s" % (hname, price, bidho2, offerho2))
#     retrun bidho2
    
    print("# __Stock_Order End : %s, hcode : %s, Price : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode, Price))
        
    instXAQueryCSPAT00600.close()

##################################################
# Target_Expcode ���� ������ ��ȸ (�ż�2ȣ��)
def __Price_Check(Target_Expcode) :
    print("# Price_Check Start : %s, hcode : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode))
    ##################################################
    # �ֽ� ���簡 ȣ�� ��ȸ
    class XAQueryEventHandlerT1101:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerT1101.query_state = 1
    ##################################################
    instXAQueryT1101 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT1101)
    instXAQueryT1101.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1101.res"
    instXAQueryT1101.SetFieldData("t1101InBlock", "shcode", 0, Target_Expcode)
    
    instXAQueryT1101.Request(0) # Request �޼��带 ȣ���ؼ� �Է� �����͸� ������ ����

    while XAQueryEventHandlerT1101.query_state == 0: # ������ TR ��û�� �ߴٸ� �ش� �۾��� �Ϸ�ƴٴ� �̺�Ʈ�� ���� ������ ���α׷��� ������� �ʰ� ���
        pythoncom.PumpWaitingMessages()

    hname = instXAQueryT1101.GetFieldData("t1101OutBlock", "hname", 0)
    price = instXAQueryT1101.GetFieldData("t1101OutBlock", "price", 0)
    bidho2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho2", 0)
    offerho2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho2", 0)
    print("���� : %s, ���� : %s, �ż�ȣ��2 : %s, �ŵ�ȣ��2 : %s" % (hname, price, bidho2, offerho2))
    
    print("# Price_Check End : %s, hcode : %s" % (datetime.datetime.today().strftime("%H:%M:%S"), Target_Expcode))

    return price, bidho2
    
    instXAQueryT1101.close()
    
################################################## 
# �ֹ� ������ �ִ��� Ȯ���ϴ� Function : ������ CallNothing 0�� return
def __Call_Check(Target_Expcode) :
    print("# Call_Check Start : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    ##################################################
    # �ֽ�ü�� ��ȸ2
    class XAQueryEventHandlerT0425:
        query_state = 0

        def OnReceiveData(self, code):
            XAQueryEventHandlerT0425.query_state = 1
    ##################################################
    
    print("Call Check about Target_Expcode : %s" % (Target_Expcode))
    
    instXAQueryT0425 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0425)
    instXAQueryT0425.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0425.res"
    instXAQueryT0425.SetFieldData("t0425InBlock", "accno", 0, Account_No) # XAQuery �ν��Ͻ��� ���� SetFieldData��� �޼��带 ȣ���� �� ������ ���� ���� ����
    instXAQueryT0425.SetFieldData("t0425InBlock", "passwd", 0, Account_PWD)
    instXAQueryT0425.SetFieldData("t0425InBlock", "sortgb", 0, 1) # sorting, �Ÿű��� ������ �־�� for������ ��ü ����Ʈ �����´�
    instXAQueryT0425.SetFieldData("t0425InBlock", "medosu", 0, 0) # sorting, �Ÿű��� ������ �־�� for������ ��ü ����Ʈ �����´�
    
    instXAQueryT0425.Request(0) # Request �޼��带 ȣ���ؼ� �Է� �����͸� ������ ����

    while XAQueryEventHandlerT0425.query_state == 0: # ������ TR ��û�� �ߴٸ� �ش� �۾��� �Ϸ�ƴٴ� �̺�Ʈ�� ���� ������ ���α׷��� ������� �ʰ� ���
        pythoncom.PumpWaitingMessages()
        # �̺���Ʈ���������� ������ TR ó���� �Ϸ�Ǹ� OnReceiveData �޼��带 �ݹ��մϴ�.
        # �̷� ���� XAQueryEventHandlerT1102.query_state ���� 1�� ����Ǿ� �̺�Ʈ ��� �������� exit

    count = instXAQueryT0425.GetBlockCount("t0425OutBlock")
#     print("Block Count : %s" % (count)) # ---> ���⼭ 0 üũ�ص� �ɵ�
    tqty = instXAQueryT0425.GetFieldData("t0425OutBlock", "tqty", 0) # �� �ֹ�����
    tcheqty = instXAQueryT0425.GetFieldData("t0425OutBlock", "tcheqty", 0) # �� ü�����
    tamt = instXAQueryT0425.GetFieldData("t0425OutBlock", "tamt", 0) # �� �ֹ��ݾ�
    tmsamt = instXAQueryT0425.GetFieldData("t0425OutBlock", "tmsamt", 0) # �� �ż�ü���
    tmdamt = instXAQueryT0425.GetFieldData("t0425OutBlock", "tmdamt", 0) # �� �ŵ�ü���
    print("�� �ֹ����� : %s, �� ü����� : %s, �� �ֹ��ݾ� : %s, �� �ż��� : %s, �� �ŵ��� : %s" % (tqty, tcheqty, tamt, tmsamt, tmdamt))
    if tqty == "" or tqty == "0":
#         print("# No All Call ---> Need Call Expcode")
        CallNothing = 0
        print("# Call_Check End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
        return CallNothing # �ֹ����� ���� ������ �ٷ� call �ϰ� �Ʒ��� �Ѿ�� �ʱ� ���ؼ�...�ǳ�?

    count1 = instXAQueryT0425.GetBlockCount("t0425OutBlock1")
#     print("Block Count : %s" % (count1))
    account_expcode = []
    for i in range(count1):
        ordno = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordno", i) # �ֹ���ȣ
        expcode = instXAQueryT0425.GetFieldData("t0425OutBlock1", "expcode", i) # �����ȣ
        medosu = instXAQueryT0425.GetFieldData("t0425OutBlock1", "medosu", i) # ����
        qty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "qty", i) # �ֹ�����
        price = instXAQueryT0425.GetFieldData("t0425OutBlock1", "price", i) # �ֹ�����
        cheqty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cheqty", i) # ü�����
        cheprice = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cheprice", i) # ü�ᰡ��
        ordrem = instXAQueryT0425.GetFieldData("t0425OutBlock1", "ordrem", i) # ��ü�� �ܷ�
        cfmqty = instXAQueryT0425.GetFieldData("t0425OutBlock1", "cfmqty", i) # Ȯ�� ����
        status = instXAQueryT0425.GetFieldData("t0425OutBlock1", "status", i) # ����
        print("�ֹ���ȣ : %s, �����ȣ : %s, ���� : %s, �ֹ����� : %s, �ֹ����� : %s, ü����� : %s, ü�ᰡ�� : %s, ��ü���ܷ� : %s, Ȯ�μ��� : %s, ���� : %s" % (ordno, expcode, medosu, qty, price, cheqty, cheprice, ordrem, cfmqty, status))
        print("Call Check TEST 2")
        account_expcode.append(expcode)

    #if Call_Expcode not in account_expcode : # ---> Argu�� �����ȣ�� ����
    if Target_Expcode not in account_expcode : # ---> Argu�� �����ȣ�� ����
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
    # �ֽ��ܰ� ��ȸ2
    class XAQueryEventHandlerT0424:
        query_state = 0
        
        def OnReceiveData(self, code):
            XAQueryEventHandlerT0424.query_state = 1
    ##################################################
    
    instXAQueryT0424 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0424)
    instXAQueryT0424.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0424.res"
    instXAQueryT0424.SetFieldData("t0424InBlock", "accno", 0, Account_No) # XAQuery �ν��Ͻ��� ���� SetFieldData��� �޼��带 ȣ���� �� ������ ���� ���� ����
    instXAQueryT0424.SetFieldData("t0424InBlock", "passwd", 0, Account_PWD)
    
    instXAQueryT0424.Request(0) # Request �޼��带 ȣ���ؼ� �Է� �����͸� ������ ����

    while XAQueryEventHandlerT0424.query_state == 0: # ������ TR ��û�� �ߴٸ� �ش� �۾��� �Ϸ�ƴٴ� �̺�Ʈ�� ���� ������ ���α׷��� ������� �ʰ� ���
        pythoncom.PumpWaitingMessages()
        # �̺���Ʈ���������� ������ TR ó���� �Ϸ�Ǹ� OnReceiveData �޼��带 �ݹ��մϴ�.
        # �̷� ���� XAQueryEventHandlerT1102.query_state ���� 1�� ����Ǿ� �̺�Ʈ ��� �������� exit
    
    t0424_count1 = instXAQueryT0424.GetBlockCount("t0424OutBlock1")
    print("t0424 Call : %s" % (t0424_count1))
    
    while datetime.datetime.today().strftime("%H:%M") < stop_time :
        print("# Time Check : %s " % (datetime.datetime.today().strftime("%H:%M:%S")))
        today_sum = 0
        Account_Expcode = []
        for i in range(t0424_count1):
            expcode = instXAQueryT0424.GetFieldData("t0424OutBlock1", "expcode", i)
            hname = instXAQueryT0424.GetFieldData("t0424OutBlock1", "hname", i) # �����
            janqty = instXAQueryT0424.GetFieldData("t0424OutBlock1", "janqty", i) # �ܰ����
            mdposqt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mdposqt", i) # �ŵ� ���ɼ���
            pamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "pamt", i) # ��մܰ�
            sunikrt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "sunikrt", i) # ������
            mamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mamt", i) # ���Աݾ�
            appamt = instXAQueryT0424.GetFieldData("t0424OutBlock1", "appamt", i) # �򰡱ݾ�
            dtsunik = instXAQueryT0424.GetFieldData("t0424OutBlock1", "dtsunik", i) # �򰡼���
            print("�����ȣ : %s, ����� : %s, �ܰ���� : %s, ��� : %s, ���� : %s, ���Ծ� : %s, �򰡱� : %s, ���� : %s" % (expcode, hname, janqty, pamt, sunikrt, mamt, appamt, dtsunik))
#             print(type(sunikrt)) #  ---> int�� ������ �ȵǰ� float���� �� (if��)
            sunikrt = float(sunikrt) # <class 'str'> ---> <class 'float'>
            appamt = int(appamt) # <class 'str'> ---> <class 'int'>
#             print(type(Limited_Amount)) # <class 'int'>
            
            # ���ͷ��� ���� �ż�, �ŵ� ����
            if (expcode == Target_Expcode) and (sunikrt < Buy_Condition) : # ������ Buy���� �۴�
                print("��1 : ���� %s �� ���� %s" % (sunikrt, Buy_Condition))
                print("---> Buy �ż� ���� ���� : ��Ÿ��")
                if appamt > Limited_Amount :
                    print("Limited_Amount �ʰ� : %s" % Limited_Amount)
                    return None
                Call_Check_Value = __Call_Check(Target_Expcode) # �ϴ� ���� �ֹ� ������ �ִ��� Ȯ�� (CallNothing 0�� �޾Ҵ��� üũ)
#                 print("Call_Check_Value : %s" % Call_Check_Value)# <class 'int'>
                if Call_Check_Value == 0 :
                    Stock_Price, Price_Check_HIDHO2 = __Price_Check(Target_Expcode) # Target_Expcode�� ���� ������ ��ȸ (�ż�2ȣ��)
#                     print(Stock_Price, Price_Check_HIDHO2)
                    __Stock_Order(Target_Expcode, 2, Price_Check_HIDHO2) # �ֹ� : �����ȣ, �ż�2ȣ��, # 1 : �ŵ�, 2 : �ż�
                    File_Name = "D:\\Python\\Order_History.txt"
                    output = open(File_Name, "a")
                    output.write("�ż� ---> %s : ���� %s, %s " % (datetime.datetime.today().strftime("%Y%m%d"), Target_Expcode, Price_Check_HIDHO2))
                    output.write("\n")
                    output.close() # ---> close �� �Ǿ�� write ó���� �Ϸ�ȴ�
            elif (expcode == Target_Expcode) and (sunikrt > Sell_Condition) : # ������ Sell���� ũ��
                print("��2 : ���� %s �� ���� %s" % (sunikrt, Buy_condition))
                if appamt > Limited_Amount : # ���ͽ��� �ܰ迡���� ��� ������ �߰�
                    print("Limited_Amount �ʰ� : %s" % Limited_Amount)
                    return None
                print("---> Sell �ŵ� ���� ���� : ���ͽ���")
                Call_Check_Value = __Call_Check(Target_Expcode) # �ϴ� ���� �ֹ� ������ �ִ��� Ȯ�� (CallNothing 0�� �޾Ҵ��� üũ)
#                 print("Call_Check_Value : %s" % Call_Check_Value)# <class 'int'>
                if Call_Check_Value == 0 :
                    Stock_Price, Price_Check_HIDHO2 = __Price_Check(Target_Expcode) # Target_Expcode�� ���� ������ ��ȸ (�ż�2ȣ��)
#                     print(Stock_Price, Price_Check_HIDHO2)
                    __Stock_Order(Target_Expcode, 1, Stock_Price) # �ֹ� : �����ȣ, �ż�2ȣ��, # 1 : �ŵ�, 2 : �ż�
                    File_Name = "D:\\Python\\Order_History.txt"
                    output = open(File_Name, "a")
                    output.write("�ŵ� ---> %s : ���� %s, %s " % (datetime.datetime.today().strftime("%Y%m%d"), Target_Expcode, Stock_Price))
                    output.write("\n")
                    output.close() # ---> close �� �Ǿ�� write ó���� �Ϸ�ȴ�
            else :
                print("�����ϴ� ���� ����")

            today_sum += int(appamt)
            Account_Expcode.append(expcode)
#         print(Account_Expcode) # ���¿� �ִ� ���� ����Ʈ
        
        # ���� ���¿� �ڽ��� ���������� �ִ��� ã�´�, ������ �ż�
        #if '233160' not in account_expcode :
        if Target_Expcode not in Account_Expcode :
            print("---> �ڻ� �� ��� ���� ����")
#             print(Target_Expcode)
            Call_Check_Value = __Call_Check(Target_Expcode) # �ϴ� ���� �ֹ� ������ �ִ��� Ȯ�� (CallNothing 0�� �޾Ҵ��� üũ)
            print("Call_Check_Value : %s" % Call_Check_Value)# <class 'int'>
            if Call_Check_Value == 0 :
                Stock_Price, Price_Check_HIDHO2 = __Price_Check(Target_Expcode) # Target_Expcode�� ���� ������ ��ȸ (�ż�2ȣ��)
                print(Stock_Price, Price_Check_HIDHO2)
                __Stock_Order(Target_Expcode, 2, Price_Check_HIDHO2) # �ֹ� : �����ȣ, �ż�2ȣ��, # 1 : �ŵ�, 2 : �ż�
                File_Name = "D:\\Python\\Order_History.txt"
                output = open(File_Name, "a")
                output.write("�ż� ---> %s : ���� %s, %s " % (datetime.datetime.today().strftime("%Y%m%d"), Target_Expcode, Price_Check_HIDHO2))
                output.write("\n")
                output.close() # ---> close �� �Ǿ�� write ó���� �Ϸ�ȴ�
        
        print("")
        time.sleep(60) # ---> ü�ᷮ ��ȸ �� 60�� �̸��� ��� ó�� �ȵǴ� ��
        
    File_Name = "D:\\Python\\Account_History.txt"
    output = open(File_Name, "a")
    output.write("%s : %s " % (datetime.datetime.today().strftime("%Y%m%d"), today_sum))
    output.write("\n")
    output.close() # ---> close �� �Ǿ�� write ó���� �Ϸ�ȴ�
    
    print("\n# Start_Service End : %s" % (datetime.datetime.today().strftime("%H:%M:%S")))
    
##################################################
# class �� ���� ����Ѵ�.
# �ٽ� �����Ϸ��� �ص� class�� �켱 �����ѵڿ� XAQuery �� ������Ѿ� �Ѵ�. (2020.06.20)
# SetFieldData�� 1��° �Ķ���ʹ� ��ϸ��̰�
# 2��° �Ķ���ʹ� �ʵ���Դϴ�.
# 3��° �Ķ���Ϳ��� ���� �����͸� ��ȸ�� ���� 0�� �����ϸ� �ǰ�
# 4��° �Ķ���ʹ� �ʵ忡 �ش��ϴ� �Է°�

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
