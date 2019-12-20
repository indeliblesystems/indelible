SHELL := bash
.ONESHELL:
.SHELLFLAGS = -o pipefail -euc
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

SRCS+=000-API-ref.doc.kt
SRCS+=100-REST-API-tour-with-curl.doc.kt
#SRCS+=101-JS-API-tour.doc.kt
SRCS+=102-Python-API-tour.doc.kt
SRCS+=103-Analytics-With-Indelible.doc.kt

PYTHON=.venv/bin/python

all: testprofile.js localsetup generate

../../doc/%.html: %.doc.kt doc.kt generated/doc generated/doc/%.extra
	./$< --verify > $@ || ( cat $@ ; exit 1 )

generated/doc/%.extra:
	@true

generated/doc/102-Python-API-tour.extra: PYTHON_VERSIONS := 3.7
generated/doc/102-Python-API-tour.extra: \
    102-verify.py \
    102-Python-API-tour.doctest.html
	$(foreach PYTHON_VERSION, $(PYTHON_VERSIONS), \
	    echo Testing python${PYTHON_VERSION}... && \
	    VENV=$$(mktemp -d /tmp/pythontest-XXXXXXXXX) && \
	    PYTHONDIST=$$(cd ../python/dist && pwd) && \
	    python${PYTHON_VERSION} -m venv $$VENV && \
	    source $$VENV/bin/activate && \
	    which pip && \
	    pip install -r $$PYTHONDIST/../indelible_log.egg-info/requires.txt && \
	    pip install indelible_log --no-index --find-links file:$$PYTHONDIST && \
	    python${PYTHON_VERSION} 102-verify.py && \
	    echo verified\! && \
	    rm -fr $$VENV && \
	    printf '\n' && \
	) \
	touch $@

generated/doc/103-Analytics-With-Indelible.extra: \
    .venv \
    103-verify.py \
    103-part1-analytics.doctest.html \
    daily_revenue.py
	${PYTHON} 103-verify.py
	touch $@

generate: generated/doc $(patsubst %.doc.kt,../../doc/%.html,${SRCS})

generated/doc:
	mkdir -p $@

testprofile.js:
	@echo Create testprofile.js from testprofile.js-example
	@exit 1

localsetup:
	@echo Create localsetup from localsetup.example
	@exit

.venv: PYTHONDIST=../python/dist
.venv:
	python3.7 -m venv .venv
	${PYTHON} -m pip install -r ${PYTHONDIST}/../indelible_log.egg-info/requires.txt
	${PYTHON} -m pip install indelible_log --no-index --find-links file:${PYTHONDIST}

clean:
	-rm -fr generated


