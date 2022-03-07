import requests
import json

class RequestService(object):
    def __init__(self):
        self.baseUrl = "http://localhost:5003"
        pass

    def get(self, url):
        return json.loads(requests.get(url).json())