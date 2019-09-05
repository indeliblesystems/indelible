This package is a client library for the managed Indelible Logs service.

What is Indelible?
------------------

Indelible is a new managed, persistent storage service, that is:
* secure by default, end-to-end encrypted, safe, and private - you never have to expose any plaintext data to us.  Even for indexes.  Did you read that right?  Yes, you did: Indelible is a persistent store that provides value without needing access to any of your unencrypted data.  This also means that, in the event of a data breach, there's nothing fun to see.
* versioned - old versions remain readable until you're done with them
* immutable - new data is put in new versions; old versions never modified == eliminates data races, simplifies processing.  This is a big whole thing that shouldn't fit in a bullet point.
* highly-available - layering atop today's great HA KV stores means 99.999% availability, much more than Google Cloud SQL's 99.95%.
* strongly consistent - sanity is more important than throughput
    * reactive - no additional pubsub/event sourcing/CQRS required.  Notifications come as pulls containing diffs showing what changed since the last version you saw.

Why do I want it to use Indelible now?
--------------------------------------
* secure by default -> encrypted by client, no plaintext to worry about breaching
* easy to plumb - diff your data like you diff your software
* you can build much more easily on a system that does not overwrite data, or make you wade through huge streams (when all you really want is diffs)
* strongly-consistent with 99.999% availability
* solves at least 1 of the major problems of computer science: versioning simplifies caching, and cache invalidation
* simpler idempotency leads to simpler systems
* immutability will change your life.  it'll put back the years on your life that eventual consistency took off.
* Indelible can eliminate polling -> lowers latency, improves user experience

Python API Tour
===============

Overview
--------

This is a quick tour of the Indelible Log API with Python.

Prerequisites
-------------

  ------------------ ------------------------------------------------------------------------------------
  Indelible apikey   Please [sign up](mailto:showmethelogs@indelible.systems) for the Developer Preview
  `Python`           Tested with 2.7 and 3.6
  ------------------ ------------------------------------------------------------------------------------

Getting started
---------------

Install the package:

``` {#input}
pip install indelible_log
```

Create `testprofile.json` for configuration:

    {
        "endpoint_url": "https://log.ndlbl.net:8443",
        "customer_id": "customer-id",
        "apikey": "api-key",
        "master_key_base64": "v7RBLmFz5oB+IWOtGBEyfgejHvyYZwMTu+x0bbzZ+/4="
    }

Start Python:

``` {#input}
python
```

    Python 3.6.9 (default, Jul 25 2019, 01:16:08) 
    [GCC 4.2.1 Compatible FreeBSD Clang 6.0.0 (tags/RELEASE_600/final 326565)] on freebsd11
    Type "help", "copyright", "credits" or "license" for more information.

    >>> from indelible_log import Cmd, Log
    >>> import json
    >>>
    >>> profile = json.loads(open("testprofile.js", "r").read())
    >>> log_name = json.dumps(["walkthrough", "Hello, world!", "v1"])
    >>>

Creating a log {#create}
--------------

Let\'s create a new log with the defaults.

    >>> log = Log(log_name, profile, encrypt=True, key_mode="string", value_mode="json")
    >>> log.create(log_group="mykey")
    >>>

Appending to a log {#upsert}
------------------

    >>> log.update(update_source="python", commands=[
    ...     indelible_log.Cmd.Upsert("foo", [1, 2, 3])
    ... ])
    >>>

Showing the contents of a log {#diff}
-----------------------------

Iterate over the log\'s current entries:

    >>> for entry in log:
    ...     print(entry)
    {'change': 'Add', 'entry': {'key': 'foo', 'value': [1, 2, 3]}, 'version': 1}
    >>>

A previous version:

    >>> diff = log.version_diff(from_version=1)
    >>> for change in diff.changes():
    ...     print(change)
    >>>

Reactive Logs --- Getting notified about new versions {#longpoll}
-----------------------------------------------------

In another window, get this update ready:

    >>> log.update(update_source="python", commands=[
    ...     Cmd.ExpectVersion(1),
    ...     Cmd.Remove("foo", [1, 2, 3]),
    ...     Cmd.Insert("bar", [4, 5, 6])
    ... ])
    >>>

Back in your original window, start monitoring, then finish that
`update()`:

    >>> diff = log.version_diff(from_version=1, wait_seconds=60)
    >>> diff.to_version
    2
    >>> for change in diff.changes():
    ...     print(change)
    {'change': 'Remove', 'entry': {'key': 'foo', 'value': [1, 2, 3]}, 'version': 1}
    {'change': 'Add', 'entry': {'key': 'bar', 'value': [4, 5, 6]}, 'version': 2}
    >>>
