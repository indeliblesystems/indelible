# -*- coding: utf-8 -*-
import sys

def _test():
    import doctest
    import json
    from pprint import pprint
    import indelible_log

    indelible_log
    try:
        profile_file = open("testprofile.json", "r")
    except FileNotFoundError:
        raise Exception("create testprofile.json from testprofile.json-example")
    profile = indelible_log.profileFromJson(profile_file.read())

    import random
    import string
    def random_string():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

    log_name = json.dumps(["docgen", random_string()])

    return doctest.testfile("102-Python-API-tour.doctest.html", globs={
        "pprint": pprint,
        "indelible_log": indelible_log,
        "log_name": log_name,
        "profile": profile
    })

if __name__ == "__main__":
    sys.exit(_test().failed)


