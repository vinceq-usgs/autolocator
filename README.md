# autolocator
* Standalone DYFI locator. Queries the DYFI database for unknown entries and determines a probable earthquake location.

The goal is to provide an earthquake location as an email product to help the analysts determine an earthquake location.

This script pulls from the online USGS Geoserve webserver to determine a location name for the derived solution.

REQUIREMENTS:

Easiest to install using conda. Run ./install.sh.

CONFIGURATION:

This package requires config.yml (in package root), example below:

```
mail:
        to: recipients@mail.to
        operator: me@mail.to
        smtp: smtp.mail.to
        mailbin: mail
db:
        password: mysqlpassword
        user: mysqluser
        database: dyfidatabase

```
