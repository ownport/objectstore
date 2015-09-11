ObjectStore
===========

ObjectStore is object storage which uses file-based objects (content and metadata) into local filesystem. 

- No need to think how to optimize many file locations on filesystem. Objectstore saves objects using 
[pairtree](https://confluence.ucop.edu/display/Curation/PairTree) method and provide flat access to objects. 
Objects can be grouped by containers. Inside of container there's no object hierarchy.

- Objectstore provide three methods for object access: get(), put(), delete() 

- The object identifiers can be several: md5 sum, sha1 sum, url, etc

- The simple representation of Objectstore: objectstore -> container -> file-based object with metadata


## Installation

to be described later


## How to use

to be described later


## For developers

To prepare dev environment in Docker

```sh
$ make create-dev-env
```

To run dev environment

```sh
$ make run-dev-env
```

To start ObjectStore as service via gunicorn

```sh
$ make run-dev-env
Creating user: ${USER}
Adding user `objectstore' ...
Adding new group `objectstore' (1000) ...
Adding new user `objectstore' (1000) with group `objectstore' ...
Creating home directory `/home/objectstore' ...
Copying files from `/etc/skel' ...
Adding user `objectstore' to group `sudo' ...
Adding user objectstore to group sudo
Done.
$ cd /app/objectstore/
$ gunicorn --reload -b 0.0.0.0 objectstore.appl
[2015-08-27 21:56:42 +0000] [46] [INFO] Starting gunicorn 19.3.0
[2015-08-27 21:56:42 +0000] [46] [INFO] Listening at: http://0.0.0.0:8000 (46)
[2015-08-27 21:56:42 +0000] [46] [INFO] Using worker: sync
[2015-08-27 21:56:42 +0000] [51] [INFO] Booting worker with pid: 51
```


## Links

- [Falcon](http://falconframework.org/) is a high-performance Python framework for building cloud APIs, smart proxies, and app backends. 
- [GitHub](https://github.com/falconry/falcon/). 
- [Documentation](http://falcon.readthedocs.org/en/stable/index.html) 

    