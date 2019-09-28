#!/usr/bin/env kscript

//INCLUDE doc.kt
//maybe later DEPS:org.jetbrains.kotlinx:kotlinx-html-jvm:0.6.12

fun GuideRunner.apiReference() {
    html("""

<h2>Overview</h2>
Indelible Logs are accessible via an HTTPS endpoint.  Requests and responses
are in JSON.

<h2>Log Commands</h2>
<h3>CreateLog</h3>
<h4>URL path</h4>
<code>/v1/log/create</code>
<h4>Request Keys</h4>
${tableFrom(
            code("authInfo") to "See <a href=\"#Authentication\">Authentication</a>.",
            code("logName") to "Name of log to create. Encoding: String.",
            code("logGroup") to "A customer-defined plaintext identifier that helps to determine which encryption key is needed to use the log.  Visible to callers which can use DescribeLog.  In the future, it'll be possible to authorize access to a group of logs that share a <code>logGroup</code>.  Encoding: String.")}
<p>
Sets policies for a log.  After successful execution, the log exists, empty, at version 0.
<p>
<h4>Response keys</h4>
An empty response indicates the log was created, or already existed with identical parameters.
Also see <a href="#Errors">Errors</a>.

<h4>Example</h4>
<ul><li> <a href="100-API-tour-with-curl.html#create">Creating a log</a> in the API Tour.</ul>

<h3>DiffLog</h3>
<h4>URL path</h4>
<code>/v1/log/diff</code>
<h4>Request Keys</h4>
${tableFrom(
            code("authInfo") to "See <a href=\"#Authentication\">Authentication</a>.",
            code("logName") to "Name of the log to diff.  Encoding: String,",
            code("fromVersion") to "<i>(Optional)</i>  The version of the log to start diffing from.  If unspecified, 0 will be used.  Encoding: Integer.",
            code("toVersion") to "<i>(Optional)</i>  The version of the log to show diffs to.  If unspecified, the latest version will be used.  Encoding: Integer.",
            code("waitSeconds") to "If there's nothing to show yet&mdash;i.e. <code>fromVersion</code> matches the current log version and <code>toVersion</code> is unspecified&mdash;wait up to this number of seconds for a new version to be created, and diff it as soon as possible.  For an example, see <a href=\"100-API-tour-with-curl.html#longpoll\">Getting notified about new versions</a> in the API Tour.  Range: 0-60.  Encoding: Integer.",
            code("orderResultsBy") to "<code>command</code> or <code>key</code>.  Defaults to <code>command</code>.  Encoding: String.",
            code("limit") to "<i>(Optional)</i>  The maximum entries to return in the response.  If unspecified, 50 will be used.  Range: 0-50.  Encoding: Integer.",
            code("paginationOptions") to "Where to start this page.  Normally from <code>nextPageOptions</code> in a previous response." +
                    "<p>When <code>orderResultsBy</code> <code>command</code> is used:" +
                    tableFrom(
                            code("skipToVersion") to "The version to start at.  Encoding: Integer.",
                            code("skipToCommand") to "The offset of the command within the version to start at.  Encoding: Integer."
                    ) +
                    "<p>When <code>orderResultsBy</code> <code>key</code> is used:" +
                    tableFrom(
                            code("skipToKey") to "The key to start the page at, in lexicographic order.  Encoding: Base64.",
                            code("removeAlreadySeen") to "Whether to start the page with the addition for the <code>skipToKey</code>, if it exists.  Used when the Remove/Add changes for a key are on different pages, or when the caller never cares about removals.  <code>true</code> or <code>false</code>.  Encoding: String."
                    )
    )}
<p>
<h4>Response keys</h4>
${tableFrom(
            code("fromVersion") to "The version this diff starts at, matching the requested version.  Encoding: Integer.",
            code("toVersion") to "The version this diff applies to.  If unspecified in the request, this is the current version of the log.  Encoding: Integer.",
            code("page") to "The changes to apply to <code>fromVersion</code> to make it have the same contents as <code>toVersion</code>.<p>" +
                    tableFrom(
                            code("change") to "<code>Add</code> or <code>Remove</code>, reflecting whether this value was added or removed.",
                            code("entry") to tableFrom(
                                    "key" to "Encoding: Base64.",
                                    "value" to "Encoding: Base64."
                            ),
                            code("version") to "The version that introduced this value.  Encoding: Integer."
                    ),
            code("nextPageOptions") to "Pagination options for subsequent <code>diff</code> requests, to see the next page of diffs in the same version.  See <code>paginationOptions</code> above."
    )}
<h4>Example</h4>
<ul>
<li> <a href="100-API-tour-with-curl.html#diff">Showing the contents of a log</a> in the API Tour
<li> <a href="100-API-tour-with-curl.html#longpoll">Getting notified about new versions</a> in the API Tour
</ul>

<h3>UpdateLog</h3>
<h4>URL path</h4>
<code>/v1/log/update</code>
<h4>Request Keys</h4>
${tableFrom(
            code("authInfo") to "See <a href=\"#Authentication\">Authentication</a>.",
            code("logName") to "Name of the log to update.  Encoding: String,",
            code("updateSource") to "Identifies the person/system making the update.  Encoding: String."
    )}
<h4>Transaction Commands</h4>
The HTTP request starts with the update parameters listed above, followed by a stream of transaction commands, encoded as JSON maps.
<h5>Request Keys</h5>
${tableFrom(
            code("type") to "Command type.  See below.  Encoding: String.",
            code("key") to " For entry commands, the key to check, update, or remove.  Encoding: Base64.",
            code("value") to " For entry commands, the value to update or remove.  Encoding: Base64.",
            code("version") to " For version commands, the version to expect.  Encoding: Integer."
    )}

<h5>Command types</h5>
<li>ExpectVersion - Fail the command with <code>UNEXPECTED_VERSION</code> if the log's current version doesn't correspond to <code>version</code>.</li>
<li>Insert - Insert a new <code>value</code> for <code>key</code>.  Fails with <code>UNEXPECTED_VALUE</code> if there was already a (different) value for <code>key</code>.  For idempotency, this command has no effect if the log already contains the given <code>value</code> for <code>key</code>.</li>
<li>Remove - Removes the <code>value</code> for <code>key</code>.  Has no effect if the key is already removed or has another value.
</li>
<li>Update - Replaces <code>value</code> for <code>key</code>.  Fails with <code>NONEXISTENT_VALUE</code> if there is not an existing value for <code>key</code>.  For idempotency, this command has no effect if the log already contains the given <code>value</code> for <code>key</code>.
</li>
<li>Upsert - "Update/Insert", sets the <code>value</code> for <code>key</code>.  For idempotency, this command has no effect if the log already contains the given <code>value</code> for <code>key</code>.
</li>
</ul>
<p>
<h4>Response keys</h4>
An empty response indicates the transaction was applied.  Otherwise, an API Error response indicates the problem with the first failing transaction command.  Also see <a href="#Errors">Errors</a>.

<h2 id="Authentication">Authentication</h2>
<h3>AuthInfo</h3>

<h4>Keys</h4>
${tableFrom(
            code("customerid") to "assigned customer ID",
            code("apikey") to "assigned API key"
    )}

<h2 id="Errors">Errors</h2>
<h3>HTTP Errors</h3>
${tableFrom(
            nb("401 Unauthorized") to "No authentication information was provided, or it was invalid.  See <a href=\"#Authentication\">Authentication</a>.",
            nb("404 Not Found") to "A log, log version, key, or value was not found, or there is no command handler for the request URL.  See the specific command documentation corresponding to any API Error.",
            nb("400 Bad Request") to "The request refers to unknown keys, undecodable or invalid values, or is missing required keys.",
            nb("412 Precondition Failed") to "When creazting a log, a log with the given name has already has been created, but with different parameters.  When updating a log, a transaction command precondition was not met&mdash;for example, <code>ExpectVersion</code> found the log to be a different version, or <code>Insert</code> found another value already set for the key.  See the specific command documentation corresponding to the API Error.",
            nb("500 Internal Server Error") to "Thanks for finding a bug!  Please report it to <a href=\"showmethelogs@indelible.systems\">showmethelogs@indelible.systems</a>."
    )}
<h3>API Errors</h3>
Where possible, the body of any HTTP error response includes a JSON-encoded API Error map with further details
about the error.
<h4>Keys</h4>
${tableFrom(
            code("code") to "Short description of the error.  Encoding: String.",
            code("codeNumber") to "Number corresponding to the code.  Encoding: Integer.",
            code("message") to "A sentence describing the error.  Encoding: String.",
            code("details") to "<i>(Optional)</i>A JSON map with code-specific details.  Encoding: Strings."
    )}
<h4>Codes</h4>
<h5>BAD_API_KEY (1001)</h5>
The request is not authenticated, or has invalid authentication information.  See <a href="#Authentication">Authentication</a>.
<h5>TRANSACTION_CONFLICT (1002)</h5>
The log was updated by another transaction, after this one started.
<h5>UNEXPECTED_VERSION (1003)</h5>
The log has a different version than an <code>ExpectVersion</code> transaction command was expecting.
<h5>NONEXISTENT_VERSION (1004)</h5>
The log does not have the requested version for a <code>diff</code>.
<h5>NONEXISTENT_LOG (1005)</h5>
The requested log has not been created yet for an <code>update</code>.
<!--
<h5>NONEXISTENT_KEY (1006)</h5>
Reserved.
<h5>INVALID_MARKER (1007)</h5>
Reserved.
-->
<h5>UNEXPECTED_VALUE (1008)</h5>
An <code>Insert</code> transaction command found the key already had a value.
<h5>NONEXISTENT_VALUE (1009)</h5>
An <code>Update</code> transaction command found no key to update.
<h5>LOG_EXISTS (1010)</h5>
The log has already been created, with different options.

""")
}

private fun tableFrom(vararg entries: Pair<String, String>): String =
        "<table>" + entries.joinToString(separator = "") { "<tr><td>${it.first}</td><td>${it.second}</td></tr>" } +
                "</table>"

fun main(args: Array<String>) =
        pickRunner(args).apiReference()

