all: README.md test

test:
	python3 testindelible.py

README.md: ../doc/generated/doc/102-Python-API-tour.html readme.part1
	@#cat ../doc/generated/doc/102-Python-API-tour.html  | sed 's/<\/pre><pre>//' | sed 's/<\/*pre[^>]*>/```/' | sed 's/<h2[^>]*>\([^<]*\)<\/h2>/\1^M----/' |tr '^M' '\n' | sed 's/&gt;/>/g' | sed 's/<tr>/ | /g' | sed 's/<td>/ | /g' | sed 's/<[^>]*>/ /g' > $@
	( cat readme.part1 ; pandoc --from html --to markdown < ../doc/generated/doc/102-Python-API-tour.html ) > $@

publish: test
	-rm -fr dist
	python3 setup.py sdist
	python3 setup.py bdist_wheel --universal 
	@#python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	python3 -m twine upload dist/*


