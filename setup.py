import objectstore

setup_args = {
    'name': 'objectstore',
    'version': objectstore.__version__,
    'url': 'https://github.com/ownport/objectstore',
    'description': 'Simple storage for file-based objects',
    'author': objectstore.__author__,
    'author_email': 'ownport@gmail.com',
    'maintainer': objectstore.__author__,
    'maintainer_email': 'ownport@gmail.com',
    'license': 'Apache 2.0',
    'packages': ['objectstore', ],
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Topic :: Database',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
}
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(**setup_args)
