PYTHON=venv/bin/python

all: README.md test

test: venv
	${PYTHON} testindelible.py

venv:
	virtualenv venv
	venv/bin/pip install pynacl requests

README.md: ../doc/generated/doc/102-Python-API-tour.html readme.part1
	@#cat ../doc/generated/doc/102-Python-API-tour.html  | sed 's/<\/pre><pre>//' | sed 's/<\/*pre[^>]*>/```/' | sed 's/<h2[^>]*>\([^<]*\)<\/h2>/\1^M----/' |tr '^M' '\n' | sed 's/&gt;/>/g' | sed 's/<tr>/ | /g' | sed 's/<td>/ | /g' | sed 's/<[^>]*>/ /g' > $@
	( cat readme.part1 ; pandoc --from html --to markdown < ../doc/generated/doc/102-Python-API-tour.html ) > $@

clean:
	-rm -fr dist

dist:
	${PYTHON} setup.py sdist
	${PYTHON} setup.py bdist_wheel --universal 

upload: dist test
	@#${PYTHON} -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	${PYTHON} -m twine upload dist/*

publish: upload

