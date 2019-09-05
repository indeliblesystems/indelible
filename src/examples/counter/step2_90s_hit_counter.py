"""
Example
-------
>>> import requests
>>> requests.get("http://localhost:6001/get").text
'0'
>>> requests.get("http://localhost:6001/click").text
''
>>> requests.get("http://localhost:6001/get").text
'1'

"""

from flask import Flask
from indelible_log import Cmd, Log, profileFromJson

APP = Flask(__name__)
PROFILE = profileFromJson(open("indelibleprofile.json", "r").read())
LOG = Log("counter", PROFILE)
LOG.create()

@APP.route("/get")
def get():
    """Return the current counter value."""
    return str(get_counter_value())

@APP.route("/click")
def click():
    """Advance the counter."""
    new = get_counter_value() + 1
    LOG.update([Cmd.Upsert("counter_value", new)])
    return ""

def get_counter_value():
    """Return the current counter value."""
    for change in LOG:
        if change["entry"]["key"] == "counter_value":
            return change["entry"]["value"]
    return 0

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=6001)
