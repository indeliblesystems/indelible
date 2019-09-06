Links
=====
* [Documentation](doc/)
* [Examples](examples/)

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

Where can I learn more?
-----------------------
Take our API Tour for [curl](https://htmlpreview.github.com/?https://github.com/indeliblesystems/indelible/blob/master/doc/100-REST-API-tour-with-curl.html) or [Python](https://htmlpreview.github.com/?https://github.com/indeliblesystems/indelible/blob/master/doc/102-Python-API-tour.html), and check out the other [Documentation](doc/) and [Examples](examples/).

