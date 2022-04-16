import math

# ToDo : Move Calculation service


class CalcService(object):
    def __init__(self):
        # self.feeRatio = 0.0005  # Fee 0.05%
        self.feeRatio = 0.0005  # Fee 0.05%
        self.slippage = 0.00005  # Slippage 0.05%
        # self.slippage = 0.00005  # Slippage 0.05%
        # self.feeRatio = 0.005  # Fee 0.5%
        # self.slippage = 0.0005  # Slippage 0.05%

        pass

    # Stride is hour
    def calcVBT(self, candles, stride):
        pass

    # Return result type of json
    def calc_marketTradeBuy(self, volume, price):
        qty = math.floor(
            ((100000) * volume / (self.getGeneralBuyFee(self.slippage) * price))) / 100000
        buyValue = math.floor(
            self.getGeneralBuyFee(self.slippage) * price * qty)

        return {"qty": qty, "balance": buyValue}

        # self.qty = round((current / ((1+self.slippage) + (1+self.feeRatio)) * targetPrice), 2)
        # self.balance = current - (((1+self.slippage) + (1+self.feeRatio)) * self.buyPrice * self.qty)

    def calc_marketTradeSell(self, qty, price):
        balance = math.floor((qty*price)*self.getGeneralSellFee(self.slippage))

        return {"qty": qty, "balance": balance}

    def getGeneralBuyFee(self, slippage = 0):
        return (1 + self.feeRatio + slippage)
    
    def getGeneralSellFee(self, slippage = 0):
        return (1 - (self.feeRatio + slippage))