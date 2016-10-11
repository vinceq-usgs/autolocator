#! /usr/local/bin/python3

import argparse
from urllib import request
from urllib.error import HTTPError
import json

class Places():
    """
A module to access the USGS Geoserve Places Service, 
earthquake.usgs.gov/ws/geoserve/places.php.

Usage:
    From the command line, places.py lat lon [gettype]
    Or call from module:
        from modules.geoserve.names import Places
        geo=Places(lat,lon)

        print(geo) : returns string version of preferred name
        geo.availabletypes : list of datatypes with data (see below)
        geo.getname : returns string version of preferred name
        geo.lat,geo.lon : store input lat/lon
        geo.names : list of raw output by datatype
        geo.preferredtype: type used for preferred name
        geo.raw : stores raw output from server
        geo.url : stores URL for Geoserve (including parameters)

    """

    RAWURL='http://earthquake.usgs.gov/ws/geoserve/places.json?latitude={}&longitude={}&type=event'

    """
GOODPRODUCTTYPES is a list of acceptable producttypes that can be used to build a stringified location name. The module will iterate through the typenames in order until it finds one with an existing proplist, and concatenates those values.  
    """
    GOODPRODUCTTYPES=[
        {
            'type':'geonames',
            'proplist':['region','country']
        },
        {
            'type':'event',
            'proplist':['name']
        }
    ]

    def __init__(self,lat,lon):
        self.lat=lat
        self.lon=lon
        self.url=self.RAWURL.format(lat,lon)

        try:
            fh=request.urlopen(self.url)
        except HTTPError:
            print('Could not open url:')
            print(self.url)
            return

        data=fh.read().decode('utf8')
        results=json.loads(data)
        if not results:
            print('WARNING: No results found (no connection?)')
            return
        fh.close
        self.raw=results

        if not self.raw:
            return
        
        self.getname()
        #print(json.dumps(self.raw,indent=2,sort_keys=True))

    def getname(self):
        bestpop=None
        bestdist=None
        full=''
        for feature in self.raw['event']['features']:
            p=feature['properties']
            pop=p['population']
            dist=p['distance']

            fullname='%s, %s, %s' % (
                    p['name'],p['admin1_name'],p['country_name'])
            distname='%i km from %s (pop: %i)' % (dist,fullname,pop)

            p['fullname']=fullname
            p['distname']=distname
            full+=distname+'\n'

            if not bestpop or bestpop['properties']['population']<pop:
                bestpop=feature
            if not bestdist or bestdist['properties']['distance']>dist:
                bestdist=feature

        nearest=bestdist['properties']['distname']
        largest=bestpop['properties']['distname']

        self.nearest=nearest
        self.largest=largest
        self.full=full
        return nearest

    def __str__(self):
        if hasattr(self,'nearest'):
            return(self.nearest)
        return self.getname()

"""
"""

if __name__=='__main__':
    parser=argparse.ArgumentParser(
        description='Get a geoserve name given lat/lon coordinates.'
    )
    parser.add_argument('lat',type=float,
        help='Latitude')
    parser.add_argument('lon',type=float,
        help='Longitude')

    args=parser.parse_args()

    geo=Places(args.lat,args.lon)
    print(geo)

