We'll make a website hit counter reminiscent of those popular ones
from the early days of the Web--except this one will be highly-available,
offloading its state to Indelible, while being fully encrypted.
We'll also take the '90s one a step further and show off how we can
keep the counter live, using Indelible's notification mechanism,
to update the counter not just when the page is loaded, but anytime
other people cause a click too.

Prerequisites
-------------

-   Indelible apikey --- Please [sign
    up](mailto:showmethelogs@indelible.systems) for the Developer
    Preview
-   `Python` --- Tested with 3.5-3.7
-   Python packages --- `flask`, `indelible_log`

Steps
-----
* [Step 0: Creating client profile](step0_creating_profile.md)
* [Step 1: Hello, Flask](step1_hello_flask.py)
* [Step 2: A '90s-style Hit Counter](step2_90s_hit_counter.py)
* [Step 3: Making it reactive (client-side)](step3_reactive_clients.py)
* [Step 4: Making it fully reactive (server+client-side)](step4_fully_reactive.py)
* [Step 5: Simplifying interfaces](step5_simplifying_interfaces.py)
