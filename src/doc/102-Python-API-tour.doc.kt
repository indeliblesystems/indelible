#!/usr/bin/env kscript

//INCLUDE doc.kt

import java.io.File

fun GuideRunner.guide() {

    html("""

<h2>Overview</h2>
This is a quick tour of the Indelible Log API with Python.

<h2>Prerequisites</h2>
<table><tr>
<td>Indelible apikey<td>Please <a href="mailto:showmethelogs@indelible.systems">sign up</a> for the Developer Preview
<tr><td><code>Python</code><td>Tested with 2.7 and 3.6
</table>
""")

    html(File("102-Python-API-tour.doctest.html").readText())
}

fun main(args: Array<String>) =
    pickRunner(args).guide()

