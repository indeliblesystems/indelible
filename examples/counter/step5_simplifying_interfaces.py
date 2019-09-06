"""
Simplifications
---------------
Since our server always has the latest counter value, we don't need
to expose version to clients anymore.  In fact, we can combine "get"
and "watch" into a single interface.

Example:
--------
>>> import requests
>>> requests.get("http://localhost:6004/watch").json()
3
>>>
>>> # Simulate a click after some delay
>>> from threading import Thread
>>> import time
>>> def request():
...     time.sleep(1)
...     requests.get("http://localhost:6004/click")
>>> t = Thread(target=request)
>>> t.start()
>>>
>>> # Back in the main thread, we wait for the new version:
>>> requests.get("http://localhost:6004/watch/3").json()
4
>>>
>>> # When there's no click, we timeout with no change:
>>> requests.get("http://localhost:6004/watch/3").json()
4

"""

from threading import Condition, Lock, Thread
from flask import Flask, jsonify
from indelible_log import Cmd, Log, profileFromJson

APP = Flask(__name__)
PROFILE = profileFromJson(open("indelibleprofile.json", "r").read())
LOG = Log("counter", PROFILE)

LOG.create()

LOCK = Lock()
COND = Condition(LOCK)
LAST_CHANGE = {
    "value": 0,
    "version": 0
}

@APP.route("/watch")
def watch_default():
    """Wait up to 5 seconds for the counter to advance past 0, then return the
       counter's current value.  Return immediately if the counter is already
       past 0."""
    return watch(0)

@APP.route("/watch/<from_value>")
def watch(from_value):
    """Wait up to 5 seconds for the counter to advance past the given value,
       then return the current value.  Return immediately if the counter
       is already past the given value."""
    with LOCK:
        if LAST_CHANGE["value"] <= int(from_value):
            COND.wait(5)
        return jsonify(LAST_CHANGE["value"])

@APP.route("/click")
def click():
    """Advance the counter."""
    with LOCK:
        LOG.update([
            Cmd.ExpectVersion(LAST_CHANGE["version"]),
            Cmd.Upsert("counter_value", LAST_CHANGE["value"] + 1)
        ])
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

def syncer():
    """Keep the counter state sync'd locally."""
    global LAST_CHANGE
    while True:
        with LOCK:
            from_version = LAST_CHANGE["version"]
        try:
            diff = get_counter_diff(from_version, wait_seconds=60)
            if diff is not None:
                with LOCK:
                    LAST_CHANGE = diff
                    COND.notify_all()
        finally:
            None

SYNC_THREAD = Thread(target=syncer, daemon=True)
SYNC_THREAD.start()

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=6004)
