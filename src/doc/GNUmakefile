SRCS=$(wildcard *.doc.kt)

all: testprofile.js localsetup generate

.SHELLFLAGS = -o pipefail -ec
.DELETE_ON_ERROR:


../../doc/%.html: %.doc.kt doc.kt generated/doc generated/doc/%.extra
	./$< --verify > $@ || ( cat $@ ; exit 1 )
	git add $@

generated/doc/%.extra:
	@true

generated/doc/102-Python-API-tour.extra: 102-verify.py 102-Python-API-tour.doctest.html ../python/indelible_log/__init__.py
	PYTHONPATH=../python python3 102-verify.py
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

clean:
	-rm -fr generated


