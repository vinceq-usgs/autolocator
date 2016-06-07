"""
Geoserve URL query is this:
http://earthquake.usgs.gov/ws/geoserve/regions.json?latitude=49.335&longitude=-76.9526&type=admin

Geoserve raw output is this:
{"metadata":{"request":"http:\/\/earthquake.usgs.gov\/ws\/geoserve\/regions.json?latitude=49.335&longitude=-76.9526&type=admin","submitted":"2016-06-07T00:06:09+00:00","types":["admin"],"version":"1.2.0"},"admin":{"type":"FeatureCollection","count":1,"features":[{"type":"Feature","id":68314,"geometry":null,"properties":{"iso":"CAN","country":"Canada","region":"Qu\u00e9bec"}}]}}

"""

URL='http://earthquake.usgs.gov/ws/geoserve/regions.json?latitude={}&longitude={}&type={}'

def getname(lat,lon):
  

