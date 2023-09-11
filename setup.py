import sys
from os import path

from pkg_resources import Requirement, parse_version
from setuptools import find_packages, setup


# Package metadata
NAME = 'interaktiv.recommendations'
DESCRIPTION = 'Interaktiv Recommendations product.'
URL = 'https://code.interaktiv.de/interaktiv/interaktiv.recommendations'
EMAIL = 'support@interaktiv.de'
AUTHOR = 'Interaktiv'
REQUIRES_PYTHON = '~=3.8'
VERSION = '1.0.3'

# Additional package requires
REQUIRED = [
    'setuptools',
    'plone.app.contenttypes',
    'plone.app.testing',
    'plone.restapi',
    'plone.app.robotframework',
    #
    'sklearn==0.0',
    'scikit-learn==1.0.1',
    'scipy==1.7.2',
    'threadpoolctl==3.0.0',
    'joblib==1.1.0',
    #
    'numpy==1.21.4',
    'pandas==1.3.4'
]
EXTRAS = {
    'test': [
            'unittest2',
            'plone.testing',
            'plone.app.testing',
    ]
}

this_directory = path.abspath(path.dirname(__file__))

# Load long description from README.md
try:
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION


# Check required python version
def check_python_version():
    required_python = Requirement.parse('python' + REQUIRES_PYTHON)
    current_version = parse_version(".".join(map(str, sys.version_info[:3])))
    if current_version not in required_python:
        sys.exit(f"'{NAME}' requires Python {REQUIRES_PYTHON} but the current Python is {current_version}")


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license='BSD License (BSD)',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['interaktiv', ],
    include_package_data=True,
    zip_safe=False,
    python_requires=check_python_version(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
