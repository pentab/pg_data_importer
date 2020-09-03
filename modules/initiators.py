from .validator import *


def check_type(value):
    field_type = None
    if isInteger(value):
        field_type = 'integer'
    elif isFloat(value):
        field_type = 'float'
    elif isDate(value):
        field_type = 'date'
    else:
        field_type = 'text'
    return field_type


def create_table(jsonObject, fid, geometry, type, crs):
    fid = '{0} SERIAL PRIMARY KEY NOT NULL'.format(fid)
    geometry = '{0} geometry({1},{2})'.format(geometry, type, crs)
    records = []
    records.extend([fid, geometry])
    for key, value in jsonObject.items():
        if not key in ['id', 'ID', 'iD', 'Id']:
            field_type = check_type(str(value))
            record = '{0} {1}'.format(key, field_type)
            records.append(record)
    records = ','.join(records)
    return records
