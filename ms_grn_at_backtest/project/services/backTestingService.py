# -*- coding: utf-8 -*-
import json
import numpy as np
from . import tradeUtils


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
        self.feeRatio = 0.0005
        self.slippage = 0.0005

    def getPredictBuyPrice(self):
        return tradeUtils.get_tick_size(self.o + (self.h - self.l) * self.k)

    def getTargetSellPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice *(1 + self.tt + self.ts))

    def getStopLossPrice(self, startPrice):
        return tradeUtils.get_tick_size(startPrice * (1 - self.sl))

    def getRorValue(self, current, targetPrice):
        # Determine Buy and sell
        self.balance = current
        # Buy Condition 
        if (self.h > targetPrice):
            self.buyPrice = targetPrice
            self.qty = round((current / ((1+self.slippage) + (1+self.feeRatio)) * targetPrice), 2)
            
            self.balance = current - (((1+self.slippage) + (1+self.feeRatio)) * self.buyPrice * self.qty)
        else:
            print ("Trade Type : No Trade")

            return self.balance
        
        # Sell Condition - 1. Arrive target price
        targetSellPrice = self.getTargetSellPrice(targetPrice)
        if (self.h > targetSellPrice):
            print ("Trade Type : Match Target")

            krwVal = targetSellPrice * self.qty * ((1 - self.feeRatio) + (1 - self.slippage))
            self.balance += krwVal;
        else:
            # check stop loss
            slPrice = self.getStopLossPrice(targetPrice)
            if (self.l < slPrice):
                print ("Trade Type : Stop Loss ")
                krwVal = slPrice * self.qty * ((1 - self.feeRatio) + (1 - self.slippage))
                self.balance += krwVal
            else:
                # Sell Close Price
                print ("Trade Type : Close Price")
                krwVal = self.c * self.qty * ((1 - self.feeRatio) + (1 - self.slippage))
                self.balance += krwVal
                
        print ("Balance : " + str(self.balance))
        return self.balance; 
            
class BackTestingService(object):
    def __init__(self, reqLib):
        self.baseUrl = "http://localhost:5003"
        self.reqLib = reqLib
        pass

    def get_backTesting_result(self, initVal, ticker, days, k, tt, ts, sl):

        apiUrl = self.baseUrl + \
            ("/get_ohlcv?ticker=%s&days=%d" % (ticker, days))
        rVal = self.reqLib.get(apiUrl)
        ## Create Models 
        
        vbtModels = []
        
        for idx in range(len(list(rVal['high'].values()))):
            o = list(rVal['open'].values())[idx]
            c = list(rVal['close'].values())[idx]
            h = list(rVal['high'].values())[idx]
            l = list(rVal['low'].values())[idx]
            v = list(rVal['volume'].values())[idx]

            vbtModel = VBTObject(o,c, h, l, v, k, tt, ts, sl)
            vbtModels.append(vbtModel)

        curVal = initVal
        for modelIdx in range(len(vbtModels)):
            if (modelIdx == 0):
                continue
            
            pbPrice = vbtModels[modelIdx - 1].getPredictBuyPrice()
            curVal = vbtModels[modelIdx].getRorValue(curVal, pbPrice)
            
        mdd = ((curVal - initVal) / initVal) * 100            

        return {'initVal': initVal, 'testVal': curVal, 'Mdd': mdd}
