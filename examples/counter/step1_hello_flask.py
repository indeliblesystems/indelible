"""
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
