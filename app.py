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

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


def processRequest(req):
    if req.get("result").get("action") != "MQTT":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    payload = {
        "city" : city
    }
    print("tuple")
    (rc, mid) = mqttc.publish("/Benz1053/room2", city, qos=2)
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
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log
mqttc.username_pw_set("Benz1053","benz1053")
mqttc.connect("km1.io", 1883, 60)
mqttc.subscribe("/Benz1053/room2”, 2)
mqttc.loop_forever()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
