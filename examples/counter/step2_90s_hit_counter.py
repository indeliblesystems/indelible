"""
Now we're going to add handlers that show and click the counter.  These could
be used to click the counter each time the page is loaded, from a script on
the page.

This shows how Indelible can provide persistence for a webapp with very few
dependencies.

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

# An Indelible Profile provides credentials, keys and other configuration
# parameters.
PROFILE = profileFromJson(open("indelibleprofile.json", "r").read())

# Create our counter log, if it wasn't created already.  The defaults ensure
# that everything we put in the log is encrypted on our side, with a key
# based on the master key set in the profile.
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
