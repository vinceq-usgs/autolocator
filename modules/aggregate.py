#! /usr/local/bin/python3.5
# -*- coding: utf-8 -*-

"""
Created on Fri Mar 11 21:08:39 2016

@author: vinceq

aggreagate.py :  Module to take GeoJSON feature collection and return
                    geocoded GeoJSON

"""

import math
import geojson
import modules.cdi as cdi
from modules.utm import OutOfRangeError,to_latlon,from_latlon

PRECISION=4

def aggregate(featurecollection,resolution):
    """
    Iterate through GeoJSON feature collection
    Returns GeoJSON feature collection of UTM boxes (polygons)
    with properties:
        utm     UTM code with correct precision
        lat     center coordinate
        lon     center coordinate
        nresp   number of responses contributing
        cdi     aggregated intensity
        
    Arguments:
    pts             GeoJSON feature collection
    resolution      size of geocoding box in km (optional, default 1km)
    """
    resolutionMeters=resolution * 1000
    pts=featurecollection['features']
    npts=len(pts)
    print('Got '+str(npts)+' entries, aggregating.')
    for pt in pts:
        loc=getAggregation(pt,resolutionMeters)
        if not loc: continue
        pt['properties']['loc']=loc
                
    rawresults={}
    earliesttimes={}
    print('Aggregating points:')
    for pt in pts:
        if 'loc' not in pt['properties']: continue
        loc=pt['properties']['loc']
        if loc in rawresults:
            rawresults[loc].append(pt)
        else:
            rawresults[loc]=[ pt ]

            
    results=[]
    for loc,pts in rawresults.items():
        intensity=cdi.calculate(pts)
                        
        # geom=getBoundingPolygon(loc,resolutionMeters)        
        coords=getCoords(loc,resolutionMeters)
        props={
            'cdi' : intensity,
            'nresp' : len(pts),
        }
        pt=geojson.Feature(
            geometry=geojson.Point(coords),
            properties=props,
            id=loc
        )
        results.append(pt)

    print('Aggregated %i pts into %i pts' % (npts,len(results)))
    return results

def myFloor(x,multiple):
    """ 
    Emulates the math.floor function but
    rounding down to different digits (i.e. 1000 or 10000 meters)

    Returns integer
    Arguments: 
        x       original value
        multiple   which digit to round to (1000 or 10000)

    """
    
    y=x/multiple
    return int(math.floor(y) * multiple)

def myCeil(x,multiple):
    return int(math.ceil(x/multiple) * multiple)

def getAggregation(pt,resolutionMeters):
    geom=pt['geometry']['coordinates']
    lat=geom[1]
    lon=geom[0]
    try: 
        loc=from_latlon(lat,lon)
    except OutOfRangeError:
        return
    if not loc: return

    x,y,zonenum,zoneletter=loc
    x0=myFloor(x,resolutionMeters)
    y0=myFloor(y,resolutionMeters)
    loc='{} {} {} {}'.format(x0,y0,zonenum,zoneletter)
    return loc
    
def getCoords(loc,resolutionMeters):
    """
    Returns a Point object of the center of the UTM location
    
    """
    x,y,zone,zoneletter=loc.split()
    x=int(x)+resolutionMeters/2
    y=int(y)+resolutionMeters/2
    zone=int(zone)
    lat,lon=to_latlon(x,y,zone,zoneletter)
    lat=round(lat,PRECISION)
    lon=round(lon,PRECISION)
    return (lon,lat)

if __name__=='__main__':
    import argparse

    parser=argparse.ArgumentParser(
              description='Get UTM aggregation for lat/lon pair.'
              )
    parser.add_argument('lat', type=str, 
                                help='latitude OR UTM string')
    parser.add_argument('lon', type=float,nargs='?', 
                                help='longitude')
    parser.add_argument('span', type=int,default=1,nargs='?', 
                                help='UTM span (default 1km)')
    args=parser.parse_args()

    if ' ' in args.lat:
        print('Parsing '+args.lat+' as UTM string.')
        coords=args.lat.split(' ');
        e=float(coords[0])
        n=float(coords[1])
        zn=int(coords[2])
        latlon=to_latlon(e,n,zn,coords[3])
        print(latlon)
        exit()

    args.lat=float(args.lat)
    if args.lat>90 or args.lat<-90:
        print('Latitude out of bounds (inputs must be lat lon [span])')
        exit()
    pt=geojson.Feature(geometry=geojson.Point((args.lon,args.lat)))
    agg=aggregate(geojson.FeatureCollection([pt]),args.span)
    print(agg)

