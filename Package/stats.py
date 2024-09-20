#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This file contains the classes related to the statistics of gymnoTOA
(Gymnosperms Taxonomy-oriented Annotation).

This software has been developed by:

    GI en Especies Leñosas (WooSp)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

import gzip
import os
import re
import subprocess
import sys
import webbrowser
import matplotlib.pyplot as plt
import plotnine
import pandas

from PyQt5.QtCore import Qt                      # pylint: disable=no-name-in-module
from PyQt5.QtGui import QCursor                  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QFontMetrics             # pylint: disable=no-name-in-module
from PyQt5.QtGui import QGuiApplication          # pylint: disable=no-name-in-module
from PyQt5.QtGui import QPainter                 # pylint: disable=no-name-in-module
from PyQt5.QtGui import QPdfWriter               # pylint: disable=no-name-in-module
from PyQt5.QtGui import QPixmap                  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QAbstractItemView    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QComboBox            # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGridLayout          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGroupBox            # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QHeaderView          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QLabel               # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QLineEdit            # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QMessageBox          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QPushButton          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidget         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidgetItem     # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QVBoxLayout          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QWidget              # pylint: disable=no-name-in-module

import dialogs
import genlib

#-------------------------------------------------------------------------------

class FormBrowseStats(QWidget):
    '''
    Class used to browse statistics data.
    '''

    #---------------

    def __init__(self, parent, stats_code):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent
        self.stats_code = stats_code

        # assign the text of the "name"
        if self.stats_code == 'species':
            self.name = 'Statistics - Species - Frequency distribution'
        elif self.stats_code == 'go':
            self.name = 'Statistics - Gene Ontology - Frequency distribution per term'
        elif self.stats_code == 'namespace':
            self.name = 'Statistics - Gene Ontology - Frequency distribution per namespace'
        elif self.stats_code == 'seq_per_goterm':
            self.name = 'Statistics - Gene Ontology - Sequences # per GO terms #'

        # call the init method of the parent class
        super().__init__()

        # set the dimensions window
        self.window_height = self.parent.WINDOW_HEIGHT - 100
        self.window_width = self.parent.WINDOW_WIDTH - 50

        # set the head and title
        self.head = f'{self.name} data'
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # build the graphic user interface of the window
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # check the content of inputs
        self.check_inputs()

        # show the window
        self.show()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the width and height of the window
        self.setFixedSize(self.window_width, self.window_height)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # create and configure "label_head"
        label_head = QLabel(self.head, alignment=Qt.AlignCenter)
        label_head.setStyleSheet('font: bold 14px; color: black; background-color: lightGray; max-height: 30px')

        # create and configure "tablewidget"
        self.tablewidget = QTableWidget()
        self.tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.column_name_list = ['Process', 'Result dataset', 'Date', 'Time', 'Status']
        self.tablewidget.setColumnCount(len(self.column_name_list))
        self.tablewidget.setHorizontalHeaderLabels(self.column_name_list)
        self.tablewidget.setColumnWidth(0, 230)
        self.tablewidget.setColumnWidth(1, 280)
        self.tablewidget.setColumnWidth(2, 85)
        self.tablewidget.setColumnWidth(3, 70)
        self.tablewidget.setColumnWidth(4, 90)
        self.tablewidget.verticalHeader().setVisible(True)
        self.tablewidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablewidget.currentCellChanged.connect(self.tablewidget_currentCellChanged)
        self.tablewidget.cellClicked.connect(self.tablewidget_cellClicked)
        self.tablewidget.cellDoubleClicked.connect(self.tablewidget_cellDoubleClicked)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setText(' ')

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.setColumnStretch(0, 1)
        gridlayout_data.addWidget(self.tablewidget, 0, 0, 1, 1)
        gridlayout_data.addWidget(label_empty, 1, 0, 1, 1)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_refresh"
        self.pushbutton_refresh = QPushButton('Refresh')
        self.pushbutton_refresh.setToolTip('Update the process list.')
        self.pushbutton_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_refresh.clicked.connect(self.pushbutton_refresh_clicked)

        # create and configure "pushbutton_execute"
        self.pushbutton_execute = QPushButton('Execute')
        self.pushbutton_execute.setToolTip('Browse the log file corresponding to the process selected.')
        self.pushbutton_execute.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_execute.clicked.connect(self.pushbutton_execute_clicked)

        # create and configure "pushbutton_close"
        pushbutton_close = QPushButton('Close')
        pushbutton_close.setToolTip('Close the window.')
        pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 15)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.setColumnStretch(2, 1)
        gridlayout_buttons.setColumnStretch(3, 1)
        gridlayout_buttons.addWidget(self.pushbutton_refresh, 0, 1, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(self.pushbutton_execute, 0, 2, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(pushbutton_close, 0, 3, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)

        # create and configure "gridlayout_central"
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 1)
        gridlayout_central.setRowStretch(1, 1)
        gridlayout_central.setRowStretch(2, 10)
        gridlayout_central.setRowStretch(3, 1)
        gridlayout_central.setColumnStretch(0, 1)
        gridlayout_central.addWidget(label_head, 0, 0)
        gridlayout_central.addWidget(QLabel(), 1, 0)
        gridlayout_central.addWidget(groupbox_data, 2, 0)
        gridlayout_central.addWidget(groupbox_buttons, 3, 0)

        # create and configure "groupbox_central"
        groupbox_central = QGroupBox()
        groupbox_central.setLayout(gridlayout_central)

        # create and configure "vboxlayout"
        vboxlayout = QVBoxLayout(self)
        vboxlayout.addWidget(groupbox_central)

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load data in "tablewidget"
        self.load_tablewidget()

    #---------------

    def check_inputs(self):
        '''
        Check the content of each input and do the actions linked to its value.
        '''

        # initialize the control variable
        OK = True

        # get the list of rows selected
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('WARNING: One or more input values are wrong or empty.')

        # enable "pushbutton_execute"
        if OK and len(row_list) == 1:
            self.pushbutton_execute.setEnabled(True)
        else:
            self.pushbutton_execute.setEnabled(False)
            OK = False

        # return the control variable
        return OK

    #---------------

    def tablewidget_currentCellChanged(self, _, __):
        '''
        Perform necessary actions after changing the current "tablewidget" cell.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellClicked(self, _, __):
        '''
        Perform necessary actions after clicking on a "tablewidget" cell.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellDoubleClicked(self, _, __):
        '''
        Perform necessary actions after double clicking on "tablewidget" cell.
        '''

        # check the content of inputs
        OK = self.check_inputs()

        # if inputs are OK, simulate a click on "pushbutton_execute"
        if OK:
            self.pushbutton_execute_clicked()

    #---------------

    def pushbutton_refresh_clicked(self):
        '''
        Refresh "tablewidget".
        '''

        # reload data in "tablewidget"
        self.load_tablewidget()

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        Browse the statistics file corresponding to the process selected.
        '''

        # initialize the control variable
        OK = True

        # get the row selected of the table
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check if there is only 1 row selected in the table
        if len(row_list) != 1:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = 'One row has to be selected.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)
            OK = False

        # get and show statistics data
        if OK:

            # set the process type
            process_type = genlib.get_result_run_subdir()

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset
            result_dataset_id = self.tablewidget.item(row_list[0], 1).text()

            # set the name of statistics file
            if self.stats_code == 'species':
                stats_file_name = 'stats-species.csv'
            elif self.stats_code == 'go':
                stats_file_name = 'stats-goterms.csv'
            elif self.stats_code == 'namespace':
                stats_file_name = 'stats-namespaces.csv'
            elif self.stats_code == 'seq_per_goterm':
                stats_file_name = 'stats-seq-per-goterm.csv'

            # get the statistics file path
            stats_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{stats_file_name}'
            if sys.platform.startswith('win32'):
                stats_file_path = genlib.wsl_path_2_windows_path(stats_file_path)

            # get statistics data
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if self.stats_code == 'species':
                (distribution_dict, data_list, data_dict, window_height, window_width) = self.get_frecuency_data(self.stats_code, stats_file_path)
            elif self.stats_code == 'go':
                (distribution_dict, data_list, data_dict, window_height, window_width) = self.get_goterm_data(self.stats_code, stats_file_path)
            elif self.stats_code == 'namespace':
                (distribution_dict, data_list, data_dict, window_height, window_width) = self.get_frecuency_data(self.stats_code, stats_file_path)
            elif self.stats_code == 'seq_per_goterm':
                (distribution_dict, data_list, data_dict, window_height, window_width) = self.get_x_per_y_data(self.stats_code, stats_file_path)
            QApplication.restoreOverrideCursor()

            # show statistics data
            head = f'Browse {stats_file_name}'
            data_table = dialogs.DialogDataTable(self, head, window_height, window_width, data_list, data_dict, distribution_dict, sorted(distribution_dict.keys()))
            data_table.exec()

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.parent.current_subwindow = None
        self.close()
        self.parent.set_background_image()

    #---------------

    def load_tablewidget(self):
        '''
        Load data in "tablewidget".
        '''

        # get the result directory
        result_dir = self.app_config_dict['Environment parameters']['result_dir']

        # set the type, name and code of the annotation pipeline datasets
        process_type = genlib.get_result_run_subdir()
        process_name = genlib.get_process_run_annotation_pipeline_name()
        process_code = genlib.get_process_id(process_name)

        # get the process dictionary
        process_dict = genlib.get_process_dict()

        # get the log directory
        log_dir = f'{result_dir}{os.sep}{process_type}'
        if sys.platform.startswith('win32'):
            log_dir = genlib.wsl_path_2_windows_path(log_dir)

        # set the command to get the result datasets of annotation pipeline in the log directory
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            if process_name == 'all':
                command = f'ls -d {log_dir}/*  | xargs -n 1 basename'
            else:
                command = f'ls -d {log_dir}{os.sep}{process_code}-*  | xargs -n 1 basename'
        elif sys.platform.startswith('win32'):
            log_dir = log_dir.replace('/', '\\')
            if process_name == 'all':
                command = f'dir /a:d /b {log_dir}\\*'
            else:
                command = f'dir /a:d /b {log_dir}\\{process_code}-*'

        # run the command to get the result datasets of annotation pipeline in the log directory
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)

        # initialize the result dataset dictionary
        result_dataset_dict = {}

        # build the result dataset dictionary
        for line in output.stdout.split('\n'):
            if line != '':

                # get data
                result_dataset_id = line.strip()
                try:
                    pattern = r'^(.+)\-(.+)\-(.+)$'
                    mo = re.search(pattern, result_dataset_id)
                    process_code = mo.group(1).strip()
                    process_name = process_dict[process_code]['name']
                    yymmdd = mo.group(2)
                    hhmmss = mo.group(3)
                    date = f'20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:]}'
                    time = f'{hhmmss[:2]}:{hhmmss[2:4]}:{hhmmss[4:]}'
                except:    # pylint: disable=bare-except
                    process_name = 'unknown process'
                    date = '0000-00-00'
                    time = '00:00:00'

                # determine the status
                status_ok = os.path.isfile(genlib.get_status_ok(os.path.join(log_dir, result_dataset_id)))
                status_wrong = os.path.isfile(genlib.get_status_wrong(os.path.join(log_dir, result_dataset_id)))
                if status_ok and not status_wrong:
                    status = 'OK'
                elif not status_ok and status_wrong:
                    status = 'wrong'
                elif not status_ok and not status_wrong:
                    status = 'not finished'
                elif status_ok and status_wrong:
                    status = 'undetermined'

                # insert data in the dictionary when the the status is OK
                if status == 'OK':
                    key = f'{process_name}-{result_dataset_id}'
                    result_dataset_dict[key] = {'process': process_name, 'result_dataset_id': result_dataset_id, 'date': date, 'time': time, 'status': status}

        # initialize "tablewidget"
        self.tablewidget.clearContents()

        # set the rows number of "tablewidget"
        self.tablewidget.setRowCount(len(result_dataset_dict))

        # load data in "tablewidget" for the OK result datasets of annotation pipeline
        if not result_dataset_dict:
            text = 'There are no result logs.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)
        else:
            row = 0
            for key in sorted(result_dataset_dict.keys()):
                self.tablewidget.setItem(row, 0, QTableWidgetItem(result_dataset_dict[key]['process']))
                self.tablewidget.setItem(row, 1, QTableWidgetItem(result_dataset_dict[key]['result_dataset_id']))
                self.tablewidget.setItem(row, 2, QTableWidgetItem(result_dataset_dict[key]['date']))
                self.tablewidget.setItem(row, 3, QTableWidgetItem(result_dataset_dict[key]['time']))
                self.tablewidget.setItem(row, 4, QTableWidgetItem(result_dataset_dict[key]['status']))
                row += 1

    #---------------

    @staticmethod
    def get_frecuency_data(stats_code, stats_file_path):
        '''
        Get frecuency data.
        '''

        # initialize the distribution dictionary
        distribution_dict = {}

        # open the statistics file
        if stats_file_path.endswith('.gz'):
            try:
                stats_file_id = gzip.open(stats_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', stats_file_path)
        else:
            try:
                stats_file_id = open(stats_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', stats_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = stats_file_id.readline()

        # while there are records
        while record != '':

            # add 1 to the record counter
            record_counter += 1

            # process the header record
            if header_record:
                header_record = False

            # process data records
            else:

                # extract data
                # record format: "stats_code_id";"best_hit";"all_hits"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    id = data_list[0]
                    best_hit = data_list[1]
                    all_hits = data_list[2]
                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(stats_file_path), record_counter)

                # add data to the dictionary
                distribution_dict[id] = {'id': id, 'best_hit': best_hit, 'all_hits': all_hits}

            # read the next record
            record = stats_file_id.readline()

        # build the data list
        data_list = ['id', 'best_hit', 'all_hits']

        # build the data dictionary
        data_dict = {}
        data_dict['id'] = {'text': stats_code.capitalize(), 'width': 320, 'alignment': 'left'}
        data_dict['best_hit'] = {'text': 'Best hit per sequence', 'width': 150, 'alignment': 'right'}
        data_dict['all_hits'] = {'text': 'All hits per sequence', 'width': 150, 'alignment': 'right'}

        # set the window height and width
        window_height = 400
        window_width = 750

        # return data
        return distribution_dict, data_list, data_dict, window_height, window_width

    #---------------

    @staticmethod
    def get_goterm_data(stats_code, stats_file_path):
        '''
        Get GO terms data.
        '''

        # initialize the distribution dictionary
        distribution_dict = {}

        # open the statistics file
        if stats_file_path.endswith('.gz'):
            try:
                stats_file_path_id = gzip.open(stats_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', stats_file_path)
        else:
            try:
                stats_file_path_id = open(stats_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', stats_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = stats_file_path_id.readline()

        # while there are records
        while record != '':

            # add 1 to the record counter
            record_counter += 1

            # process the header record
            if header_record:
                header_record = False

            # process data records
            else:

                # extract data
                # record format: "stats_code_id";"best_hit";"all_hits"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    id = data_list[0]
                    desc = data_list[1]
                    namespace = data_list[2]
                    best_hit = data_list[3]
                    all_hits = data_list[4]
                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(stats_file_path), record_counter)

                # add dato to the dictionary
                distribution_dict[id] = {'id': id, 'desc': desc, 'namespace': namespace, 'best_hit': best_hit, 'all_hits': all_hits}

            # read the next record
            record = stats_file_path_id.readline()

        # build the data list
        data_list = ['id', 'desc', 'namespace', 'best_hit', 'all_hits']

        # build the data dictionary
        data_dict = {}
        data_dict['id'] = {'text': 'GO term', 'width': 140, 'alignment': 'left'}
        data_dict['desc'] = {'text': 'Description', 'width': 400, 'alignment': 'left'}
        data_dict['namespace'] = {'text': 'Namespace', 'width': 145, 'alignment': 'left'}
        data_dict['best_hit'] = {'text': 'Best hit per sequence', 'width': 150, 'alignment': 'right'}
        data_dict['all_hits'] = {'text': 'All hits per sequence', 'width': 150, 'alignment': 'right'}

        # set the window height and width
        window_height = 400
        window_width = 1100

        # return data
        return distribution_dict, data_list, data_dict, window_height, window_width

    #---------------

    @staticmethod
    def get_x_per_y_data(stats_code, stats_file_path):
        '''
        Browse x per y data.
        '''

        # initialize the distribution dictionary
        distribution_dict = {}

        # open the statistics file
        if stats_file_path.endswith('.gz'):
            try:
                stats_file_id = gzip.open(stats_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', stats_file_path)
        else:
            try:
                stats_file_id = open(stats_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', stats_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = stats_file_id.readline()

        # while there are records
        while record != '':

            # add 1 to the record counter
            record_counter += 1

            # process the header record
            if header_record:
                header_record = False

            # process data records
            else:

                # extract data
                # record format: "x_count";"y_count"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    x_count = data_list[0]
                    y_count = data_list[1]
                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(stats_file_path), record_counter)

                # add dato to the dictionary
                distribution_dict[record_counter] = {'x_count': x_count, 'y_count': y_count}

            # read the next record
            record = stats_file_id.readline()

        # build the data list
        data_list = ['x_count', 'y_count']

        # build the data dictionary
        data_dict = {}
        if stats_code == 'seq_per_goterm':
            data_dict['x_count'] = {'text': 'GO terms #', 'width': 100, 'alignment': 'right'}
            data_dict['y_count'] = {'text': 'Sequences #', 'width': 100, 'alignment': 'right'}

        # set the window height and width
        window_height = 400
        window_width = 320

        # return data
        return distribution_dict, data_list, data_dict, window_height, window_width

    #---------------

#-------------------------------------------------------------------------------

class FormPlotStats(QWidget):
    '''
    Class used to plot statistics.
    '''

    #---------------

    def __init__(self, parent, stats_code):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent
        self.stats_code = stats_code

        # assign the text of the "name", "default_image_name"
        if self.stats_code == 'species':
            self.name = 'Statistics - Species - Frequency distribution'
            self.default_image_name = 'figure-species'
        elif self.stats_code == 'go':
            self.name = 'Statistics - Gene Ontology - Frequency distribution per GO term'
            self.default_image_name = 'figure-goterms'
        elif self.stats_code == 'namespace':
            self.name = 'Statistics - Gene Ontology - Frequency distribution per namespace'
            self.default_image_name = 'figure-namespaces'
        elif self.stats_code == 'seq_per_goterm':
            self.name = 'Statistics - Gene Ontology - Sequences # per GO terms #'
            self.default_image_name = 'figure-seq-per-goterm'

        # call the init method of the parent class
        super().__init__()

        # set the dimensions window
        self.window_height = self.parent.WINDOW_HEIGHT - 100
        self.window_width = self.parent.WINDOW_WIDTH - 50

        # set the head and title
        self.head = f'{self.name} plot'
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # get the the code list and text list of annotation result types
        self.annotation_result_type_code_list = genlib.get_annotation_result_type_code_list()
        self.annotation_result_type_text_list = genlib.get_annotation_result_type_text_list()

        # build the graphic user interface of the window
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # check the content of inputs
        self.check_inputs()

        # show the window
        self.show()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the width and height of the window
        self.setFixedSize(self.window_width, self.window_height)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # get font metrics information
        fontmetrics = QFontMetrics(QApplication.font())

        # create and configure "label_head"
        label_head = QLabel(self.head, alignment=Qt.AlignCenter)
        label_head.setStyleSheet('font: bold 14px; color: black; background-color: lightGray; max-height: 30px')

        # create and configure "label_annotation_result_type"
        label_annotation_result_type = QLabel()
        label_annotation_result_type.setText('Result type')
        label_annotation_result_type.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "combobox_annotation_result_type"
        self.combobox_annotation_result_type = QComboBox()
        self.combobox_annotation_result_type.currentIndexChanged.connect(self.combobox_annotation_result_type_currentIndexChanged)
        self.combobox_annotation_result_type.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "tablewidget"
        self.tablewidget = QTableWidget()
        self.tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.column_name_list = ['Process', 'Result dataset', 'Date', 'Time', 'Status']
        self.tablewidget.setColumnCount(len(self.column_name_list))
        self.tablewidget.setHorizontalHeaderLabels(self.column_name_list)
        self.tablewidget.setColumnWidth(0, 230)
        self.tablewidget.setColumnWidth(1, 280)
        self.tablewidget.setColumnWidth(2, 85)
        self.tablewidget.setColumnWidth(3, 70)
        self.tablewidget.setColumnWidth(4, 90)
        self.tablewidget.verticalHeader().setVisible(True)
        self.tablewidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablewidget.currentCellChanged.connect(self.tablewidget_currentCellChanged)
        self.tablewidget.cellClicked.connect(self.tablewidget_cellClicked)
        self.tablewidget.cellDoubleClicked.connect(self.tablewidget_cellDoubleClicked)

        # create and configure "label_image_name"
        label_image_name = QLabel()
        label_image_name.setText('Image name (no extension)')
        label_image_name.setFixedWidth(fontmetrics.width('9'*22))

        # create and configure "lineedit_image_name"
        self.lineedit_image_name  = QLineEdit()
        self.lineedit_image_name.setFixedWidth(fontmetrics.width('9'*33))
        self.lineedit_image_name.editingFinished.connect(self.check_inputs)

        # create and configure "label_image_format"
        label_image_format = QLabel()
        label_image_format.setText('Format')
        label_image_format.setFixedWidth(fontmetrics.width('9'*7))

        # create and configure "combobox_image_format"
        self.combobox_image_format = QComboBox()
        self.combobox_image_format.currentIndexChanged.connect(self.check_inputs)
        self.combobox_image_format.setFixedWidth(fontmetrics.width('9'*8))

        # create and configure "label_dpi"
        label_dpi = QLabel()
        label_dpi.setText('DPI')
        label_dpi.setFixedWidth(fontmetrics.width('9'*4))

        # create and configure "lineedit_dpi"
        self.lineedit_dpi  = QLineEdit()
        self.lineedit_dpi.setFixedWidth(fontmetrics.width('9'*4))
        self.lineedit_dpi.editingFinished.connect(self.check_inputs)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setFixedWidth(fontmetrics.width('9'*3))

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.setColumnStretch(0, 1)
        gridlayout_data.setColumnStretch(1, 1)
        gridlayout_data.setColumnStretch(2, 1)
        gridlayout_data.setColumnStretch(3, 1)
        gridlayout_data.setColumnStretch(4, 1)
        gridlayout_data.setColumnStretch(5, 1)
        gridlayout_data.setColumnStretch(6, 1)
        gridlayout_data.setColumnStretch(7, 1)
        gridlayout_data.addWidget(label_annotation_result_type, 0, 0, 1, 1)
        gridlayout_data.addWidget(self.combobox_annotation_result_type, 0, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(self.tablewidget, 1, 0, 1, 8)
        gridlayout_data.addWidget(label_image_name, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_image_name, 2, 1, 1, 1)
        gridlayout_data.addWidget(label_empty, 2, 2, 1, 1)
        gridlayout_data.addWidget(label_image_format, 2, 3, 1, 1)
        gridlayout_data.addWidget(self.combobox_image_format, 2, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 2, 5, 1, 1)
        gridlayout_data.addWidget(label_dpi, 2, 6, 1, 1)
        gridlayout_data.addWidget(self.lineedit_dpi, 2, 7, 1, 1, alignment=Qt.AlignLeft)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_refresh"
        self.pushbutton_refresh = QPushButton('Refresh')
        self.pushbutton_refresh.setToolTip('Update the process list.')
        self.pushbutton_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_refresh.clicked.connect(self.pushbutton_refresh_clicked)

        # create and configure "pushbutton_execute"
        self.pushbutton_execute = QPushButton('Execute')
        self.pushbutton_execute.setToolTip('Browse the log file corresponding to the process selected.')
        self.pushbutton_execute.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_execute.clicked.connect(self.pushbutton_execute_clicked)

        # create and configure "pushbutton_close"
        pushbutton_close = QPushButton('Close')
        pushbutton_close.setToolTip('Close the window.')
        pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 15)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.setColumnStretch(2, 1)
        gridlayout_buttons.setColumnStretch(3, 1)
        gridlayout_buttons.addWidget(self.pushbutton_refresh, 0, 1, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(self.pushbutton_execute, 0, 2, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(pushbutton_close, 0, 3, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)

        # create and configure "gridlayout_central"
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 1)
        gridlayout_central.setRowStretch(1, 10)
        gridlayout_central.setRowStretch(2, 1)
        gridlayout_central.setColumnStretch(0, 1)
        gridlayout_central.addWidget(label_head, 0, 0)
        gridlayout_central.addWidget(groupbox_data, 1, 0)
        gridlayout_central.addWidget(groupbox_buttons, 2, 0)

        # create and configure "groupbox_central"
        groupbox_central = QGroupBox()
        groupbox_central.setLayout(gridlayout_central)

        # create and configure "vboxlayout"
        vboxlayout = QVBoxLayout(self)
        vboxlayout.addWidget(groupbox_central)

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # populate data in "combobox_annotation_results"
        self.combobox_annotation_result_type_populate()

        # load data in "tablewidget"
        self.load_tablewidget()

        # populate data in "combobox_image_format"
        self.combobox_image_format_populate()

        # set initial value in "lineedit_dpi"
        self.lineedit_dpi.setText('600')

        # set initial value in "lineedit_image_name"
        self.lineedit_image_name.setText(self.default_image_name)

    #---------------

    def check_inputs(self):
        '''
        Check the content of each input and do the actions linked to its value.
        '''

        # initialize the control variable
        OK = True

        # get the list of rows selected
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check "lineedit_dpi" when the editing finished
        if not self.lineedit_dpi_editing_finished():
            OK = False

        # check "lineedit_image_name" when the editing finished
        if not self.lineedit_image_name_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('WARNING: One or more input values are wrong or empty.')

        # enable "pushbutton_execute"
        if OK and len(row_list) == 1 and self.combobox_annotation_result_type.currentText() != '' and self.lineedit_dpi.text() != '' and self.lineedit_image_name.text() != '':
            self.pushbutton_execute.setEnabled(True)
        else:
            self.pushbutton_execute.setEnabled(False)

        # return the control variable
        return OK

    #---------------

    def combobox_annotation_result_type_populate(self):
        '''
        Populate data in "combobox_annotation_result_type".
        '''

        # load the annotation result type list in "combobox_annotation_result_type"
        self.combobox_annotation_result_type.addItems(self.annotation_result_type_text_list)

        # select the annotation result type
        self.combobox_annotation_result_type.setCurrentIndex(1)

        # simulate the annotation result type has changed
        self.combobox_annotation_result_type_currentIndexChanged()

    #---------------

    def combobox_annotation_result_type_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_annotation_result_type" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_currentCellChanged(self, _, __):
        '''
        Perform necessary actions after changing the current "tablewidget" cell.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellClicked(self, _, __):
        '''
        Perform necessary actions after clicking on a "tablewidget" cell.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellDoubleClicked(self, _, __):
        '''
        Perform necessary actions after double clicking on "tablewidget" cell.
        '''

        # check the content of inputs
        OK = self.check_inputs()

        # if inputs are OK, simulate a click on "pushbutton_execute"
        if OK:
            self.pushbutton_execute_clicked()

    #---------------

    def combobox_image_format_populate(self):
        '''
        Populate data in "combobox_image_format".
        '''

        # set the image format list
        image_format_list = ['EPS', 'JPEG', 'PDF', 'PNG', 'PS', 'SVG', 'TIFF']

        # load the image format list into "combobox_image_format"
        self.combobox_image_format.addItems(image_format_list)

        # set PNG as image format selected
        self.combobox_image_format.setCurrentIndex(3)

        # simulate the image format has changed
        self.combobox_image_format_currentIndexChanged()

    #---------------

    def combobox_image_format_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_image_format" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def lineedit_dpi_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_dpi"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_dpi" is empty
        if self.lineedit_dpi.text() == '':
            OK = False
            self.lineedit_dpi.setStyleSheet('background-color: white')

        # chek if "lineedit_dpi" is an integer number between 1 and 600
        elif self.lineedit_dpi.text() != '' and not genlib.check_int(self.lineedit_dpi.text(), minimum=1, maximum=600):
            OK = False
            self.lineedit_dpi.setStyleSheet('background-color: red')
            text = 'The value of DPI number has to be an integer number between 1 and 600.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_dpi.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def lineedit_image_name_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_image_name"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_image_name" is empty
        if self.lineedit_image_name.text() == '':
            OK = False
            self.lineedit_image_name.setStyleSheet('background-color: white')

        else:
            self.lineedit_image_name.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def pushbutton_refresh_clicked(self):
        '''
        Refresh "tablewidget".
        '''

        # reload data in "tablewidget"
        self.load_tablewidget()

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        Browse the statistics plot corresponding to the process selected.
        '''

        # initialize the control variable
        OK = True

        # get the row selected of the table
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check if there is only 1 row selected in the table
        if len(row_list) != 1:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = 'One row has to be selected.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)
            OK = False

        # build and show the plot
        if OK:

            # get the annotation result type
            annotation_result_type = self.annotation_result_type_code_list[self.annotation_result_type_text_list.index(self.combobox_annotation_result_type.currentText())]

            # set the process type
            process_type = genlib.get_result_run_subdir()

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset
            result_dataset_id = self.tablewidget.item(row_list[0], 1).text()

            # set the name of statistics file
            if self.stats_code == 'species':
                stats_file_name = 'stats-species.csv'
            elif self.stats_code == 'go':
                stats_file_name = 'stats-goterms.csv'
            elif self.stats_code == 'namespace':
                stats_file_name = 'stats-namespaces.csv'
            elif self.stats_code == 'seq_per_goterm':
                stats_file_name = 'stats-seq-per-goterm.csv'

            # get the statistics file path
            stats_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{stats_file_name}'
            if sys.platform.startswith('win32'):
                stats_file_path = genlib.wsl_path_2_windows_path(stats_file_path)

            # get the image name
            image_file_name = self.lineedit_image_name.text()

            # set the image file path
            image_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{image_file_name}.{self.combobox_image_format.currentText().lower()}'
            if sys.platform.startswith('win32'):
                image_file_path = genlib.wsl_path_2_windows_path(image_file_path)

            # get the DPI
            dpi = int(self.lineedit_dpi.text())

            # build the plot
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if self.stats_code == 'species':
                self.plot_frecuency_data(self.stats_code, annotation_result_type, stats_file_path, image_file_path, dpi, self.name)
            elif self.stats_code == 'go':
                self.plot_frecuency_data(self.stats_code, annotation_result_type, stats_file_path, image_file_path, dpi, self.name)
            elif self.stats_code == 'namespace':
                self.plot_frecuency_data(self.stats_code, annotation_result_type, stats_file_path, image_file_path, dpi, self.name)
            elif self.stats_code == 'seq_per_goterm':
                self.plot_x_per_y_data(self.stats_code, stats_file_path, image_file_path, dpi, self.name)
            QApplication.restoreOverrideCursor()

            # show the plot
            QApplication.setOverrideCursor(Qt.WaitCursor)
            webbrowser.open_new(f'file://{image_file_path}')
            QApplication.restoreOverrideCursor()

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.parent.current_subwindow = None
        self.close()
        self.parent.set_background_image()

    #---------------

    def load_tablewidget(self):
        '''
        Load data in "tablewidget".
        '''

        # get the result directory
        result_dir = self.app_config_dict['Environment parameters']['result_dir']

        # set the type, name and code of the annotation pipeline datasets
        process_type = genlib.get_result_run_subdir()
        process_name = genlib.get_process_run_annotation_pipeline_name()
        process_code = genlib.get_process_id(process_name)

        # get the process dictionary
        process_dict = genlib.get_process_dict()

        # get the log directory
        log_dir = f'{result_dir}{os.sep}{process_type}'
        if sys.platform.startswith('win32'):
            log_dir = genlib.wsl_path_2_windows_path(log_dir)

        # set the command to get the result datasets of annotation pipeline in the log directory
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            if process_name == 'all':
                command = f'ls -d {log_dir}/*  | xargs -n 1 basename'
            else:
                command = f'ls -d {log_dir}{os.sep}{process_code}-*  | xargs -n 1 basename'
        elif sys.platform.startswith('win32'):
            log_dir = log_dir.replace('/', '\\')
            if process_name == 'all':
                command = f'dir /a:d /b {log_dir}\\*'
            else:
                command = f'dir /a:d /b {log_dir}\\{process_code}-*'

        # run the command to get the result datasets of annotation pipeline in the log directory
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)

        # initialize the result dataset dictionary
        result_dataset_dict = {}

        # build the result dataset dictionary
        for line in output.stdout.split('\n'):
            if line != '':

                # get data
                result_dataset_id = line.strip()
                try:
                    pattern = r'^(.+)\-(.+)\-(.+)$'
                    mo = re.search(pattern, result_dataset_id)
                    process_code = mo.group(1).strip()
                    process_name = process_dict[process_code]['name']
                    yymmdd = mo.group(2)
                    hhmmss = mo.group(3)
                    date = f'20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:]}'
                    time = f'{hhmmss[:2]}:{hhmmss[2:4]}:{hhmmss[4:]}'
                except:    # pylint: disable=bare-except
                    process_name = 'unknown process'
                    date = '0000-00-00'
                    time = '00:00:00'

                # determine the status
                status_ok = os.path.isfile(genlib.get_status_ok(os.path.join(log_dir, result_dataset_id)))
                status_wrong = os.path.isfile(genlib.get_status_wrong(os.path.join(log_dir, result_dataset_id)))
                if status_ok and not status_wrong:
                    status = 'OK'
                elif not status_ok and status_wrong:
                    status = 'wrong'
                elif not status_ok and not status_wrong:
                    status = 'not finished'
                elif status_ok and status_wrong:
                    status = 'undetermined'

                # insert data in the dictionary when the the status is OK
                if status == 'OK':
                    key = f'{process_name}-{result_dataset_id}'
                    result_dataset_dict[key] = {'process': process_name, 'result_dataset_id': result_dataset_id, 'date': date, 'time': time, 'status': status}

        # initialize "tablewidget"
        self.tablewidget.clearContents()

        # set the rows number of "tablewidget"
        self.tablewidget.setRowCount(len(result_dataset_dict))

        # load data in "tablewidget" for the OK result datasets of annotation pipeline
        if not result_dataset_dict:
            text = 'There are no result logs.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)
        else:
            row = 0
            for key in sorted(result_dataset_dict.keys()):
                self.tablewidget.setItem(row, 0, QTableWidgetItem(result_dataset_dict[key]['process']))
                self.tablewidget.setItem(row, 1, QTableWidgetItem(result_dataset_dict[key]['result_dataset_id']))
                self.tablewidget.setItem(row, 2, QTableWidgetItem(result_dataset_dict[key]['date']))
                self.tablewidget.setItem(row, 3, QTableWidgetItem(result_dataset_dict[key]['time']))
                self.tablewidget.setItem(row, 4, QTableWidgetItem(result_dataset_dict[key]['status']))
                row += 1

    #---------------

    @staticmethod
    def plot_frecuency_data(stats_code, annotation_result_type, stats_file_path, image_file_path, dpi, name):
        '''
        Plot a bar plot when x is a interger number and y is a literal.
        '''

        # initialize the data dictionary
        data_dict = {}

        # open the statistics file
        if stats_file_path.endswith('.gz'):
            try:
                stats_file_path_id = gzip.open(stats_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', stats_file_path)
        else:
            try:
                stats_file_path_id = open(stats_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', stats_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = stats_file_path_id.readline()

        # while there are records
        while record != '':

            # add 1 to the record counter
            record_counter += 1

            # process the header record
            if header_record:
                header_record = False

            # process data records
            else:

                # extract data
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    # record format: "stats_code_id";"best_hit";"all_hits"
                    if stats_code in ['species', 'namespace']:
                        # format: "id";"best_hit";"all_hits"
                        key = data_list[0]
                        if annotation_result_type == 'best':
                            value = int(data_list[1])
                        elif annotation_result_type == 'complete':
                            value = int(data_list[2])
                        if value > 0:
                            data_dict[key] = value
                    # record format: "go_id";"description";"namespace";"best_hit";"all_hits"
                    elif stats_code == 'go':
                        key = f'{data_list[0]} ({data_list[1]})'
                        if annotation_result_type == 'best':
                            value = int(data_list[3])
                        elif annotation_result_type == 'complete':
                            value = int(data_list[4])
                        if value > 0:
                            data_dict[key] = value
                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(stats_file_path), record_counter)

            # read the next record
            record = stats_file_path_id.readline()

        # initialize the lists associated to the distribution dictionary
        text_list = []
        value_list = []

        # initialize the item counter
        item_counter = 0

        # initialize the value sum of remainder items
        remainder_sum = 0

        # sort the data dictionary by value
        for (key, value) in sorted(data_dict.items(), reverse=True, key=lambda x: x[1]):

            # check if item counter is less than the maximum of items to show
            if item_counter < 10:
                text_list.append(key)
                value_list.append(value)

            # if it not is less
            else:
                remainder_sum += value

            # add 1 to the item counter
            item_counter += 1

        # build distribution dictionary
        text_list = list(reversed(text_list))
        value_list = list(reversed(value_list))
        distribution_dict = {'text_list': text_list, 'value_list': value_list}

        # load data in a Pandas DataFrame
        distribution_df = pandas.DataFrame(distribution_dict)
        distribution_df['text_list'] = pandas.Categorical(distribution_df['text_list'], categories=text_list, ordered=False)

        # build the "plot"
        if stats_code == 'namespace':
            # pie chart
            if annotation_result_type == 'best':
                title = f'{name}\n(best hit per sequence)'
            elif annotation_result_type == 'complete':
                title = f'{name}\n(all hits per sequence)'
            explode = [0.01] * len(value_list)
            (fig1, ax1) = plt.subplots()
            (patches, texts, autotexts) = ax1.pie(value_list, explode=explode, labels=text_list, autopct='%1.1f%%', shadow=False, startangle=270)
            ax1.axis('equal')
            for text in texts:
                text.set_color('grey')
            plt.title(title, color='blue')
            plt.savefig(image_file_path, dpi=dpi)
        else:
            # bar plot
            title = name
            if annotation_result_type == 'best':
                caption = 'Best hit per sequence'
            elif annotation_result_type == 'complete':
                caption = 'All hits per sequence'
            label_y = 'Alignments #'
            plot = (plotnine.ggplot(data=distribution_df) +
                        plotnine.aes(x='text_list', y='value_list') +
                        plotnine.geom_bar(stat='identity', size=0.1, color='green', fill='green') +
                        plotnine.geom_text(plotnine.aes(label='value_list'), va='center') +
                        plotnine.coord_flip() +
                        plotnine.labs(title=title, caption=caption, x='', y=label_y) +
                        plotnine.theme_grey() +
                        plotnine.theme(plot_title=plotnine.element_text(color='blue', margin={'b':15})) +
                        plotnine.theme(axis_title_x=plotnine.element_text(color='black')) +
                        plotnine.theme(axis_title_y=plotnine.element_text(color='black'))
            )
            plot.save(filename=image_file_path, height=6, width=10, dpi=dpi, verbose=False)

    #---------------

    @staticmethod
    def plot_x_per_y_data(stats_code, stats_file_path, image_file_path, dpi, name):
        '''
        Plot x # per y #.
        '''

        # initialize the lists associated to the distribution dictionary
        x_count_list = []
        y_count_list = []

        # open the statistics file
        if stats_file_path.endswith('.gz'):
            try:
                stats_file_path_id = gzip.open(stats_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', stats_file_path)
        else:
            try:
                stats_file_path_id = open(stats_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', stats_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = stats_file_path_id.readline()

        # while there are records
        while record != '':

            # add 1 to the record counter
            record_counter += 1

            # process the header record
            if header_record:
                header_record = False

            # process data records
            else:

                # extract data
                # record format: "x_count";"y_count"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    x_count_list.append(int(data_list[0]))
                    y_count_list.append(int(data_list[1]))
                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(stats_file_path), record_counter)

            # read the next record
            record = stats_file_path_id.readline()

        # build distribution dictionary
        distribution_dict = {'x_count': x_count_list, 'y_count': y_count_list}

        # load data in a Pandas DataFrame
        distribution_df = pandas.DataFrame(distribution_dict)

        # set the title, caption and labels
        title = name
        caption = ''
        if stats_code == 'seq_per_goterm':
            label_x = 'GO terms #'
            label_y = 'Sequences #'

        # build the plot
        plot = (plotnine.ggplot(data=distribution_df) +
                    plotnine.aes(x='x_count', y='y_count') +
                    plotnine.geom_bar(stat='identity', color='red', fill='red') +
                    plotnine.labs(title=title, caption=caption, x=label_x, y=label_y) +
                    plotnine.theme_grey() +
                    plotnine.theme(plot_title=plotnine.element_text(color='blue', margin={'b':15})) +
                    plotnine.theme(axis_title_x=plotnine.element_text(color='black')) +
                    plotnine.theme(axis_title_y=plotnine.element_text(color='black'))
        )
        plot.save(filename=image_file_path, height=4.8, width=6.4, dpi=dpi, verbose=False)

    #---------------

#-------------------------------------------------------------------------------

class FormViewSummaryReport(QWidget):
    '''
    Class used to view a summary report of statistics.
    '''

    #---------------

    def __init__(self, parent):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent

        # assign the text of the "name"
        self.name = 'Statistics - Summary report'

        # call the init method of the parent class
        super().__init__()

        # set the dimensions window
        self.window_height = self.parent.WINDOW_HEIGHT - 100
        self.window_width = self.parent.WINDOW_WIDTH - 50

        # set the head and title
        self.head = f'{self.name}'
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # build the graphic user interface of the window
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # check the content of inputs
        self.check_inputs()

        # show the window
        self.show()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the width and height of the window
        self.setFixedSize(self.window_width, self.window_height)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # create and configure "label_head"
        label_head = QLabel(self.head, alignment=Qt.AlignCenter)
        label_head.setStyleSheet('font: bold 14px; color: black; background-color: lightGray; max-height: 30px')

        # create and configure "tablewidget"
        self.tablewidget = QTableWidget()
        self.tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.column_name_list = ['Process', 'Result dataset', 'Date', 'Time', 'Status']
        self.tablewidget.setColumnCount(len(self.column_name_list))
        self.tablewidget.setHorizontalHeaderLabels(self.column_name_list)
        self.tablewidget.setColumnWidth(0, 230)
        self.tablewidget.setColumnWidth(1, 280)
        self.tablewidget.setColumnWidth(2, 85)
        self.tablewidget.setColumnWidth(3, 70)
        self.tablewidget.setColumnWidth(4, 90)
        self.tablewidget.verticalHeader().setVisible(True)
        self.tablewidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablewidget.currentCellChanged.connect(self.tablewidget_currentCellChanged)
        self.tablewidget.cellClicked.connect(self.tablewidget_cellClicked)
        self.tablewidget.cellDoubleClicked.connect(self.tablewidget_cellDoubleClicked)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setText(' ')

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.setColumnStretch(0, 1)
        gridlayout_data.addWidget(self.tablewidget, 0, 0, 1, 1)
        gridlayout_data.addWidget(label_empty, 1, 0, 1, 1)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_refresh"
        self.pushbutton_refresh = QPushButton('Refresh')
        self.pushbutton_refresh.setToolTip('Update the process list.')
        self.pushbutton_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_refresh.clicked.connect(self.pushbutton_refresh_clicked)

        # create and configure "pushbutton_execute"
        self.pushbutton_execute = QPushButton('Execute')
        self.pushbutton_execute.setToolTip('Browse the log file corresponding to the process selected.')
        self.pushbutton_execute.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_execute.clicked.connect(self.pushbutton_execute_clicked)

        # create and configure "pushbutton_close"
        pushbutton_close = QPushButton('Close')
        pushbutton_close.setToolTip('Close the window.')
        pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 15)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.setColumnStretch(2, 1)
        gridlayout_buttons.setColumnStretch(3, 1)
        gridlayout_buttons.addWidget(self.pushbutton_refresh, 0, 1, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(self.pushbutton_execute, 0, 2, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(pushbutton_close, 0, 3, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)

        # create and configure "gridlayout_central"
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 1)
        gridlayout_central.setRowStretch(1, 1)
        gridlayout_central.setRowStretch(2, 10)
        gridlayout_central.setRowStretch(3, 1)
        gridlayout_central.setColumnStretch(0, 1)
        gridlayout_central.addWidget(label_head, 0, 0)
        gridlayout_central.addWidget(QLabel(), 1, 0)
        gridlayout_central.addWidget(groupbox_data, 2, 0)
        gridlayout_central.addWidget(groupbox_buttons, 3, 0)

        # create and configure "groupbox_central"
        groupbox_central = QGroupBox()
        groupbox_central.setLayout(gridlayout_central)

        # create and configure "vboxlayout"
        vboxlayout = QVBoxLayout(self)
        vboxlayout.addWidget(groupbox_central)

    #---------------

    def initialize_inputs(self):
        '''
        Load initial data in inputs.
        '''

        # load data in "tablewidget"
        self.load_tablewidget()

    #---------------

    def check_inputs(self):
        '''
        Check the content of each input and do the actions linked to its value.
        '''

        # initialize the control variable
        OK = True

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('WARNING: One or more input values are wrong or empty.')

        # return the control variable
        return OK

    #---------------

    def tablewidget_currentCellChanged(self, _, __):
        '''
        Perform necessary actions after changing the current "tablewidget" cell.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellClicked(self, _, __):
        '''
        Perform necessary actions after clicking on a "tablewidget" cell.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellDoubleClicked(self, _, __):
        '''
        Perform necessary actions after double clicking on "tablewidget" cell.
        '''

        # check the content of inputs
        OK = self.check_inputs()

        # if inputs are OK, simulate a click on "pushbutton_execute"
        if OK:
            self.pushbutton_execute_clicked()

    #---------------

    def pushbutton_refresh_clicked(self):
        '''
        Refresh "tablewidget".
        '''

        # reload data in "tablewidget"
        self.load_tablewidget()

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        View a summary report of statistics corresponding to the process selected.
        '''

        # get the row selected of the table
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check if there is only 1 row selected in the table
        if len(row_list) != 1:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = 'One row has to be selected.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)

        # build plots to include in the summary
        else:

            # set the process type
            process_type = genlib.get_result_run_subdir()

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset
            result_dataset_id = self.tablewidget.item(row_list[0], 1).text()

            # set file name, file path, image name and image path corresponding to species frequency distribution
            species_stats_file_name = 'stats-species.csv'
            species_stats_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{species_stats_file_name}'
            if sys.platform.startswith('win32'):
                species_stats_file_path = genlib.wsl_path_2_windows_path(species_stats_file_path)
            species_image_file_name = 'figure-species'
            species_image_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{species_image_file_name}.png'
            if sys.platform.startswith('win32'):
                species_image_file_path = genlib.wsl_path_2_windows_path(species_image_file_path)

            # set file name, file path, image name and image path corresponding to GO terms frequency distribution
            go_stats_file_name = 'stats-goterms.csv'
            go_stats_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{go_stats_file_name}'
            if sys.platform.startswith('win32'):
                go_stats_file_path = genlib.wsl_path_2_windows_path(go_stats_file_path)
            go_image_file_name = 'figure-goterms'
            go_image_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{go_image_file_name}.png'
            if sys.platform.startswith('win32'):
                go_image_file_path = genlib.wsl_path_2_windows_path(go_image_file_path)

            # set file name, file path, image name and image path corresponding to namespaces frequency distribution
            namespace_stats_file_name = 'stats-namespaces.csv'
            namespace_stats_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{namespace_stats_file_name}'
            if sys.platform.startswith('win32'):
                namespace_stats_file_path = genlib.wsl_path_2_windows_path(namespace_stats_file_path)
            namespace_image_file_name = 'figure-namespaces'
            namespace_image_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{namespace_image_file_name}.png'
            if sys.platform.startswith('win32'):
                namespace_image_file_path = genlib.wsl_path_2_windows_path(namespace_image_file_path)

            # set file name, file path, image name and image path corresponding to sequences number per GO terms umber
            seq_per_goterm_stats_file_name = 'stats-seq-per-goterm.csv'
            seq_per_goterm_stats_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{seq_per_goterm_stats_file_name}'
            if sys.platform.startswith('win32'):
                seq_per_goterm_stats_file_path = genlib.wsl_path_2_windows_path(seq_per_goterm_stats_file_path)
            seq_per_goterm_image_file_name = 'figure-seq-per-goterm'
            seq_per_goterm_image_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{seq_per_goterm_image_file_name}.png'
            if sys.platform.startswith('win32'):
                seq_per_goterm_image_file_path = genlib.wsl_path_2_windows_path(seq_per_goterm_image_file_path)

            # get the DPI
            dpi = 600

            # build plots
            QApplication.setOverrideCursor(Qt.WaitCursor)
            FormPlotStats.plot_frecuency_data('species', 'best', species_stats_file_path, species_image_file_path, dpi, self.name)
            FormPlotStats.plot_frecuency_data('go', 'best', go_stats_file_path, go_image_file_path, dpi, self.name)
            FormPlotStats.plot_frecuency_data('namespace', 'best', namespace_stats_file_path, namespace_image_file_path, dpi, self.name)
            FormPlotStats.plot_x_per_y_data('seq_per_goterm', seq_per_goterm_stats_file_path, seq_per_goterm_image_file_path, dpi, self.name)
            QApplication.restoreOverrideCursor()

            # set the plot list
            images_path_list = [species_image_file_path, go_image_file_path, namespace_image_file_path, seq_per_goterm_image_file_path]

            # set the summary report path
            summary_report_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}summary_report.pdf'
            if sys.platform.startswith('win32'):
                summary_report_path = genlib.wsl_path_2_windows_path(summary_report_path)

            # create a QPdfWriter object
            pdf_writer = QPdfWriter(summary_report_path)

            # create a QPainter object
            painter = QPainter()

            # begin to paint in QPainter object
            painter.begin(pdf_writer)

            # set the PDF width
            pdf_width = 9000

            # initialize the y position
            y = 0

            # paint every plot
            for i, image_path in enumerate(images_path_list):

                # load the plot
                pixmap = QPixmap(image_path)

                # set the current x position
                x = int((pdf_width - pixmap.width()) / 2)

                # draw the plot in the PDF
                painter.drawPixmap(x, y, pixmap)

                # update the next y position
                y += pixmap.height() + 100

            # end to paint in QPainter object
            painter.end()

            # show the summary report
            QApplication.setOverrideCursor(Qt.WaitCursor)
            webbrowser.open_new(f'file://{summary_report_path}')
            QApplication.restoreOverrideCursor()

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.parent.current_subwindow = None
        self.close()
        self.parent.set_background_image()

    #---------------

    def load_tablewidget(self):
        '''
        Load data in "tablewidget".
        '''

        # get the result directory
        result_dir = self.app_config_dict['Environment parameters']['result_dir']

        # set the type, name and code of the annotation pipeline datasets
        process_type = genlib.get_result_run_subdir()
        process_name = genlib.get_process_run_annotation_pipeline_name()
        process_code = genlib.get_process_id(process_name)

        # get the process dictionary
        process_dict = genlib.get_process_dict()

        # get the log directory
        log_dir = f'{result_dir}{os.sep}{process_type}'
        if sys.platform.startswith('win32'):
            log_dir = genlib.wsl_path_2_windows_path(log_dir)

        # set the command to get the result datasets of annotation pipeline in the log directory
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            if process_name == 'all':
                command = f'ls -d {log_dir}/*  | xargs -n 1 basename'
            else:
                command = f'ls -d {log_dir}{os.sep}{process_code}-*  | xargs -n 1 basename'
        elif sys.platform.startswith('win32'):
            log_dir = log_dir.replace('/', '\\')
            if process_name == 'all':
                command = f'dir /a:d /b {log_dir}\\*'
            else:
                command = f'dir /a:d /b {log_dir}\\{process_code}-*'

        # run the command to get the result datasets of annotation pipeline in the log directory
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)
        result_dataset_dict = {}
        for line in output.stdout.split('\n'):
            if line != '':

                # get data
                result_dataset_id = line.strip()
                try:
                    pattern = r'^(.+)\-(.+)\-(.+)$'
                    mo = re.search(pattern, result_dataset_id)
                    process_code = mo.group(1).strip()
                    process_name = process_dict[process_code]['name']
                    yymmdd = mo.group(2)
                    hhmmss = mo.group(3)
                    date = f'20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:]}'
                    time = f'{hhmmss[:2]}:{hhmmss[2:4]}:{hhmmss[4:]}'
                except:    # pylint: disable=bare-except
                    process_name = 'unknown process'
                    date = '0000-00-00'
                    time = '00:00:00'

                # determine the status
                status_ok = os.path.isfile(genlib.get_status_ok(os.path.join(log_dir, result_dataset_id)))
                status_wrong = os.path.isfile(genlib.get_status_wrong(os.path.join(log_dir, result_dataset_id)))
                if status_ok and not status_wrong:
                    status = 'OK'
                elif not status_ok and status_wrong:
                    status = 'wrong'
                elif not status_ok and not status_wrong:
                    status = 'not finished'
                elif status_ok and status_wrong:
                    status = 'undetermined'

                # insert data in the dictionary when the the status is OK
                if status == 'OK':
                    key = f'{process_name}-{result_dataset_id}'
                    result_dataset_dict[key] = {'process': process_name, 'result_dataset_id': result_dataset_id, 'date': date, 'time': time, 'status': status}

        # initialize "tablewidget"
        self.tablewidget.clearContents()

        # set the rows number of "tablewidget"
        self.tablewidget.setRowCount(len(result_dataset_dict))

        # load data in "tablewidget" for the OK result datasets of annotation pipeline
        if not result_dataset_dict:
            text = 'There are no result logs.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)
        else:
            row = 0
            for key in sorted(result_dataset_dict.keys()):
                self.tablewidget.setItem(row, 0, QTableWidgetItem(result_dataset_dict[key]['process']))
                self.tablewidget.setItem(row, 1, QTableWidgetItem(result_dataset_dict[key]['result_dataset_id']))
                self.tablewidget.setItem(row, 2, QTableWidgetItem(result_dataset_dict[key]['date']))
                self.tablewidget.setItem(row, 3, QTableWidgetItem(result_dataset_dict[key]['time']))
                self.tablewidget.setItem(row, 4, QTableWidgetItem(result_dataset_dict[key]['status']))
                row += 1

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'This file contains the classes related to statistics used in {genlib.get_app_long_name()}')
    sys.exit(0)

#-------------------------------------------------------------------------------
