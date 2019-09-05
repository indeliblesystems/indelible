#!/usr/bin/env kscript

//INCLUDE doc.kt
//INCLUDE ../releaseInfo.kt

import java.io.File

val isMac =
    System.getProperty("os.name").toLowerCase().indexOf("mac") >= 0

val htmlDir = kotlin.io.createTempDir()

fun stage(f: String) =
    File(f).copyTo(File(htmlDir, f))

fun GuideRunner.guide() {
    System.err.println("check $htmlDir")
    stage("testprofile.js")

    html("""
<h2>Overview</h2>
This is a quick tour of the Opionated Indelible Log API that uses
a web browser and our .js file.

<h2>Prerequisites</h2>
<table>
<tr><td>Indelible apikey<td>Please <a href="mailto:showmethelogs@indelible.systems">sign up</a> for the Developer Preview
<tr><td>Web browser<td>Tested with Firefox, Chrome, and Safari
</table>

<h2>Getting started</h2>

API credentials and an encryption key will be accessed from <code>testprofile.js</code>:
<pre id="input">
var profileJson = JSON.stringify({
    endpointUrl: "https://log.ndlbl.net:8443",
    customerId: "<i><b>customer-id</b></i>",
    apikey: "<i><b>api-key</b></i>",
    masterKeyBase64: "<code id="randomKey">zZHo1y1QAkzIT8BuNiLG8GVmwjN9VVfTq4v49LrWMIk=</code>"
})
</pre>

We'll also need an <code>index.html</code> to start from:
""")

    val baseHtml = """
<html>
<head>
    <title>Indelible Log - API Tour</title>
</head>
<body>
    <script src="testprofile.js"></script>
    <script>
        var indelible
        var log
        async function main() {
            indelible = window["indelible-log"]
            var profile = indelible.profileFromJson(profileJson)
            console.log("ready to rock!  put your API calls here!")
        }

        window["indelible-log"] = { onload: main }
    </script>
    <script src="$jsScriptUrl"></script> <!-- must be after onload is set -->
</body>
"""
    setDocument(baseHtml)
    html(
            """<p>On opening the page, you should see the following
in the JavaScript Console:
""")
    expectJsConsole(
            """ready to rock!  put your API calls here!
""")

    html("""
<h2>Creating a log</h2>
Replacing the <code>console.log</code> above with:
""")
    updateCode(
            """var path = indelible.path(["walkthrough", "Hello, World!", "v3"])
var clientId = "browser"
var log = indelible.encryptingTransactor(path, profile, clientId)
await log.create({"logGroup": "key1"})
console.log("created log")
""",
            oldPattern = "console.log.*")
    html("<p>Now the console will show:\n")
    expectJsConsole("created log\n")

    html("""
<h2>Appending to a log</h2>
""")
    val code =
            """await log.update({
    commands: [
        {
            type: "Upsert",
            key: "foo",
            value: JSON.stringify([1, 2, 3])
        }
    ]
})
console.log("upserted value for 'foo'")
"""
    updateCode(code, "console.log.*")
    html("shows:")
    expectJsConsole("upserted value for 'foo'\n")

    html("""
<h2>Getting the contents of a log</h2>
Say you just want the current contents of the log.  Indelible provides this
by doing the diff between two versions &mdash; the original, empty log (version 0),
and the current version.  We'll just say <code>null</code> for the current version,
and Indelible will tell us what it is.
""")
    updateCode(
            """
var diff = await log.diff(0, null)
console.log(JSON.stringify(diff, null, "    "))
""",
            "console.log.*"
    )
    html("shows:")
    expectJsConsole(
            """{
    "fromVersion": "0",
    "toVersion": "1",
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "foo",
                "value": "[1,2,3]"
            },
            "version": "1"
        }
    ],
    "nextPageOptions": null
}
""")

    html("""
<h2>Reactive logs &mdash; Keeping up to date</h2>
We can subscribe to diffs.  This works very similarly to the diff above,
except when we're done seeing the difference to the latest version, the
client <i>keeps waiting for changes</i>, and will keep invoking our handler
for new versions, until we cancel it.
""")
    updateCode(
            """
const afterVersion = 0

function onDiff(diff) {
    console.log("got a diff! " + JSON.stringify(diff, null, "    "))
}

log.subscribeToDiffs(afterVersion, onDiff)
""",
            "console.log.*"
    )
    html("shows:")
    expectJsConsole(
            """got a diff! {
    "fromVersion": "0",
    "toVersion": "1",
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "foo",
                "value": "[1,2,3]"
            },
            "version": "1"
        }
    ],
    "nextPageOptions": null
}
""")
}

fun main(args: Array<String>) =
    pickRunner(args).guide()

val chromeFun = 
"""
<script>
var output = ""
var origConsole = console.log
console = {
    log(...s) { origConsole(s); output += s.join(" ") + "\n" },
    error(...s) { origConsole(s); output += s.join(" ") + "\n" },
    info(...s) { origConsole(s); output += s.join(" ") + "\n" },
    warn(...s) { origConsole(s); output += s.join(" ") + "\n" }
}
var lastError
window.onerror = function(message, source, lineno, colno, error) {
    console.log("Exception:", error)
}
window.addEventListener('unhandledrejection', function(event) {
    event.preventDefault()
    console.log("unhandled Promise rejection:", event.reason)
});
</script>
"""

val chrome = 
    if (isMac)
        "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome"
    else
        "chrome"
        
var currentDocument: String = ""
fun GuideRunner.setDocument(s: String, show: Boolean = true) {
    val htmlFile = File(htmlDir, "index.html")
    htmlFile.writeText(chromeFun + s)
    val path = htmlFile.absolutePath
    if (show)
        showPre(s.replace("<", "&lt;"))
    shellinput("$chrome --headless --repl $path 2> /dev/null\n", show = false)
    Thread.sleep(10000)
    shellinput("output\nquit\n\n", show = false)
    currentDocument = s
}

fun GuideRunner.expectJsConsole(expected: String, show: Boolean = true) {
    expectOutput(">>> {\"result\":{\"type\":\"string\",\"value\":\"${expected.escape()}\"}}\n>>>", show = false)
    if (show)
        showPre(expected)
    newProcess()
}

fun GuideRunner.updateCode(new: String, oldPattern: String, show: Boolean = true) {
    val orig = currentDocument
    setDocument(
            currentDocument.replace(Regex(oldPattern, RegexOption.MULTILINE), new),
            false)
    if (orig == currentDocument)
        error("replace failed")
    if (show)
        showPre(new)
}
