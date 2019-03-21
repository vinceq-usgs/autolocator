# autolocator
* Standalone DYFI locator. Queries the DYFI database for unknown entries and determines a probable earthquake location.

The goal is to provide an earthquake location as an email product to help the analysts determine an earthquake location.

This script pulls from the online USGS Geoserve webserver to determine a location name for the derived solution.

REQUIREMENTS:

Easiest to use miniconda installation. Make sure you have python3.
The following packages may be installed using pip:
- mysql
- mysq-connector
- pyyaml
- geopy

#mysql.connector:
#  - download from http://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.4.tar.gz
#  - untar
#  - python3 setup.py install
#pyyaml:
#  - download from http://pyyaml.org/download/pyyaml/PyYAML-3.12.tar.gz
#geopy

link to an intensity color file e.g. lib/mmi.cpt

-  
