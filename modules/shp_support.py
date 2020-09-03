import shapefile
import json


def shp_handle(filename):
    global error
    try:
        json_template = {"type": "FeatureCollection", "features": []}
        sf = shapefile.Reader(filename)
        records = sf.shapeRecords()
        jsonObject = records.__geo_interface__['features']
        json_template['features'] = jsonObject
        error = None
        return error, json_template
    except Exception as error:
        error = error
        json_template = None
        return error, json_template
