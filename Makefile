prepare-env:
	@ echo 'install/update `python-xattr`'
	@ pip install -U xattr


prepare-dev-env: prepare-env
	@ echo 'install/update `nose`'
	@ pip install -U nose
	@ echo 'install/update `coverage`'
	@ pip install -U coverage


test-all-with-coverage: 
	@ nosetests --with-coverage --cover-package=objectstore  --verbosity=1 --cover-erase

