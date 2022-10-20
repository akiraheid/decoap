.PHONY: all check clean dist

all: check clean dist install

check:
	echo Testing

clean:
	-rm -r dist venv src/*.egg-info

dist:
	if [ ! -d venv ]; then python3 -m venv venv; fi
	. venv/bin/activate \
		&& python3 -m pip install --upgrade pip build \
		&& python3 -m build

install: dist
	if [ ! -d venv ]; then python3 -m venv venv; fi
	. venv/bin/activate \
		&& python3 -m pip install --force-reinstall dist/decoap-0.0.1-py3-none-any.whl \
		&& decoap -h
