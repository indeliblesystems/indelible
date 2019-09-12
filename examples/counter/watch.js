

var value = 0

async function watchCounter(cb) {
    var delay = 0
    try {
        response = await fetch("/watch/" + value)
        text = await response.text()
        value = Number(text)
        if (isNaN(value))
            value = 0
        cb(value)
    } catch (e) {
        console.warn(e)
        delay = 5000
        value = 0
    }
    setTimeout(() => watchCounter(cb), delay)
}
