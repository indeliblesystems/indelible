//INCLUDE lib/escape.kt

import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.InputStream
import java.io.IOException
import java.lang.System.exit

interface GuideRunner {
    fun html(string: String)
    fun shellinput(string: String, show: Boolean = true)
    fun expectOutput(expected: String, show: Boolean = true)
    fun expectError(expected: String, show: Boolean = true)
    fun seeOutput(): String
    fun newProcess()
}

class GenerateGuide : GuideRunner {
    init {
        println("""
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
code, pre {
    font-family: "Lucida Console", Menlo, monospace;
}
pre {
    margin-left: 10px;
}
#input {
    font-style: italic;
}
h1 {
    margin-left: -68px;
}
h2 {
    margin-left: -58px;
}
h3 {
    margin-left: -48px;
}
h4 {
    margin-left: -38px;
}
h5 {
    margin-left: -28px;
}
h6 {
    margin-left: -18px;
}
table {
    border-collapse: collapse;
}
table, th, td {
    border: 1px solid black;
}
body {
    margin-left: 75px;
    max-width: 700px;
}
</style>
<body>
""")
    }

    override fun html(string: String) {
        print(string)
    }

    override fun shellinput(string: String, show: Boolean) {
        if (show)
            showPre(string, id = "input")
    }

    override fun expectOutput(expected: String, show: Boolean) {
        if (show)
            showPre(expected)
    }

    override fun expectError(expected: String, show: Boolean) {
        if (show)
            showPre(expected)
    }

    override fun seeOutput(): String = ""
    override fun newProcess() = Unit
}

class VerifyGuide(
        var outputTimeout: Long = 10000
) : GuideRunner {
    var proc: Process? = null
    var input: BufferedInputStream? = null
    var error: BufferedInputStream? = null
    var output: BufferedOutputStream? = null

    init {
        newProcess()
    }

    override fun html(string: String) {
        //println(string.prependIndent("# "))
    }

    override fun shellinput(string: String, show: Boolean) {
        if (show)
            println(string)
        input!!.mark(1048576)
        error!!.mark(1048576)
        output!!.write(string.toByteArray())
        output!!.flush()
    }

    var timeout: Long = 0

    var stream: BufferedInputStream? = null

    override fun expectOutput(expected: String, show: Boolean) {
        startTimeout(input!!)
        val read = input!!.expect(expected!!)
        //println("NO MATCH so far, will try again (${read.escape()})")
        if (!read.startsWith(expected)) {
            println("expected:\n${expected.escape()}\nbut got:\n${read.escape()}")
            exit(1)
        }
        clearTimeout()
        input!!.mark(1048576)
        if (show)
            println(read)
    }

    override fun expectError(expected: String, show: Boolean) {
        startTimeout(error!!)
        val read = error!!.expect(expected)
        //println("NO MATCH so far, will try again (${read.escape()}")
        if (!read.startsWith(expected)) {
            println("expected:\n${expected.escape()}\nbut got:\n${read.escape()}")
            exit(1)
        }
        clearTimeout()
        input!!.mark(1048576)
        if (show)
            println(read)
    }

    override fun seeOutput(): String =
        input!!.readFromMark()

    private fun startTimeout(stream: BufferedInputStream) {
        this.stream = stream
        timeout = System.currentTimeMillis() + outputTimeout
    }

    private fun clearTimeout() {
        timeout = 0
        stream = null
    }

    private fun BufferedInputStream.readFromMark(): String {
        reset()
        //println("$this available: ${available()}")
        val res = String(ByteArray(available()).apply { read(this) })
        //println("$this sees: $res")
        return res
    }
/*
    private fun getInput(): String {
        return input.readFromMark() + error.readFromMark()
    }
 */

    override fun newProcess() {
        clearTimeout()
        if (proc != null) {
            proc!!.destroy()
            //println("NEW PROCESS")
        }
	proc = ProcessBuilder("bash")
		.redirectOutput(ProcessBuilder.Redirect.PIPE)
		.redirectError(ProcessBuilder.Redirect.PIPE)
		.redirectInput(ProcessBuilder.Redirect.PIPE)
		.start()
	input = proc!!.inputStream.buffered(1048576)
        error = proc!!.errorStream.buffered(1048576)
        output = proc!!.outputStream.buffered(1048576)
        val thread = object : Thread() {
            override fun run() {
                while (true) {
                    sleep(outputTimeout)
                    if (timeout < System.currentTimeMillis()) {
                        if (timeout != 0L) {
                            timeout = 0L
                            if (stream != null) {
                                stream?.close()
                                stream = null
                            }
                        }
                    }
                }
            }
        }
        thread.isDaemon = true
        thread.start()

        shellinput("alias echo=/bin/echo\necho hi\n", false)
        expectOutput("hi\n", false)
    }
}

private tailrec fun BufferedInputStream.expect(expect: String): String =
        expect("", expect)
private tailrec fun BufferedInputStream.expect(seen: String, expect: String): String {
    if (expect == "") {
        //println("all good!")
        return seen
    } else {
        //println("expecting: ${expect.escape()}")
    }
    val read = readAvailable(1..expect.length)
    return if (read.length > 0 && expect.startsWith(read)) {
        //println("looks good  so far:")
        //println("seen: $seen")
        //println("read: $read")
        //println("expect: $expect")
        expect(
                seen + read,
                expect.substring(read.length))
    } else {
        seen + read + readAvailable(0..1048576)
    }
}

private fun BufferedInputStream.readAvailable(range: IntRange): String {
//    println("calling available...")
    try {
        val len = Math.max(range.first, Math.min(available(), range.last))
        val array = ByteArray(len)
//        println("to read: $len")
        val actual = read(array)
        if (actual < 0)
            return ""
        return String(array.sliceArray(0 until actual))
    } catch (ioException: IOException) {
        return ""
    }
}

class GenerateAndVerify(
        val verify: VerifyGuide = VerifyGuide(),
        val generate: GenerateGuide = GenerateGuide()
) : GuideRunner {
    override fun html(string: String) {
        verify.html(string)
        generate.html(string)
    }
    override fun shellinput(string: String, show: Boolean) {
        verify.shellinput(string, false)
        generate.shellinput(string, show)
    }
    override fun expectOutput(expected: String, show: Boolean) {
        verify.expectOutput(expected, false)
        generate.expectOutput(expected, show)
    }
    override fun expectError(expected: String, show: Boolean) {
        verify.expectError(expected, false)
        generate.expectError(expected, show)
    }
    override fun seeOutput(): String {
        return generate.seeOutput()
    }
    override fun newProcess() {
        verify.newProcess()
    }
}

fun pickRunner(args: Array<String>): GuideRunner {
    args.isEmpty() && return GenerateGuide()
    if (args.size > 1 || args[0] != "--verify") {
        System.err.println("Usage: <guide> [--verify]")
        exit(1)
    }
    return GenerateAndVerify()
}

fun code(s: String) =
        "<code>$s</code>"
fun nb(s: String) =
        s.replace(" ", "&nbsp;")

fun GuideRunner.showPre(string: String, id: String? = null) {
    val id = id?.let { " id=\"$it\"" } ?: ""
    html("""
<pre$id>${string.trimEnd()}</pre>
""")
}

