#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

# Note to self:
# python setup.py sdist --formats=zip
# To create the zip file

# python setup.py --command-packages=setuptools.command bdist_egg
# To create the egg file

# python setup.py register
# to register with PyPI
# 

# create an egg and upload it
# setup.py register bdist_egg upload

# Set this on command line
# DISTUTILS_DEBUG=true
# 
setup(
    name='dot2svg',
    version='0.1.0',
    description="Convert a dot file into a prettier SVG or PNG.",
    long_description=
"""Converts a .dot file into an SVN and/or a PNG file.
Pretties up the image by adding shadows.""",
    author='Scott Kirkwood',
    author_email='scottakirkwood@gmail.com',
    url='http://code.google.com/dot2svg/',
    download_url='http://dot2svg.googlecode.com/files/dot2svg-0.1.0.zip',
    keywords=['dot', 'svg', 'png', 'diagram', 'Python'],
    license='GNU GPL 3',
    platforms=['POSIX', 'Windows'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ], 
    packages=['dot2svg'],
    scripts=['scripts/dot2svg'],
    package_data = {
      '' : ['batik/*.jar', 'batik/lib/*.jar'],
    },
    zip_safe=False,
)
