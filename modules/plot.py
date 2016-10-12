"""

plot
====

"""

from math import cos,pi

import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as Pyplot
from matplotlib.patches import Polygon,Circle
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap

from modules.thirdparty.gmtcolormap import GMTColorMap
import modules.backgroundImage as BackgroundImage


class Plot:
    """
        :synopsis: Create a static map
        :param str filename: The filename to create
        :param Event event: An Event object
        :param dict mapparams: A dict of params from a eventMap
        :param dict data: Aggregated data in GeoJSON format
        
    """
    
    def __init__(self,filename,event,mapparams,data):
        self.filename=filename
        self.event=event
        self.mapparams=mapparams
        self.data=data
        self.m=None
        self.fig=None
        
        self.colors=GMTColorMap.loadFromCPT('./lib/mmi.cpt')
        
        
    def create(self):
        filename=self.filename
        
        self.getParams()

        self.fig=Pyplot.figure(dpi=250)
        self.ax=self.fig.add_subplot(111)
        
        # epsg=3857 to match NatGeo_World_Map
        m=Basemap(projection='merc',
                  llcrnrlat=self.south,
                  llcrnrlon=self.west,
                  urcrnrlat=self.north,
                  urcrnrlon=self.east,
                  lat_ts=(self.north+self.south)/2,
                  epsg=3857,
                  ellps='WGS84',
                  fix_aspect=False,
                  resolution='i')

        self.m=m
        BackgroundImage.addImage(self)

        titletext='DYFI %s' % (self.mapparams.eventid)
        Pyplot.title(titletext)

        m.drawcoastlines(zorder=3)
        #m.drawmapboundary(fill_color='aqua',zorder=3)
        #m.fillcontinents(color=(0.7,0.7,0.7),
        #                 lake_color='aqua',zorder=3)
        
        m.drawparallels(Plot.degreelines(self.south,self.north),
                        labels=[1,0,0,1])
        m.drawmeridians(Plot.degreelines(self.west,self.east),
                        labels=[1,0,0,1])

        self.plotData(m)

        m.plot(self.event.lon,self.event.lat,'k*',
               latlon=True,mew=0.2,markersize=20,
               mfc='red',mec='black',zorder=5)        
        
        try:
            pass
#            Pyplot.show()
        except:
            pass
        Pyplot.savefig(filename,dpi=250)
        Pyplot.close()
        
        return filename
    
        
    def getParams(self):
        event=self.event
        mp=self.mapparams
        
        lat_span=0
        lon_span=0
        lat_offset=0
        lon_offset=0
        
        if hasattr(mp,'lat_span') and mp.lat_span:
            lat_span=mp.lat_span
            print('Asserting lat_span',lat_span)
        if hasattr(mp,'lon_span') and mp.lon_span:
            lon_span=mp.lon_span
            print('Asserting lon_span',lon_span)
        if hasattr(mp,'lat_offset') and mp.lat_offset:
            lat_offset=mp.lat_offset
        if hasattr(mp,'lon_offset') and mp.lon_offset:
            lon_offset=mp.lon_offset
        
        if lon_span==0:
            lon_span=10
        
        if lat_span==0:
            lat_span=Plot.get_latspan(event.lat+lat_offset,lon_span)
        
        north=event.lat+lat_offset+lat_span/2
        south=event.lat+lat_offset-lat_span/2
        east=event.lon+lon_offset+lon_span/2
        west=event.lon+lon_offset-lon_span/2
        
        print('Plot: bounds lat:%s,%s lon:%s,%s' %
              (south,north,west,east))

        self.north=north
        self.south=south
        self.west=west
        self.east=east

        return
    
    
    def plotData(self,m):
        """
            :synopsis:
            :param m: A map object returned by Basemap
        """
        
        data=self.data
        patches=[]
        colors=[]

        for pt in data.features:

            ### TODO: Plot a Point as a circle

            featuretype=pt.geometry.type
            

            if featuretype=='Point':
                coords=pt.geometry.coordinates
                coords=Plot.transform([coords],m)
                poly=Circle(coords[0],
                             fill=True,radius=10000)

            elif featuretype=='Polygon':
                coords=pt.geometry.coordinates[0]
                coords=Plot.transform(coords,m)
                poly=Polygon(np.array(coords),
                             closed=True)
            patches.append(poly)

            if 'intensity' in pt.properties:
                intensity=pt.properties['intensity']
            elif 'cdi' in pt.properties:
                intensity=pt.properties['cdi']
            else:
                intensity=9
                    
            col=self.colors.getHexColor(intensity)[0]
            colors.append(col)

        if patches:
            coll=PatchCollection(
                patches,zorder=4,
                edgecolor='k',
                linewidth=0.2
            )
            coll.set_facecolor(colors)
            self.ax.add_collection(coll)

        return m
        
    
    # Below these are class methods

    
    def get_latspan(lat,lon_span):
        scale=cos(lat*pi/180)
        if scale>2:
            print('WARNING: Plot::get_latspan scale',scale,'.')
            print('WARNING: Plot::get_latspan set to 2.')
            print('WARNING: Plot may not be square.')
            scale=2

        return scale*lon_span
    
    
    def degreelines(a,b):
        aint=int(a)
        bint=int(b+0.5)
        return range(aint,bint)
        

    def transform(coords,m):
        newcoords=[]
        for pt in coords:
            x,y=m(pt[0],pt[1])
            newcoords.append([x,y])
            
        return newcoords
    
