import sys

def _test():
    import doctest

    return doctest.testfile("103-part1-analytics.doctest.html", globs={
    })

if __name__ == "__main__":
    sys.exit(_test().failed)


