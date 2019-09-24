#!/usr/bin/env kscript

//INCLUDE doc.kt

import java.io.File

fun GuideRunner.guide() {

    html("""

<h2>Overview</h2>
Indelible's <code>diff</code>ing simplifies tracking changes into aggregations
for analytics.  .
This is a brief discussion of how analytics can be done with Indelible.

<h2>Prerequisites</h2>
<table><tr>
<td>Indelible apikey<td>Please <a href="mailto:showmethelogs@indelible.systems">sign up</a> for the Developer Preview
<tr><td><code>Python</code><td>Tested with 2.7 and 3.6
</table>
""")

    val source = File("daily_revenue.py").readText()
    html(
        File("103-part1-analytics.doctest.html")
            .readText()
            .replace("DAILY_REVENUE_SOURCE", source)
    )
}

fun main(args: Array<String>) =
    pickRunner(args).guide()

