import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Pio - a PioSolver plugin",
    version = "0.0.1",
    author = "Divya Venn",
    author_email = "venn.divya@gmail.com",
    description = ("A set of tools to build "),
    license = "BSD",
    keywords = "poker simulation runner",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['an_example_pypi_project', 'tests'],
    long_description=read('README'),
)