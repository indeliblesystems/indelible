"""
Having a live counter is nice, but it would be even nicer to keep
the server in sync with the counter all the time--it'll mean we
can respond to requests immediately, without touching the persistence
store.  Plus, the process of decoding the response felt kinda clunky.

We'll add a thread that constantly syncs the counter state locally,
and use that state to serve requests instead of calling Indelible
per-request.

Example:
--------
>>> import requests
>>> requests.get("http://localhost:6003/watch/0").json()
{'value': 2, 'version': 2}
>>>
>>> # Simulate a click after some delay
>>> from threading import Thread
>>> import time
>>> def request():
...     time.sleep(1)
...     requests.get("http://localhost:6003/click")
>>> t = Thread(target=request)
>>> t.start()
>>>
>>> # Back in the main thread, we wait for the new version:
>>> requests.get("http://localhost:6003/watch/2").json()
{'value': 3, 'version': 3}
>>>
>>> # When there's no click, we timeout with no change:
>>> requests.get("http://localhost:6003/watch/3").json()
{'value': 3, 'version': 3}

OBSERVATIONS:
- we can get rid of get()
- we can get rid of version!
- the threading code is kinda ugly, maybe can replace with channels?
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

@APP.route("/get")
def get():
    """Return the current counter value and log version."""
    with LOCK:
        return jsonify(LAST_CHANGE)

@APP.route("/watch/<from_version>")
def watch(from_version):
    """Return the current counter value and log version, if it's later than
       the given version, waiting up to 5 seconds for the counter to change."""
    with LOCK:
        if LAST_CHANGE["version"] <= int(from_version):
            COND.wait(5)
        return jsonify(LAST_CHANGE)

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
    APP.run(host="0.0.0.0", port=6003)
