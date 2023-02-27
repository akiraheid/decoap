.PHONY: all test clean dist venv

all: test clean dist install

test:
	PYTHONPATH=${PYTHONPATH}:${PWD}/src python3 -m unittest

clean:
	-rm -r dist venv src/*.egg-info

dist: venv
	. venv/bin/activate \
		&& python3 -m pip install --upgrade pip build \
		&& python3 -m build

install: dist venv
	. venv/bin/activate \
		&& python3 -m pip install --force-reinstall dist/decoap-0.0.1-py3-none-any.whl \
		&& decoap -h

venv:
	if [ ! -d venv ]; then python3 -m venv venv; fi
