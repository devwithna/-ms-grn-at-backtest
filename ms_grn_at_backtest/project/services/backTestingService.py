# -*- coding: utf-8 -*-
import requests
import json
import numpy as np


class BackTestingService(object):
    def __init__(self):
        self.baseUrl = "http://localhost:5003"
        pass

    def get_backTesting_result(self, ticker, days, k):

        r = requests.get(
            self.baseUrl + "/get_ohlcv?ticker=%s&days=%d" % (ticker, days))

        print (r.json())

        rVal = json.loads(r.json())
        print (type(rVal))
        print (rVal['high'])

        dfHigh = np.array([])
        dfLow = np.array([])
        dfOpen = np.array([])        
        dfClose = np.array([])

        for high in rVal['high'].values():
            dfHigh = np.append(dfHigh, high)     
        print (dfHigh)
        
        for low in rVal['low'].values():
            dfLow = np.append(dfLow, low)     
        print (dfLow)

        for open in rVal['open'].values():
            dfOpen = np.append(dfOpen, open)     
        print (dfOpen)
        
        for close in rVal['close'].values():
            dfClose = np.append(dfClose, close)     
        print (dfClose)

        # 변동폭 * k 계산, (고가 - 저가) * k값
        dfRange = (dfHigh - dfLow) * k

        # target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
        dfTarget = dfOpen + np.roll(dfRange, 1)
        
        # ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
        dfRor = np.where(dfHigh > dfTarget, dfClose / dfTarget, 1)

        # 누적 곱 계산(cumprod) => 누적 수익률
        dfHpr = dfRor.cumprod()

        # Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
        dfDd = ((np.maximum.accumulate(dfHpr) - dfHpr) / np.maximum.accumulate(dfHpr)) * 100

        return {'Mdd': dfDd.max()}
