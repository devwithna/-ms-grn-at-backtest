# -*- coding: utf-8 -*-
import json
# from tkinter import ttk
import numpy as np
from . import tradeUtils
from project.services.calcService import CalcService


class TestModel(object):
    def __init__(self, ol, cl, hl, ll, vl):
        self.ol = ol
        self.cl = cl
        self.hl = hl
        self.ll = ll
        self.vl = vl

        self.isBuyied = False
        self.isSelled = False

    def test(self, predictBuyPrice, predictSellPrices):
        pass


class NewVBTObject(object):

    # o : Open
    # c : Close
    # h : High
    # l : Low
    # tt : Trailing Trigger
    # ts : Trailing Stop
    # sl : Stop loss

    def __init__(self, o, c, h, l, v, k, tt, ts, sl):
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

    def getPredictBuyPrice(self):
        
        halfLen = int(len(self.h)/2 -1)
        startPrice = self.o[halfLen + 1]
        highPrice = max(self.h[0:halfLen])
        lowPrice = min(self.l[0:halfLen])  
        
        # print("Start Price : %d" % startPrice)
        # print("high Price : %d" % highPrice)
        # print("low Price : %d" % lowPrice)
        
        return tradeUtils.get_tick_size(startPrice + (highPrice - lowPrice) * self.k)

    def getTargetSellPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 + self.tt + self.ts))

    def getFirstSellPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 + self.tt))

    def getStopLossPrice(self, startPrice):
        # print ("StartPrice : %d :: StopLossRatio : %f" % (startPrice, self.sl))
        return tradeUtils.get_tick_size(startPrice * (1 - self.sl))

    def printRes(self, res):
        print ("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (res["TargetPrice"],res["Buy"],res["FirstSell"],res["SecondSell"],res["StopLoss"],res["CloseSell"],res["Balance"], res["BuyIdx"], res["SellIdx"], res["StopIdx"], res["High"], res["Low"], res["Stride"]))

    def getRorValue(self, current):
        # Determine Buy and sell
        self.balance = current
        halfLen = int(len(self.h)/2)
        # halfLen = int(len(self.h)/2 -1)
        # startPrice = self.o[halfLen + 1]
        highPrice = max(self.h[halfLen:-1])
        lowPrice = min(self.l[halfLen:-1]) 
        
        pHighPrice = max(self.h[0:halfLen])
        pLowPrice = min(self.l[0:halfLen])  
        stride = (pHighPrice - pLowPrice)
        # Buy Condition
        res = {"TargetPrice":0, "Buy":0,"FirstSell":0,"SecondSell":0,"StopLoss":0,"CloseSell":0, "Balance":0, "BuyIdx":0, "SellIdx":0, "StopIdx": 0, "High":highPrice, "Low":lowPrice, "Stride":stride }
        targetPrice = self.getPredictBuyPrice()
        targetFirstSellPrice = self.getFirstSellPrice(targetPrice)
        targetSecondSellPrice = self.getTargetSellPrice(targetPrice)
        slPrice = self.getStopLossPrice(targetPrice)
        res["TargetPrice"] =  targetPrice
        for idx in range(len(self.h[halfLen:-1]), len(self.h)):
            if self.h[idx] < targetPrice and self.isNotBuyed:
                continue            
            
            if (self.isNotBuyed):
                self.isNotBuyed = False
                self.buyPrice = targetPrice
                buyRes = self.calcSvc.calc_marketTradeBuy(
                    self.balance, self.buyPrice)

                self.qty = buyRes["qty"]
                self.balance = current - (buyRes["balance"])
                res["Buy"] = buyRes["balance"]
                res["BuyIdx"] = idx
                        
            # Sell Condition - 1. Arrive target price
            if (self.h[idx] > targetFirstSellPrice and self.isNotFirstSelled):
                #print ("Trade Type : Match Target")
                sellRes = self.calcSvc.calc_marketTradeSell(
                self.qty, targetFirstSellPrice)
                self.balance += sellRes["balance"]
                self.isNotFirstSelled = False
                res["FirstSell"] = sellRes["balance"]
                res["SellIdx"] = idx

                break
                
            if (self.h[idx] > targetSecondSellPrice and not(self.isNotFirstSelled) and self.isNotSecondSelled):
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, targetSecondSellPrice)
                self.balance += sellRes["balance"]
                self.isNotSecondSelled = False
                res["SecondSell"] = sellRes["balance"]
                break

            # check stop loss
            if (self.l[idx] < slPrice and not (self.isNotBuyed)):
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, slPrice)
                self.balance += sellRes["balance"]
                res["StopLoss"] = sellRes["balance"]
                res["StopIdx"] = idx
                break

            if (idx == len(self.h) - 1 and (self.isNotFirstSelled or self.isNotSecondSelled) and not(self.qty == 0)):
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, self.c[-1])
                res["CloseSell"] = sellRes["balance"]
                self.balance += sellRes["balance"]

        res["Balance"] = self.balance
        self.printRes(res)
        return self.balance

class VBTObject(object):

    # o : Open
    # c : Close
    # h : High
    # l : Low
    # tt : Trailing Trigger
    # ts : Trailing Stop
    # sl : Stop loss

    def __init__(self, o, c, h, l, v, k, tt, ts, sl):
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

        self.calcSvc = CalcService()

    def getPredictBuyPrice(self):
        return tradeUtils.get_tick_size(self.o + (self.h - self.l) * self.k)

    def getTargetSellPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 + self.tt + self.ts))

    def getStopLossPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 - self.sl))

    def getRorValue(self, current, targetPrice):
        # Determine Buy and sell
        self.balance = current
        # Buy Condition
        if (self.h > targetPrice):
            self.buyPrice = targetPrice

            buyRes = self.calcSvc.calc_marketTradeBuy(
                self.balance, self.buyPrice)

            self.qty = buyRes["qty"]
            self.balance = current - (buyRes["balance"])

            # self.qty = round((current / ((1+self.slippage) + (1+self.feeRatio)) * targetPrice), 2)
            # self.balance = current - (((1+self.slippage) + (1+self.feeRatio)) * self.buyPrice * self.qty)
        else:
            #print ("Trade Type : No Trade")

            return self.balance

        # Sell Condition - 1. Arrive target price
        targetSellPrice = self.getTargetSellPrice(targetPrice)
        if (self.h > targetSellPrice):
            #print ("Trade Type : Match Target")
            sellRes = self.calcSvc.calc_marketTradeSell(
                self.qty, targetSellPrice)
            self.balance += sellRes["balance"]
        else:
            # check stop loss
            slPrice = self.getStopLossPrice(targetPrice)
            if (self.l < slPrice):
                # print ("Trade Type : Stop Loss ")
                # krwVal = slPrice * self.qty * ((1 - self.feeRatio) + (1 - self.slippage))

                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, slPrice)
                self.balance += sellRes["balance"]
            else:
                # Sell Close Price
                #print ("Trade Type : Close Price")
                # krwVal = self.c * self.qty * ((1 - self.feeRatio) + (1 - self.slippage))
                sellRes = self.calcSvc.calc_marketTradeSell(self.qty, self.c)
                self.balance += sellRes["balance"]

        # print ("Balance : " + str(self.balance))
        return self.balance


class BackTestingService(object):
    def __init__(self, reqLib):
        self.baseUrl = "http://localhost:5003"
        self.reqLib = reqLib
        pass

    def get_backTesting_result(self, initVal, ticker, days, k, tt, ts, sl):

        apiUrl = self.baseUrl + \
            ("/get_ohlcv?ticker=%s&days=%d" % (ticker, days))
        rVal = self.reqLib.get(apiUrl)
        # Create Models

        vbtModels = []

        for idx in range(len(list(rVal['high'].values()))):
            o = list(rVal['open'].values())[idx]
            c = list(rVal['close'].values())[idx]
            h = list(rVal['high'].values())[idx]
            l = list(rVal['low'].values())[idx]
            v = list(rVal['volume'].values())[idx]

            vbtModel = VBTObject(o, c, h, l, v, k, tt, ts, sl)
            vbtModels.append(vbtModel)

        curVal = initVal
        for modelIdx in range(len(vbtModels)):
            if (modelIdx == 0):
                continue

            pbPrice = vbtModels[modelIdx - 1].getPredictBuyPrice()
            curVal = vbtModels[modelIdx].getRorValue(curVal, pbPrice)

        mdd = ((curVal - initVal) / initVal) * 100

        return {'initVal': initVal, 'testVal': curVal, 'Mdd': mdd}

    def get_new_backTesting_result(self, initVal, ticker, days, k, tt, ts, sl, stride):
        apiUrl = self.baseUrl + \
            ("/get_ohlcv_time_candle?ticker=%s&days=%d" % (ticker, days))
        rVal = self.reqLib.get(apiUrl)
        # Create Models

        vbtModels = []
        openList = list(rVal['open'].values())
        closeList = list(rVal['close'].values())
        highList = list(rVal['high'].values())        
        lowList = list(rVal['low'].values())        
        volumeList = list(rVal['volume'].values())
        
        for idx in range(0, (days - 1) * int(24 / stride)):
            ol = openList[idx*stride:idx*stride + stride*2]
            cl = closeList[idx*stride:idx*stride + stride*2]
            hl = highList[idx*stride:idx*stride + stride*2]
            ll = lowList[idx*stride:idx*stride + stride*2]
            vl = volumeList[idx*stride:idx*stride + stride*2]

            vbtModel = NewVBTObject(ol, cl, hl, ll, vl, k, tt, ts, sl)
            vbtModels.append(vbtModel)
            
        curVal = initVal
        for modelIdx in range(len(vbtModels)):
            curVal = vbtModels[modelIdx].getRorValue(curVal)
            # print  ("###############################Model Indx %d ######################################" % modelIdx)

        mdd = ((curVal - initVal) / initVal) * 100
        return {'initVal': initVal, 'testVal': curVal, 'Mdd': mdd}

