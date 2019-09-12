
We'll make a website hit counter reminiscent of those popular ones from the early days of the Web--except this one will be highly-available, offloading its state to Indelible, while being fully encrypted.  We'll also take the '90s one a step further and show off how we can keep the counter live, using Indelible's notification mechanism, to update the counter not just when the page is loaded, but anytime other people cause a click too.

See:

* code at https://repl.it/@indelible/counter
* the finished counter at https://counter.indelible.repl.co/ 

If you open the above in separate tabs, you can see each reload is reflected immediately in both tabs.

Our overall design is that we're going to take advantage of Indelible's reactive interfaces to ensure each webserver is receiving new counter values, so the webserver can serve the current value without making any calls.

Repl.it is the awesomest way to get familiar with the code and fork your own Indelible-backed counter.  (Yes--repl.it is awesome!  No account required!)

In addition to this shiny flipclock-style counter, this example provides an API for incrementing/getting the counter, showing how Indelible can provide persistence for a webapp with very few dependencies.

