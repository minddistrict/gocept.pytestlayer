"""Integration of zope.testrunner-style test layers into pytest framework"""

from setuptools import find_packages
from setuptools import setup


setup(
    name='gocept.pytestlayer',
    version='8.2.dev0',

    python_requires=', '.join([
        '>=3.7',
    ]),
    install_requires=[
        'pytest >= 6.0',
        'setuptools',
        'zope.dottedname',
    ],

    extras_require={
        'test': [
            'plone.testing',
        ],
    },

    entry_points={
        'console_scripts': [
            # 'binary-name = gocept.pytestlayer.module:function'
        ],
        'pytest11': [
            'zopelayer = gocept.pytestlayer.plugin',
        ],
    },

    author='gocept <mail@gocept.com>',
    author_email='mail@gocept.com',
    license='ZPL 2.1',
    url='https://github.com/gocept/gocept.pytestlayer/',

    keywords='pytest zope.testrunner layer fixture',
    classifiers="""\
Development Status :: 4 - Beta
Environment :: Console
Framework :: Pytest
Framework :: Plone
Framework :: Zope2
Framework :: Zope3
Intended Audience :: Developers
License :: OSI Approved
License :: OSI Approved :: Zope Public License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: Implementation
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Testing
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'HACKING.rst',
        'CHANGES.rst',
    )),
    namespace_packages=['gocept'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
