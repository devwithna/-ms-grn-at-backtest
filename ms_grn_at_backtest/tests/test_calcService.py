import json
import os
import unittest
from .mocks import mockRequests
from project.services.calcService import CalcService
from typing import Dict, List, Union, Text


class BackTestingCase(unittest.TestCase):

    def setUp(self):
        self.testService = CalcService()

        pass

    def tearDown(self):
        pass

    def calcDayVBTCalc(self, candles, stride):
        pass

    def test_market_trade_buy(self):
        testVolume = 1000000
        testTargetPrice = 34000
        result = self.testService.calc_marketTradeBuy(
            testVolume, testTargetPrice)

        self.assertEqual(result["qty"], 29.25)
        self.assertEqual(result["balance"], 999969)
        self.assertTrue(result["qty"] * testTargetPrice <= testVolume)

    def test_market_trade_sell(self):
        testQty = 29.26
        testTargetPrice = 35000
        result = self.testService.calc_marketTradeSell(
            testQty / 2, testTargetPrice)

        self.assertEqual(result["balance"], 509233)
        self.assertEqual(testQty - result["qty"], 14.63)
