#!/usr/bin/env kscript

//INCLUDE doc.kt

fun GuideRunner.createLogWithCurl() {

    fun abbreviatedTx(s: String) {
        val debug = false
        shellinput(
"""curl -v -s ${'$'}ENDPOINT/v1/log/update -X POST -H "Content-Type: application/json" -d "
{
  authinfo: { customer_id: \"${'$'}CUSTOMERID\", apikey: \"${'$'}APIKEY\" },
  logName: \"${'$'}LOGNAME\",
  updateSource: \"walkthrough\"
}
""", show = debug)
        shellinput(s)
        shellinput("""
"
echo hi
""", show = debug)
        expectOutput("hi\n", show = debug)
    }

    html("""

<h2>Overview</h2>
This is a quick tour of the Indelible Log API that uses
what's already on your machine.

<h2>Prerequisites</h2>
<table><tr>
<td>Indelible apikey</td><td>Please <a href="mailto:showmethelogs@indelible.systems">sign up</a> for the Developer Preview</td><tr>
<td><code>curl</code></td><td>for issuing HTTP requests to the Indelible API</td></tr><tr>
<td><code>base64</code></td><td>for doing base64 encoding/decoding</td></tr><tr>
<td><i>Optional:</i> <code>jq</code></td><td>for filtering and formatting results</td></tr>
</table>
""")

    html("""
<h2 id="create">Creating a log</h2>
Let's create a new log with the defaults.
<pre id="input">
ENDPOINT=https://log.ndlbl.net:8443
CUSTOMERID=<i><b>customer-id</b></i>
APIKEY=<i><b>"api-key"</b></i>
LOGNAME=`echo -n "Hello, Indelible\!"`
</pre>
""")
    shellinput("if ! [ -f localsetup ] ; then echo localsetup is missing -- please create from localsetup.example ; exit 1 ; else . ./localsetup ; echo localsetup loaded ; fi\n", show = false)
    expectOutput("localsetup loaded\n", show = false)
    shellinput("""if [ -z "${'$'}APIKEY" ] ; then echo APIKEY is not set.  Do you need to create \'localsetup\' from the example in this directory\? ; fi
""", show = false)
    expectOutput("", show = false)
    shellinput("""if [ -z "${'$'}LOGNAME" ] ; then echo LOGNAME is not set.  Do you need to create \'localsetup\'\ from the example in this directory\? ; fi
""", show = false)
    expectOutput("", show = false)
    shellinput("echo hi\n", show = false)
    expectOutput("hi\n", show = false)
    shellinput("""
curl -s ${'$'}ENDPOINT/v1/log/create -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\",
  logGroup: \"unencrypted\"
}"
""")
    shellinput("echo hi\n", show = false)
    expectOutput("hi\n", show = false)

    html("""<p>
<h2 id="upsert">Appending to a log</h2>
Now we can append some entries to the log.
""")
    shellinput(
"""curl -s ${'$'}ENDPOINT/v1/log/update -X POST -H "Content-Type: application/json" -d "
{
  authinfo: { customer_id: \"${'$'}CUSTOMERID\", apikey: \"${'$'}APIKEY\" },
  logName: \"${'$'}LOGNAME\",
  updateSource: \"walkthrough\"
}
{type: 'Upsert', key: \"`echo -n foo | base64`\", value: \"`echo -n bar | base64`\"}
{type: 'Upsert', key: \"`echo -n foo2 | base64`\", value: \"`echo -n bar2 | base64`\"}
"
""")
    shellinput("echo hi\n", show = false)
    expectOutput("hi\n", show = false)
    html("""
<p>
To facilitate encryption, and keep Indelible agnostic, the keys and values are
treated as binary, so they are base64-encoded over the wire.

<h2 id="diff">Showing the contents of a log</h2>
Let's see what it looks like:
""")

    // turn on history expansion
    shellinput("set -o history -H; echo hi\n", show = false)
    expectOutput("hi\n", show = false)

    shellinput("""
curl -s ${'$'}ENDPOINT/v1/log/diff -s -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\"
}"
""")
    expectOutput(
"""{
    "fromVersion": 0,
    "toVersion": 1,
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "Zm9v",
                "value": "YmFy"
            },
            "version": 1
        },
        {
            "change": "Add",
            "entry": {
                "key": "Zm9vMg==",
                "value": "YmFyMg=="
            },
            "version": 1
        }
    ],
    "nextPageOptions": null
}""")
    html("""
We can see the entries we added, shown in base64.  We're also
starting to see how Indelible presents logs in terms of <i>versions</i>
and <i>diffs</i>, which we'll dig into later.
""")

    html("""
<p>
If we want to summarize the contents of a log, we can filter out
everything but the entries, and base64-decode them with <code>jq</code>.
""")

    shellinput(
"""!! | jq '.page[]|.entry|[(.key|@base64d),(.value|@base64d)]' | jq -c
""")
    expectOutput(
"""["foo","bar"]
["foo2","bar2"]
""")
    // don't bother showing the shell history expansion
    expectError(
"""curl -s ${'$'}ENDPOINT/v1/log/diff -s -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\"
}" | jq '.page[]|.entry|[(.key|@base64d),(.value|@base64d)]' | jq -c
""", show = false)

    html("""
<h2 id="longpoll">Reactive Logs &mdash; Getting notified about new versions</h2>
If we're asking for a diff when there isn't one yet, we can optionally
wait until it shows up.  

From another terminal window, you could issue this update:
""")
   shellinput(
"""curl -s ${'$'}ENDPOINT/v1/log/update -X POST -H "Content-Type: application/json" -d "
{
  authinfo: { customer_id: \"${'$'}CUSTOMERID\", apikey: \"${'$'}APIKEY\" },
  logName: \"${'$'}LOGNAME\",
  updateSource: \"walkthrough\"
}
{type: 'ExpectVersion', version: '1'}
{type: 'Upsert', key: \"`echo -n foo3 | base64`\", value: \"`echo -n bar3 | base64`\"}
"
""") 
    html("""
While in your first terminal window, this diff request will wait up to a minute for
the new version to show up:
""")
    shellinput("""
curl -s ${'$'}ENDPOINT/v1/log/diff -s -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\",
  fromVersion: 1,
  waitSeconds: 60
}"
""")
    expectOutput("""{
    "fromVersion": 1,
    "toVersion": 2,
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "Zm9vMw==",
                "value": "YmFyMw=="
            },
            "version": 2
        }
    ],
    "nextPageOptions": null
}""")

    html("""
<h2>Tracing the history of a key</h2>
If we want to know the previous values of a key, we can take advantage of
the <code>version</code> response field to put together the chain of versions
that affected the key.
<p>
For example, with 3 separate transactions:
""")
    abbreviatedTx(
"""{type: 'ExpectVersion', version: 2}
{type: 'Upsert', key: \"`echo -n foo | base64`\", value: \"`echo -n bar2 | base64`\"}""")
    abbreviatedTx(
            """{type: 'ExpectVersion', version: 3}
{type: 'Upsert', key: \"`echo -n foo | base64`\", value: \"`echo -n bar3 | base64`\"}""")
    abbreviatedTx(
            """{type: 'ExpectVersion', version: 4}
{type: 'Upsert', key: \"`echo -n somethingElse | base64`\", value: \"`echo -n somethingElse | base64`\"}""")

    html("""We can see the diff for the latest version points us to version 4 as having created the value for <code>foo</code>:""")
    shellinput(
"""curl -s ${'$'}ENDPOINT/v1/log/diff -s -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\",
  orderResultsBy: \"key\",
  paginationOptions: {
    skipToKey: \"`echo -n foo | base64`\"
  },
  limit: 1
}"
""")
    expectOutput(
            """{
    "fromVersion": 0,
    "toVersion": 5,
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "Zm9v",
                "value": "YmFyMw=="
            },
            "version": 4
        }
    ],
""")
    html("<pre>...</pre>")
    expectOutput(
"""    "nextPageOptions": {
        "skipToKey": "Zm9vMg==",
        "removeAlreadySeen": true,
        "skipToVersion": null,
        "skipToCommand": null
    }
}""", show = false)

    html("We can ask for the previous version, 3, to see what <code>foo</code> was before that:")
       shellinput(
"""curl -s ${'$'}ENDPOINT/v1/log/diff -s -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\",
  orderResultsBy: \"key\",
  fromVersion: 0,
  toVersion: 3,
  paginationOptions: {
    skipToKey: \"`echo -n foo | base64`\"
  },
  limit: 1
}"
""")
    expectOutput(
            """{
    "fromVersion": 0,
    "toVersion": 3,
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "Zm9v",
                "value": "YmFyMg=="
            },
            "version": 3
        }
    ],
""")
    html("<pre>...</pre>")
    expectOutput(
"""    "nextPageOptions": {
        "skipToKey": "Zm9vMg==",
        "removeAlreadySeen": true,
        "skipToVersion": null,
        "skipToCommand": null
    }
}""", show = false)

    html("The result above shows that version 3 set the value to YmFyMg== (bar2).  How about what happened before version 3?")

    shellinput(
"""curl -s ${'$'}ENDPOINT/v1/log/diff -s -X POST -H "Content-Type: application/json" -d "
{
  authinfo: {
    customer_id: \"${'$'}CUSTOMERID\",
    apikey: \"${'$'}APIKEY\"
  },
  logName: \"${'$'}LOGNAME\",
  orderResultsBy: \"key\",
  fromVersion: 0,
  toVersion: 2,
  paginationOptions: {
    skipToKey: \"`echo -n foo | base64`\"
  },
  limit: 1
}"
""")
    expectOutput(
            """{
    "fromVersion": 0,
    "toVersion": 2,
    "page": [
        {
            "change": "Add",
            "entry": {
                "key": "Zm9v",
                "value": "YmFy"
            },
            "version": 1
        }
    ],
""")
    html("<pre>...</pre>")
    expectOutput(
"""    "nextPageOptions": {
        "skipToKey": "Zm9vMg==",
        "removeAlreadySeen": true,
        "skipToVersion": null,
        "skipToCommand": null
    }
}""", show = false)

    html("Version 1 is as early as we can go.")

html("""
<h2>Troubleshooting</h2>

<h3>Error: Bad API Key</h3>
<pre>
{"code":1001,"message":"bad API key","details":{}}
</pre>
Are you sure your shell-fu is alright?  Strings properly escaped?  If so, contact us at youbrokeit<i>@</i>indelible.systems for verification (but please don't send your apikey in email).
""")

}

fun main(args: Array<String>) =
    pickRunner(args).createLogWithCurl()

