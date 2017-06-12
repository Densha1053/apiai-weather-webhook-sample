#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "MQTT":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    payload = {
        "city" : city
    }
    baseurl = "https://api.join.me/v1/meetings"
    p = Request(baseurl)
    p.add_header('Content-Type', 'application/json; charset=utf-8')
    p.add_header('Authorization', 'Bearer ' + access_token) #from oauth
    jsondata = json.dumps(payload)
    jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    jresult = urlopen(p, jsondataasbytes).read()
    data = json.loads(jresult)
    res = makeWebhookResult(data)
    return res



def makeWebhookResult(data):
    speech = "ok"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
