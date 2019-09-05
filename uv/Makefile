VERSION=$(shell cat LATEST)

all:
	-mkdir release
	cp ${HOME}/projects/progfun/immutable-persistent-structures/subproject/hellodiffdb-js/closure/indelible-log-${VERSION}.js release
	fossil uv add release/indelible-log-${VERSION}.js

