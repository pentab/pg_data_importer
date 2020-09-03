import csv
from .validator import *


def csv_handle(filename, delimiter, crs):
    try:
        global sql_file
        global fieldsNames
        global records
        global error
        csvContents = []
        geometries = ['point', 'multipoint', 'linestring',
                      'multilinestring', 'polygon', 'multipolygon', 'geometrycollection']
        with open(filename, newline='', encoding='utf8') as lookupHandle:
            fileContents = csv.reader(
                lookupHandle, delimiter=delimiter, quoting=csv.QUOTE_NONE)
            header = next(fileContents)
            for row in fileContents:
                csvContents.append(row)
        fieldsNames = []
        for i in range(0, len(header)):
            if not header[i].islower():
                header[i] = '"' + header[i] + '"'
            fieldsNames.append(header[i])
        fieldsNames = '(' + ', '.join(fieldsNames) + ')'
        records = []
        for row in csvContents:
            row[0] = int(row[0])
            tableIDs = []
            tableIDs.append(row[0])
            tableRecord = []
            tableRecord.append(row[1:])
            for i in range(0, len(tableRecord[0])):
                tableRecord[0][i] = tableRecord[0][i].strip()
                if '\'' in str(tableRecord[0][i]):
                    tableRecord[0][i] = tableRecord[0][i].replace("'", "''")
                if not isFloat(tableRecord[0][i]) or not isInteger(tableRecord[0][i]):
                    if tableRecord[0][i] == '' or tableRecord[0][i] == None:
                        tableRecord[0][i] = 'Null'
                    else:
                        tableRecord[0][i] = "'" + tableRecord[0][i] + "'"
                if any(x in tableRecord[0][i].lower() for x in geometries):
                    queryStart = '(SELECT ST_GeomFromText('
                    queryEnd = ', {0}))'.format(crs)
                    tableRecord[0][i] = queryStart + \
                        tableRecord[0][i] + queryEnd
            tableRecord = '(' + str(tableIDs[0]) + \
                ', ' + ', '.join(tableRecord[0]) + ')'
            records.append(tableRecord)
        records = ', '.join(records)
        sql_file = True
        error = None
        return sql_file, error, fieldsNames, records
    except ValueError:
        error = 'Invalid delimiter'
        sql_file = False
        fieldsNames = None
        records = None
        return sql_file, error, fieldsNames, records
    except Exception as error:
        error = error
        sql_file = False
        fieldsNames = None
        records = None
        return sql_file, error, fieldsNames, records
