# encoding: utf-8

from flask import jsonify, request

from flask_script import Manager
from project.services import backTestingService
from project.app import create_app
from flask_cors import CORS, cross_origin

app = create_app()

manager = Manager(app)
CORS(app, resources={r'*': {'origins': '*'}})

myBacktestingService = backTestingService.BackTestingService()

@app.route("/backTesting")
def get_ohlcv():
    ticker = request.args.get('ticker')
    days = int(request.args.get('days'))
    k = float(request.args.get('k'))
    
    return jsonify(myBacktestingService.get_backTesting_result(ticker, days, k));
    
if __name__ == '__main__':
    manager.run()
