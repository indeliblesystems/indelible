
fun CharSequence.escape(): String = this.map { it.escape() }.joinToString("")

fun Char.escape(): String {
    if (this == '\b')
        return "\\b"
    if (this == '\r')
        return "\\r"
    if (this == '\n')
        return "\\n"
    if (this == '\"')
        return "\\\""
    if (this == '\\')
        return "\\\\"
    val n = toInt()
    if ((n > 27) and (n < 128))
        return this.toString()
    return "\\x%02X".format(toInt())
}

