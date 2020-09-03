import json
from .validator import *
import sys


def get_file_attributes(filename):
    with open(filename, 'r') as json_file:
        fileContents = json.load(json_file)
    pureOriginalKeys = []
    for key in fileContents['features'][0]['properties'].keys():
        pureOriginalKeys.append(key.lower())
    return pureOriginalKeys, fileContents


def json_handle(*args, **kwargs):
    global sql_file
    global fieldsNames
    global records
    global error
    try:
        fieldsNames = kwargs['fieldsNames']
        crs = kwargs['crs']
        filename = kwargs['filename']
        skipAttributes = kwargs['skipAttributes']
        askToSelect = kwargs['askToSelect']
        selectedAttr = kwargs['selectedAttr']
        renameAttr = kwargs['renameAttr']
        renamedAttr = kwargs['renamedAttr']
        genID = kwargs['genID']
        append = kwargs['append']
        pureOriginalKeys, fileContents = get_file_attributes(filename)
        originalKeys = []
        if len(pureOriginalKeys) == 1 and pureOriginalKeys[0] in ['id', 'ID', 'iD', 'Id']:
            skipAttributes = True
        elif 'id' in pureOriginalKeys:
            pureOriginalKeys.remove('id')
        if skipAttributes:
            skipAttrib = True
            fieldsNames = fieldsNames
        else:
            skipAttrib = False
            if askToSelect:
                selectFlag = True
                for value in selectedAttr:
                    if not value in pureOriginalKeys:
                        error = 'The attribute {0} not present in current attributes'.format(
                            value)
                        raise Exception(error)
                        selectFlag = False
            else:
                selectFlag = False
            if selectFlag:
                originalKeys = selectedAttr
            else:
                originalKeys = pureOriginalKeys
            if renameAttr:
                modifyFlag = True
                if len(renamedAttr) > len(originalKeys):
                    error = 'Attributes to be modified is greater than current attributes'
                    raise Exception(error)
                    modifyFlag = False
                else:
                    modifyFlag = True
                    keysToBeModifiedIndexes = []
                    for item in selectedAttr:
                        if item in originalKeys:
                            keysToBeModifiedIndexes.append(
                                pureOriginalKeys.index(item))
                            modifyFlag = True
                        else:
                            error = 'Item "{0}" not found in original attributes'.format(
                                item)
                            raise Exception(error)
                            modifyFlag = False
                if modifyFlag:
                    if len(selectedAttr) != len(renamedAttr):
                        error = 'Length does not match'
                        raise Exception(error)
                        modifyFlag = False
                    else:
                        modkey = originalKeys[:]
                        modPair = []
                        for i in range(0, len(renamedAttr)):
                            modPair.append(selectedAttr[i])
                            if not renamedAttr[i].islower():
                                renamedAttr[i] = '"' + renamedAttr[i] + '"'
                            modkey[i] = renamedAttr[i]
                        fieldsNames = fieldsNames + modkey
                else:
                    fieldsNames = fieldsNames + originalKeys
            else:
                modifyFlag = False
                fieldsNames = fieldsNames + originalKeys
        if append:
            fieldsNames.remove('id')
        fieldsNames = '(' + ', '.join(fieldsNames) + ')'
        tableIDs = []
        if append:
            pass
        else:
            if genID:
                for i in range(1, len(fileContents['features']) + 1):
                    tableIDs.append(i)
            else:
                if 'id' in fileContents['features'][0]['properties']:
                    for i in range(0, len(fileContents['features'])):
                        tableIDs.append(
                            int(fileContents['features'][i]['properties']['id']))
                else:
                    if 'id' in fileContents['features'][0]:
                        for i in range(0, len(fileContents['features'])):
                            tableIDs.append(
                                int(fileContents['features'][i]['id']))
                    else:
                        for i in range(1, len(fileContents['features']) + 1):
                            tableIDs.append(i)
        queryStart = '(SELECT ST_GeomFromGeoJSON(\''
        geoJSON = {"type": "value", "coordinates": "value", "crs": {
            "type": "name", "properties": {"name": "value"}}}
        geoJSON['type'] = fileContents['features'][0]['geometry']['type']
        geoJSON['crs']['properties']['name'] = 'epsg:{0}'.format(crs)
        queryEnd = '\'))'
        geometries = []
        initRecords = []
        for i in range(0, len(fileContents['features'])):
            geoJSON['coordinates'] = fileContents['features'][i]['geometry']['coordinates']
            geoQuery = queryStart + json.dumps(geoJSON) + queryEnd
            geometries.append(geoQuery)
            if not skipAttrib:
                record = []
                for key, value in fileContents['features'][i]['properties'].items():
                    if modifyFlag:
                        if key.lower() in modPair:
                            if isInteger(str(value)) or isFloat(str(value)):
                                record.append(str(value))
                            else:
                                if value == '':
                                    value = 'Null'
                                    record.append(value)
                                elif '\'' in value:
                                    value = value.replace("'", "''")
                                    record.append("'" + value + "'")
                                else:
                                    record.append("'" + value + "'")
                    else:
                        if selectFlag:
                            if key.lower() in selectedAttr:
                                if isInteger(str(value)) or isFloat(str(value)):
                                    record.append(str(value))
                                else:
                                    if value == '':
                                        value = 'Null'
                                        record.append(value)
                                    elif '\'' in value:
                                        value = value.replace("'", "''")
                                        record.append("'" + value + "'")
                                    else:
                                        record.append("'" + value + "'")
                        else:
                            if key.lower() in pureOriginalKeys:
                                if isInteger(str(value)) or isFloat(str(value)):
                                    record.append(str(value))
                                else:
                                    if value == '' or value == None:
                                        value = 'Null'
                                        record.append(value)
                                    elif '\'' in value:
                                        value = value.replace("'", "''")
                                        record.append("'" + value + "'")
                                    else:
                                        record.append("'" + value + "'")
                initRecords.append(','.join(record))
        records = []
        if append:
            for i in range(0, len(fileContents['features'])):
                if not skipAttrib:
                    tabRecord = '(' + geometries[i].replace('\\',
                                                            '') + ', ' + initRecords[i] + ')'
                else:
                    tabRecord = '(' + geometries[i].replace('\\', '') + ')'
                records.append(tabRecord)
        else:
            for i in range(0, len(tableIDs)):
                if not skipAttrib:
                    tabRecord = '(' + str(tableIDs[i]) + ', ' + geometries[i].replace(
                        '\\', '') + ', ' + initRecords[i] + ')'
                else:
                    tabRecord = '(' + str(tableIDs[i]) + ', ' + \
                        geometries[i].replace('\\', '') + ')'
                records.append(tabRecord)
        records = ', '.join(records)
        sql_file = True
        error = None
    except Exception as exError:
        error = 'Error while generating SQL statement: ' + str(exError)
        sql_file = False
        fieldsNames = None
        records = None
    return sql_file, error, fieldsNames, records
