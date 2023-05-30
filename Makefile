# Makefile for res2-service
# uses version from git with commit hash

help:
	@echo "make <target>"
	@echo "build	build platformw package in 'dist' directory."
	@echo "clean	clean all temporary directories."
	@echo ""

build:
	python setup.py bdist_wheel	

check:
	pylint dms_collector -E

clean:
	rm -fr build
	rm -fr dist
	rm -fr dms_collector/*.egg-info


