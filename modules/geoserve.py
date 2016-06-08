#! /usr/local/bin/python3

import argparse
from urllib import request
import json

"""
A module to access the USGS Geoserve Places Service.

Usage:
    From the command line, geosoerve.py lat lon [gettype]
    Or call from module:
        import geoserve
        resultsdict=geoserve.getname(lat,lon[,gettype])

Results:

    The server earthquake.usgs.gov/ws/geoserve gives different properties depending on gettype. If not specified, it will try 'admin', then 'fe'. 

    admin: iso [country code e.g. USA],country,region [e.g. California]
    fe: name,number

"""

RAWURL='http://earthquake.usgs.gov/ws/geoserve/regions.json?latitude={}&longitude={}'
GOODPRODUCTTYPES=[
        {
            'typename':'admin',
            'proplist':['region','country']
        },
        {
            'typename':'fe',
            'proplist':['name']
        }
]

def getname(lat,lon,gettype=''):
    url=RAWURL.format(lat,lon,gettype)
    producttypes=GOODPRODUCTTYPES
    if gettype:
        url+='&type={}'.format(gettype)
        producttypes=[x for x in GOODPRODUCTTYPES if x['typename']==gettype]
        if not producttypes:
            print('WARNING: Unknown product type '+gettype)
            return
    
    print('Accessing URL: '+url)
    fh=request.urlopen(url)
    data=fh.read().decode('utf8')
    fh.close

    results=json.loads(data)
    if not results:
        print('WARNING: No results found (no connection?)')
        return

    name=''
    raw=''
    for parse in producttypes:
        typename=parse['typename']
        if typename in results:
            features=results[typename]['features']
            if not features:
                continue
            props=features[0]['properties']
            featurelist=[props[x] for x in parse['proplist']]
            name=', '.join(featurelist)
            break

    if not name:
        print('WARNING: No results found (bad location?)')
        return

    return({'raw':results,'name':name})

if __name__=='__main__':
    parser=argparse.ArgumentParser(
        description='Check the extended table for unknown entries and attempt to locate them.'
    )
    parser.add_argument('lat',type=float,
        help='Latitude')
    parser.add_argument('lon',type=float,
        help='Longitude')
    parser.add_argument('gettype',type=str,nargs='?',
        help='Data type to query')

    args=parser.parse_args()
    results=getname(args.lat,args.lon,args.gettype)
    print(results['name'])







  

