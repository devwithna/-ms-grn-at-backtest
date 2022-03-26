import json
import os
import unittest
from .mocks import mockRequests
from project.services import backTestingService
from typing import Dict, List, Union, Text

class BackTestingCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_mockDataLoad(self):
        mockReq = mockRequests.MockRequests()

        res = mockReq.get("get_ohlcv")
        
        self.assertTrue(len(res['open']) == 7)
        # self.assertTrue(res == 'test', 'res value is ' + res)

    def test_mockDataLoadTimeCandle(self):
        mockReq = mockRequests.MockRequests()

        res = mockReq.get("get_ohlcv_time_candle")
        
        self.assertEqual(len(res['open']), 4675, '# of open : %d' % len(res['open']))
        # self.assertTrue(res == 'test', 'res value is ' + res)

    def test_backtesting(self):
        mockObj = backTestingService.BackTestingService(mockRequests.MockRequests())
        
        res = mockObj.get_backTesting_result(1000000, 'KRW-ETH', 7, 0.2, 0.01, 0.015, 0.01)
        self.assertTrue(res['Mdd'] == -0.7678, 'res value is ' + str(res['Mdd']))
        self.assertEqual(res['initVal'], 1000000)
        self.assertEqual(res['testVal'], 992322)
        
    def test_CalcTradeModel_Case_NotBuy(self):
        mockModel = backTestingService.VBTObject(3383000, 3218000, 3383000, 3166000, 184000675861, 0.2, 0.01, 0.015, 0.01)
        
        pbPrice = mockModel.getPredictBuyPrice()
        ptsPrice = mockModel.getTargetSellPrice(pbPrice)
        slPrice = mockModel.getStopLossPrice(pbPrice)
        expectedRorVal = mockModel.getRorValue(1000000, pbPrice)
  
        self.assertEqual(3426000, pbPrice, "Predict Buy Price is " + str(pbPrice))
        self.assertEqual(3511000, ptsPrice, "Trailing Traget Price is " + str(ptsPrice))
        self.assertEqual(3391000, slPrice, "Stop loss Price is " + str(slPrice))
        
        self.assertEqual(expectedRorVal, expectedRorVal, "Ror Value is " + str(expectedRorVal))
        
    def test_CalcTradeModel_Case_ArrivedTarget(self):
        mockModel = backTestingService.VBTObject(3373000, 3218000, 3483000, 3166000, 184000675861, 0.2, 0.005, 0.007, 0.01)
        
        pbPrice = mockModel.getPredictBuyPrice()
        ptsPrice = mockModel.getTargetSellPrice(pbPrice)
        slPrice = mockModel.getStopLossPrice(pbPrice)
        expectedRorVal = mockModel.getRorValue(1000000, pbPrice)
  
        self.assertEqual(3436000, pbPrice, "Predict Buy Price is " + str(pbPrice))
        self.assertEqual(3477000, ptsPrice, "Trailing Traget Price is " + str(ptsPrice))
        self.assertEqual(3401000, slPrice, "Stop loss Price is " + str(slPrice))
        
        self.assertEqual(1000862, expectedRorVal, "Ror Value is " + str(expectedRorVal))
        
    def test_CalcTradeModel_Case_Stoploss(self):
        mockModel = backTestingService.VBTObject(3373000, 3218000, 3474000, 3166000, 184000675861, 0.2, 0.005, 0.007, 0.01)
        
        pbPrice = mockModel.getPredictBuyPrice()
        ptsPrice = mockModel.getTargetSellPrice(pbPrice)
        slPrice = mockModel.getStopLossPrice(pbPrice)
        expectedRorVal = mockModel.getRorValue(1000000, pbPrice)
  
        self.assertEqual(3434000, pbPrice, "Predict Buy Price is " + str(pbPrice))
        self.assertEqual(3475000, ptsPrice, "Trailing Traget Price is " + str(ptsPrice))
        self.assertEqual(3399000, slPrice, "Stop loss Price is " + str(slPrice))
        
        self.assertEqual(978980, expectedRorVal, "Ror Value is " + str(expectedRorVal))
        
    def test_CalcTradeModel_Case_NotArrivedTarget(self):
        mockModel = backTestingService.VBTObject(3350000, 3345000, 3452000, 3343000, 184000675861, 0.2, 0.01, 0.015, 0.01)
        
        pbPrice = mockModel.getPredictBuyPrice()
        ptsPrice = mockModel.getTargetSellPrice(pbPrice)
        slPrice = mockModel.getStopLossPrice(pbPrice)
        expectedRorVal = mockModel.getRorValue(1000000, pbPrice)
  
        self.assertEqual(3371000, pbPrice, "Predict Buy Price is " + str(pbPrice))
        self.assertEqual(3455000, ptsPrice, "Trailing Traget Price is " + str(ptsPrice))
        self.assertEqual(3337000, slPrice, "Stop loss Price is " + str(slPrice))
        
        self.assertEqual(981432, expectedRorVal, "Ror Value is " + str(expectedRorVal))
        
        
    def test_CalcTradeModel_NewCase_StepSell(self):
        mockObj = backTestingService.BackTestingService(mockRequests.MockRequests())
        
        # res = mockObj.get_new_backTesting_result(1000000, 'KRW-BTC', 150, 0.2, 0.01, 0.01, 0.01, 24)
        # res = mockObj.get_new_backTesting_result(1000000, 'KRW-BTC', 150, 0.3, 0.01, 0.01, 0.01, 24)
        # res = mockObj.get_new_backTesting_result(1000000, 'KRW-BTC', 150, 0.4, 0.01, 0.01, 0.01, 24)
        # res = mockObj.get_new_backTesting_result(1000000, 'KRW-BTC', 150, 0.5, 0.01, 0.01, 0.01, 24)
        
        
        res = mockObj.get_new_backTesting_result(3000000, 'KRW-BTC', 150, 0.3, 0.9, 0.00, 0.9, 24)
        # print ("#######################################################################################")
        # res = mockObj.get_new_backTesting_result(3000000, 'KRW-BTC', 150, 0.3, 0.02, 0.02, 0.01, 12)
        # print ("#######################################################################################")
        # res = mockObj.get_new_backTesting_result(3000000, 'KRW-BTC', 150, 0.3, 0.02, 0.02, 0.01, 8)


        
        self.assertTrue(res['Mdd'] == -51.575300000000006, 'Mdd value is ' + str(res['Mdd']))
        # self.assertEqual(res['initVal'], 1000000)
        # self.assertEqual(res['testVal'], 992241)