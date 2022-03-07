import json 
import os

class MockRequests():
    
    def __init__(self):
        pass
    
    def get(self, msg):
        if msg.find("get_ohlcv") != -1:
            f = open(os.getcwd() + '/tests/mockData/ohlcv_7days.json')
            datas = json.load(f)
            f.close()
            
            return datas
            
        return 'error'