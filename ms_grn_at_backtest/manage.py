# encoding: utf-8

from flask import jsonify, request

from flask_script import Manager
from project.services import backTestingService
from project.services import requestService
from project.app import create_app
from flask_cors import CORS, cross_origin

app = create_app()

manager = Manager(app)
CORS(app, resources={r'*': {'origins': '*'}})
myReqService = requestService.RequestService()
myBacktestingService = backTestingService.BackTestingService(myReqService)

@app.route("/backTesting")
def get_ohlcv():
    ticker = request.args.get('ticker')
    initVal = int(request.args.get('initVal'))
    days = int(request.args.get('days'))
    k = float(request.args.get('k')) * 0.01
    tt = float(request.args.get('tt')) * 0.01
    ts = float(request.args.get('ts')) * 0.01
    sl = float(request.args.get('sl')) * 0.01
    
    return jsonify(myBacktestingService.get_backTesting_result(initVal, ticker, days, k, tt, ts, sl));
    
if __name__ == '__main__':
    manager.run()
