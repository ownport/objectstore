objectstore
===========

Objectstore is storage library that stores file-based objects (content and metadata) into local filesystem. The main 
idea is to get access to many files in simplest way. 

- No need to think how to optimize many file locations on filesystem. Objectstore saves objects using 
[pairtree](https://confluence.ucop.edu/display/Curation/PairTree) method and provide flat access to objects. 
Objects can be grouped by containers. Inside of container there's no object hierarchy.

- Objectstore provide three methods for object access: get(), put(), delete() 

- The object identifiers can be several: md5 sum, sha1 sum, url, etc

- The simple representation of Objectstore: objectstore -> container -> file-based object with metadata


## Installation

`objectstore` based on:
- file system should support [extended attributes](http://en.wikipedia.org/wiki/Extended_file_attributes)
- [python-xattr](https://pypi.python.org/pypi/xattr) should be installed
```
$ pip install python-xattr
```

## How to use


`objectstore` can be used as library or as console application

## For developers

```
$ pip install nose
$ pip install coverage
```
or 
```
$ make prepare-dev-env
```

In case if your file system does not support external attributes you can create image file and mount it:
```
$ fallocate -l 4G objectstore.img
$ mkfs.ext4 objectstore.img
$ sudo mount -t ext4 -o loop,rw,use_xattr objectstore.img tests/store/
```

## Links to similar topics

- [OpenStack/Swift](http://docs.openstack.org/developer/swift/index.html) is a highly available, distributed, 
eventually consistent object/blob store. Organizations can use Swift to store lots of data efficiently, safely, 
and cheaply.



