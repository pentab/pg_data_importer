# IMPORTS
import os
import sys
import json
import psycopg2
from psycopg2.errors import *
from datetime import datetime
from modules import csv_support
from modules import json_support
from modules import shp_support
from modules.validator import *
from modules.initiators import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
# VARIABLES
cwd = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
cmd = cwd + 'modules'
logs = cwd + 'logs'
icons = cwd + 'icons'
data = cwd + 'data'
if not os.path.exists(logs):
    os.mkdir(logs)
log_date = datetime.now()
log_date = log_date.strftime("%d-%m-%Y_%H-%M-%S")
logFile = logs + os.path.sep + 'log-{}.log'.format(log_date)
operations = data + os.path.sep + 'gen.json'
output_sql = cwd + 'output.sql'
shp_json = cwd + 'shp_contents.json'
file_filter = None
file_selector = None
opened_file = None
fieldsNames = None
records = None
layer_attributes = None
error = None
connection = None
# READING GENERATOR FILE
with open(operations, '+r') as opHandler:
    genData = json.load(opHandler)
# LOAD UI WINDOW-
app = QtWidgets.QApplication([])
app.setApplicationName('Data Importer')
app.setWindowIcon(QIcon(os.path.join(icons, "icon.ico")))
win = uic.loadUi(os.path.join(data, "main.ui"))
with open(os.path.join(cwd, 'servers.json'), 'r', encoding='utf8') as json_file:
    servers = json.load(json_file)
for i in servers['names']:
    win.serverList.addItem(i)
# UI TRIGGER FUNCTIONS


def selector_changed():
    global file_filter
    global file_selector
    file_selector = win.fileSelector.currentText()
    if file_selector == 'Choose file':
        win.browse.setEnabled(False)
    elif file_selector == 'CSV':
        file_filter = "csv (*.csv)"
        win.browse.setEnabled(True)
    elif file_selector == 'GeoJSON':
        file_filter = "json (*.json *.geojson)"
        win.browse.setEnabled(True)
    elif file_selector == 'Shapefile':
        file_filter = "Esri-Shapefile (*.shp *.dbf)"
        win.browse.setEnabled(True)


def update_creds():
    value = win.serverList.currentText()
    if value == 'Select server':
        reset_conn_values()
    else:
        itemIndex = servers['names'].index(value)
        win.conName.setText(servers['names'][itemIndex])
        win.server.setText(servers['servers'][itemIndex])
        win.port.setText(servers['ports'][itemIndex])
        win.username.setText(servers['users'][itemIndex])
        win.password.setText(servers['passwords'][itemIndex])
        win.database.setText(servers['databases'][itemIndex])


def file_name_checker():
    value = win.filename.text()
    if value == '':
        win.load.setEnabled(False)
    else:
        win.load.setEnabled(True)


def change_trigger():
    if win.defaultChecker.isChecked():
        win.jsonID.setEnabled(True)
        win.jsonGeom.setEnabled(True)
    else:
        win.jsonID.setEnabled(False)
        win.jsonGeom.setEnabled(False)


def skip_trigger():
    if win.skipChecker.isChecked():
        win.selectChecker.setChecked(False)
        win.selectChecker.setEnabled(False)
        win.renameChecker.setChecked(False)
        win.renameChecker.setEnabled(False)
        win.selectFields.setText('')
        win.renameFields.setText('')
        win.createTable.setChecked(False)
        win.createTable.setEnabled(False)
    else:
        win.selectChecker.setEnabled(True)
        win.renameChecker.setEnabled(False)
        win.selectChecker.setChecked(False)
        win.renameChecker.setChecked(False)
        win.selectFields.setText('')
        win.renameFields.setText('')
        if win.append.isChecked() or win.truncateData.isChecked():
            pass
        else:
            win.createTable.setChecked(False)
            win.createTable.setEnabled(True)


def select_trigger():
    if win.selectChecker.isChecked():
        win.skipChecker.setEnabled(False)
        win.skipChecker.setChecked(False)
        win.selectFields.setEnabled(True)
        win.selectFields.setText('')
        win.renameChecker.setEnabled(True)
        win.renameChecker.setChecked(False)
        win.renameFields.setText('')
        win.createTable.setChecked(False)
        win.createTable.setEnabled(False)
    else:
        win.skipChecker.setEnabled(True)
        win.skipChecker.setChecked(False)
        win.selectFields.setEnabled(False)
        win.selectFields.setText('')
        win.renameChecker.setEnabled(False)
        win.renameChecker.setChecked(False)
        win.renameFields.setText('')
        if win.append.isChecked() or win.truncateData.isChecked():
            pass
        else:
            win.createTable.setChecked(False)
            win.createTable.setEnabled(True)


def rename_trigger():
    if win.renameChecker.isChecked():
        win.renameFields.setEnabled(True)
        win.renameFields.setText('')
    else:
        win.renameFields.setEnabled(False)
        win.renameFields.setText('')


def create_table_trigger():
    if win.createTable.isChecked():
        win.skipChecker.setEnabled(False)
        win.skipChecker.setChecked(False)
        win.selectChecker.setEnabled(False)
        win.selectChecker.setChecked(False)
        win.truncateData.setEnabled(False)
        win.truncateData.setChecked(False)
        win.append.setEnabled(False)
        win.append.setChecked(False)
    else:
        win.skipChecker.setEnabled(True)
        win.skipChecker.setChecked(False)
        win.selectChecker.setEnabled(True)
        win.selectChecker.setChecked(False)
        win.truncateData.setEnabled(True)
        win.truncateData.setChecked(False)
        win.append.setEnabled(True)
        win.append.setChecked(False)


def append_trigger():
    if win.append.isChecked():
        win.truncateData.setEnabled(False)
        win.truncateData.setChecked(False)
        win.createTable.setEnabled(False)
        win.createTable.setChecked(False)
    else:
        win.truncateData.setEnabled(True)
        win.truncateData.setChecked(False)
        if win.truncateData.isChecked() or win.skipChecker.isChecked():
            pass
        else:
            win.createTable.setEnabled(True)
            win.createTable.setChecked(False)


def truncate_trigger():
    if win.truncateData.isChecked():
        win.append.setEnabled(False)
        win.append.setChecked(False)
        win.createTable.setEnabled(False)
        win.createTable.setChecked(False)
    else:
        win.append.setEnabled(True)
        win.append.setChecked(False)
        if win.append.isChecked() or win.skipChecker.isChecked():
            pass
        else:
            win.createTable.setEnabled(True)
            win.createTable.setChecked(False)
# UI HELPING FUNCTIONS


def directory_browser():
    global error
    global opened_file
    global layer_attributes
    current_time = datetime.now().time()
    opened_file = QFileDialog.getOpenFileName(filter=file_filter)
    opened_file = opened_file[0]
    win.filename.setText(opened_file)
    if opened_file == '':
        win.browser.append('[+] {0}: No selected files'.format(current_time))
        win.fileOptions.setTabEnabled(0, False)
        win.fileOptions.setTabEnabled(1, False)
        win.fileOptions.setCurrentIndex(0)
    elif '.csv' in opened_file:
        win.fileOptions.setEnabled(True)
        win.browser.append(
            '[+] {0}: File {1} added'.format(current_time, opened_file))
        win.fileOptions.setTabEnabled(0, True)
        win.fileOptions.setTabEnabled(1, False)
        win.fileOptions.setCurrentIndex(0)
        win.csv.setEnabled(True)
    elif any(x in opened_file for x in ['.json', '.geojson', '.dbf', '.shp']):
        win.fileOptions.setEnabled(True)
        win.browser.append(
            '[+] {0}: File {1} added'.format(current_time, opened_file))
        win.fileOptions.setTabEnabled(0, False)
        win.fileOptions.setTabEnabled(1, True)
        win.fileOptions.setCurrentIndex(1)
        if any(x in opened_file for x in ['.dbf', '.shp']):
            error, contents = shp_support.shp_handle(opened_file)
            if error == None:
                with open(shp_json, 'w+') as shp_handle:
                    json.dump(contents, shp_handle)
                layer_attributes, fileContents = json_support.get_file_attributes(
                    shp_json)
            else:
                win.browser.append(
                    '[-] {0}: Error: {1}'.format(current_time, error))
        else:
            layer_attributes, fileContents = json_support.get_file_attributes(
                opened_file)
        win.browser.append('[+] {0}: Attributes are:'.format(current_time))
        for record in layer_attributes:
            win.browser.append('\t[*] {0}'.format(record))
    else:
        win.browser.append(
            '[+] {0}: No valid files selected'.format(current_time))
        win.fileOptions.setTabEnabled(0, False)
        win.fileOptions.setTabEnabled(1, False)
        win.fileOptions.setCurrentIndex(0)


def connection_enabled():
    win.fileSelector.setEnabled(False)
    win.browse.setEnabled(False)
    win.load.setEnabled(False)
    win.server.setEnabled(True)
    win.port.setEnabled(True)
    win.username.setEnabled(True)
    win.password.setEnabled(True)
    win.database.setEnabled(True)
    win.schema.setEnabled(True)
    win.table.setEnabled(True)
    win.run.setEnabled(True)


def load_file():
    global fieldsNames
    global records
    global error
    current_time = datetime.now().time()
    if file_selector == 'CSV':
        delimiter = win.csv.currentText()
        crs = win.csvcrs.text()
        if delimiter == 'Choose delimiter':
            win.browser.append(
                '[-] {0}: Please choose a delimiter'.format(current_time))
        else:
            if delimiter == 'Comma':
                delimiter = ','
            elif delimiter == 'Tab':
                delimiter = '	'
            if isInteger(crs):
                if int(crs) < 2000 or int(crs) > 69036405:
                    win.browser.append(
                        '[-] {0}: Valid crs is between 2000 & 69036405'.format(current_time))
                else:
                    sql_file, error, fieldsNames, records = csv_support.csv_handle(
                        opened_file, delimiter, crs)
                    if error == None:
                        win.csv.setEnabled(False)
                        win.csvcrs.setEnabled(False)
                        connection_enabled()
                    else:
                        win.browser.append(
                            '[-] {0}: Error: {1}'.format(current_time, error))
            else:
                win.browser.append(
                    '[-] {0}: Valid crs is between 2000 & 69036405'.format(current_time))
    elif file_selector == 'GeoJSON' or file_selector == 'Shapefile':
        skipAttr = win.skipChecker.isChecked()
        selectAttr = win.selectChecker.isChecked()
        selectedAttr = win.selectFields.text().split(',')
        renAttr = win.renameChecker.isChecked()
        renamedAttr = win.renameFields.text().split(',')
        append = win.append.isChecked()
        fieldsNames = []
        fieldsNames.extend([win.jsonID.text(), win.jsonGeom.text()])
        genID = win.genIDs.isChecked()
        crs = win.jsoncrs.text()
        if isInteger(crs):
            if int(crs) >= 2000 and int(crs) <= 69036405:
                if file_selector == 'Shapefile':
                    sql_file, error, fieldsNames, records = json_support.json_handle(
                        crs=crs, fieldsNames=fieldsNames, filename=shp_json, skipAttributes=skipAttr, askToSelect=selectAttr, selectedAttr=selectedAttr, renameAttr=renAttr, renamedAttr=renamedAttr, genID=genID, append=append)
                else:
                    sql_file, error, fieldsNames, records = json_support.json_handle(
                        crs=crs, fieldsNames=fieldsNames, filename=opened_file, skipAttributes=skipAttr, askToSelect=selectAttr, selectedAttr=selectedAttr, renameAttr=renAttr, renamedAttr=renamedAttr, genID=genID, append=append)
                if error == None:
                    win.jsonID.setEnabled(False)
                    win.jsonGeom.setEnabled(False)
                    win.defaultChecker.setEnabled(False)
                    win.jsoncrs.setEnabled(False)
                    win.skipChecker.setEnabled(False)
                    win.selectFields.setEnabled(False)
                    win.selectChecker.setEnabled(False)
                    win.renameFields.setEnabled(False)
                    win.renameChecker.setEnabled(False)
                    win.genIDs.setEnabled(False)
                    connection_enabled()
                else:
                    win.browser.append(
                        '[-] {0}: {1}'.format(current_time, error))
            else:
                win.browser.append(
                    '[-] {0}: Valid SRS is between "2000-69036405"'.format(current_time))
        else:
            win.browser.append(
                '[-] {0}: Valid SRS is between "2000-69036405"'.format(current_time))


def connector():
    global connection
    global error
    try:
        connection = psycopg2.connect(host=win.server.text(),
                                      port=win.port.text(),
                                      user=win.username.text(),
                                      password=win.password.text(),
                                      dbname=win.database.text(),
                                      connect_timeout=10)
    except Exception as error:
        error = error
        return connection, error
    else:
        error = None
        return connection, error


def initiator():
    global opened_file
    current_time = datetime.now().time()
    schema = win.schema.text()
    table = win.table.text()
    with open(output_sql, 'w', encoding='utf8') as fileHandle:
        if file_selector == 'CSV':
            seq = 'SELECT setval(\'{0}.{1}_{2}_seq\', COALESCE((SELECT MAX({2})+1 FROM {0}.{1}), 1), false);'.format(
                schema, table, fieldsNames[1:fieldsNames.index(',')])
        else:
            seq = 'SELECT setval(\'{0}.{1}_{2}_seq\', COALESCE((SELECT MAX({2})+1 FROM {0}.{1}), 1), false);'.format(
                schema, table, win.jsonID.text())
        fileHandle.write('INSERT INTO {0}.{1} {2} VALUES {3};{4};'.format(
            schema, table, fieldsNames, records, seq))
    with open(output_sql, 'r', encoding='utf8') as handler:
        query = handler.read()
    connection, error = connector()
    if connection and error == None:
        try:
            if file_selector == 'Shapefile':
                opened_file = shp_json
            else:
                opened_file = opened_file
            if win.truncateData.isChecked():
                trunQuery = genData['sql']['table']['truncate'].format(
                    schema, table)
                trunCursor = connection.cursor()
                trunCursor.execute(trunQuery)
                connection.commit()
            if win.createTable.isChecked():
                with open(opened_file, '+r') as handle:
                    fileContents = json.load(handle)
                props = fileContents['features'][0]['properties']
                geomType = fileContents['features'][0]['geometry']['type']
                attrbs = create_table(props, win.jsonID.text(
                ), win.jsonGeom.text(), geomType, win.jsoncrs.text())
                createQuery = genData['sql']['table']['create'].format(
                    schema, table, attrbs)
                createCursor = connection.cursor()
                createCursor.execute(createQuery)
                connection.commit()
            if win.createIndex.isChecked():
                indexQuery = genData['sql']['table']['index'].format(
                    table, win.jsonGeom.text(), schema)
                indexCursor = connection.cursor()
                indexCursor.execute(indexQuery)
                connection.commit()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            win.browser.append(
                '[+] {0}: File import: Success'.format(current_time))
            connection.close()
            cancel()
        except InvalidParameterValue as error:
            if file_selector == 'Shapefile':
                error = 'The file contains mixed geometries, which is not supported, please export file as GeoJSON from QGIS or make sure the file of single geometry and try again!'
                win.browser.append(
                    '[-] {0}: Error: {1}'.format(current_time, error))
            else:
                error = error
                win.browser.append(
                    '[-] {0}: Error: {1}'.format(current_time, error))
        except Exception as error:
            win.browser.append(
                '[-] {0}: Error: {1}'.format(current_time, error))
    else:
        win.browser.append('[-] {0} Error: {1}'.format(current_time, error))


def reset_json_ui():
    win.jsonID.setEnabled(False)
    win.jsonID.setText('id')
    win.jsonGeom.setEnabled(False)
    win.jsonGeom.setText('geometry')
    win.jsoncrs.setEnabled(True)
    win.jsoncrs.setText('4326')
    win.defaultChecker.setEnabled(True)
    win.defaultChecker.setChecked(False)
    win.skipChecker.setEnabled(True)
    win.skipChecker.setChecked(False)
    win.selectChecker.setEnabled(True)
    win.selectChecker.setChecked(False)
    win.renameChecker.setEnabled(False)
    win.renameChecker.setChecked(False)
    win.genIDs.setEnabled(True)
    win.genIDs.setChecked(False)
    win.selectFields.setEnabled(False)
    win.selectFields.setText('')
    win.renameFields.setEnabled(False)
    win.renameFields.setText('')
    win.truncateData.setChecked(False)
    win.createIndex.setChecked(False)
    win.createTable.setChecked(False)
    win.append.setChecked(False)


def reset_csv_ui():
    win.csv.setEnabled(True)
    win.csv.setCurrentIndex(0)
    win.csvcrs.setEnabled(True)
    win.csvcrs.setText('4326')


def reset_other_ui():
    win.fileOptions.setEnabled(False)
    win.filename.setText('')
    win.fileSelector.setCurrentIndex(0)
    win.fileSelector.setEnabled(True)
    win.server.setEnabled(False)
    win.port.setEnabled(False)
    win.username.setEnabled(False)
    win.password.setEnabled(False)
    win.database.setEnabled(False)
    win.schema.setEnabled(False)
    win.table.setEnabled(False)
    win.run.setEnabled(False)
    win.serverList.setCurrentIndex(0)


def reset_conn_values():
    win.conName.setText('')
    win.server.setText('')
    win.port.setText('')
    win.username.setText('')
    win.password.setText('')
    win.database.setText('')
    win.schema.setText('')
    win.table.setText('')


def cancel():
    reset_csv_ui()
    reset_json_ui()
    reset_other_ui()


def write_log():
    logged = win.browser.toPlainText()
    if not logged == '':
        with open(logFile, '+w') as log_handle:
            log_handle.write(win.browser.toPlainText())


# MAIN CODE
if __name__ == "__main__":
    try:
        # INITIAL TAB VISIBILITY AND LOCATION
        win.fileOptions.setTabEnabled(0, False)
        win.fileOptions.setTabEnabled(1, False)
        win.fileOptions.setCurrentIndex(0)
        # SIGNALS
        win.append.stateChanged.connect(append_trigger)
        win.truncateData.stateChanged.connect(truncate_trigger)
        win.browse.clicked.connect(directory_browser)
        win.fileSelector.currentTextChanged.connect(selector_changed)
        win.serverList.currentTextChanged.connect(update_creds)
        win.filename.textChanged.connect(file_name_checker)
        win.createTable.stateChanged.connect(create_table_trigger)
        win.defaultChecker.stateChanged.connect(change_trigger)
        win.skipChecker.stateChanged.connect(skip_trigger)
        win.selectChecker.stateChanged.connect(select_trigger)
        win.renameChecker.stateChanged.connect(rename_trigger)
        win.load.clicked.connect(load_file)
        win.run.clicked.connect(initiator)
        win.cancel.clicked.connect(cancel)
        # LOAD MAIN WINDOW
        win.show()
        app.exec()
    except Exception as halt_error:
        win.browser.append('[!] Critical: {0}'.format(halt_error))
    if os.path.exists(shp_json):
        os.remove(shp_json)
    if os.path.exists(output_sql):
        os.remove(output_sql)
    write_log()
