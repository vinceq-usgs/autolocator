#! /usr/local/bin/python3

import mysql.connector
import geojson
import datetime
import json

class Db():
    """
Interface for connecting to the MySQL database.

Requirements:
    A dbconfigfile in JSON format with the following keys: USER,PASSWORD,DATABASE. The default lives in '/home/shake/db.json.' Otherwise, specify the location when calling Db().

Usage:
    from db import Db
    db=Db([configfile.json])
    results=db.extquery(columns,table,querytext) : 
        returns extended entries in geojson format.
        columns : column name, or list of columns, or comma-delimited list, or
            all : get all columns
            cdi : get columns from db.cdicolumns
        table : table name, list of tables, or comma-delimited list, or
            (blank) : all extended tables
            latest : only the latest extended table
        query : MySQL query text after 'WHERE'

    results=db.query(columns,table,querytext) :
        simpler version that returns a raw dict.
        columns : column name or comma-delimited list
        table : table name only
        query : MySQL query text after 'WHERE'

    db.connector : ref to MySQL connector
    db.cursor : ref to MySQL cursor, for making custom queries
    db.allcolumns : list of all columns in the database
    db.cdicolumns : list of columns used for calculating CDI


    """

    def __init__(self,dbconfigfile='/home/shake/db.json'):

        self.allcolumns=['subid','eventid','orig_id','suspect','region','usertime','time_now','latitude','longitude','geo_source','zip','zip_4','city','admin_region','country','street','name','email','phone','situation','building','asleep','felt','other_felt','motion','duration','reaction','response','stand','sway','creak','shelf','picture','furniture','heavy_appliance','walls','slide_1_foot','d_text','damage','building_details','comments','user_cdi','city_latitude','city_longitude','city_population','zip_latitude','zip_longitude','location','tzoffset','confidence','version','citydb','cityid']
        self.cdicolumns=['subid','latitude','longitude','felt','other_felt','motion','reaction','stand','shelf','picture','furniture','damage','time_now']

        dbparams=json.load(open(dbconfigfile))
        EXT_MINYR=2003;
        EXT_MAXYR=2016;

        self.exttables=['extended_' + str(x) for x in
            (['pre'] + list(range(EXT_MINYR,EXT_MAXYR+1)))]
        self.latesttable=self.exttables[-1]

        connector=mysql.connector.connect(
            user=dbparams['USER'],
            password=dbparams['PASSWORD'],
            database=dbparams['DATABASE'])
        self.connector=connector
        self.cursor=self.connector.cursor(dictionary=True)

    def extquery(self,columns,table,text):
        """
The main API function for making extended database queries. Mostly a
wrapper to query(), but converts output to geojson.

    columns: single column, list, or comma-delimited string
    table: single table, list, or comma-delimited string
    text: text after WHERE in MySQL query

        """

        if not columns or columns=='all':
            columns='*'
        elif not isinstance(columns,str):
            columns=','.join(columns)
        elif columns=='cdi':
            columns=','.join(self.cdicolumns)

        if not table or table=='extended' or table=='all':
            tables=self.exttables
        elif table=='latest':
            tables=[self.latesttable]
        elif ',' in table:
            tables=table.split(',')
        else:
            tables=[table]

        results=[]
        for table in tables:
            result=self.query(table,columns,text)
            for rowdata in result:
                rowgeojson=self.row2geojson(rowdata)
                if not rowgeojson:
                    continue
                rowgeojson['properties']['table']=table
                results.append(rowgeojson)
      
        fc=geojson.FeatureCollection(results)
        print('Done with extquery, returning.')
        return fc 

    def query(self,table,column,text):
        """
Simpler MySQL query. The parameters table and column must be strings.

        """
        template='SELECT '+column+' FROM '+table+' WHERE '+text
        results=self.rawquery(template)
        return results

    def rawquery(self,text):
        """
Simplest MySQL query with the raw query string, no formatting.

        """
        print("Query: "+text)
        self.cursor.execute(text)
        results=self.cursor.fetchall()
        return results

    def timedelta(self,t,t0=None):
        if t0:
            t0=datetime.datetime.strptime(t0,'%Y-%m-%d %H:%M:%S')
        else:
            t0=datetime.datetime.now()
            t0=t0.replace(microsecond=0)

        tdelta=datetime.timedelta(minutes=t)
        """"
        if reverse:
            tnew=t0+tdelta
        else:
            tnew=t0-tdelta
        """
        tnew=t0+tdelta
        return(tnew)

    def row2geojson(self,row):
        lat=row['latitude']
        lon=row['longitude']
        if not lat or not lon:
            print('Unable to get lat/lon for this row')
            return
        pt=geojson.Point((lon,lat))
        props={}
        for key,val in row.items():
            if key=='latitude' or key=='longitude':
                continue
            if val=='null' or val=='': 
                val=None
            props[key]=val
        feature=geojson.Feature(geometry=pt,properties=props)
        return(feature)

    # Class method
    def serialize_datetime(obj):

        if isinstance(obj,datetime.datetime):
            serial = obj.isoformat()
            return serial


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(
        description='Access the DYFI MySQL database.'
    )
    parser.add_argument('--extended',type=str,nargs='?',
        help="Extended query with geojson output")
    parser.add_argument('query',type=str,nargs='?',
        help="MySQL query (raw query, if no --extended)")
    args=parser.parse_args()

    db=Db()
    if args.extended:
        if not args.query:
            args.query=args.extended
            args.extended=True

        table='all'
        if isinstance(args.extended,str):
            table=args.extended
        results=db.extquery('*',table,args.query)
        for row in results:
            print(row.properties['table']+':'+str(row.properties['subid']))
        exit()

    else:
        results=db.rawquery(args.query)

    print(results)


