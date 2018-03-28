#! /usr/bin/env python3

import geojson
import argparse
import copy

from modules.plot import Plot

resizeplot='800'

def main():
    parser=argparse.ArgumentParser(
        description='Convert GeoJSON results file to PNG file.'
    )
    parser.add_argument('resultfile',type=str,default='./latest.geojson',
        help='input file in GeoJSON format')

    args=parser.parse_args()

    with open(args.resultfile,'r') as f:
        input=geojson.load(f)

    event=Event(input)
    mapparams=mapParams(input)
    data=Data(input)

    plot=Plot('latest.png',event,mapparams,data)
    plot.create()

    plotresize(['/bin/convert','-resize',resizeplot,'latest.png','latest.jpg'])



class Event:
    def __init__(self,input):

        p=input['properties']
        self.lat=p['lat']
        self.lon=p['lon']
        self.mag=p['mag']


class mapParams:
    def __init__(self,input):
        self.eventid=input['id']
        

def Data(input):

    class myDict(dict):
        pass

    data=myDict()
    features=input['features']
    rfeatures=[x for x in features if 'magnitude' not in x['properties']]
    data.features=rfeatures

    return(data)


def plotresize(commands):
    import subprocess
    print('Resizing with:',commands)
    subprocess.call(commands)  


if __name__=='__main__':
    main()

