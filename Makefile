#
#	variables
#

SHELL := /bin/bash
DOCKER_VOLUMES_PATH := `cat local_settings.yml | grep DOCKER_VOLUMES_PATH | cut -d : -f 2`

#
#	actions
#

create-dev-env:
	@ docker build -t 'ownport/objectstore:dev' docker/dev-env/

run-dev-env: 
	@ mkdir -p $$(pwd)/deploy/data/objectstore/
	@ docker run -ti --rm --name=objectstore-dev \
		-v $$(pwd)/objectstore/:/app/objectstore/objectstore/ \
		-v $$(pwd)/tests/:/app/objectstore/tests/ \
		-v $$(pwd)/Makefile:/app/objectstore/Makefile \
		-v $$(pwd)/.coveragerc:/app/objectstore/.coveragerc \
		-v $$(pwd)/deploy/data/objectstore/:/data/objectstore/ \
		ownport/objectstore:dev

test-all:
	@ nosetests \
		--cover-package=objectstore \
		--verbosity=1 \
		--cover-erase 

test-all-with-coverage: 
	@ nosetests \
		--with-coverage \
		--cover-package=objectstore  \
		--verbosity=1 \
		--cover-erase

