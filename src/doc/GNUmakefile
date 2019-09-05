SRCS=$(wildcard *.doc.kt)

all: testprofile.js localsetup generate

.SHELLFLAGS = -o pipefail -ec
.DELETE_ON_ERROR:


generated/doc/%.html: %.doc.kt doc.kt generated/doc generated/doc/%.extra
	./$< --verify > $@ || ( cat $@ ; exit 1 )

generated/doc/%.extra:
	@true

generated/doc/102-Python-API-tour.extra: 102-verify.py 102-Python-API-tour.doctest.html ../python/indelible_log/__init__.py
	PYTHONPATH=../python python3 102-verify.py
	touch $@

generate: generated/doc $(patsubst %.doc.kt,generated/doc/%.html,${SRCS})

generated/doc:
	mkdir -p $@

publish: $(patsubst %.doc.kt,publish/doc/%.html,${SRCS})
	fossil uv sync

publish/doc/%.html: generated/doc/%.html
	cd generated ; fossil uv add $(patsubst publish/%,%,$@)

testprofile.js:
	@echo Create testprofile.js from testprofile.js-example
	@exit 1

localsetup:
	@echo Create localsetup from localsetup.example
	@exit

clean:
	-rm -fr generated


