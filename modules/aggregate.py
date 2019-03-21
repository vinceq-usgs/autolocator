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


def getUtmPolyFromString(utm,span):
    """

    :synopsis: Compute the (lat/lon) bounds and center from a UTM string
    :param utm: A UTM string
    :param int span: The size of the UTM box in meters
    :return: :py:obj:`dict`, see below

    Get the bounding box polygon and center point for a UTM string suitable for plotting.

    The return value has two keys:

    ======    ========================
    center    A GeoJSON Point object
    bounds    A GeoJSON Polygon object
    ======    ========================

    """

    x,y,zone,zoneletter=utm.split()
    x=int(x)
    y=int(y)
    zone=int(zone)

    # Compute bounds. Need to reverse-tuple here because the
    # to_latlon function returns lat/lon and geojson requires lon/lat.
    # Rounding needed otherwise lat/lon coordinates are arbitrarily long

    ebound=zone*6-180
    wbound=ebound-6

    def _reverse(tup,eastborder=None):

        (y,x)=tup
        if eastborder and x>ebound:
            x=ebound
        elif x<wbound:
            x=wbound
        x=round(x,PRECISION)
        y=round(y,PRECISION)
        return (x,y)

    p1=_reverse(to_latlon(x,y,zone,zoneletter))
    p2=_reverse(to_latlon(x,y+span,zone,zoneletter))
    p3=_reverse(to_latlon(x+span,y+span,zone,zoneletter),'e')
    p4=_reverse(to_latlon(x+span,y,zone,zoneletter),'e')
    bounds=geojson.Polygon([[p1,p2,p3,p4,p1]])

    # Compute center
    cx=int(x)+span/2
    cy=int(y)+span/2
    clat,clon=to_latlon(cx,cy,zone,zoneletter)
    clat=round(clat,PRECISION)
    clon=round(clon,PRECISION)
    center=geojson.Point((clon,clat))

    return ({'center':center,'bounds':bounds})

