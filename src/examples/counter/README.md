Let's make a website hit counter reminiscent of those popular ones
from the early days of the Web.  
In the modern era, where almost
every site is made high-availability by being served from an army of
stateless machines, we want to offload our counter state to a highly-available
persistent store too.  In this example we'll demonstrate using Indelible as
that store, then we'll take the '90s web counter
a step further and show off how we can keep the counter live, using
Indelible's notification mechanism, to update the counter not just when
the page is loaded, but anytime other people cause a click too.

Prerequisites
-------------

-   Indelible apikey --- Please [sign
    up](mailto:showmethelogs@indelible.systems) for the Developer
    Preview
-   `Python` --- Tested with 3.5
-   Python packages --- `flask`, `indelible_log`

Steps
-----
* [Step 1: Hello, Flask](/src/examples/counter/step1_hello_flask.py)
* [Step 2: A '90s-style Hit Counter](step2_90s_hit_counter.py)
* [Step 3: Making it reactive](step3_making_it_reactive.py)
