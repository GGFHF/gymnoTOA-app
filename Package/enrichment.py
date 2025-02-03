#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This file contains the classes related to the enrichment analysis of gymnoTOA
(Gymnosperms Taxonomy-oriented Annotation).

This software has been developed by:

    GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
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

from PyQt5.QtCore import Qt                      # pylint: disable=no-name-in-module
from PyQt5.QtGui import QCursor                  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QFontMetrics             # pylint: disable=no-name-in-module
from PyQt5.QtGui import QGuiApplication          # pylint: disable=no-name-in-module
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
import sqllib

#-------------------------------------------------------------------------------

class FormRunEnrichmentAnalysis(QWidget):
    '''
    Class used to run an enrichment analysis pipeline.
    '''

    #---------------

    def __init__(self, parent):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent

        # call the init method of the parent class
        super().__init__()

        # set the dimensions window
        self.window_height = self.parent.WINDOW_HEIGHT - 100
        self.window_width = self.parent.WINDOW_WIDTH - 50

        # set the head and title
        self.head = 'Run an enrichment analysis'
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # connect to the SQLite database
        app_db_path = self.app_config_dict[f'{genlib.get_app_short_name()} database']['app_db_path']
        if sys.platform.startswith('win32'):
            app_db_path = genlib.wsl_path_2_windows_path(app_db_path)
        self.conn = sqllib.connect_database(app_db_path)

        # get the the code list and text list of FDR method
        self.fdr_method_code_list = genlib.get_fdr_method_code_list()
        self.fdr_method_text_list = genlib.get_fdr_method_text_list()

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

        # create and configure "label_fasta_file"
        label_fasta_file = QLabel()
        label_fasta_file.setText('FASTA file')
        label_fasta_file.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_fasta_file"
        self.lineedit_fasta_file = QLineEdit()
        self.lineedit_fasta_file.editingFinished.connect(self.check_inputs)
        self.lineedit_fasta_file.setDisabled(True)

        # create and configure "label_species_mame"
        label_species_name = QLabel()
        label_species_name.setText('Species')
        label_species_name.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "combobox_species_name"
        self.combobox_species_name = QComboBox()
        self.combobox_species_name.currentIndexChanged.connect(self.combobox_species_name_currentIndexChanged)
        self.combobox_species_name.setFixedWidth(fontmetrics.width('9'*25))

        # create and configure "label_fdr_method"
        label_fdr_method = QLabel()
        label_fdr_method.setText('FDR method')
        label_fdr_method.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "combobox_fdr_method"
        self.combobox_fdr_method = QComboBox()
        self.combobox_fdr_method.currentIndexChanged.connect(self.combobox_fdr_method_currentIndexChanged)
        self.combobox_fdr_method.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "label_min_seqnum_annotations"
        label_min_seqnum_annotations = QLabel()
        label_min_seqnum_annotations.setText('Min seq# in annotations')
        label_min_seqnum_annotations.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "lineedit_min_seqnum_annotations"
        self.lineedit_min_seqnum_annotations = QLineEdit()
        self.lineedit_min_seqnum_annotations.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_min_seqnum_annotations.editingFinished.connect(self.check_inputs)

        # create and configure "label_min_seqnum_species"
        label_min_seqnum_species = QLabel()
        label_min_seqnum_species.setText('Min seq# in species')
        label_min_seqnum_species.setFixedWidth(fontmetrics.width('9'*17))

        # create and configure "lineedit_min_seqnum_species"
        self.lineedit_min_seqnum_species  = QLineEdit()
        self.lineedit_min_seqnum_species.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_min_seqnum_species.editingFinished.connect(self.check_inputs)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setFixedWidth(fontmetrics.width('9'*3))

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.addWidget(self.tablewidget, 0, 0, 1, 5)
        gridlayout_data.addWidget(label_fasta_file, 1, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fasta_file, 1, 1, 1, 4)
        gridlayout_data.addWidget(label_species_name, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.combobox_species_name, 2, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 2, 2, 1, 1)
        gridlayout_data.addWidget(label_fdr_method, 2, 3, 1, 1)
        gridlayout_data.addWidget(self.combobox_fdr_method, 2, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_min_seqnum_annotations, 3, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_min_seqnum_annotations, 3, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 3, 2, 1, 1)
        gridlayout_data.addWidget(label_min_seqnum_species, 3, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_min_seqnum_species, 3, 4, 1, 1, alignment=Qt.AlignLeft)

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

        # populate data in "combobox_species_name"
        self.combobox_species_name_populate()

        # populate data in "combobox_fdr_method"
        self.combobox_fdr_method_populate()

        # set initial value in "lineedit_min_seqnum_annotations"
        self.lineedit_min_seqnum_annotations.setText(str(genlib.Const.DEFAULT_MIN_SEQNUM_ANNOTATIONS))

        # set initial value in "lineedit_min_seqnum_species"
        self.lineedit_min_seqnum_species.setText(str(genlib.Const.DEFAULT_MIN_SEQNUM_SPECIES))

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

        # check "lineedit_fasta_file" when the editing finished
        if not self.lineedit_fasta_file_editing_finished():
            OK = False

        # check "lineedit_min_seqnum_annotations" when the editing finished
        if not self.lineedit_min_seqnum_annotations_editing_finished():
            OK = False

        # check "lineedit_min_seqnum_species" when the editing finished
        if not self.lineedit_min_seqnum_species_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('There are one or more inputs without data or with wrong value.')

        # enable "pushbutton_execute"
        if OK and len(row_list) == 1 and self.lineedit_fasta_file.text() != '' and self.combobox_species_name.currentText() != '' and self.combobox_fdr_method.currentText() != '' and self.lineedit_min_seqnum_annotations.text() != '' and self.lineedit_min_seqnum_species.text() != '':
            self.pushbutton_execute.setEnabled(True)
        else:
            self.pushbutton_execute.setEnabled(False)
            OK = False

        # return the control variable
        return OK

    #---------------

    def tablewidget_currentCellChanged(self, row, _):
        '''
        Perform necessary actions after changing the current "tablewidget" cell.
        '''

        # check if there is a row selected
        if row >= 0:

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset corresponding to the row clicked
            result_dataset_id = self.tablewidget.item(row, 1).text()

            # get the parameters file corresponding to the result dataset
            params_file = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset_id}{os.sep}{genlib.get_params_file_name()}'
            if sys.platform.startswith('win32'):
                params_file = genlib.wsl_path_2_windows_path(params_file)

            # get the dictionary of parameters
            params_dict = genlib.get_config_dict(params_file)

            # set the FASTA file path in "lineedit_fasta_file"
            fasta_file = params_dict['Annotation parameters']['fasta_file']
            if sys.platform.startswith('win32'):
                fasta_file = genlib.wsl_path_2_windows_path(fasta_file)
            self.lineedit_fasta_file.setText(fasta_file)

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

    def lineedit_fasta_file_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_fasta_file"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def combobox_species_name_populate(self):
        '''
        Populate data in "combobox_speciesgenlib.get_all_species_code()".
        '''

        # get the species names list
        species_name_list = [genlib.get_all_species_name()] + sqllib.get_mmseqs2_species_list(self.conn)

        # load the species names list into "combobox_speciesgenlib.get_all_species_code()"
        self.combobox_species_name.addItems(species_name_list)

        # simulate the species has changed
        self.combobox_species_name_currentIndexChanged()

    #---------------

    def combobox_species_name_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_species_name" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def combobox_fdr_method_populate(self):
        '''
        Populate data in "combobox_fdr_method".
        '''

        # load the method text list in "combobox_fdr_method"
        self.combobox_fdr_method.addItems(self.fdr_method_text_list)

        # select the method Benjamini-Yekutieli
        self.combobox_fdr_method.setCurrentIndex(1)

        # simulate the method has changed
        self.combobox_fdr_method_currentIndexChanged()

    #---------------

    def combobox_fdr_method_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_fdr_method" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def lineedit_min_seqnum_annotations_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_min_seqnum_annotations"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_min_seqnum_annotations" is empty
        if self.lineedit_min_seqnum_annotations.text() == '':
            OK = False
            self.lineedit_min_seqnum_annotations.setStyleSheet('background-color: white')

        # chek if "lineedit_min_seqnum_annotations" is an integer number greater than 1
        elif self.lineedit_min_seqnum_annotations.text() != '' and not genlib.check_int(self.lineedit_min_seqnum_annotations.text(), minimum=1):
            OK = False
            self.lineedit_min_seqnum_annotations.setStyleSheet('background-color: red')
            text = 'The value of min seq# in annotations has to be an integer number greater than 1.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_min_seqnum_annotations.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def lineedit_min_seqnum_species_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_min_seqnum_species"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_min_seqnum_species" is empty
        if self.lineedit_min_seqnum_species.text() == '':
            OK = False
            self.lineedit_min_seqnum_species.setStyleSheet('background-color: white')

        # chek if "lineedit_min_seqnum_species" is an integer number greater than 1
        elif self.lineedit_min_seqnum_species.text() != '' and not genlib.check_int(self.lineedit_min_seqnum_species.text(), minimum=1):
            OK = False
            self.lineedit_min_seqnum_species.setStyleSheet('background-color: red')
            text = 'The value of min seq# in species has to be an integer number greater than 1.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_min_seqnum_species.setStyleSheet('background-color: white')

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
        Execute the process.
        '''

        # initialize the control variable
        OK = True

        # get the list of rows selected
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check if there is only a row selected
        if len(row_list) != 1:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = 'One row has to be selected.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)
            OK = False

        # confirm the process is executed
        if OK:
            text = 'The enrichment analysis is going to be run.\n\nAre you sure to continue?'
            botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
            if botton == QMessageBox.No:
                OK = False

        # execute the process
        if OK:

            # get the identification of the functional annotation dataset
            functional_annotation_dataset = self.tablewidget.item(row_list[0], 1).text()

            # get species
            species = self.combobox_species_name.currentText()
            if species == genlib.get_all_species_name():
                species = genlib.get_all_species_code()

            # get the FDR method
            fdr_method = self.fdr_method_code_list[self.fdr_method_text_list.index(self.combobox_fdr_method.currentText())]

            # get the min seq# in annotations
            min_seqnum_annotations = self.lineedit_min_seqnum_annotations.text()

            # get the min seq# in species
            min_seqnum_species = self.lineedit_min_seqnum_species.text()

            # create and execute "DialogProcess"
            process = dialogs.DialogProcess(self, self.head, self.run_enrichment_analysis, functional_annotation_dataset, species, fdr_method, min_seqnum_annotations, min_seqnum_species)
            process.exec()

        # close the windows
        # -- if OK:
        # --     self.pushbutton_close_clicked()

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

        # initialize "lineedit_fasta_file"
        self.lineedit_fasta_file.setText('')

        # set the type, name and code of the annotation pipeline datasets
        process_type = genlib.get_result_run_subdir()
        process_name = genlib.get_process_run_annotation_pipeline_name()
        process_code = genlib.get_process_id(process_name)

        # get the process dictionary
        process_dict = genlib.get_process_dict()

        # get the log directory
        log_dir = f'{result_dir}/{process_type}'
        if sys.platform.startswith('win32'):
            log_dir = genlib.wsl_path_2_windows_path(log_dir)

        # set the command to get the result datasets of annotation pipeline in the log directory
        command = ''
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            if process_name == 'all':
                command = f'ls -d {log_dir}/*  | xargs -n 1 basename'
            else:
                command = f'ls -d {log_dir}/{process_code}-*  | xargs -n 1 basename'
        elif sys.platform.startswith('win32'):
            log_dir = log_dir.replace('/', '\\')
            if process_name == 'all':
                command = f'dir /a:d /b {log_dir}\\*'
            else:
                command = f'dir /a:d /b {log_dir}\\{process_code}-*'

        # run the command to get the result datasets of enrichment analysis in the log directory
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
                status = ''
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
            text = 'There is no run ended OK.'
            QMessageBox.warning(self, self.title, text, buttons=QMessageBox.Ok)
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

    def run_enrichment_analysis(self, process, functional_annotation_dataset, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species):
        '''
        Run an enrichment analysis.
        '''

        # initialize the control variable
        OK = True

        # warn that the log window does not have to be closed
        process.write('Do not close this window, please wait!\n')

        # warn that the requirements are being verified
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write('Checking process requirements ...\n')

        # check the gymnoTOA config file
        if OK:
            if not os.path.isfile(genlib.get_app_config_file()):
                process.write(f'*** ERROR: The {genlib.get_app_short_name()} config file does not exist. Please, recreate it.\n')
                OK = False

        # warn that the requirements are OK
        if OK:
            process.write('Process requirements are OK.\n')

        # determine the temporal directory
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write('Determining the temporal directory ...\n')
            temp_dir = genlib.get_temp_dir()
            command = f'mkdir -p {temp_dir}'
            rc = genlib.run_command(command, process, is_script=False)
            if rc == 0:
                process.write(f'The directory path is {temp_dir}.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')
                OK = False

        # determine the run directory
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write('Determining the run directory ...\n')
            result_dir = self.app_config_dict['Environment parameters']['result_dir']
            current_run_dir = genlib.get_current_run_dir(result_dir, genlib.get_result_run_subdir(), genlib.get_process_run_enrichment_analysis_code())
            command = f'mkdir -p {current_run_dir}'
            rc = genlib.run_command(command, process, is_script=False)
            if rc == 0:
                process.write(f'The directory path is {current_run_dir}.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')
                OK = False

        # build the script
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            script_name = f'{genlib.get_process_run_enrichment_analysis_code()}-process.sh'
            process.write(f'Building the process script {script_name} ...\n')
            (OK, _) = self.build_run_enrichment_analysis_script(temp_dir, script_name, current_run_dir, functional_annotation_dataset, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species)
            if OK:
                process.write('The file is built.\n')
            else:
                process.write('*** ERROR: The file could not be built.\n')

        # copy the script to the current run directory
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write(f'Copying the script {script_name} to the directory {current_run_dir} ...\n')
            command = f'cp {temp_dir}/{script_name} {current_run_dir}; [ $? -eq 0 ] &&  exit 0 || exit 1'
            rc = genlib.run_command(command, process, is_script=False)
            if rc == 0:
                process.write('The file is copied.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')

        # set run permision to the script
        if OK and not sys.platform.startswith('win32'):
            process.write(f'{genlib.get_separator()}\n')
            process.write(f'Setting on the run permision of {script_name} ...\n')
            command = f'chmod u+x {current_run_dir}/{script_name}'
            rc = genlib.run_command(command, process, is_script=False)
            if rc == 0:
                process.write('The run permision is set.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')
                OK = False

        # build the starter script in the temporal directory
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            starter_name = f'{genlib.get_process_run_enrichment_analysis_code()}-process-starter.sh'
            process.write(f'Building the starter script {starter_name} ...\n')
            (OK, _) = genlib.build_starter(temp_dir, starter_name, script_name, current_run_dir)
            if OK:
                process.write('The file is built.\n')
            if not OK:
                process.write('***ERROR: The file could not be built.\n')

        # copy the starter script to the current run directory
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write(f'Copying the starter {starter_name} to the directory {current_run_dir} ...\n')
            command = f'cp {temp_dir}/{starter_name} {current_run_dir}; [ $? -eq 0 ] &&  exit 0 || exit 1'
            rc = genlib.run_command(command, process, is_script=False)
            if rc == 0:
                process.write('The file is copied.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')

        # set run permision to the starter script
        if OK and not sys.platform.startswith('win32'):
            process.write(f'{genlib.get_separator()}\n')
            process.write(f'Setting on the run permision of {starter_name} ...\n')
            command = f'chmod u+x {current_run_dir}/{starter_name}'
            rc = genlib.run_command(command, process, is_script=False)
            if rc == 0:
                process.write('The run permision is set.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')
                OK = False

        # submit the starter
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write(f'Submitting the starter {starter_name} ...\n')
            command = f'{current_run_dir}/{starter_name} &'
            rc = genlib.run_command(command, process, is_script=True)
            if rc == 0:
                process.write('The script is submitted.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')
                OK = False

        # warn that the log window can be closed
        process.write(f'{genlib.get_separator()}\n')
        process.write('You can close this window now.\n')

        # return the control variable
        return OK

    #---------------

    def build_run_enrichment_analysis_script(self, directory, script_name, current_run_dir, functional_annotation_dataset, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species):
        '''
        Build the script to run an enrichment analysis.
        '''

        # initialize the control variable and error list
        OK = True
        error_list = []

        # get the Miniforge3 directory and its bin subdirectory
        miniforge3_dir = ''
        if sys.platform.startswith('win32'):
            miniforge3_dir = genlib.get_miniforge3_dir_in_wsl()
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            miniforge3_dir = genlib.get_miniforge3_current_dir()
        miniforge3_bin_dir = f'{miniforge3_dir}/bin'

        # get items from dictionary of application configuration
        app_dir = self.app_config_dict['Environment parameters']['app_dir']
        app_db_path = self.app_config_dict[f'{genlib.get_app_short_name()} database']['app_db_path']
        result_dir = self.app_config_dict['Environment parameters']['result_dir']

        # set the parameters file of the functional annotation
        functional_annotation_params_file = f'{result_dir}/{genlib.get_result_run_subdir()}/{functional_annotation_dataset}/{genlib.get_params_file_name()}'

        # set the parameters file of the enrichment analysis
        enrichment_analysis_params_file = f'./{genlib.get_params_file_name()}'

        # set the CSV files with the functional annotations
        besthit_functional_annotation_file = f'{result_dir}/{genlib.get_result_run_subdir()}/{functional_annotation_dataset}/{genlib.get_besthit_functional_annotation_file_name()}'
        complete_functional_annotation_file = f'{result_dir}/{genlib.get_result_run_subdir()}/{functional_annotation_dataset}/{genlib.get_complete_functional_annotation_file_name()}'

        # set the CSV files with the GO enrichment_analysis
        besthit_goea_file = f'./{genlib.get_besthit_goea_file_name()}'
        complete_goea_file = f'./{genlib.get_complete_goea_file_name()}'

        # set the CSV files with the Metacyc pathway enrichment_analysis
        besthit_mpea_file = f'./{genlib.get_besthit_mpea_file_name()}'
        complete_mpea_file = f'./{genlib.get_complete_mpea_file_name()}'

        # set the CSV files with the KO enrichment_analysis
        besthit_koea_file = f'./{genlib.get_besthit_koea_file_name()}'
        complete_koea_file = f'./{genlib.get_complete_koea_file_name()}'

        # set the CSV files with the KEGG pathway enrichment_analysis
        besthit_kpea_file = f'./{genlib.get_besthit_kpea_file_name()}'
        complete_kpea_file = f'./{genlib.get_complete_kpea_file_name()}'

        # set the script path
        script_path = f'{directory}/{script_name}'

        # write the script
        try:
            with open(script_path, mode='w', encoding='iso-8859-1', newline='\n') as file_id:
                file_id.write( '#!/bin/bash\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write(f'export PATH={miniforge3_bin_dir}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin\n')
                file_id.write( 'SEP="#########################################"\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write(f'STATUS_DIR={genlib.get_status_dir(current_run_dir)}\n')
                file_id.write(f'SCRIPT_STATUS_OK={genlib.get_status_ok(current_run_dir)}\n')
                file_id.write(f'SCRIPT_STATUS_WRONG={genlib.get_status_wrong(current_run_dir)}\n')
                file_id.write( 'mkdir -p $STATUS_DIR\n')
                file_id.write( 'if [ -f $SCRIPT_STATUS_OK ]; then rm $SCRIPT_STATUS_OK; fi\n')
                file_id.write( 'if [ -f $SCRIPT_STATUS_WRONG ]; then rm $SCRIPT_STATUS_WRONG; fi\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function init\n')
                file_id.write( '{\n')
                file_id.write( '    INIT_DATETIME=`date +%s`\n')
                file_id.write( '    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Script started at $FORMATTED_INIT_DATETIME."\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function copy_annotation_params\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Copying functional annotation parameters ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/copy-annotation-params.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        cp {functional_annotation_params_file} {enrichment_analysis_params_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error cp $RC; fi\n')
                file_id.write( '        echo "Parameters are copied."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function append_enrichment_params\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Appending enrichment analysis parameters ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/append-enrichment-params.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        echo >> {enrichment_analysis_params_file}\n')
                file_id.write(f'        echo "[Enrichment parameters]" >> {enrichment_analysis_params_file}\n')
                file_id.write(f'        echo "species_name = {species_name}" >> {enrichment_analysis_params_file}\n')
                file_id.write(f'        echo "fdr_method = {fdr_method}" >> {enrichment_analysis_params_file}\n')
                file_id.write(f'        echo "min_seqnum_annotations = {min_seqnum_annotations}" >> {enrichment_analysis_params_file}\n')
                file_id.write(f'        echo "min_seqnum_species = {min_seqnum_species}" >> {enrichment_analysis_params_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error echo $RC; fi\n')
                file_id.write( '        echo "Parameters are appended."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function calculate_besthit_enrichment_analysis\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Calculation the enrichment analysis (best hit per sequence) ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/calculate_besthit_enrichment_analysis.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_gymnotoa_environment()}\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write(f'            {app_dir}/calculate-enrichment-analysis.py \\\n')
                file_id.write(f'                --db={app_db_path} \\\n')
                file_id.write(f'                --annotations={besthit_functional_annotation_file} \\\n')
                file_id.write(f'                --species="{species_name}" \\\n')
                file_id.write(f'                --method={fdr_method} \\\n')
                file_id.write(f'                --msqannot={min_seqnum_annotations} \\\n')
                file_id.write(f'                --msqspec={min_seqnum_species} \\\n')
                file_id.write(f'                --goea={besthit_goea_file} \\\n')
                file_id.write(f'                --mpea={besthit_mpea_file} \\\n')
                file_id.write(f'                --koea={besthit_koea_file} \\\n')
                file_id.write(f'                --kpea={besthit_kpea_file} \\\n')
                file_id.write( '                --verbose=N \\\n')
                file_id.write( '                --trace=N\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error load-blast-data.py $RC; fi\n')
                file_id.write( '        conda deactivate\n')
                file_id.write( '        echo "Analysis is calculated."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function calculate_complete_enrichment_analysis\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write('     echo "Calculation the enrichment analysis (all hits per sequence) ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/calculate_complete_enrichment_analysis.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_gymnotoa_environment()}\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write(f'            {app_dir}/calculate-enrichment-analysis.py \\\n')
                file_id.write(f'                --db={app_db_path} \\\n')
                file_id.write(f'                --annotations={complete_functional_annotation_file} \\\n')
                file_id.write(f'                --species="{species_name}" \\\n')
                file_id.write(f'                --method={fdr_method} \\\n')
                file_id.write(f'                --msqannot={min_seqnum_annotations} \\\n')
                file_id.write(f'                --msqspec={min_seqnum_species} \\\n')
                file_id.write(f'                --goea={complete_goea_file} \\\n')
                file_id.write(f'                --mpea={complete_mpea_file} \\\n')
                file_id.write(f'                --koea={complete_koea_file} \\\n')
                file_id.write(f'                --kpea={complete_kpea_file} \\\n')
                file_id.write( '                --verbose=N \\\n')
                file_id.write( '                --trace=N\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error load-blast-data.py $RC; fi\n')
                file_id.write( '        conda deactivate\n')
                file_id.write( '        echo "Analysis is calculated."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function end\n')
                file_id.write( '{\n')
                file_id.write( '    END_DATETIME=`date +%s`\n')
                file_id.write( '    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`\n')
                file_id.write( '    calculate_duration\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Script ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    touch $SCRIPT_STATUS_OK\n')
                file_id.write( '    exit 0\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function manage_error\n')
                file_id.write( '{\n')
                file_id.write( '    END_DATETIME=`date +%s`\n')
                file_id.write( '    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`\n')
                file_id.write( '    calculate_duration\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "ERROR: $1 returned error $2"\n')
                file_id.write( '    echo "Script ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    touch $SCRIPT_STATUS_WRONG\n')
                file_id.write( '    exit 3\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function calculate_duration\n')
                file_id.write( '{\n')
                file_id.write( '    DURATION=`expr $END_DATETIME - $INIT_DATETIME`\n')
                file_id.write( '    HH=`expr $DURATION / 3600`\n')
                file_id.write( '    MM=`expr $DURATION % 3600 / 60`\n')
                file_id.write( '    SS=`expr $DURATION % 60`\n')
                file_id.write( '    FORMATTED_DURATION=`printf "%03d:%02d:%02d\\n" $HH $MM $SS`\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'init\n')
                file_id.write( 'copy_annotation_params\n')
                file_id.write( 'append_enrichment_params\n')
                file_id.write( 'calculate_besthit_enrichment_analysis\n')
                file_id.write( 'calculate_complete_enrichment_analysis\n')
                file_id.write( 'end\n')
        except Exception as e:
            error_list.append(f'*** EXCEPTION: "{e}".')
            error_list.append(f'*** ERROR: The file {script_path} is not created.')
            OK = False

        # return the control variable and error list
        return (OK, error_list)

    #---------------

#-------------------------------------------------------------------------------

class FormRestartEnrichmentAnalysis(QWidget):
    '''
    Class used to restart an enrichment analysis pipeline.
    '''

    #---------------

    def __init__(self, parent):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent

        # call the init method of the parent class
        super().__init__()

        # set the dimensions window
        self.window_height = self.parent.WINDOW_HEIGHT - 100
        self.window_width = self.parent.WINDOW_WIDTH - 50

        # set the head and title
        self.head = 'Restart an enrichment analysis'
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # get the the code list and text list of FDR method
        self.fdr_method_code_list = genlib.get_fdr_method_code_list()
        self.fdr_method_text_list = genlib.get_fdr_method_text_list()

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

        # create and configure "label_fasta_file"
        label_fasta_file = QLabel()
        label_fasta_file.setText('FASTA file')
        label_fasta_file.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_fasta_file"
        self.lineedit_fasta_file = QLineEdit()
        self.lineedit_fasta_file.editingFinished.connect(self.check_inputs)
        self.lineedit_fasta_file.setDisabled(True)

        # create and configure "label_species_name"
        label_species_name = QLabel()
        label_species_name.setText('Species')
        label_species_name.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_species_name"
        self.lineedit_species_name = QLineEdit()
        self.lineedit_species_name.editingFinished.connect(self.check_inputs)
        self.lineedit_species_name.setFixedWidth(fontmetrics.width('9'*20))
        self.lineedit_species_name.setDisabled(True)

        # create and configure "fdr_method"
        label_fdr_method = QLabel()
        label_fdr_method.setText('FDR method')
        label_fdr_method.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_fdr_method"
        self.lineedit_fdr_method = QLineEdit()
        self.lineedit_fdr_method.editingFinished.connect(self.check_inputs)
        self.lineedit_fdr_method.setFixedWidth(fontmetrics.width('9'*20))
        self.lineedit_fdr_method.setDisabled(True)

        # create and configure "label_min_seqnum_annotations"
        label_min_seqnum_annotations = QLabel()
        label_min_seqnum_annotations.setText('Min seq# in annotations')
        label_min_seqnum_annotations.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "lineedit_min_seqnum_annotations"
        self.lineedit_min_seqnum_annotations = QLineEdit()
        self.lineedit_min_seqnum_annotations.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_min_seqnum_annotations.setDisabled(True)

        # create and configure "label_min_seqnum_species"
        label_min_seqnum_species = QLabel()
        label_min_seqnum_species.setText('Min seq# in species')
        label_min_seqnum_species.setFixedWidth(fontmetrics.width('9'*17))

        # create and configure "lineedit_min_seqnum_species"
        self.lineedit_min_seqnum_species  = QLineEdit()
        self.lineedit_min_seqnum_species.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_min_seqnum_species.setDisabled(True)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setFixedWidth(fontmetrics.width('9'*3))

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.addWidget(self.tablewidget, 0, 0, 1, 16)
        gridlayout_data.addWidget(label_fasta_file, 1, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fasta_file, 1, 1, 1, 15)
        gridlayout_data.addWidget(label_species_name, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_species_name, 2, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 2, 2, 1, 1)
        gridlayout_data.addWidget(label_fdr_method, 2, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fdr_method, 2, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_min_seqnum_annotations, 3, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_min_seqnum_annotations, 3, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 3, 2, 1, 1)
        gridlayout_data.addWidget(label_min_seqnum_species, 3, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_min_seqnum_species, 3, 4, 1, 1, alignment=Qt.AlignLeft)

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

        # set initial value in "lineedit_fasta_file"
        self.lineedit_fasta_file.setText('')

        # initialize "lineedit_species_name"
        self.lineedit_species_name.setText('')

        # initialize "lineedit_min_seqnum_annotations"
        self.lineedit_min_seqnum_annotations.setText('')

        # initialize "lineedit_min_seqnum_species"
        self.lineedit_min_seqnum_species.setText('')

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

        # check "lineedit_fasta_file" when the editing finished
        if not self.lineedit_fasta_file_editing_finished():
            OK = False

        # check "lineedit_species_name" when the editing finished
        if not self.lineedit_species_name_editing_finished():
            OK = False

        # check "lineedit_fdr_method" when the editing finished
        if not self.lineedit_fdr_method_editing_finished():
            OK = False

        # check "lineedit_min_seqnum_annotations" when the editing finished
        if not self.lineedit_min_seqnum_annotations_editing_finished():
            OK = False

        # check "lineedit_min_seqnum_species" when the editing finished
        if not self.lineedit_min_seqnum_species_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('There are one or more inputs without data or with wrong value.')

        # enable "pushbutton_execute"
        if OK and len(row_list) == 1 and self.lineedit_fasta_file.text() != '' and self.lineedit_species_name.text() != '' and self.lineedit_fdr_method.text() != '' and self.lineedit_min_seqnum_annotations.text() != '' and self.lineedit_min_seqnum_species.text() != '':
            self.pushbutton_execute.setEnabled(True)
        else:
            self.pushbutton_execute.setEnabled(False)
            OK = False

        # return the control variable
        return OK

    #---------------

    def tablewidget_currentCellChanged(self, row, _):
        '''
        Perform necessary actions after changing the current "tablewidget" cell.
        '''

        # check if there is a row selected
        if row >= 0:

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset corresponding to the row clicked
            result_dataset_id = self.tablewidget.item(row, 1).text()

            # get the parameters file corresponding to the result dataset
            params_file = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset_id}{os.sep}{genlib.get_params_file_name()}'
            if sys.platform.startswith('win32'):
                params_file = genlib.wsl_path_2_windows_path(params_file)

            # get the dictionary of parameters
            params_dict = genlib.get_config_dict(params_file)

            # set the FASTA file path in "lineedit_fasta_file"
            fasta_file = params_dict['Annotation parameters']['fasta_file']
            if sys.platform.startswith('win32'):
                fasta_file = genlib.wsl_path_2_windows_path(fasta_file)
            self.lineedit_fasta_file.setText(fasta_file)

            # set the species in "lineedit_species_name"
            species_name = params_dict['Enrichment parameters']['species_name']
            if species_name == genlib.get_all_species_code():
                species_name = genlib.get_all_species_name()
            self.lineedit_species_name.setText(species_name)

            # set the FDR method in "lineedit_fdr_method"
            fdr_method_code = params_dict['Enrichment parameters']['fdr_method']
            fdr_method_text = self.fdr_method_text_list[self.fdr_method_code_list.index(fdr_method_code)]
            self.lineedit_fdr_method.setText(fdr_method_text)

            # set the min seq# in annotations
            min_seqnum_annotations = params_dict['Enrichment parameters']['min_seqnum_annotations']
            self.lineedit_min_seqnum_annotations.setText(min_seqnum_annotations)

            # set the min seq# in species
            min_seqnum_species = params_dict['Enrichment parameters']['min_seqnum_species']
            self.lineedit_min_seqnum_species.setText(min_seqnum_species)

        # check the content of inputs
        self.check_inputs()

    #---------------

    def tablewidget_cellClicked(self, _, __):
        '''
        Perform necessary actions afterclicking on a "tablewidget" cell.
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

    def lineedit_fasta_file_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_fasta_file"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_species_name_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_species_name"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_fdr_method_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_fdr_method"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_min_seqnum_annotations_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_min_seqnum_annotations"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_min_seqnum_species_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_min_seqnum_species"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def pushbutton_refresh_clicked(self):
        '''
        Refresh "tablewidget" and initialize other inputs.
        '''

        # check the content of inputs
        self.initialize_inputs()

        # check the content of inputs
        self.check_inputs()

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        Execute the process.
        '''

        # initialize the control variable
        OK = True

        # get the list of rows selected
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check if there is only a row selected
        if len(row_list) != 1:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = 'One row has to be selected.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)
            OK = False

        # confirm the process is executed
        if OK:
            text = 'The enrichment analysis is going to be restarted.\n\nAre you sure to continue?'
            botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
            if botton == QMessageBox.No:
                OK = False

        # execute the process
        if OK:

            # get the identification of the enrichment analysis dataset
            result_dataset_id = self.tablewidget.item(row_list[0], 1).text()

            # create and execute "DialogProcess"
            process = dialogs.DialogProcess(self, self.head, self.restart_enrichment_analysis, result_dataset_id)
            process.exec()

        # close the windows
        # -- if OK:
        # --     self.pushbutton_close_clicked()

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

        # set the type, name and code of the enrichment analysis datasets
        process_type = genlib.get_result_run_subdir()
        process_name = genlib.get_process_run_enrichment_analysis_name()
        process_code = genlib.get_process_id(process_name)

        # get the process dictionary
        process_dict = genlib.get_process_dict()

        # get the log directory
        log_dir = f'{result_dir}/{process_type}'
        if sys.platform.startswith('win32'):
            log_dir = genlib.wsl_path_2_windows_path(log_dir)

        # set the command to get the result datasets of enrichment analysis in the log directory
        command = ''
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            if process_name == 'all':
                command = f'ls -d {log_dir}/*  | xargs -n 1 basename'
            else:
                command = f'ls -d {log_dir}/{process_code}-*  | xargs -n 1 basename'
        elif sys.platform.startswith('win32'):
            log_dir = log_dir.replace('/', '\\')
            if process_name == 'all':
                command = f'dir /a:d /b {log_dir}\\*'
            else:
                command = f'dir /a:d /b {log_dir}\\{process_code}-*'

        # run the command to get the result datasets of enrichment analysis in the log directory
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
                status = ''
                if status_ok and not status_wrong:
                    status = 'OK'
                elif not status_ok and status_wrong:
                    status = 'wrong'
                elif not status_ok and not status_wrong:
                    status = 'not finished'
                elif status_ok and status_wrong:
                    status = 'undetermined'

                # insert data in the dictionary when the the status is wrong
                if status == 'wrong':
                    key = f'{process_name}-{result_dataset_id}'
                    result_dataset_dict[key] = {'process': process_name, 'result_dataset_id': result_dataset_id, 'date': date, 'time': time, 'status': status}

        # initialize "tablewidget"
        self.tablewidget.clearContents()

        # set the rows number of "tablewidget"
        self.tablewidget.setRowCount(len(result_dataset_dict))

        # load data in "tablewidget" for the wrong result datasets of enrichment analysis
        if not result_dataset_dict:
            text = 'There is no run ended wrong.'
            QMessageBox.warning(self, self.title, text, buttons=QMessageBox.Ok)
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

    def restart_enrichment_analysis(self, process, result_dataset_id):
        '''
        Restart an enrichment analysis.
        '''

        # initialize the control variable
        OK = True

        # warn that the log window does not have to be closed
        process.write('Do not close this window, please wait!\n')

        # warn that the requirements are being verified
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write('Checking process requirements ...\n')

        # check the gymnoTOA config file
        if OK:
            if not os.path.isfile(genlib.get_app_config_file()):
                process.write(f'*** ERROR: The {genlib.get_app_short_name()} config file does not exist. Please, recreate it.\n')
                OK = False

        # warn that the requirements are OK
        if OK:
            process.write('Process requirements are OK.\n')

        # determine the run directory
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write('Determining the run directory ...\n')
            result_dir = self.app_config_dict['Environment parameters']['result_dir']
            current_run_dir = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset_id}'
            process.write(f'The directory path is {current_run_dir}.\n')

        # set the starter script name
        if OK:
            starter_name = f'{genlib.get_process_run_enrichment_analysis_code()}-process-starter.sh'

        # submit the starter
        if OK:
            process.write(f'{genlib.get_separator()}\n')
            process.write(f'Submitting the starter {starter_name} ...\n')
            command = f'{current_run_dir}/{starter_name} &'
            rc = genlib.run_command(command, process, is_script=True)
            if rc == 0:
                process.write('The script is submitted.\n')
            else:
                process.write(f'*** ERROR: RC {rc} in command -> {command}\n')
                OK = False

        # warn that the log window can be closed
        process.write(f'{genlib.get_separator()}\n')
        process.write('You can close this window now.\n')

        # return the control variable
        return OK

    #---------------

#-------------------------------------------------------------------------------

class FormBrowseEnrichmentAnalysis(QWidget):
    '''
    Class used to browse results of an enrichment analysis.
    '''

    #---------------

    def __init__(self, parent, code):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent
        self.code = code

        # call the init method of the parent class
        super().__init__()

        # set the dimensions window
        self.window_height = self.parent.WINDOW_HEIGHT - 100
        self.window_width = self.parent.WINDOW_WIDTH - 50

        # set the head and title
        if self.code == genlib.get_goea_code():
            self.head = f'Browse results of a {genlib.get_goea_name()}'
        elif self.code == genlib.get_mpea_code():
            self.head = f'Browse results of a {genlib.get_mpea_name()}'
        elif self.code == genlib.get_koea_code():
            self.head = f'Browse results of a {genlib.get_koea_name()}'
        elif self.code == genlib.get_kpea_code():
            self.head = f'Browse results of a {genlib.get_kpea_name()}'
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # get the the code list and text list of annotation result types
        self.annotation_result_type_code_list = genlib.get_annotation_result_type_code_list()
        self.annotation_result_type_text_list = genlib.get_annotation_result_type_text_list()

        # get the the code list and text list of FDR method
        self.fdr_method_code_list = genlib.get_fdr_method_code_list()
        self.fdr_method_text_list = genlib.get_fdr_method_text_list()

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

        # create and configure "label_fasta_file"
        label_fasta_file = QLabel()
        label_fasta_file.setText('FASTA file')
        label_fasta_file.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_fasta_file"
        self.lineedit_fasta_file = QLineEdit()
        self.lineedit_fasta_file.editingFinished.connect(self.check_inputs)
        self.lineedit_fasta_file.setDisabled(True)

        # create and configure "label_species_name"
        label_species_name = QLabel()
        label_species_name.setText('Species')
        label_species_name.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_species_name"
        self.lineedit_species_name = QLineEdit()
        self.lineedit_species_name.editingFinished.connect(self.check_inputs)
        self.lineedit_species_name.setFixedWidth(fontmetrics.width('9'*20))
        self.lineedit_species_name.setDisabled(True)

        # create and configure "fdr_method"
        label_fdr_method = QLabel()
        label_fdr_method.setText('FDR method')
        label_fdr_method.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_fdr_method"
        self.lineedit_fdr_method = QLineEdit()
        self.lineedit_fdr_method.editingFinished.connect(self.check_inputs)
        self.lineedit_fdr_method.setFixedWidth(fontmetrics.width('9'*20))
        self.lineedit_fdr_method.setDisabled(True)

        # create and configure "label_min_seqnum_annotations"
        label_min_seqnum_annotations = QLabel()
        label_min_seqnum_annotations.setText('Min seq# in annotations')
        label_min_seqnum_annotations.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "lineedit_min_seqnum_annotations"
        self.lineedit_min_seqnum_annotations = QLineEdit()
        self.lineedit_min_seqnum_annotations.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_min_seqnum_annotations.setDisabled(True)

        # create and configure "label_min_seqnum_species"
        label_min_seqnum_species = QLabel()
        label_min_seqnum_species.setText('Min seq# in species')
        label_min_seqnum_species.setFixedWidth(fontmetrics.width('9'*17))

        # create and configure "lineedit_min_seqnum_species"
        self.lineedit_min_seqnum_species  = QLineEdit()
        self.lineedit_min_seqnum_species.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_min_seqnum_species.setDisabled(True)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setFixedWidth(fontmetrics.width('9'*3))

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.addWidget(label_annotation_result_type, 0, 0, 1, 1)
        gridlayout_data.addWidget(self.combobox_annotation_result_type, 0, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(self.tablewidget, 1, 0, 1, 16)
        gridlayout_data.addWidget(label_fasta_file, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fasta_file, 2, 1, 1, 15)
        gridlayout_data.addWidget(label_species_name, 3, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_species_name, 3, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 3, 2, 1, 1)
        gridlayout_data.addWidget(label_fdr_method, 3, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fdr_method, 3, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_min_seqnum_annotations, 4, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_min_seqnum_annotations, 4, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 4, 2, 1, 1)
        gridlayout_data.addWidget(label_min_seqnum_species, 4, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_min_seqnum_species, 4, 4, 1, 1, alignment=Qt.AlignLeft)

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

        # set initial value in "lineedit_fasta_file"
        self.lineedit_fasta_file.setText('')

        # initialize "lineedit_species_name"
        self.lineedit_species_name.setText('')

        # initialize "lineedit_fdr_method"
        self.lineedit_fdr_method.setText('')

        # initialize "lineedit_min_seqnum_annotations"
        self.lineedit_min_seqnum_annotations.setText('')

        # initialize "lineedit_min_seqnum_species"
        self.lineedit_min_seqnum_species.setText('')

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

        # check "lineedit_fasta_file" when the editing finished
        if not self.lineedit_fasta_file_editing_finished():
            OK = False

        # check "lineedit_species_name" when the editing finished
        if not self.lineedit_species_name_editing_finished():
            OK = False

        # check "lineedit_fdr_method" when the editing finished
        if not self.lineedit_fdr_method_editing_finished():
            OK = False

        # check "lineedit_min_seqnum_annotations" when the editing finished
        if not self.lineedit_min_seqnum_annotations_editing_finished():
            OK = False

        # check "lineedit_min_seqnum_species" when the editing finished
        if not self.lineedit_min_seqnum_species_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('There are one or more inputs without data or with wrong value.')

        # enable "pushbutton_execute"
        if OK and self.combobox_annotation_result_type.currentText() != '' and len(row_list) == 1 and self.lineedit_fasta_file.text() != '' and self.lineedit_species_name.text() != '' and self.lineedit_fdr_method.text() != '' and self.lineedit_min_seqnum_annotations.text() != '' and self.lineedit_min_seqnum_species.text() != '':
            self.pushbutton_execute.setEnabled(True)
        else:
            self.pushbutton_execute.setEnabled(False)
            OK = False

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

    def tablewidget_currentCellChanged(self, row, _):
        '''
        Perform necessary actions after changing the current "tablewidget" cell.
        '''

        # check if there is a row selected
        if row >= 0:

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset corresponding to the row clicked
            result_dataset_id = self.tablewidget.item(row, 1).text()

            # get the parameters file corresponding to the result dataset
            params_file = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset_id}{os.sep}{genlib.get_params_file_name()}'
            if sys.platform.startswith('win32'):
                params_file = genlib.wsl_path_2_windows_path(params_file)

            # get the dictionary of parameters
            params_dict = genlib.get_config_dict(params_file)

            # set the FASTA file path in "lineedit_fasta_file"
            fasta_file = params_dict['Annotation parameters']['fasta_file']
            if sys.platform.startswith('win32'):
                fasta_file = genlib.wsl_path_2_windows_path(fasta_file)
            self.lineedit_fasta_file.setText(fasta_file)

            # set the species in "lineedit_species_name"
            species_name = params_dict['Enrichment parameters']['species_name']
            if species_name == genlib.get_all_species_code():
                species_name = genlib.get_all_species_name()
            self.lineedit_species_name.setText(species_name)

            # set the FDR method in "lineedit_fdr_method"
            fdr_method_code = params_dict['Enrichment parameters']['fdr_method']
            fdr_method_text = self.fdr_method_text_list[self.fdr_method_code_list.index(fdr_method_code)]
            self.lineedit_fdr_method.setText(fdr_method_text)

            # set the min seq# in annotations
            min_seqnum_annotations = params_dict['Enrichment parameters']['min_seqnum_annotations']
            self.lineedit_min_seqnum_annotations.setText(min_seqnum_annotations)

            # set the min seq# in species
            min_seqnum_species = params_dict['Enrichment parameters']['min_seqnum_species']
            self.lineedit_min_seqnum_species.setText(min_seqnum_species)

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

    def lineedit_fasta_file_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_fasta_file"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_species_name_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_species_name"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_fdr_method_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_fdr_method"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_min_seqnum_annotations_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_min_seqnum_annotations"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_min_seqnum_species_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_min_seqnum_species"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def pushbutton_refresh_clicked(self):
        '''
        Refresh "tablewidget" and initialize other inputs.
        '''

        # check the content of inputs
        self.initialize_inputs()

        # check the content of inputs
        self.check_inputs()

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        Execute the process.
        '''

        # initialize the control variable
        OK = True

        # get the list of rows selected
        row_list = []
        for idx in self.tablewidget.selectionModel().selectedIndexes():
            row_list.append(idx.row())
        row_list = list(set(row_list))

        # check if there is only a row selected
        if len(row_list) != 1:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = 'One row has to be selected.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)
            OK = False

        # confirm the process is executed
        if OK:
            text = 'The result of the enrichment analysis is going to be browsed.\n\nAre you sure to continue?'
            botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
            if botton == QMessageBox.No:
                OK = False

        # execute the process
        if OK:

            # set the process type
            process_type = genlib.get_result_run_subdir()

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the identification of the enrichment analysis dataset
            result_dataset_id = self.tablewidget.item(row_list[0], 1).text()

            # get the annotation result type
            annotation_result_type = self.annotation_result_type_code_list[self.annotation_result_type_text_list.index(self.combobox_annotation_result_type.currentText())]

            # get the file path of the enrichment analysis
            if self.code == genlib.get_goea_code():
                if annotation_result_type == 'best':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_besthit_goea_file_name()}'
                elif annotation_result_type == 'complete':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_complete_goea_file_name()}'
            elif self.code == genlib.get_mpea_code():
                if annotation_result_type == 'best':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_besthit_mpea_file_name()}'
                elif annotation_result_type == 'complete':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_complete_mpea_file_name()}'
            elif self.code == genlib.get_koea_code():
                if annotation_result_type == 'best':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_besthit_koea_file_name()}'
                elif annotation_result_type == 'complete':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_complete_koea_file_name()}'
            elif self.code == genlib.get_kpea_code():
                if annotation_result_type == 'best':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_besthit_kpea_file_name()}'
                elif annotation_result_type == 'complete':
                    enrichment_analysis_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_complete_kpea_file_name()}'
            if sys.platform.startswith('win32'):
                enrichment_analysis_file_path = genlib.wsl_path_2_windows_path(enrichment_analysis_file_path)

            # get enrichment analysis data
            QApplication.setOverrideCursor(Qt.WaitCursor)
            enrichment_analysis_dict = {}
            data_list = []
            data_dict = {}
            window_height = 0
            window_width = 0
            explanatory_text = ''
            if self.code == genlib.get_goea_code():
                (enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text) = self.get_goterm_enrichment_analysis_data(enrichment_analysis_file_path)
            elif self.code == genlib.get_mpea_code():
                (enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text) = self.get_metacyc_pathway_enrichment_analysis_data(enrichment_analysis_file_path)
            elif self.code == genlib.get_koea_code():
                (enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text) = self.get_kegg_ko_enrichment_analysis_data(enrichment_analysis_file_path)
            elif self.code == genlib.get_kpea_code():
                (enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text) = self.get_kegg_pathway_enrichment_analysis_data(enrichment_analysis_file_path)
            QGuiApplication.restoreOverrideCursor()

            # show enrichment analysis data
            head = f'Enrichment analysis file {enrichment_analysis_file_path}'
            data_table = dialogs.DialogDataTable(self, head, window_height, window_width, data_list, data_dict, enrichment_analysis_dict, enrichment_analysis_dict.keys(), explanatory_text, 'browse-enrichment-analysis')
            data_table.exec()

        # close the windows
        # -- if OK:
        # --     self.pushbutton_close_clicked()

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

        # set the type, name and code of the enrichment analysis datasets
        process_type = genlib.get_result_run_subdir()
        process_name = genlib.get_process_run_enrichment_analysis_name()
        process_code = genlib.get_process_id(process_name)

        # get the process dictionary
        process_dict = genlib.get_process_dict()

        # get the log directory
        log_dir = f'{result_dir}/{process_type}'
        if sys.platform.startswith('win32'):
            log_dir = genlib.wsl_path_2_windows_path(log_dir)

        # set the command to get the result datasets of enrichment analysis in the log directory
        command = ''
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            if process_name == 'all':
                command = f'ls -d {log_dir}/*  | xargs -n 1 basename'
            else:
                command = f'ls -d {log_dir}/{process_code}-*  | xargs -n 1 basename'
        elif sys.platform.startswith('win32'):
            log_dir = log_dir.replace('/', '\\')
            if process_name == 'all':
                command = f'dir /a:d /b {log_dir}\\*'
            else:
                command = f'dir /a:d /b {log_dir}\\{process_code}-*'

        # run the command to get the result datasets of enrichment analysis in the log directory
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
                status = ''
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

        # load data in "tablewidget" for the OK result datasets of enrichment analysis
        if not result_dataset_dict:
            text = 'There is no run ended OK.'
            QMessageBox.warning(self, self.title, text, buttons=QMessageBox.Ok)
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
    def get_goterm_enrichment_analysis_data(enrichment_analysis_file_path):
        '''
        Get GO term enrichment analysis data.
        '''

        # initialize the enrichment analysis dictionary
        enrichment_analysis_dict = {}

        # open the enrichment analysis file
        if enrichment_analysis_file_path.endswith('.gz'):
            try:
                enrichment_analysis_file_path_id = gzip.open(enrichment_analysis_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', enrichment_analysis_file_path)
        else:
            try:
                enrichment_analysis_file_path_id = open(enrichment_analysis_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', enrichment_analysis_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = enrichment_analysis_file_path_id.readline()

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
                # record format: "GOterm";"Description";"Namespace";"Sequences# with this GOterm in annotations";"Sequences# with GOterms in annotations";"Sequences# with this GOterm in species";"Sequences# with GOterms in species";"Enrichment";"p-value";"FDR"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    goterm = data_list[0]
                    description = data_list[1]
                    namespace = data_list[2]
                    annotation_seqs_count = data_list[3]
                    annotation_seqs_wgoterms = data_list[4]
                    species_seqs_count = data_list[5]
                    species_seqs_wgoterms = data_list[6]
                    enrichment = data_list[7]
                    pvalue= data_list[8]
                    fdr = data_list[9]

                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(enrichment_analysis_file_path), record_counter)

                # add data to the dictionary
                enrichment_analysis_dict[goterm] = {'goterm': goterm, 'description': description, 'namespace': namespace, 'annotation_seqs_count': annotation_seqs_count, 'annotation_seqs_wgoterms': annotation_seqs_wgoterms, 'species_seqs_count': species_seqs_count, 'species_seqs_wgoterms': species_seqs_wgoterms, 'enrichment': enrichment, 'pvalue': pvalue, 'fdr': fdr}

            # read the next record
            record = enrichment_analysis_file_path_id.readline()

        # build the data list
        data_list = ['goterm', 'description', 'namespace', 'annotation_seqs_count', 'annotation_seqs_wgoterms', 'species_seqs_count', 'species_seqs_wgoterms', 'enrichment', 'pvalue', 'fdr']

        # build the data dictionary
        data_dict = {}
        data_dict['goterm'] = {'text': 'GOterm', 'width': 100, 'alignment': 'left'}
        data_dict['description'] = {'text': 'Description', 'width': 200, 'alignment': 'left'}
        data_dict['namespace'] = {'text': 'Namespace', 'width': 140, 'alignment': 'left'}
        data_dict['annotation_seqs_count'] = {'text': '(1)', 'width': 50, 'alignment': 'right'}
        data_dict['annotation_seqs_wgoterms'] = {'text': '(2)', 'width': 60, 'alignment': 'right'}
        data_dict['species_seqs_count'] = {'text': '(3)', 'width': 50, 'alignment': 'right'}
        data_dict['species_seqs_wgoterms'] = {'text': '(4)', 'width': 60, 'alignment': 'right'}
        data_dict['enrichment'] = {'text': 'Enrichment', 'width': 160, 'alignment': 'right'}
        data_dict['pvalue'] = {'text': 'p-value', 'width': 190, 'alignment': 'right'}
        data_dict['fdr'] = {'text': 'FDR', 'width': 190, 'alignment': 'right'}

        # set the explanatory text
        explanatory_text = '(1) Sequences# with this GOterm in annotations - (2) Sequences# with GOterms in annotations - (3) Sequences# with this GOterm in species - (4) Sequences# with GOterms in species'

        # set the window height and width
        window_height = 800
        window_width = 1330

        # return data
        return enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text

    #---------------

    @staticmethod
    def get_metacyc_pathway_enrichment_analysis_data(enrichment_analysis_file_path):
        '''
        Get Metacyc pathway enrichment analysis data.
        '''

        # initialize the enrichment analysis dictionary
        enrichment_analysis_dict = {}

        # open the enrichment analysis file
        if enrichment_analysis_file_path.endswith('.gz'):
            try:
                enrichment_analysis_file_path_id = gzip.open(enrichment_analysis_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', enrichment_analysis_file_path)
        else:
            try:
                enrichment_analysis_file_path_id = open(enrichment_analysis_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', enrichment_analysis_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = enrichment_analysis_file_path_id.readline()

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
                # record format: "Metacyc pathway";"Sequences# with this Metacyc pathway in annotations";"Sequences# with Metacyc pathways in annotations";"Sequences# with this Metacyc pathway in species";"Sequences# with Metacyc pathways in species";"Enrichment";"p-value";"FDR"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    metacyc_pathway_id = data_list[0]
                    annotation_seqs_count = data_list[1]
                    annotation_seqs_wpathways = data_list[2]
                    species_seqs_count = data_list[3]
                    species_seqs_wpathways = data_list[4]
                    enrichment = data_list[5]
                    pvalue= data_list[6]
                    fdr = data_list[7]

                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(enrichment_analysis_file_path), record_counter)

                # add data to the dictionary
                enrichment_analysis_dict[metacyc_pathway_id] = {'metacyc_pathway_id': metacyc_pathway_id, 'annotation_seqs_count': annotation_seqs_count, 'annotation_seqs_wpathways': annotation_seqs_wpathways, 'species_seqs_count': species_seqs_count, 'species_seqs_wpathways': species_seqs_wpathways, 'enrichment': enrichment, 'pvalue': pvalue, 'fdr': fdr}

            # read the next record
            record = enrichment_analysis_file_path_id.readline()

        # build the data list
        data_list = ['metacyc_pathway_id', 'annotation_seqs_count', 'annotation_seqs_wpathways', 'species_seqs_count', 'species_seqs_wpathways', 'enrichment', 'pvalue', 'fdr']

        # build the data dictionary
        data_dict = {}
        data_dict['metacyc_pathway_id'] = {'text': 'Metacyc pathway', 'width': 160, 'alignment': 'left'}
        data_dict['annotation_seqs_count'] = {'text': '(1)', 'width': 50, 'alignment': 'right'}
        data_dict['annotation_seqs_wpathways'] = {'text': '(2)', 'width': 60, 'alignment': 'right'}
        data_dict['species_seqs_count'] = {'text': '(3)', 'width': 50, 'alignment': 'right'}
        data_dict['species_seqs_wpathways'] = {'text': '(4)', 'width': 60, 'alignment': 'right'}
        data_dict['enrichment'] = {'text': 'Enrichment', 'width': 160, 'alignment': 'right'}
        data_dict['pvalue'] = {'text': 'p-value', 'width': 190, 'alignment': 'right'}
        data_dict['fdr'] = {'text': 'FDR', 'width': 190, 'alignment': 'right'}

        # set the explanatory text
        explanatory_text = '(1) Sequences# with this pathway in annotations - (2) Sequences# with pathways in annotations - (3) Sequences# with this pathway in species\n(4) Sequences# with pathways in species'

        # set the window height and width
        window_height = 800
        window_width = 1050

        # return data
        return enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text

    #---------------

    @staticmethod
    def get_kegg_ko_enrichment_analysis_data(enrichment_analysis_file_path):
        '''
        Get KEGG KO enrichment analysis data.
        '''

        # initialize the enrichment analysis dictionary
        enrichment_analysis_dict = {}

        # open the enrichment analysis file
        if enrichment_analysis_file_path.endswith('.gz'):
            try:
                enrichment_analysis_file_path_id = gzip.open(enrichment_analysis_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', enrichment_analysis_file_path)
        else:
            try:
                enrichment_analysis_file_path_id = open(enrichment_analysis_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', enrichment_analysis_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = enrichment_analysis_file_path_id.readline()

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
                # record format: "KEGG KO";"Sequences# with this KEGG KO in annotations";"Sequences# with KEGG KOs in annotations";"Sequences# with this KEGG KO in species";"Sequences# with KEGG KOs in species";"Enrichment";"p-value";"FDR"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    kegg_ko_id = data_list[0]
                    annotation_seqs_count = data_list[1]
                    annotation_seqs_wpathways = data_list[2]
                    species_seqs_count = data_list[3]
                    species_seqs_wpathways = data_list[4]
                    enrichment = data_list[5]
                    pvalue= data_list[6]
                    fdr = data_list[7]

                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(enrichment_analysis_file_path), record_counter)

                # add data to the dictionary
                enrichment_analysis_dict[kegg_ko_id] = {'kegg_ko_id': kegg_ko_id, 'annotation_seqs_count': annotation_seqs_count, 'annotation_seqs_wpathways': annotation_seqs_wpathways, 'species_seqs_count': species_seqs_count, 'species_seqs_wpathways': species_seqs_wpathways, 'enrichment': enrichment, 'pvalue': pvalue, 'fdr': fdr}

            # read the next record
            record = enrichment_analysis_file_path_id.readline()

        # build the data list
        data_list = ['kegg_ko_id', 'annotation_seqs_count', 'annotation_seqs_wpathways', 'species_seqs_count', 'species_seqs_wpathways', 'enrichment', 'pvalue', 'fdr']

        # build the data dictionary
        data_dict = {}
        data_dict['kegg_ko_id'] = {'text': 'KEGG ko', 'width': 160, 'alignment': 'left'}
        data_dict['annotation_seqs_count'] = {'text': '(1)', 'width': 50, 'alignment': 'right'}
        data_dict['annotation_seqs_wpathways'] = {'text': '(2)', 'width': 60, 'alignment': 'right'}
        data_dict['species_seqs_count'] = {'text': '(3)', 'width': 50, 'alignment': 'right'}
        data_dict['species_seqs_wpathways'] = {'text': '(4)', 'width': 60, 'alignment': 'right'}
        data_dict['enrichment'] = {'text': 'Enrichment', 'width': 160, 'alignment': 'right'}
        data_dict['pvalue'] = {'text': 'p-value', 'width': 190, 'alignment': 'right'}
        data_dict['fdr'] = {'text': 'FDR', 'width': 190, 'alignment': 'right'}

        # set the explanatory text
        explanatory_text = '(1) Sequences# with this pathway in annotations - (2) Sequences# with pathways in annotations - (3) Sequences# with this pathway in species\n(4) Sequences# with pathways in species'

        # set the window height and width
        window_height = 800
        window_width = 1050

        # return data
        return enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text

    #---------------

    @staticmethod
    def get_kegg_pathway_enrichment_analysis_data(enrichment_analysis_file_path):
        '''
        Get KEGG pathway enrichment analysis data.
        '''

        # initialize the enrichment analysis dictionary
        enrichment_analysis_dict = {}

        # open the enrichment analysis file
        if enrichment_analysis_file_path.endswith('.gz'):
            try:
                enrichment_analysis_file_path_id = gzip.open(enrichment_analysis_file_path, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', enrichment_analysis_file_path)
        else:
            try:
                enrichment_analysis_file_path_id = open(enrichment_analysis_file_path, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', enrichment_analysis_file_path)

        # initialize the record counter
        record_counter = 0

        # initialize the header record control
        header_record = True

        # read the first record
        record = enrichment_analysis_file_path_id.readline()

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
                # record format: "KEGG pathway";"Sequences# with this KEGG pathway in annotations";"Sequences# with KEGG pathways in annotations";"Sequences# with this KEGG pathway in species";"Sequences# with KEGG pathways in species";"Enrichment";"p-value";"FDR"
                data_list = []
                begin = 0
                for end in [i for i, chr in enumerate(record) if chr == ';']:
                    data_list.append(record[begin:end].strip('"'))
                    begin = end + 1
                data_list.append(record[begin:].strip('\n').strip('"'))
                try:
                    kegg_pathway_id = data_list[0]
                    annotation_seqs_count = data_list[1]
                    annotation_seqs_wpathways = data_list[2]
                    species_seqs_count = data_list[3]
                    species_seqs_wpathways = data_list[4]
                    enrichment = data_list[5]
                    pvalue= data_list[6]
                    fdr = data_list[7]

                except Exception as e:
                    raise genlib.ProgramException(e, 'F006', os.path.basename(enrichment_analysis_file_path), record_counter)

                # add data to the dictionary
                enrichment_analysis_dict[kegg_pathway_id] = {'kegg_pathway_id': kegg_pathway_id, 'annotation_seqs_count': annotation_seqs_count, 'annotation_seqs_wpathways': annotation_seqs_wpathways, 'species_seqs_count': species_seqs_count, 'species_seqs_wpathways': species_seqs_wpathways, 'enrichment': enrichment, 'pvalue': pvalue, 'fdr': fdr}

            # read the next record
            record = enrichment_analysis_file_path_id.readline()

        # build the data list
        data_list = ['kegg_pathway_id', 'annotation_seqs_count', 'annotation_seqs_wpathways', 'species_seqs_count', 'species_seqs_wpathways', 'enrichment', 'pvalue', 'fdr']

        # build the data dictionary
        data_dict = {}
        data_dict['kegg_pathway_id'] = {'text': 'KEGG pathway', 'width': 160, 'alignment': 'left'}
        data_dict['annotation_seqs_count'] = {'text': '(1)', 'width': 50, 'alignment': 'right'}
        data_dict['annotation_seqs_wpathways'] = {'text': '(2)', 'width': 60, 'alignment': 'right'}
        data_dict['species_seqs_count'] = {'text': '(3)', 'width': 50, 'alignment': 'right'}
        data_dict['species_seqs_wpathways'] = {'text': '(4)', 'width': 60, 'alignment': 'right'}
        data_dict['enrichment'] = {'text': 'Enrichment', 'width': 160, 'alignment': 'right'}
        data_dict['pvalue'] = {'text': 'p-value', 'width': 190, 'alignment': 'right'}
        data_dict['fdr'] = {'text': 'FDR', 'width': 190, 'alignment': 'right'}

        # set the explanatory text
        explanatory_text = '(1) Sequences# with this pathway in annotations - (2) Sequences# with pathways in annotations - (3) Sequences# with this pathway in species\n(4) Sequences# with pathways in species'

        # set the window height and width
        window_height = 800
        window_width = 1050

        # return data
        return enrichment_analysis_dict, data_list, data_dict, window_height, window_width, explanatory_text

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'This file contains the classes related to the enrichment Analysis used in {genlib.get_app_long_name()}')
    sys.exit(0)

#-------------------------------------------------------------------------------
