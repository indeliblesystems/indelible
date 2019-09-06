from threading import Thread
import base64
import doctest
import json
import os
import re
import requests
import runpy
import sys
import time

testprofile = json.loads(open("../../src/doc/testprofile.json", "r").read())
indelibleprofile = testprofile.copy()
indelibleprofile["master_key_base64"] = base64.standard_b64encode(os.urandom(32)).decode()
json.dump(indelibleprofile, open("indelibleprofile.json", "w"))

if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    files = sorted(filter(lambda x: re.match("^step.*py$", x), os.listdir()))

for file in files:
    if not re.match("^step.*py$", file):
        continue

    print("verifying %s..." % file)

    def server():
        runpy.run_path(file, run_name="__main__")

    server_thread = Thread(target=server, daemon=True)
    server_thread.start()
    time.sleep(1)
    res = doctest.testfile(file)
    if res.failed > 0:
        sys.exit(1)

