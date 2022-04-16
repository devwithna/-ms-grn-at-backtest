# -*- coding: utf-8 -*-
import json
from mimetypes import init
# from tkinter import ttk
import numpy as np
from . import tradeUtils
from project.services.calcService import CalcService
import datetime
import time

class NewVBTObject(object):

    # o : Open
    # c : Close
    # h : High
    # l : Low
    # tt : Trailing Trigger
    # ts : Trailing Stop
    # sl : Stop loss

    def __init__(self, st, o, c, h, l, v, k, tt, ts, sl):
        self.st = st
        self.o = o
        self.c = c
        self.h = h
        self.l = l
        self.v = v
        self.k = k
        self.tt = tt
        self.ts = ts
        self.sl = sl
        self.buyPrice = 0
        self.sellPrice = 0
        self.qty = 0
        self.feeRatio = 0.0005
        self.slippage = 0.0002
        self.isNotBuyed = True
        self.isNotFirstSelled = True
        self.isNotSecondSelled = True

        self.calcSvc = CalcService()
        
        self.debugStr = ""

    def getAppliedKValue(self):
        halfLen = int(len(self.h)/2 - 1)
        highPrice = max(self.h[0:halfLen])
        lowPrice = min(self.l[0:halfLen])

        return tradeUtils.get_tick_size((highPrice - lowPrice) * self.k)

    def getPredictBuyPrice(self):
        halfLen = int(len(self.h)/2)
        startPrice = self.o[halfLen]
        modKValue = self.getAppliedKValue()
        return tradeUtils.get_tick_size(startPrice + modKValue)

    def getTargetSellPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 + self.tt + self.ts))

    def getFirstSellPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 + self.tt))

    def getStopLossPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 - self.sl))

    def saveDebugRes(self, res):
        halfLen = int(len(self.h)/2)
        strTime = self.st[halfLen]
        self.debugStr = ("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (strTime, res["High"], res["Low"], res["Stride"], res["ModKValue"], res["TargetPrice"], res["FirstSellPrice"], res["SecondSellPrice"], res["StopPrice"], res["Open"], res["Close"], res["Buy"], res["FirstSell"], res["SecondSell"], res["StopLoss"],
               res["CloseSell"], res["Balance"], res["BuyIdx"], res["SellIdx"], res["StopIdx"]))

    def getDebugRes(self):
        return self.debugStr;

    def genDebugStr(self):
        halfLen = int(len(self.h)/2)
        startPrice = self.o[halfLen]
        
        closePrice = self.c[len(self.c) -1 ]
        pHighPrice = max(self.h[0:halfLen-1])
        pLowPrice = min(self.l[0:halfLen-1])
        stride = (pHighPrice - pLowPrice)
        targetPrice = self.getPredictBuyPrice()
        return {"High": max(self.h[halfLen:len(self.h)-1]), "Low": min(self.l[halfLen:len(self.h)-1]), "Stride": stride, "ModKValue": self.getAppliedKValue(),
                "TargetPrice": self.getPredictBuyPrice(), "FirstSellPrice": self.getFirstSellPrice(targetPrice), "SecondSellPrice": self.getTargetSellPrice(targetPrice), "StopPrice":self.getStopLossPrice(targetPrice), "Open": startPrice, "Close":closePrice, "Buy": 0, "FirstSell": 0, "SecondSell": 0, "StopLoss": 0,
                "CloseSell": 0, "Balance": 0, "BuyIdx": 0, "SellIdx": 0, "StopIdx": 0}

    def getRorValue(self, current):
        # Determine Buy and sell
        self.balance = current
        halfLen = int(len(self.h)/2)

        # Buy Condition
        targetPrice = self.getPredictBuyPrice()
        targetFirstSellPrice = self.getFirstSellPrice(targetPrice)
        targetSecondSellPrice = self.getTargetSellPrice(targetPrice)
        slPrice = self.getStopLossPrice(targetPrice)

        res = self.genDebugStr()

        for idx in range(halfLen, len(self.h)):
            if self.h[idx] < targetPrice and self.isNotBuyed:
                continue

            if (self.isNotBuyed):
                self.isNotBuyed = False
                self.buyPrice = targetPrice
                buyRes = self.calcSvc.calc_marketTradeBuy(self.balance, self.buyPrice)

                self.qty = buyRes["qty"]
                self.balance = current - (buyRes["balance"])
                res["Buy"] = buyRes["balance"]
                res["BuyIdx"] = idx

            # Sell Condition - 1. Arrive target price
            if (self.h[idx] > targetFirstSellPrice and self.isNotFirstSelled):
                self.isNotFirstSelled = False

            if (self.h[idx] > targetSecondSellPrice and not(self.isNotFirstSelled) and self.isNotSecondSelled):
                
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, targetSecondSellPrice)

                print ("Activate Second : %f, %d" % (self.qty, sellRes["balance"]))

                self.balance += sellRes["balance"]
                self.isNotSecondSelled = False
                self.qty = sellRes["qty"]
                res["SecondSell"] = sellRes["balance"]
                res["SellIdx"] = idx
                break

            # check stop loss
            if (self.l[idx] < slPrice and not (self.isNotBuyed)):
                print ("Idx : %d ST : %s Low Price %d :: StopLoss : %d" % (idx, self.st[idx], self.l[idx], slPrice))
                
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, slPrice)
                print ("Activate Stoploss : %f, %d" % (self.qty, sellRes["balance"]))
                self.balance += sellRes["balance"]
                res["StopLoss"] = sellRes["balance"]
                res["StopIdx"] = idx
                break

            if (idx == len(self.h) - 1 and (self.isNotFirstSelled or self.isNotSecondSelled) and not(self.qty == 0)):
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, self.c[-1])
                res["CloseSell"] = sellRes["balance"]
                res["StopIdx"] = idx
                self.balance += sellRes["balance"]

        res["Balance"] = self.balance
        self.saveDebugRes(res);
        return self.balance

class BackTestingService(object):
    def __init__(self, reqLib):
        self.baseUrl = "http://localhost:5003"
        self.reqLib = reqLib
        pass

    def exportCSV(self, res):
        # First Row
        f = open("TestResult.csv", "w")
        f.write("StartTime,High,Low,Stride,ModKValue,TargetPrice,FirstSellPrice,SecondSellPrice,StopPrice,Open,Close,Buy,FirstSell,SecondSell,StopLoss,CloseSell,Balance,BuyIdx,SellIdx,StopIdx\n")
        
        for item in res:
            f.write(item)
            f.write('\n')
            
        f.close()
            

    def get_backTesting_result(self, initVal, ticker, days, k, tt, ts, sl, stride):
        apiUrl = self.baseUrl + \
            ("/get_ohlcv_time_candle?ticker=%s&days=%d" % (ticker, days))
        rVal = self.reqLib.get(apiUrl)
     
        # Create Models
        vbtModels = []
        timeList = list(rVal['open'].keys())

        # Default TimeStride 1 Hour
        stideTimeStamp = stride * 3600
        initTime = time.mktime(datetime.datetime.strptime(timeList[0], "%Y-%m-%dT%H:%M:%S").timetuple())
        stampIdx = 0;
        for idx in range(0, (days - 1)):
            # Collect TimeStamp
            # Time Stride Day 0
            # Test and Train stide 2 
            dstTime =  initTime + (2 * stideTimeStamp)
   
            st = []         
            for timeItem in timeList[stampIdx:]:
                stamp = time.mktime(datetime.datetime.strptime(timeItem, "%Y-%m-%dT%H:%M:%S").timetuple())
                if (stamp >= initTime and stamp < dstTime):
                    st.append(timeItem)            

            ol = []
            cl = []
            hl = []
            ll = []
            vl = []
            for timeItem in st:
                ol.append(rVal['open'][timeItem])
                cl.append(rVal['close'][timeItem])
                hl.append(rVal['high'][timeItem])
                ll.append(rVal['low'][timeItem])
                vl.append(rVal['volume'][timeItem])

            initTime = initTime + stideTimeStamp
            
            vbtModel = NewVBTObject(st, ol, cl, hl, ll, vl, k, tt, ts, sl)
            vbtModels.append(vbtModel)

        curVal = initVal
        debugStr = [];
        for modelIdx in range(len(vbtModels)):
            curVal = vbtModels[modelIdx].getRorValue(curVal)
            debugStr.append(vbtModels[modelIdx].getDebugRes());
        self.exportCSV(debugStr)
        mdd = ((curVal - initVal) / initVal) * 100
        return {'initVal': initVal, 'testVal': curVal, 'Mdd': mdd}
