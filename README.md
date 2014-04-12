objectstore
===========

Simple storage for file-based objects based on file system with [extended attributes](http://en.wikipedia.org/wiki/Extended_file_attributes)

## Installation

`objectstore` based on:
- file system should support extended attributes
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



