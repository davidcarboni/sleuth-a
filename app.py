import logging
import sleuth

from flask import Flask, jsonify
import requests
import os

import b3


app = Flask("sleuth-a")

port = int(os.getenv("PORT", "8001"))
service_b = os.getenv("SERVICE_B", "http://localhost:8002/")

# Set the root logger to INFO so we can see B3 messages:
logging.getLogger().setLevel(logging.INFO)


@app.route('/')
def service():
    log = logging.getLogger(app.name)
    log.setLevel(logging.INFO)
    log.info(app.name + " has been called.")
    log.info("B3 span values: " + str(b3.values()))

    with b3.SubSpan() as headers:
        log.info("B3 subspan values: " + str(b3.values()))
        log.debug("Making a request to service B")
        r = requests.get(service_b, headers=headers)
        log.debug("Service B said: " + str(r.text))

    result = b3.values()
    result["service"] = app.name
    return jsonify(result)


@app.before_request
def before_request():
    b3.start_span()


@app.after_request
def after_request(response):
    return b3.end_span(response)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(port),
        debug=True,
        threaded=True
    )
