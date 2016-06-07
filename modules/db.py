import mysql.connector
import geojson
import datetime
import json

class Db():
  """
Prototype database class for connecting to the MySQL database.

  """

  def __init__(self,inputfile='/home/shake/db.json'):

    self.CDICOLUMNS=['subid','latitude','longitude','felt','other_felt','motion','reaction','stand','shelf','picture','furniture','damage']

    
    dbparams=json.load(open(inputfile))
    EXT_MINYR=2003;
    EXT_MAXYR=2016;

    self.EXTTABLES=['extended_' + str(x) for x in
      (['pre'] + list(range(EXT_MINYR,EXT_MAXYR+1)))]
    self.TABLE_LATEST=self.EXTTABLES[-1]

    connector=mysql.connector.connect(
          user=dbparams['USER'],
          password=dbparams['PASSWORD'],
          database=dbparams['DATABASE'])
    self.connector=connector
    self.cursor=self.connector.cursor()

  def query(self,columns,table,text):
    """
The main interface for making database queries

columns: single column or comma-delimited string
table: single table, list, or comma-delimited string
text: text after WHERE in MySQL query

    """

    if not columns:
      columns='count(*)'
    elif columns=='cdi':
      columns=','.join(self.CDICOLUMNS)

    template='SELECT '+columns+' FROM {!s} WHERE '+text
    templatetotal='SELECT count(*) FROM {!s}'

    if (not table) or (table=='extended'):
      tables=self.EXTTABLES
    elif table=='latest':
      tables=[self.TABLE_LATEST]
    elif ',' in table:
      tables=table.split(',')
    else:
      tables=[table]

    results=[]
    for table in tables:
      result=self._querytable(table,template)

      tableresult=[]
      for rowdata in result:
        rowresult={}
        for column,datum in zip(columns.split(','),rowdata):
          rowresult[column]=datum
        tableresult.append(rowresult)

      if tableresult:
        results.append({table:tableresult})

    if results:
      results=self.raw2geojson(results)       
    return results

  def _querytable(self,table,template):
      querytext=template.format(table)
      print("Query: "+querytext)
      self.cursor.execute(querytext)
      print("Done with query.")
      thisresults=self.cursor.fetchall()
      return thisresults

  def timeago(self,t):
    t0=datetime.datetime.now()
    tdelta=datetime.timedelta(minutes=t)
    tnew=t0-tdelta
    return(tnew)

  def raw2geojson(self,raw):
    features=[]
    for table in raw[0]:
      for row in raw[0][table]:
        lat=row['latitude']
        lon=row['longitude']
        pt=geojson.Point((lon,lat))
        props={}
        for col in self.CDICOLUMNS:
          if col=='latitude' or col=='longitude':
            continue

          val=row[col]
          newval=val
          if val=='null': newval=None
          elif isinstance(newval,str) and (' ' in val): 
            newval=newval.split(' ')
            newval=newval[0]

          if isinstance(newval,str):
            newval=int(newval)
 
          props[col]=newval
 
        feature=geojson.Feature(geometry=pt,properties=props)
        features.append(feature)

    output=geojson.FeatureCollection(features)
    return(output)

 
