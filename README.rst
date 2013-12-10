MadeToMeasure README
====================

.. image:: https://travis-ci.org/GlobalActionPlan/MadeToMeasure.png?branch=master
   :target: https://travis-ci.org/GlobalActionPlan/MadeToMeasure

Made to Measure is a survey system. Its primary goal is to promote reusability of questions and surveys
over organisations. It's currently under development.


Installation
------------

This assumes you have the following things installed

* Python 2.7
* virtualenv Python package
* A C-compiler. (GCC, part of build-essentials package in Linux systems like Debian and Ubuntu)
* Python dev headers. (Usually something like python2.7-dev)

 .. code:: python

  wget http://downloads.buildout.org/2/bootstrap.py
  virtualenv .
  bin/python bootstrap.py
  bin/buildout

Done

To start the server, use the bin/pserve command and specify a paster.ini file.
(An example should be included)
