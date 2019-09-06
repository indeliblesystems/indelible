"""
Our first step is to set up a basic webserver as a foundation for our counter.

Example usage:
--------------
>>> import requests
>>> requests.get("http://localhost:6000/").text
'Hello, World!'

"""

from flask import Flask

APP = Flask(__name__)

@APP.route("/")
def home():
    """Respond with the simplest possible method."""
    return "Hello, World!"

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=6000)

"""
Troubleshooting:

If you run into any trouble with dependencies, try using a `virtualenv`
(https://docs.python.org/3/library/venv.html) like:

```
python3 -m venv $HOME/makeitwork
source $HOME/makeitwork/bin/activate
pip install flask indelible_log
```
"""
