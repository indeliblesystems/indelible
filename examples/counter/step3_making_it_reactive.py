"""
We'd really like to have the counter be live.  For that we need a
mechanism that a webpage could use to determine when the counter
changes, nost just when the page is loaded but anytime it's being
viewed.

Now, instead of just returning the counter value, we'll also include
a 'version' in the response, that'll be used to tell when clients
are not in sync.

Example:
--------
>>> import requests
>>> requests.get("http://localhost:6002/watch/0").json()
{'value': 1, 'version': 1}
>>>
>>> # Simulate a click after some delay
>>> from threading import Thread
>>> import time
>>> def request():
...     time.sleep(1)
...     requests.get("http://localhost:6002/click")
>>> t = Thread(target=request)
>>> t.start()
>>>
>>> # Back in the main thread, we wait for the new version:
>>> requests.get("http://localhost:6002/watch/1").json()
{'value': 2, 'version': 2}
>>>
>>> # When there's no click, we timeout with no change:
>>> requests.get("http://localhost:6002/watch/2").json()
{}

"""

from flask import Flask, jsonify
from indelible_log import Cmd, Log, profileFromJson

APP = Flask(__name__)
PROFILE = profileFromJson(open("indelibleprofile.json", "r").read())
LOG = Log("counter", PROFILE)
LOG.create()

@APP.route("/get")
def get():
    """Return the current counter value and log version."""
    return jsonify(get_counter_diff(from_version=0) or {})

@APP.route("/watch/<from_version>")
def watch(from_version):
    """Return the current counter value and log version, if it's later than
       the given version, waiting up to 5 seconds for the counter to change."""
    return jsonify(get_counter_diff(from_version, wait_seconds=5) or {})

@APP.route("/click")
def click():
    """Advance the counter."""
    diff = get_counter_diff(from_version=0)
    if diff is None:
        LOG.update([Cmd.Upsert("counter_value", 1)])
    else:
        new = diff["value"] + 1
        LOG.update([Cmd.Upsert("counter_value", new)])
    return jsonify({})

def get_counter_diff(from_version=0, wait_seconds=None):
    """Return the latest counter value and log version, unless the
       requestor has already seen the latest version.  Will wait up
       to wait_seconds (max 60) for a new version."""
    diff = LOG.version_diff(from_version, None, wait_seconds=wait_seconds)
    for change in diff.changes():
        if change["change"] == "Add" \
            and change["entry"]["key"] == "counter_value":
            return {
                "version": diff.to_version,
                "value": change["entry"]["value"]
            }
    return None

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=6002)
