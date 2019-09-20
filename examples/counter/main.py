import os, sys, time

from threading import Condition, Lock, Thread
from flask import Flask, jsonify, render_template
from indelible_log import Cmd, Log, profileFromJson

"""
We'll make a website hit counter reminiscent of those popular ones from the early days of the Web--except this one will be highly-available, offloading its state to Indelible, while being fully encrypted.  We'll also take the '90s one a step further and show off how we can keep the counter live, using Indelible's notification mechanism, to update the counter not just when the page is loaded, but anytime other people cause a click too.

See:

* https://repl.it/@indelible/counter, code
* https://counter.indelible.repl.co/, the finished counter

If you open the above in separate tabs, you can see each reload is reflected immediately in both tabs.

Our overall design is that we're going to take advantage of Indelible's reactive interfaces to ensure each webserver is receiving new counter values, so the webserver can serve the current value without making any calls.

Repl.it is the awesomest way to get familiar with the code and fork your own Indelible-backed counter.  (Yes--repl.it is awesome!  No account required!)

In addition to this shiny flipclock-style counter, this example provides an API for incrementing/getting the counter, showing how Indelible can provide persistence for a webapp with very few dependencies.
"""

profileJson = os.getenv("PROFILEJSON")
if profileJson is None:
    # If they don't have a profile yet, how an example with a new random key.
    import base64
    key = base64.standard_b64encode(os.urandom(32)).decode()
    print("""
Set up your Indelible API key by creating a file called ".env" with your credentials like:

PROFILEJSON={"endpoint_url":"https://log.ndlbl.net:8443","customer_id":"1234123412341234123","apikey":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/","master_key_base64":"%s"}

If you're not using repl.it, you could set the above as an environment variable, or load the profile directly.
""" % key)
    sys.exit(1)

# Load Indelible profile
profile = profileFromJson(profileJson)

# Here's an HTTP server!  If you didn't know, as I recently learned, Flask is wonderful, and well-supported if you want to deploy on repl.it, Google Cloud Functions, Heroku or AWS Lambda.

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static',
    template_folder='template')
log = Log("counter", profile)

# We're going to subscribe to the counter value in one thread, so here's all the stuff we need to synchronize access to it.
lock = Lock()
cond = Condition(lock)
last_change = {
    "value": 0,
    "version": 0
}

@app.route("/")
def default():
    """Increment the counter for this page load, and show the fancy jsflipclock."""
    with lock:
        try:
            log.update([
                Cmd.ExpectVersion(last_change["version"]),
                Cmd.Upsert("counter_value", last_change["value"] + 1)
            ])
        except:
            # TODO: We might get an error if two people click at exactly the same time.  
            pass
        return render_template("flipclock/index.html", value=last_change["value"])

# Flask routes for the API

@app.route("/watch")
def watch_default():
    """Wait up to 5 seconds for the counter to advance past 0, then return the
       counter's current value.  Return immediately if the counter is already
       past 0."""
    return watch(0)

@app.route("/watch/<from_value>")
def watch(from_value):
    """Wait up to 5 seconds for the counter to advance past the given value,
       then return the current value.  Return immediately if the counter
       is already past the given value."""
    with lock:
        if last_change["value"] <= int(from_value):
            cond.wait(5)
        return jsonify(last_change["value"])

@app.route("/click")
def click():
    """Advance the counter."""
    with lock:
        log.update([
            Cmd.ExpectVersion(last_change["version"]),
            Cmd.Upsert("counter_value", last_change["value"] + 1)
        ])
    return jsonify({})

@app.route("/nop")
def nop():
    """Measure the minimum API latency."""
    return ""

@app.route("/rtt")
def rtt():
    """Measure API latency including Indelible."""
    log.create()
    return ""

# Flask routes for static content:

@app.route("/plain")
def plain():
    with lock:
        return render_template("plain.html", value=last_change["value"])

def syncer():
    """Keep the counter state sync'd locally."""
    global last_change
    while True:
        with lock:
            from_version = last_change["version"]
        try:
            new_counter = get_counter(from_version, wait_seconds=60)
            if new_counter is not None:
                with lock:
                    last_change = new_counter
                    cond.notify_all()
        except:
            print("Error syncing:", sys.exc_info()[0])
            time.sleep(1)
        finally:
            None

def get_counter(from_version=0, wait_seconds=None):
    """Return the latest counter value and log version, unless the
       requestor has already seen the latest version.  Will wait up
       to wait_seconds (max 60) for a new version."""
    diff = log.version_diff(from_version, None, wait_seconds=wait_seconds)
    for change in diff.changes():
        if change["change"] == "Add" \
            and change["entry"]["key"] == "counter_value":
            return {
                "version": diff.to_version,
                "value": change["entry"]["value"]
            }
    return None

if __name__ == "__main__":
    log.create()
    sync_thread = Thread(target=syncer)
    sync_thread.daemon = True
    sync_thread.start()
    app.run(host="0.0.0.0", port=6004)
