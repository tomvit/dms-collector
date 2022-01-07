# Makefile for res2-service
# uses version from git with commit hash

help:
	@echo "make <target>"
	@echo "build	build platformw package in 'dist' directory."
	@echo "clean	clean all temporary directories."
	@echo ""

build:
	python setup.py egg_info sdist	

check:
	pylint dms_collector 

clean:
	rm -fr build
	rm -fr dist
	rm -fr dms_collector/*.egg-info


