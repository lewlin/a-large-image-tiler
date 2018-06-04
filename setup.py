import re

from setuptools import setup



setup(
    name='cropper',
    version='0.1',
    description='my description',
    long_description='my long description',
    url='https://github.com/lewlin',

    # Author details
    author='Tommaso Biancalani',
    author_email='tommasob@mit.edu',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='keywords',

    py_modules=['cropper'],

    install_requires=['numpy','PyQt5'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [
            'pip-tools',
        ],
        'test': [
            'ddt',
        ],
        'doc': [
            'numpydoc',
            'sphinx',
            'sphinx_rtd_theme',
        ]
    },
)