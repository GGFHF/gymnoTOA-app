#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=unnecessary-pass

#-------------------------------------------------------------------------------

'''
This file contains the classes related to the functional annotation of gymnoTOA
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
from PyQt5.QtWidgets import QFileDialog          # pylint: disable=no-name-in-module
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

class FormRunAnnotationPipeline(QWidget):
    '''
    Class used to run a functional annotation pipeline.
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
        self.head = 'Run an annotation pipeline'
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

        # get font metrics information
        fontmetrics = QFontMetrics(QApplication.font())

        # create and configure "label_head"
        label_head = QLabel(self.head, alignment=Qt.AlignCenter)
        label_head.setStyleSheet('font: bold 14px; color: black; background-color: lightGray; max-height: 30px')

        # create and configure "label_threads"
        label_threads = QLabel()
        label_threads.setText('Threads')
        label_threads.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "lineedit_threads"
        self.lineedit_threads  = QLineEdit()
        self.lineedit_threads.setFixedWidth(fontmetrics.width('9'*6))
        self.lineedit_threads.editingFinished.connect(self.check_inputs)

        # create and configure "label_fasta_type"
        label_fasta_type = QLabel()
        label_fasta_type.setText('FASTA type')
        label_fasta_type.setFixedWidth(fontmetrics.width('9'*10))

        # create and configure "combobox_fasta_type"
        self.combobox_fasta_type = QComboBox()
        self.combobox_fasta_type.currentIndexChanged.connect(self.check_inputs)
        self.combobox_fasta_type.setFixedWidth(fontmetrics.width('9'*22))

        # create and configure "label_fasta_file"
        label_fasta_file = QLabel()
        label_fasta_file.setText('FASTA file')

        # create and configure "lineedit_fasta_file"
        self.lineedit_fasta_file = QLineEdit()
        self.lineedit_fasta_file.editingFinished.connect(self.check_inputs)

        # create and configure "pushbutton_search_fasta_file"
        pushbutton_search_fasta_file = QPushButton('Search ...')
        pushbutton_search_fasta_file.setToolTip('Search and select the FASTA file.')
        pushbutton_search_fasta_file.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_search_fasta_file.clicked.connect(self.pushbutton_search_fasta_file_clicked)

        # create and configure "label_codan_model"
        label_codan_model = QLabel()
        label_codan_model.setText('CodAn model')
        label_codan_model.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "combobox_codan_model"
        self.combobox_codan_model = QComboBox()
        self.combobox_codan_model.currentIndexChanged.connect(self.check_inputs)
        self.combobox_codan_model.setFixedWidth(fontmetrics.width('9'*22))

        # create and configure "label_alignment_tool"
        label_alignment_tool = QLabel()
        label_alignment_tool.setText('Alignment tool')
        label_alignment_tool.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "combobox_alignment_tool"
        self.combobox_alignment_tool = QComboBox()
        self.combobox_alignment_tool.currentIndexChanged.connect(self.check_inputs)
        self.combobox_alignment_tool.setFixedWidth(fontmetrics.width('9'*22))

        # create and configure "evalue"
        label_evalue = QLabel()
        label_evalue.setText('evalue')
        label_evalue.setFixedWidth(fontmetrics.width('9'*12))

        # create and configure "lineedit_evalue"
        self.lineedit_evalue  = QLineEdit()
        self.lineedit_evalue.setFixedWidth(fontmetrics.width('9'*10))
        self.lineedit_evalue.editingFinished.connect(self.check_inputs)

        # create and configure "label_max_target_seqs"
        label_max_target_seqs = QLabel()
        label_max_target_seqs.setText('max_target_seqs')
        label_max_target_seqs.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_max_target_seqs"
        self.lineedit_max_target_seqs  = QLineEdit()
        self.lineedit_max_target_seqs.setFixedWidth(fontmetrics.width('9'*4))
        self.lineedit_max_target_seqs.editingFinished.connect(self.check_inputs)

        # create and configure "label_max_hsps"
        label_max_hsps = QLabel()
        label_max_hsps.setText('max_hsps')
        label_max_hsps.setFixedWidth(fontmetrics.width('9'*9))

        # create and configure "lineedit_max_hsps"
        self.lineedit_max_hsps  = QLineEdit()
        self.lineedit_max_hsps.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_max_hsps.editingFinished.connect(self.check_inputs)

        # create and configure "label_qcov_hsp_perc"
        label_qcov_hsp_perc = QLabel()
        label_qcov_hsp_perc.setText('qcov_hsp_perc')
        label_qcov_hsp_perc.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_qcov_hsp_perc"
        self.lineedit_qcov_hsp_perc = QLineEdit()
        self.lineedit_qcov_hsp_perc.setFixedWidth(fontmetrics.width('9'*6))
        self.lineedit_qcov_hsp_perc.editingFinished.connect(self.check_inputs)

        # create and configure "label_other_parameters"
        label_other_parameters = QLabel()
        label_other_parameters.setText('Other params')
        label_other_parameters.setFixedWidth(fontmetrics.width('9'*12))

        # create and configure "lineedit_other_parameters"
        self.lineedit_other_parameters = QLineEdit()
        self.lineedit_other_parameters.setFixedWidth(fontmetrics.width('9'*75))
        self.lineedit_other_parameters.editingFinished.connect(self.check_inputs)

        # create and configure "empty"
        label_empty = QLabel()
        label_empty.setFixedWidth(fontmetrics.width('9'*3))

        # create and configure "gridlayout_blast_param"
        gridlayout_blast_param = QGridLayout()
        gridlayout_blast_param.setRowMinimumHeight(0, 30)
        gridlayout_blast_param.setRowMinimumHeight(1, 30)
        gridlayout_blast_param.setColumnStretch(0, 1)
        gridlayout_blast_param.setColumnStretch(1, 1)
        gridlayout_blast_param.setColumnStretch(2, 1)
        gridlayout_blast_param.setColumnStretch(3, 1)
        gridlayout_blast_param.setColumnStretch(4, 1)
        gridlayout_blast_param.setColumnStretch(5, 1)
        gridlayout_blast_param.setColumnStretch(6, 1)
        gridlayout_blast_param.setColumnStretch(7, 1)
        gridlayout_blast_param.setColumnStretch(8, 1)
        gridlayout_blast_param.setColumnStretch(9, 1)
        gridlayout_blast_param.setColumnStretch(10, 1)
        gridlayout_blast_param.addWidget(label_evalue, 0, 0, 1, 1)
        gridlayout_blast_param.addWidget(self.lineedit_evalue, 0, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_blast_param.addWidget(label_empty, 0, 2, 1, 1)
        gridlayout_blast_param.addWidget(label_max_target_seqs, 0, 3, 1, 1)
        gridlayout_blast_param.addWidget(self.lineedit_max_target_seqs, 0, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_blast_param.addWidget(label_empty, 0, 5, 1, 1)
        gridlayout_blast_param.addWidget(label_max_hsps, 0, 6, 1, 1)
        gridlayout_blast_param.addWidget(self.lineedit_max_hsps, 0, 7, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_blast_param.addWidget(label_empty, 0, 8, 1, 1)
        gridlayout_blast_param.addWidget(label_qcov_hsp_perc, 0, 9, 1, 1)
        gridlayout_blast_param.addWidget(self.lineedit_qcov_hsp_perc, 0, 10, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_blast_param.addWidget(label_other_parameters, 1, 0, 1, 1)
        gridlayout_blast_param.addWidget(self.lineedit_other_parameters, 1, 1, 1, 10, alignment=Qt.AlignLeft)

        # create and configure "groupbox_blast_param"
        groupbox_blast_param = QGroupBox('Alignment parameters')
        groupbox_blast_param.setLayout(gridlayout_blast_param)

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.setRowMinimumHeight(0, 40)
        gridlayout_data.setRowMinimumHeight(1, 40)
        gridlayout_data.setRowMinimumHeight(2, 40)
        gridlayout_data.setRowMinimumHeight(3, 120)
        gridlayout_data.setColumnStretch(0,1)
        gridlayout_data.setColumnStretch(1,1)
        gridlayout_data.setColumnStretch(2,1)
        gridlayout_data.setColumnStretch(3,1)
        gridlayout_data.setColumnStretch(4,15)
        gridlayout_data.setColumnStretch(5,1)
        gridlayout_data.addWidget(label_threads, 0, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_threads, 0, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 0, 2, 1, 1)
        gridlayout_data.addWidget(label_fasta_type, 0, 3, 1, 1)
        gridlayout_data.addWidget(self.combobox_fasta_type, 0, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_fasta_file, 1, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fasta_file, 1, 1, 1, 4)
        gridlayout_data.addWidget(pushbutton_search_fasta_file, 1, 5, 1, 1)
        gridlayout_data.addWidget(label_codan_model, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.combobox_codan_model, 2, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_empty, 2, 2, 1, 1)
        gridlayout_data.addWidget(label_alignment_tool, 2, 3, 1, 1)
        gridlayout_data.addWidget(self.combobox_alignment_tool, 2, 4, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(groupbox_blast_param, 3, 0, 1, 6)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_execute"
        self.pushbutton_execute = QPushButton('Execute')
        self.pushbutton_execute.setToolTip('Execute the functional annotation pipeline.')
        self.pushbutton_execute.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_execute.clicked.connect(self.pushbutton_execute_clicked)

        # create and configure "pushbutton_close"
        pushbutton_close = QPushButton('Close')
        pushbutton_close.setToolTip('Cancel the run of the functional annotation pipeline and close the window.')
        pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 10)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.setColumnStretch(2, 1)
        gridlayout_buttons.addWidget(self.pushbutton_execute, 0, 1, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(pushbutton_close, 0, 2, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)

        # create and configure "gridlayout_central"
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 1)
        gridlayout_central.setRowStretch(1, 1)
        gridlayout_central.setRowStretch(2, 1)
        gridlayout_central.setRowStretch(3, 1)
        gridlayout_central.setRowStretch(4, 1)
        gridlayout_central.setColumnStretch(0, 0)
        gridlayout_central.setColumnStretch(1, 1)
        gridlayout_central.setColumnStretch(2, 0)
        gridlayout_central.addWidget(label_head, 0, 1)
        gridlayout_central.addWidget(QLabel(), 1, 1)
        gridlayout_central.addWidget(groupbox_data, 2, 1)
        gridlayout_central.addWidget(QLabel(), 3, 1)
        gridlayout_central.addWidget(groupbox_buttons, 4, 1)

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

        # set initial value in "lineedit_threads"
        self.lineedit_threads.setText('4')

        # populate data in "combobox_fasta_type"
        self.combobox_fasta_type_populate()

        # set initial value in "lineedit_fasta_file"
        self.lineedit_fasta_file.setText('')

        # populate data in "combobox_codan_model"
        self.combobox_codan_model_populate()

        # populate data in "combobox_alignment_tool"
        self.combobox_alignment_tool_populate()

        # set initial value in "lineedit_evalue"
        self.lineedit_evalue.setText('1E-6')

        # set initial value in "lineedit_max_target_seqs"
        self.lineedit_max_target_seqs.setText('20')

        # set initial value in "lineedit_max_hsps"
        self.lineedit_max_hsps.setText('999999')

        # set initial value in "lineedit_qcov_hsp_perc"
        self.lineedit_qcov_hsp_perc.setText('0.0')

        # set initial value in "lineedit_other_parameters"
        self.lineedit_other_parameters.setText('NONE')

    #---------------

    def check_inputs(self):
        '''
        Check the content of each input and do the actions linked to its value.
        '''

        # initialize the control variable
        OK = True

        # check "lineedit_threads" when the editing finished
        if not self.lineedit_threads_editing_finished():
            OK = False

        # check "lineedit_fasta_file" when the editing finished
        if not self.lineedit_fasta_file_editing_finished():
            OK = False

        # check "lineedit_evalue" when the editing finished
        if not self.lineedit_evalue_editing_finished():
            OK = False

        # check "lineedit_max_target_seqs" when the editing finished
        if not self.lineedit_max_target_seqs_editing_finished():
            OK = False

        # check "lineedit_max_hsps" when the editing finished
        if not self.lineedit_max_hsps_editing_finished():
            OK = False

        # check "lineedit_qcov_hsp_perc" when the editing finished
        if not self.lineedit_qcov_hsp_perc_editing_finished():
            OK = False

        # check "lineedit_other_parameters" when the editing finished
        if not self.lineedit_other_parameters_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('WARNING: One or more input values are wrong or empty.')

        # enable "pushbutton_execute"
        if OK and self.lineedit_threads.text() != '' and self.lineedit_fasta_file.text() != '' and self.lineedit_evalue.text() != '' and self.lineedit_max_target_seqs.text() != '' and self.lineedit_max_hsps.text() != '' and self.lineedit_qcov_hsp_perc.text() != '' and self.lineedit_other_parameters.text() != '':
            self.pushbutton_execute.setEnabled(True)
        else:
            self.pushbutton_execute.setEnabled(False)

        # return the control variable
        return OK

    #---------------

    def lineedit_threads_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_threads"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_threads" is empty
        if self.lineedit_threads.text() == '':
            OK = False
            self.lineedit_threads.setStyleSheet('background-color: white')

        # chek if "lineedit_threads" is an integer number between 1 and the CPUs number in the computer
        elif self.lineedit_threads.text() != '' and not genlib.check_int(self.lineedit_threads.text(), minimum=1, maximum=os.cpu_count()):
            OK = False
            self.lineedit_threads.setStyleSheet('background-color: red')
            text = f'The value of threads number has to be an integer number between 1 and {os.cpu_count()} (threads available in the computer).'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_threads.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def combobox_fasta_type_populate(self):
        '''
        Populate data in "combobox_fasta_type".
        '''

        # populate data in "combobox_fasta_type"
        self.combobox_fasta_type.addItems([genlib.get_fasta_type_transcripts(), genlib.get_fasta_type_proteins()])

        # simultate "combobox_fasta_type" index has changed
        self.combobox_fasta_type_currentIndexChanged()

    #---------------

    def combobox_fasta_type_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_fasta_type" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def lineedit_fasta_file_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_fasta_file"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_fasta_file" is empty
        if self.lineedit_fasta_file.text() == '':
            self.lineedit_fasta_file.setStyleSheet('background-color: white')
            OK = False

        # chek if "lineedit_fasta_file" exists
        elif not os.path.isfile(self.lineedit_fasta_file.text()):
            self.lineedit_fasta_file.setStyleSheet('background-color: red')
            OK = False

        else:
            self.lineedit_fasta_file.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def pushbutton_search_fasta_file_clicked(self):
        '''
        Search and select the FASTA file.
        '''

        # search the FASTA file
        (fasta_file, _) = QFileDialog.getOpenFileName(self, f'{self.head} - Selection of FASTA file', os.path.expanduser('~'), "FASTA files (*.fasta *.FASTA *.fas *.FAS *.fa *.FA *.fsa *.FSA);;all (*.*)")

        # set "lineedit_fasta_file" with the FASTA file selected
        if fasta_file != '':
            self.lineedit_fasta_file.setText(fasta_file)

        # check the content of inputs
        self.check_inputs()

    #---------------

    def combobox_codan_model_populate(self):
        '''
        Populate data in "combobox_codan_model".
        '''

        # get mode directories from the dictionary of application configuration
        codan_full_plants_model_dir = self.app_config_dict['CodAn models']['codan_full_plants_model_dir']
        codan_partial_plants_model_dir = self.app_config_dict['CodAn models']['codan_partial_plants_model_dir']

        # populate data in "combobox_codan_model"
        self.combobox_codan_model.addItems([os.path.basename(codan_full_plants_model_dir), os.path.basename(codan_partial_plants_model_dir)])

        # simultate "combobox_codan_model" index has changed
        self.combobox_codan_model_currentIndexChanged()

    #---------------

    def combobox_codan_model_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_codan_model" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def combobox_alignment_tool_populate(self):
        '''
        Populate data in "combobox_alignment_tool".
        '''

        # populate data in "combobox_alignment_tool"
        self.combobox_alignment_tool.addItems([genlib.get_blastplus_name(), genlib.get_diamond_name()])

        # simultate "combobox_alignment_tool" index has changed
        self.combobox_alignment_tool_currentIndexChanged()

    #---------------

    def combobox_alignment_tool_currentIndexChanged(self):
        '''
        Process the event when an item of "combobox_alignment_tool" has been selected.
        '''

        # check the content of inputs
        self.check_inputs()

    #---------------

    def lineedit_evalue_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_evalue"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_evalue" is empty
        if self.lineedit_evalue.text() == '':
            OK = False
            self.lineedit_evalue.setStyleSheet('background-color: white')

        # chek if "lineedit_evalue" is a float number greater than 0.
        elif self.lineedit_evalue.text() != '' and not genlib.check_float(self.lineedit_evalue.text(), minimum=1E-999):
            OK = False
            self.lineedit_evalue.setStyleSheet('background-color: red')
            text = 'The value of evalue has to be a float number greater than 0.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_evalue.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def lineedit_max_target_seqs_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_max_target_seqs"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_max_target_seqs" is empty
        if self.lineedit_max_target_seqs.text() == '':
            OK = False
            self.lineedit_max_target_seqs.setStyleSheet('background-color: white')

        # chek if "lineedit_max_target_seqs" is an integer number greater than 1
        elif self.lineedit_max_target_seqs.text() != '' and not genlib.check_int(self.lineedit_max_target_seqs.text(), minimum=1):
            OK = False
            self.lineedit_max_target_seqs.setStyleSheet('background-color: red')
            text = 'The value of max_target_seqs has to be an integer number greater than 1.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)
        else:
            self.lineedit_max_target_seqs.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def lineedit_max_hsps_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_max_hsps"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_max_hsps" is empty
        if self.lineedit_max_hsps.text() == '':
            OK = False
            self.lineedit_max_hsps.setStyleSheet('background-color: white')

        # chek if "lineedit_max_hsps" is an integer number greater than 1
        elif self.lineedit_max_hsps.text() != '' and not genlib.check_int(self.lineedit_max_hsps.text(), minimum=1):
            OK = False
            self.lineedit_max_hsps.setStyleSheet('background-color: red')
            text = 'The value of max_hsps has to be an integer number greater than 1.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_max_hsps.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def lineedit_qcov_hsp_perc_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_qcov_hsp_perc"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_qcov_hsp_perc" is empty
        if self.lineedit_qcov_hsp_perc.text() == '':
            OK = False
            self.lineedit_qcov_hsp_perc.setStyleSheet('background-color: white')

        # chek if "lineedit_qcov_hsp_perc" is a float number greater than 0.
        elif self.lineedit_qcov_hsp_perc.text() != '' and not genlib.check_float(self.lineedit_qcov_hsp_perc.text(), minimum=1E-999):
            OK = False
            self.lineedit_qcov_hsp_perc.setStyleSheet('background-color: red')
            text = 'The value of qcov_hsp_perc has to be a float number greater than 0.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_qcov_hsp_perc.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def lineedit_other_parameters_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_other_parameters"
        '''

        # initialize the control variable
        OK = True

        # chek if "lineedit_other_parameters" is empty
        if self.lineedit_other_parameters.text() == '':
            OK = False
            self.lineedit_other_parameters.setStyleSheet('background-color: white')

        # chek if "lineedit_other_parameters" is NONE
        elif self.lineedit_other_parameters.text().upper() == 'NONE':
            self.lineedit_other_parameters.setText('NONE')
            self.lineedit_other_parameters.setStyleSheet('background-color: white')

        # chek if lineedit_other_parameters" is OK
        elif self.lineedit_other_parameters.text() != '' and self.lineedit_other_parameters.text() != 'NONE':
            not_allowed_parameters_list = ['num_threads', 'db', 'query', 'evalue', 'max_target_seqs', 'max_hsps', 'qcov_hsp_perc', 'outfmt', 'out']
            (OK, error_list) = genlib.check_parameter_list(self.lineedit_other_parameters.text(), 'other_parameters', not_allowed_parameters_list)
            if OK:
                self.lineedit_other_parameters.setStyleSheet('background-color: white')
            else:
                self.lineedit_other_parameters.setStyleSheet('background-color: red')
                error_list_text = '\n'.join(error_list)
                text = f'Other params format:\n\n--parameter-1[=value-1][; --parameter-2[=value-2][; ...]]\n\n{error_list_text}'
                QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        else:
            self.lineedit_other_parameters.setStyleSheet('background-color: white')

        # return the control variable
        return OK

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        Execute the process.
        '''

        # initialize the control variable
        OK = True

        # confirm the process is executed
        text = 'The functional annotation pipeline is going to be run.\n\nAre you sure to continue?'
        botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
        if botton == QMessageBox.No:
            OK = False

        # execute the process
        if OK:

            # get the threads number
            threads = self.lineedit_threads.text()

            # get the FASTA type
            fasta_type = self.combobox_fasta_type.currentText()

            # get the FASTA file
            fasta_file = self.lineedit_fasta_file.text()
            if sys.platform.startswith('win32'):
                fasta_file = genlib.windows_path_2_wsl_path(fasta_file)

            # get the CONDA model
            codan_model = self.combobox_codan_model.currentText()

            # get the alignment tool
            alignment_tool = self.combobox_alignment_tool.currentText()

            # get the alignment parameter evalue
            evalue = self.lineedit_evalue.text()

            # get the alignment parameter max_target_seqs
            max_target_seqs = self.lineedit_max_target_seqs.text()

            # get the alignment parameter max_hsps
            max_hsps = self.lineedit_max_hsps.text()

            # get the alignment parameter qcov_hsp_perc
            qcov_hsp_perc = self.lineedit_qcov_hsp_perc.text()

            # get other parameters of the alignment
            other_parameters = self.lineedit_other_parameters.text()

            # create and execute "DialogProcess"
            process = dialogs.DialogProcess(self, self.head, self.run_annotation_pipeline, threads, fasta_type, fasta_file, codan_model, alignment_tool, evalue, max_target_seqs, max_hsps, qcov_hsp_perc, other_parameters)
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

    def run_annotation_pipeline(self, process, threads, fasta_type, fasta_file, codan_model, alignment_tool, evalue, max_target_seqs, max_hsps, qcov_hsp_perc, other_parameters):
        '''
        Run a functional annotation pipeline.
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
            current_run_dir = genlib.get_current_run_dir(result_dir, genlib.get_result_run_subdir(), genlib.get_process_run_annotation_pipeline_code())
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
            script_name = f'{genlib.get_process_run_annotation_pipeline_code()}-process.sh'
            process.write(f'Building the process script {script_name} ...\n')
            (OK, _) = self.build_run_annotation_pipeline_script(temp_dir, script_name, current_run_dir, threads, fasta_type, fasta_file, codan_model, alignment_tool, evalue, max_target_seqs, max_hsps, qcov_hsp_perc, other_parameters)
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
            starter_name = f'{genlib.get_process_run_annotation_pipeline_code()}-process-starter.sh'
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

    def build_run_annotation_pipeline_script(self, directory, script_name, current_run_dir, threads, fasta_type, fasta_file, codan_model, alignment_tool, evalue, max_target_seqs, max_hsps, qcov_hsp_perc, other_parameters):
        '''
        Build the script to run a functional annotation pipeline.
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
        acrogymnospermae_blastplus_db_name = self.app_config_dict[f'{genlib.get_app_short_name()} database']['acrogymnospermae_blastplus_db_name']
        acrogymnospermae_blastplus_db_dir = self.app_config_dict[f'{genlib.get_app_short_name()} database']['acrogymnospermae_blastplus_db_dir']
        acrogymnospermae_diamond_db_name = self.app_config_dict[f'{genlib.get_app_short_name()} database']['acrogymnospermae_diamond_db_name']
        acrogymnospermae_diamond_db_dir = self.app_config_dict[f'{genlib.get_app_short_name()} database']['acrogymnospermae_diamond_db_dir']
        lncrna_blastplus_db_name = self.app_config_dict[f'{genlib.get_app_short_name()} database']['lncrna_blastplus_db_name']
        lncrna_blastplus_db_dir = self.app_config_dict[f'{genlib.get_app_short_name()} database']['lncrna_blastplus_db_dir']

        # set the CodAn output directory
        codan_output_dir = f'{current_run_dir}/codan_output'

        # set the parameters file
        params_file = f'./{genlib.get_params_file_name()}'

        # set the temporal directory
        temp_dir = f'{current_run_dir}/temp'

        # set the CSV files with alignments
        blastp_clade_alignment_file = f'{temp_dir}/{genlib.get_blastp_clade_alignment_file_name()}'
        blastx_clade_alignment_file = f'{temp_dir}/{genlib.get_blastx_clade_alignment_file_name()}'
        blastn_lncrna_alignment_file = f'{temp_dir}/{genlib.get_blastn_lncrna_alignment_file_name()}'

        # set the CSV files with the annotations
        complete_functional_annotation_file = f'./{genlib.get_complete_functional_annotation_file_name()}'
        besthit_functional_annotation_file = f'./{genlib.get_besthit_functional_annotation_file_name()}'

        # set the annotation file head
        # -- head = '1i qseqid;sseqid;pident;length;mismatch;gapopen;qstart;qend;sstart;send;evalue;bitscore;algorithm;ncbi_description;ncbi_species;tair10_ortholog_seq_id;interpro_goterms;panther_goterms;metacyc_pathways;reactome_pathways;eggnog_ortholog_seq_id;eggnog_ortholog_species;eggnog_ogs;cog_category;eggnog_description;eggnog_goterms;ec;kegg_kos;kegg_pathways;kegg_modules;kegg_reactions;kegg_rclasses;brite;kegg_tc;cazy;pfams'
        head = '1i qseqid;sseqid;pident;length;mismatch;gapopen;qstart;qend;sstart;send;evalue;bitscore;algorithm;ncbi_description;ncbi_species;tair10_ortholog_seq_id;interpro_goterms;panther_goterms;metacyc_pathways;eggnog_ortholog_seq_id;eggnog_ortholog_species;eggnog_ogs;cog_category;eggnog_description;eggnog_goterms;ec;kegg_kos;kegg_pathways;kegg_modules;kegg_reactions;kegg_rclasses;brite;kegg_tc;cazy;pfams'

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
                file_id.write(f'mkdir -p {temp_dir}\n')
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
                file_id.write('function save_params\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Saving parameters ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/save-parms.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        echo "[Annotation parameters]" > {params_file}\n')
                file_id.write(f'        echo "fasta_type = {fasta_type}" >> {params_file}\n')
                file_id.write(f'        echo "fasta_file = {fasta_file}" >> {params_file}\n')
                file_id.write(f'        echo "codan_model = {codan_model}" >> {params_file}\n')
                file_id.write(f'        echo "alignment_tool = {alignment_tool}" >> {params_file}\n')
                file_id.write(f'        echo "evalue = {evalue}" >> {params_file}\n')
                file_id.write(f'        echo "max_target_seqs = {max_target_seqs}" >> {params_file}\n')
                file_id.write(f'        echo "max_hsps = {max_hsps}" >> {params_file}\n')
                file_id.write(f'        echo "qcov_hsp_perc = {qcov_hsp_perc}" >> {params_file}\n')
                file_id.write(f'        echo "other_parameters = {other_parameters}" >> {params_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error echo $RC; fi\n')
                file_id.write( '        echo "Parameters are saved."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function predict_orfs\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Predicting ORFs and getting peptide sequences ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/predict-orfs.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                if fasta_type ==  genlib.get_fasta_type_transcripts():
                    file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_codan_environment()}\n')
                    file_id.write( '        MODELS_DIR=`echo $CONDA_PREFIX`/models\n')
                    file_id.write( '        /usr/bin/time \\\n')
                    file_id.write( '            codan.py \\\n')
                    file_id.write(f'                --cpu={threads} \\\n')
                    file_id.write(f'                --model=$MODELS_DIR/{codan_model} \\\n')
                    file_id.write(f'                --transcripts={fasta_file} \\\n')
                    file_id.write(f'                --output={codan_output_dir}\n')
                    file_id.write( '        RC=$?\n')
                    file_id.write( '        if [ $RC -ne 0 ]; then manage_error codan.py $RC; fi\n')
                    if codan_model.endswith('_partial'):
                        file_id.write( '        /usr/bin/time \\\n')
                        file_id.write( '            TranslatePartial.py \\\n')
                        file_id.write(f'                {codan_output_dir}/ORF_sequences.fasta \\\n')
                        file_id.write(f'                {codan_output_dir}/PEP_sequences.fa\n')
                        file_id.write( '        RC=$?\n')
                        file_id.write( '        if [ $RC -ne 0 ]; then manage_error TranslatePartial.py $RC; fi\n')
                    file_id.write( '        conda deactivate\n')
                    file_id.write( '        echo "ORFs are predicted and peptide sequences are gotten."\n')
                elif fasta_type ==  genlib.get_fasta_type_proteins():
                    file_id.write( '        echo "This step is not run with a proteins file."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function align_peptides_2_alignment_tool_acrogymnospermae_db\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write(f'    echo "Aligning peptides to the {alignment_tool} Acrogymnospermae database ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/align-peptides-2-alignment-tool-acrogymnospermae-db.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                if fasta_type ==  genlib.get_fasta_type_transcripts():
                    file_id.write(f'        PEPTIDE_FILE={codan_output_dir}/PEP_sequences.fa\n')
                elif fasta_type ==  genlib.get_fasta_type_proteins():
                    file_id.write(f'        PEPTIDE_FILE={fasta_file}\n')
                if alignment_tool == genlib.get_blastplus_name():
                    file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_blastplus_environment()}\n')
                    file_id.write(f'        export BLASTDB={acrogymnospermae_blastplus_db_dir}\n')
                    file_id.write( '        /usr/bin/time \\\n')
                    file_id.write( '            blastp \\\n')
                    file_id.write(f'                -num_threads {threads} \\\n')
                    file_id.write(f'                -db {acrogymnospermae_blastplus_db_name} \\\n')
                    file_id.write( '                -query $PEPTIDE_FILE \\\n')
                    file_id.write(f'                -evalue {evalue} \\\n')
                    file_id.write(f'                -max_target_seqs {max_target_seqs} \\\n')
                    file_id.write(f'                -max_hsps {max_hsps} \\\n')
                    file_id.write(f'                -qcov_hsp_perc {qcov_hsp_perc} \\\n')
                    file_id.write( '                -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \\\n')
                    if other_parameters.upper() != 'NONE':
                        parameter_list = [x.strip() for x in other_parameters.split(';')]
                        for parameter in parameter_list:
                            if parameter.find('=') > 0:
                                pattern = r'^--(.+)=(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                                parameter_value = mo.group(2).strip()
                                file_id.write(f'                -{parameter_name} {parameter_value} \\\n')
                            else:
                                pattern = r'^--(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                                file_id.write(f'                -{parameter_name} \\\n')
                    file_id.write(f'                -out {blastp_clade_alignment_file}\n')
                    file_id.write( '        RC=$?\n')
                    file_id.write( '        if [ $RC -ne 0 ]; then manage_error blastp $RC; fi\n')
                    file_id.write( '        conda deactivate\n')
                elif alignment_tool == genlib.get_diamond_name():
                    file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_diamond_environment()}\n')
                    file_id.write( '        /usr/bin/time \\\n')
                    file_id.write( '            diamond blastp \\\n')
                    file_id.write(f'                --threads {threads} \\\n')
                    file_id.write(f'                --db {acrogymnospermae_diamond_db_dir}/{acrogymnospermae_diamond_db_name} \\\n')
                    file_id.write( '                --query $PEPTIDE_FILE \\\n')
                    file_id.write(f'                --evalue {evalue} \\\n')
                    file_id.write(f'                --max-target-seqs {max_target_seqs} \\\n')
                    file_id.write(f'                --max-hsps {max_hsps} \\\n')
                    file_id.write( '                --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \\\n')
                    if other_parameters.upper() != 'NONE':
                        parameter_list = [x.strip() for x in other_parameters.split(';')]
                        for parameter in parameter_list:
                            if parameter.find('=') > 0:
                                pattern = r'^--(.+)=(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                                parameter_value = mo.group(2).strip()
                                file_id.write(f'                --{parameter_name} {parameter_value} \\\n')
                            else:
                                pattern = r'^--(.+)$'
                                mo = re.search(pattern, parameter)
                                parameter_name = mo.group(1).strip()
                                file_id.write(f'                --{parameter_name} \\\n')
                    file_id.write(f'                --out {blastp_clade_alignment_file}\n')
                    file_id.write( '        RC=$?\n')
                    file_id.write( '        if [ $RC -ne 0 ]; then manage_error diamond-blastp $RC; fi\n')
                    file_id.write( '        conda deactivate\n')
                file_id.write( '        echo "Alignment is done."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function align_transcriptome_2_alignment_tool_acrogymnospermae_db\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write(f'    echo "Aligning transcriptome to the {alignment_tool} Acrogymnospermae database ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/align-transcriptome-2-alignment-tool-acrogymnospermae-db.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                if fasta_type ==  genlib.get_fasta_type_transcripts():
                    if alignment_tool == genlib.get_blastplus_name():
                        file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_blastplus_environment()}\n')
                        file_id.write(f'        export BLASTDB={acrogymnospermae_blastplus_db_dir}\n')
                        file_id.write( '        /usr/bin/time \\\n')
                        file_id.write( '            blastx \\\n')
                        file_id.write(f'                -num_threads {threads} \\\n')
                        file_id.write(f'                -db {acrogymnospermae_blastplus_db_name} \\\n')
                        file_id.write(f'                -query {fasta_file} \\\n')
                        file_id.write(f'                -evalue {evalue} \\\n')
                        file_id.write(f'                -max_target_seqs {max_target_seqs} \\\n')
                        file_id.write(f'                -max_hsps {max_hsps} \\\n')
                        file_id.write(f'                -qcov_hsp_perc {qcov_hsp_perc} \\\n')
                        file_id.write( '                -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \\\n')
                        if other_parameters.upper() != 'NONE':
                            parameter_list = [x.strip() for x in other_parameters.split(';')]
                            for parameter in parameter_list:
                                if parameter.find('=') > 0:
                                    pattern = r'^--(.+)=(.+)$'
                                    mo = re.search(pattern, parameter)
                                    parameter_name = mo.group(1).strip()
                                    parameter_value = mo.group(2).strip()
                                    file_id.write(f'                -{parameter_name} {parameter_value} \\\n')
                                else:
                                    pattern = r'^--(.+)$'
                                    mo = re.search(pattern, parameter)
                                    parameter_name = mo.group(1).strip()
                                    file_id.write(f'                -{parameter_name} \\\n')
                        file_id.write(f'                -out {blastx_clade_alignment_file}\n')
                        file_id.write( '        RC=$?\n')
                        file_id.write( '        if [ $RC -ne 0 ]; then manage_error blastx $RC; fi\n')
                        file_id.write( '        conda deactivate\n')
                    elif alignment_tool == genlib.get_diamond_name():
                        file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_diamond_environment()}\n')
                        file_id.write( '        /usr/bin/time \\\n')
                        file_id.write( '            diamond blastx \\\n')
                        file_id.write(f'                --threads {threads} \\\n')
                        file_id.write(f'                --db {acrogymnospermae_diamond_db_dir}/{acrogymnospermae_diamond_db_name} \\\n')
                        file_id.write(f'                --query {fasta_file} \\\n')
                        file_id.write(f'                --evalue {evalue} \\\n')
                        file_id.write(f'                --max-target-seqs {max_target_seqs} \\\n')
                        file_id.write(f'                --max-hsps {max_hsps} \\\n')
                        file_id.write( '                --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \\\n')
                        if other_parameters.upper() != 'NONE':
                            parameter_list = [x.strip() for x in other_parameters.split(';')]
                            for parameter in parameter_list:
                                if parameter.find('=') > 0:
                                    pattern = r'^--(.+)=(.+)$'
                                    mo = re.search(pattern, parameter)
                                    parameter_name = mo.group(1).strip()
                                    parameter_value = mo.group(2).strip()
                                    file_id.write(f'                --{parameter_name} {parameter_value} \\\n')
                                else:
                                    pattern = r'^--(.+)$'
                                    mo = re.search(pattern, parameter)
                                    parameter_name = mo.group(1).strip()
                                    file_id.write(f'                --{parameter_name} \\\n')
                        file_id.write(f'                --out {blastx_clade_alignment_file}\n')
                        file_id.write( '        RC=$?\n')
                        file_id.write( '        if [ $RC -ne 0 ]; then manage_error diamond-blastx $RC; fi\n')
                        file_id.write( '        conda deactivate\n')
                    file_id.write( '        echo "Alignment is done."\n')
                elif fasta_type ==  genlib.get_fasta_type_proteins():
                    file_id.write(f'        touch {blastx_clade_alignment_file}\n')
                    file_id.write( '        echo "This step is not run with a proteins file."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function align_transcriptome_2_blastplus_lncrna_db\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Aligning transcriptome to the BLAST+ lncRNA database ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/align-transcriptome-2-blastplus-lncRNA-db.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                if fasta_type ==  genlib.get_fasta_type_transcripts():
                    file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_blastplus_environment()}\n')
                    file_id.write(f'        export BLASTDB={lncrna_blastplus_db_dir}\n')
                    file_id.write( '        /usr/bin/time \\\n')
                    file_id.write( '            blastn \\\n')
                    file_id.write(f'                -num_threads {threads} \\\n')
                    file_id.write(f'                -db {lncrna_blastplus_db_name} \\\n')
                    file_id.write(f'                -query {fasta_file} \\\n')
                    file_id.write( '                -evalue 1E-3 \\\n')
                    file_id.write( '                -max_target_seqs 1 \\\n')
                    file_id.write( '                -max_hsps 1 \\\n')
                    file_id.write( '                -qcov_hsp_perc 0.0 \\\n')
                    file_id.write( '                -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \\\n')
                    file_id.write(f'                -out {blastn_lncrna_alignment_file}\n')
                    file_id.write( '        RC=$?\n')
                    file_id.write( '        if [ $RC -ne 0 ]; then manage_error blastn $RC; fi\n')
                    file_id.write( '        conda deactivate\n')
                    file_id.write( '        echo "Alignment is done."\n')
                elif fasta_type ==  genlib.get_fasta_type_proteins():
                    file_id.write(f'        touch {blastn_lncrna_alignment_file}\n')
                    file_id.write( '        echo "This step is not run with a proteins file."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function concat_functional_annotations\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Concatenating functional annotation to alignment file ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/concat-functional-annotations.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_gymnotoa_env_code()}\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write(f'            {app_dir}/concat-functional-annotations.py \\\n')
                file_id.write(f'                --db={app_db_path} \\\n')
                file_id.write(f'                --blastp-alignments={blastp_clade_alignment_file} \\\n')
                file_id.write(f'                --blastx-alignments={blastx_clade_alignment_file} \\\n')
                file_id.write(f'                --blastn-alignments={blastn_lncrna_alignment_file} \\\n')
                file_id.write(f'                --complete_annotations={complete_functional_annotation_file} \\\n')
                file_id.write(f'                --besthit_annotations={besthit_functional_annotation_file} \\\n')
                file_id.write( '                --verbose=N \\\n')
                file_id.write( '                --trace=N\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error concat-functional-annotations.py $RC; fi\n')
                file_id.write( '        conda deactivate\n')
                file_id.write( '        echo "Data are loaded."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function sort_functional_annotations\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Sorting functional annotations files ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/sort-annotations.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write( '            sort \\\n')
                file_id.write(f'                --output={complete_functional_annotation_file} \\\n')
                file_id.write(f'                {complete_functional_annotation_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error sort $RC; fi\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write( '            sort \\\n')
                file_id.write(f'                --output={besthit_functional_annotation_file} \\\n')
                file_id.write(f'                {besthit_functional_annotation_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error sort $RC; fi\n')
                file_id.write( '        echo "Files are sorted."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function add_heads\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Adding head to annotations files ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/add-head.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write( '            sed \\\n')
                file_id.write( '                --in-place \\\n')
                file_id.write(f'                "{head}" \\\n')
                file_id.write(f'                {complete_functional_annotation_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error sed $RC; fi\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write( '            sed \\\n')
                file_id.write( '                --in-place \\\n')
                file_id.write(f'                "{head}" \\\n')
                file_id.write(f'                {besthit_functional_annotation_file}\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error sed $RC; fi\n')
                file_id.write( '        echo "Heads are added."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function calculate_functional_annotation_stats\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Calculating functional annotation statistics ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/calculate-functional-annotation-stats.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_gymnotoa_env_code()}\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write(f'            {app_dir}/calculate-functional-annotation-stats.py \\\n')
                file_id.write(f'                --db={app_db_path} \\\n')
                file_id.write(f'                --annotations={complete_functional_annotation_file} \\\n')
                file_id.write(f'                --outdir={current_run_dir} \\\n')
                file_id.write( '                --verbose=N \\\n')
                file_id.write( '                --trace=N\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error calculate-functional-annotation-stats.py $RC; fi\n')
                file_id.write( '        conda deactivate\n')
                file_id.write( '        echo "Statistics are calculated."\n')
                file_id.write( '        touch $STEP_STATUS\n')
                file_id.write( '    fi\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write('function build_external_inputs\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Building inputs to external applications ..."\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    STEP_STATUS=$STATUS_DIR/build-external-inputs.ok\n')
                file_id.write( '    if [ -f $STEP_STATUS ]; then\n')
                file_id.write( '        echo "This step was previously run."\n')
                file_id.write( '    else\n')
                file_id.write(f'        source {miniforge3_bin_dir}/activate {genlib.get_gymnotoa_env_code()}\n')
                file_id.write( '        /usr/bin/time \\\n')
                file_id.write(f'            {app_dir}/build-external-inputs.py \\\n')
                file_id.write(f'                --annotations={complete_functional_annotation_file} \\\n')
                file_id.write(f'                --outdir={current_run_dir} \\\n')
                file_id.write( '                --verbose=N \\\n')
                file_id.write( '                --trace=N\n')
                file_id.write( '        RC=$?\n')
                file_id.write( '        if [ $RC -ne 0 ]; then manage_error build-external-inputs.py $RC; fi\n')
                file_id.write( '        conda deactivate\n')
                file_id.write( '        echo "Inputs are built."\n')
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
                file_id.write( 'save_params\n')
                file_id.write( 'predict_orfs\n')
                file_id.write( 'align_peptides_2_alignment_tool_acrogymnospermae_db\n')
                file_id.write( 'align_transcriptome_2_alignment_tool_acrogymnospermae_db\n')
                file_id.write( 'align_transcriptome_2_blastplus_lncrna_db\n')
                file_id.write( 'concat_functional_annotations\n')
                file_id.write( 'sort_functional_annotations\n')
                file_id.write( 'add_heads\n')
                file_id.write( 'calculate_functional_annotation_stats\n')
                file_id.write( 'build_external_inputs\n')
                file_id.write( 'end\n')
        except Exception as e:
            error_list.append(f'*** EXCEPTION: "{e}".')
            error_list.append(f'*** ERROR: The file {script_path} is not created.')
            OK = False

        # return the control variable and error list
        return (OK, error_list)

    #---------------

#-------------------------------------------------------------------------------

class FormRestartAnnotationPipeline(QWidget):
    '''
    Class used to restart a functional annotation pipeline.
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
        self.head = 'Restart an annotation pipeline'
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

        # create and configure "lineedit_fasta_file"
        self.lineedit_fasta_file = QLineEdit()
        self.lineedit_fasta_file.editingFinished.connect(self.check_inputs)
        self.lineedit_fasta_file.setDisabled(True)

        # create and configure "label_codan_model"
        label_codan_model = QLabel()
        label_codan_model.setText('CodAn model')
        label_codan_model.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_codan_model"
        self.lineedit_codan_model = QLineEdit()
        self.lineedit_codan_model.setFixedWidth(fontmetrics.width('9'*12))
        self.lineedit_codan_model.editingFinished.connect(self.check_inputs)
        self.lineedit_codan_model.setDisabled(True)

        # create and configure "label_alignment_tool"
        label_alignment_tool = QLabel()
        label_alignment_tool.setText('Alignment tool')
        label_alignment_tool.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_alignment_tool"
        self.lineedit_alignment_tool = QLineEdit()
        self.lineedit_alignment_tool.setFixedWidth(fontmetrics.width('9'*12))
        self.lineedit_alignment_tool.editingFinished.connect(self.check_inputs)
        self.lineedit_alignment_tool.setDisabled(True)

        # create and configure "evalue"
        label_evalue = QLabel()
        label_evalue.setText('evalue')
        label_evalue.setFixedWidth(fontmetrics.width('9'*12))

        # create and configure "lineedit_evalue"
        self.lineedit_evalue  = QLineEdit()
        self.lineedit_evalue.setFixedWidth(fontmetrics.width('9'*10))
        self.lineedit_evalue.editingFinished.connect(self.check_inputs)
        self.lineedit_evalue.setDisabled(True)

        # create and configure "label_max_target_seqs"
        label_max_target_seqs = QLabel()
        label_max_target_seqs.setText('max_target_seqs')
        label_max_target_seqs.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_max_target_seqs"
        self.lineedit_max_target_seqs  = QLineEdit()
        self.lineedit_max_target_seqs.setFixedWidth(fontmetrics.width('9'*4))
        self.lineedit_max_target_seqs.editingFinished.connect(self.check_inputs)
        self.lineedit_max_target_seqs.setDisabled(True)

        # create and configure "label_max_hsps"
        label_max_hsps = QLabel()
        label_max_hsps.setText('max_hsps')
        label_max_hsps.setFixedWidth(fontmetrics.width('9'*9))

        # create and configure "lineedit_max_hsps"
        self.lineedit_max_hsps  = QLineEdit()
        self.lineedit_max_hsps.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_max_hsps.editingFinished.connect(self.check_inputs)
        self.lineedit_max_hsps.setDisabled(True)

        # create and configure "label_qcov_hsp_perc"
        label_qcov_hsp_perc = QLabel()
        label_qcov_hsp_perc.setText('qcov_hsp_perc')
        label_qcov_hsp_perc.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_qcov_hsp_perc"
        self.lineedit_qcov_hsp_perc = QLineEdit()
        self.lineedit_qcov_hsp_perc.setFixedWidth(fontmetrics.width('9'*6))
        self.lineedit_qcov_hsp_perc.editingFinished.connect(self.check_inputs)
        self.lineedit_qcov_hsp_perc.setDisabled(True)

        # create and configure "label_other_parameters"
        label_other_parameters = QLabel()
        label_other_parameters.setText('Other params')
        label_other_parameters.setFixedWidth(fontmetrics.width('9'*12))

        # create and configure "lineedit_other_parameters"
        self.lineedit_other_parameters = QLineEdit()
        self.lineedit_other_parameters.setFixedWidth(fontmetrics.width('9'*52))
        self.lineedit_other_parameters.editingFinished.connect(self.check_inputs)
        self.lineedit_other_parameters.setDisabled(True)

        # create and configure "empty"
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
        gridlayout_data.setColumnStretch(8, 1)
        gridlayout_data.setColumnStretch(9, 1)
        gridlayout_data.setColumnStretch(10, 1)
        gridlayout_data.addWidget(self.tablewidget, 0, 0, 1, 11)
        gridlayout_data.addWidget(label_fasta_file, 1, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fasta_file, 1, 1, 1, 7)
        gridlayout_data.addWidget(label_empty, 1, 8, 1, 1)
        gridlayout_data.addWidget(label_codan_model, 1, 9, 1, 1)
        gridlayout_data.addWidget(self.lineedit_codan_model, 1, 10, 1, 1)
        gridlayout_data.addWidget(label_alignment_tool, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_alignment_tool, 2, 1, 1, 1)
        gridlayout_data.addWidget(label_empty, 2, 2, 1, 1)
        gridlayout_data.addWidget(label_evalue, 2, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_evalue, 2, 4, 1, 1)
        gridlayout_data.addWidget(label_empty, 2, 5, 1, 1)
        gridlayout_data.addWidget(label_max_target_seqs, 2, 6, 1, 1)
        gridlayout_data.addWidget(self.lineedit_max_target_seqs, 2, 7, 1, 1)
        gridlayout_data.addWidget(label_empty, 2, 8, 1, 1)
        gridlayout_data.addWidget(label_max_hsps, 2, 9, 1, 1)
        gridlayout_data.addWidget(self.lineedit_max_hsps, 2, 10, 1, 1)
        gridlayout_data.addWidget(label_qcov_hsp_perc, 3, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_qcov_hsp_perc, 3, 1, 1, 1)
        gridlayout_data.addWidget(label_empty, 3, 2, 1, 1)
        gridlayout_data.addWidget(label_other_parameters, 3, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_other_parameters, 3, 4, 1, 1)

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

        # initialize "lineedit_fasta_file"
        self.lineedit_fasta_file.setText('')

        # initialize "lineedit_codan_model"
        self.lineedit_codan_model.setText('')

        # initialize "lineedit_alignment_tool"
        self.lineedit_alignment_tool.setText('')

        # initialize "lineedit_evalue"
        self.lineedit_evalue.setText('')

        # initialize "lineedit_max_target_seqs"
        self.lineedit_max_target_seqs.setText('')

        # initialize "lineedit_max_hsps"
        self.lineedit_max_hsps.setText('')

        # initialize "lineedit_qcov_hsp_perc"
        self.lineedit_qcov_hsp_perc.setText('')

        # initialize "lineedit_other_parameters"
        self.lineedit_other_parameters.setText('')

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

        # check "lineedit_codan_model" when the editing finished
        if not self.lineedit_codan_model_editing_finished():
            OK = False

        # check "lineedit_alignment_tool" when the editing finished
        if not self.lineedit_alignment_tool_editing_finished():
            OK = False

        # check "lineedit_evalue" when the editing finished
        if not self.lineedit_evalue_editing_finished():
            OK = False

        # check "lineedit_max_target_seqs" when the editing finished
        if not self.lineedit_max_target_seqs_editing_finished():
            OK = False

        # check "lineedit_max_hsps" when the editing finished
        if not self.lineedit_max_hsps_editing_finished():
            OK = False

        # check "lineedit_qcov_hsp_perc" when the editing finished
        if not self.lineedit_qcov_hsp_perc_editing_finished():
            OK = False

        # check "lineedit_other_parameters" when the editing finished
        if not self.lineedit_other_parameters_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('There are one or more inputs without data or with wrong value.')

        # enable "pushbutton_execute"
        if OK and len(row_list) == 1 and self.lineedit_fasta_file.text() != '' and self.lineedit_codan_model.text() != '' and self.lineedit_alignment_tool.text() != '' and self.lineedit_evalue.text() != '' and self.lineedit_max_target_seqs.text() != '' and self.lineedit_max_hsps.text() != '' and self.lineedit_qcov_hsp_perc.text() != '' and self.lineedit_other_parameters.text() != '':
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

            # get the dictionary of application configuration
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset corresponding to the row clicked
            result_dataset = self.tablewidget.item(row, 1).text()

            # get the parameters file corresponding to the result dataset
            params_file = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset}{os.sep}{genlib.get_params_file_name()}'
            if sys.platform.startswith('win32'):
                params_file = genlib.wsl_path_2_windows_path(params_file)

            # get the dictionary of parameters
            params_dict = genlib.get_config_dict(params_file)

            # set the FASTA file path in "lineedit_fasta_file"
            fasta_file = params_dict['Annotation parameters']['fasta_file']
            if sys.platform.startswith('win32'):
                fasta_file = genlib.wsl_path_2_windows_path(fasta_file)
            self.lineedit_fasta_file.setText(fasta_file)

            # set the CodAn model in "lineedit_codan_model"
            self.lineedit_codan_model.setText(params_dict['Annotation parameters']['codan_model'])

            # set the alignment tool in "lineedit_alignment_tool"
            self.lineedit_alignment_tool.setText(params_dict['Annotation parameters']['alignment_tool'])

            # set the evalue in "lineedit_evalue"
            self.lineedit_evalue.setText(params_dict['Annotation parameters']['evalue'])

            # set the max_target_seqs in "lineedit_max_target_seqs"
            self.lineedit_max_target_seqs.setText(params_dict['Annotation parameters']['max_target_seqs'])

            # set the max_hsps in "lineedit_max_hsps"
            self.lineedit_max_hsps.setText(params_dict['Annotation parameters']['max_hsps'])

            # set the qcov_hsp_perc in "lineedit_qcov_hsp_perc"
            self.lineedit_qcov_hsp_perc.setText(params_dict['Annotation parameters']['qcov_hsp_perc'])

            # set other parameters in "lineedit_other_parameters"
            self.lineedit_other_parameters.setText(params_dict['Annotation parameters']['other_parameters'])

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

    def lineedit_codan_model_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_codan_model"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_alignment_tool_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_alignment_tool"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_evalue_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_evalue"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_max_target_seqs_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_max_target_seqs"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_max_hsps_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_max_hsps"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_qcov_hsp_perc_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_qcov_hsp_perc"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_other_parameters_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_other_parameters"
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
            text = 'The functional annotation pipeline is going to be restarted.\n\nAre you sure to continue?'
            botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
            if botton == QMessageBox.No:
                OK = False

        # execute the process
        if OK:

            # get the result dataset
            result_dataset = self.tablewidget.item(row_list[0], 1).text()

            # create and execute "DialogProcess"
            process = dialogs.DialogProcess(self, self.head, self.restart_annotation_pipeline, result_dataset)
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

                # insert data in the dictionary when the the status is wrong
                if status == 'wrong':
                    key = f'{process_name}-{result_dataset_id}'
                    result_dataset_dict[key] = {'process': process_name, 'result_dataset_id': result_dataset_id, 'date': date, 'time': time, 'status': status}

        # initialize "tablewidget"
        self.tablewidget.clearContents()

        # set the rows number of "tablewidget"
        self.tablewidget.setRowCount(len(result_dataset_dict))

        # load data in "tablewidget" for the OK result datasets of annotation pipeline
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

    def restart_annotation_pipeline(self, process, result_dataset):
        '''
        Restart a functioanl annotation pipeline.
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
            current_run_dir = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset}'
            process.write(f'The directory path is {current_run_dir}.\n')

        # set the starter script name
        if OK:
            starter_name = f'{genlib.get_process_run_annotation_pipeline_code()}-process-starter.sh'

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

class FormBrowseAnnotationResults(QWidget):
    '''
    Class used to browse results of a annotation pipeline.
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
        self.head = 'Browse results of an annotation pipeline'
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

        # create and configure "label_fasta_file"
        label_fasta_file = QLabel()
        label_fasta_file.setText('FASTA file')
        label_fasta_file.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_fasta_file"
        self.lineedit_fasta_file = QLineEdit()
        self.lineedit_fasta_file.editingFinished.connect(self.check_inputs)
        self.lineedit_fasta_file.setDisabled(True)

        # create and configure "label_codan_model"
        label_codan_model = QLabel()
        label_codan_model.setText('CodAn model')
        label_codan_model.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_codan_model"
        self.lineedit_codan_model = QLineEdit()
        self.lineedit_codan_model.setFixedWidth(fontmetrics.width('9'*12))
        self.lineedit_codan_model.editingFinished.connect(self.check_inputs)
        self.lineedit_codan_model.setDisabled(True)

        # create and configure "label_alignment_tool"
        label_alignment_tool = QLabel()
        label_alignment_tool.setText('Alignment tool')
        label_alignment_tool.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_alignment_tool"
        self.lineedit_alignment_tool = QLineEdit()
        self.lineedit_alignment_tool.setFixedWidth(fontmetrics.width('9'*12))
        self.lineedit_alignment_tool.editingFinished.connect(self.check_inputs)
        self.lineedit_alignment_tool.setDisabled(True)

        # create and configure "evalue"
        label_evalue = QLabel()
        label_evalue.setText('evalue')
        label_evalue.setFixedWidth(fontmetrics.width('9'*12))

        # create and configure "lineedit_evalue"
        self.lineedit_evalue  = QLineEdit()
        self.lineedit_evalue.setFixedWidth(fontmetrics.width('9'*10))
        self.lineedit_evalue.editingFinished.connect(self.check_inputs)
        self.lineedit_evalue.setDisabled(True)

        # create and configure "label_max_target_seqs"
        label_max_target_seqs = QLabel()
        label_max_target_seqs.setText('max_target_seqs')
        label_max_target_seqs.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_max_target_seqs"
        self.lineedit_max_target_seqs  = QLineEdit()
        self.lineedit_max_target_seqs.setFixedWidth(fontmetrics.width('9'*4))
        self.lineedit_max_target_seqs.editingFinished.connect(self.check_inputs)
        self.lineedit_max_target_seqs.setDisabled(True)

        # create and configure "label_max_hsps"
        label_max_hsps = QLabel()
        label_max_hsps.setText('max_hsps')
        label_max_hsps.setFixedWidth(fontmetrics.width('9'*9))

        # create and configure "lineedit_max_hsps"
        self.lineedit_max_hsps  = QLineEdit()
        self.lineedit_max_hsps.setFixedWidth(fontmetrics.width('9'*8))
        self.lineedit_max_hsps.editingFinished.connect(self.check_inputs)
        self.lineedit_max_hsps.setDisabled(True)

        # create and configure "label_qcov_hsp_perc"
        label_qcov_hsp_perc = QLabel()
        label_qcov_hsp_perc.setText('qcov_hsp_perc')
        label_qcov_hsp_perc.setFixedWidth(fontmetrics.width('9'*18))

        # create and configure "lineedit_qcov_hsp_perc"
        self.lineedit_qcov_hsp_perc = QLineEdit()
        self.lineedit_qcov_hsp_perc.setFixedWidth(fontmetrics.width('9'*6))
        self.lineedit_qcov_hsp_perc.editingFinished.connect(self.check_inputs)
        self.lineedit_qcov_hsp_perc.setDisabled(True)

        # create and configure "label_other_parameters"
        label_other_parameters = QLabel()
        label_other_parameters.setText('Other params')
        label_other_parameters.setFixedWidth(fontmetrics.width('9'*12))

        # create and configure "lineedit_other_parameters"
        self.lineedit_other_parameters = QLineEdit()
        self.lineedit_other_parameters.setFixedWidth(fontmetrics.width('9'*52))
        self.lineedit_other_parameters.editingFinished.connect(self.check_inputs)
        self.lineedit_other_parameters.setDisabled(True)

        # create and configure "empty"
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
        gridlayout_data.setColumnStretch(8, 1)
        gridlayout_data.setColumnStretch(9, 1)
        gridlayout_data.setColumnStretch(10, 1)
        gridlayout_data.addWidget(label_annotation_result_type, 0, 0, 1, 1)
        gridlayout_data.addWidget(self.combobox_annotation_result_type, 0, 1, 1, 1, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(self.tablewidget, 1, 0, 1, 11)
        gridlayout_data.addWidget(label_fasta_file, 2, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_fasta_file, 2, 1, 1, 7)
        gridlayout_data.addWidget(label_empty, 2, 8, 1, 1)
        gridlayout_data.addWidget(label_codan_model, 2, 9, 1, 1)
        gridlayout_data.addWidget(self.lineedit_codan_model, 2, 10, 1, 1)
        gridlayout_data.addWidget(label_alignment_tool, 3, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_alignment_tool, 3, 1, 1, 1)
        gridlayout_data.addWidget(label_evalue, 3, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_evalue, 3, 4, 1, 1)
        gridlayout_data.addWidget(label_empty, 3, 5, 1, 1)
        gridlayout_data.addWidget(label_max_target_seqs, 3, 6, 1, 1)
        gridlayout_data.addWidget(self.lineedit_max_target_seqs, 3, 7, 1, 1)
        gridlayout_data.addWidget(label_empty, 3, 8, 1, 1)
        gridlayout_data.addWidget(label_max_hsps, 3, 9, 1, 1)
        gridlayout_data.addWidget(self.lineedit_max_hsps, 3, 10, 1, 1)
        gridlayout_data.addWidget(label_qcov_hsp_perc, 4, 0, 1, 1)
        gridlayout_data.addWidget(self.lineedit_qcov_hsp_perc, 4, 1, 1, 1)
        gridlayout_data.addWidget(label_empty, 4, 2, 1, 1)
        gridlayout_data.addWidget(label_other_parameters, 4, 3, 1, 1)
        gridlayout_data.addWidget(self.lineedit_other_parameters, 4, 4, 1, 1)

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

        # initialize "lineedit_fasta_file"
        self.lineedit_fasta_file.setText('')

        # initialize "lineedit_codan_model"
        self.lineedit_codan_model.setText('')

        # initialize "lineedit_alignment_tool"
        self.lineedit_alignment_tool.setText('')

        # initialize "lineedit_evalue"
        self.lineedit_evalue.setText('')

        # initialize "lineedit_max_target_seqs"
        self.lineedit_max_target_seqs.setText('')

        # initialize "lineedit_max_hsps"
        self.lineedit_max_hsps.setText('')

        # initialize "lineedit_qcov_hsp_perc"
        self.lineedit_qcov_hsp_perc.setText('')

        # initialize "lineedit_other_parameters"
        self.lineedit_other_parameters.setText('')

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

        # check "lineedit_codan_model" when the editing finished
        if not self.lineedit_codan_model_editing_finished():
            OK = False

        # check "lineedit_alignment_tool" when the editing finished
        if not self.lineedit_alignment_tool_editing_finished():
            OK = False

        # check "lineedit_evalue" when the editing finished
        if not self.lineedit_evalue_editing_finished():
            OK = False

        # check "lineedit_max_target_seqs" when the editing finished
        if not self.lineedit_max_target_seqs_editing_finished():
            OK = False

        # check "lineedit_max_hsps" when the editing finished
        if not self.lineedit_max_hsps_editing_finished():
            OK = False

        # check "lineedit_qcov_hsp_perc" when the editing finished
        if not self.lineedit_qcov_hsp_perc_editing_finished():
            OK = False

        # check "lineedit_other_parameters" when the editing finished
        if not self.lineedit_other_parameters_editing_finished():
            OK = False

        # check all inputs are OK
        if OK:
            self.parent.statusBar().showMessage('')
        else:
            self.parent.statusBar().showMessage('There are one or more inputs without data or with wrong value.')

        # enable "pushbutton_execute"
        if OK and self.combobox_annotation_result_type.currentText() != '' and len(row_list) == 1 and self.lineedit_fasta_file.text() != '' and self.lineedit_codan_model.text() != '' and self.lineedit_alignment_tool.text() != '' and self.lineedit_evalue.text() != '' and self.lineedit_max_target_seqs.text() != '' and self.lineedit_max_hsps.text() != '' and self.lineedit_qcov_hsp_perc.text() != '' and self.lineedit_other_parameters.text() != '':
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

            # get the dictionary of application configuration
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the result dataset corresponding to the row clicked
            result_dataset = self.tablewidget.item(row, 1).text()

            # get the parameters file corresponding to the result dataset
            params_file = f'{result_dir}{os.sep}{genlib.get_result_run_subdir()}{os.sep}{result_dataset}{os.sep}{genlib.get_params_file_name()}'
            if sys.platform.startswith('win32'):
                params_file = genlib.wsl_path_2_windows_path(params_file)

            # get the dictionary of parameters
            params_dict = genlib.get_config_dict(params_file)

            # set the FASTA file path in "lineedit_fasta_file"
            fasta_file = params_dict['Annotation parameters']['fasta_file']
            if sys.platform.startswith('win32'):
                fasta_file = genlib.wsl_path_2_windows_path(fasta_file)
            self.lineedit_fasta_file.setText(fasta_file)

            # set the CodAn model in "lineedit_codan_model"
            self.lineedit_codan_model.setText(params_dict['Annotation parameters']['codan_model'])

            # set the alignment tool in "lineedit_alignment_tool"
            self.lineedit_alignment_tool.setText(params_dict['Annotation parameters']['alignment_tool'])

            # set the evalue in "lineedit_evalue"
            self.lineedit_evalue.setText(params_dict['Annotation parameters']['evalue'])

            # set the max_target_seqs in "lineedit_max_target_seqs"
            self.lineedit_max_target_seqs.setText(params_dict['Annotation parameters']['max_target_seqs'])

            # set the max_hsps in "lineedit_max_hsps"
            self.lineedit_max_hsps.setText(params_dict['Annotation parameters']['max_hsps'])

            # set the qcov_hsp_perc in "lineedit_qcov_hsp_perc"
            self.lineedit_qcov_hsp_perc.setText(params_dict['Annotation parameters']['qcov_hsp_perc'])

            # set other parameters in "lineedit_other_parameters"
            self.lineedit_other_parameters.setText(params_dict['Annotation parameters']['other_parameters'])

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

    def lineedit_codan_model_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_codan_model"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_alignment_tool_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_alignment_tool"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_evalue_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_evalue"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_max_target_seqs_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_max_target_seqs"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_max_hsps_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_max_hsps"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_qcov_hsp_perc_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_qcov_hsp_perc"
        '''

        # initialize the control variable
        OK = True

        # return the control variable
        return OK

    #---------------

    def lineedit_other_parameters_editing_finished(self):
        '''
        Perform necessary actions after finishing editing "lineedit_other_parameters"
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
            text = 'The results of the functional annotation is going to be browsed.\n\nAre you sure to continue?'
            botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
            if botton == QMessageBox.No:
                OK = False

        # execute the process
        if OK:

            # set the process type
            process_type = genlib.get_result_run_subdir()

            # get the result directory
            result_dir = self.app_config_dict['Environment parameters']['result_dir']

            # get the identification of the annotation pipeline dataset
            result_dataset_id = self.tablewidget.item(row_list[0], 1).text()

            # get the annotation result type
            annotation_result_type = self.annotation_result_type_code_list[self.annotation_result_type_text_list.index(self.combobox_annotation_result_type.currentText())]

            # get the file path of the functional annotation
            if annotation_result_type == 'best':
                functional_annotation_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_besthit_functional_annotation_file_name()}'
            elif annotation_result_type == 'complete':
                functional_annotation_file_path = f'{result_dir}{os.sep}{process_type}{os.sep}{result_dataset_id}{os.sep}{genlib.get_complete_functional_annotation_file_name()}'
            if sys.platform.startswith('win32'):
                functional_annotation_file_path = genlib.wsl_path_2_windows_path(functional_annotation_file_path)

            # get functional annotation data
            QApplication.setOverrideCursor(Qt.WaitCursor)
            (functional_annotation_dict, data_list, data_dict, window_height, window_width, explanatory_text) = self.get_functional_annotation_data(functional_annotation_file_path)
            QGuiApplication.restoreOverrideCursor()

            # show functional annotation data
            head = f'Functional annotation file {functional_annotation_file_path}'
            data_table = dialogs.DialogDataTable(self, head, window_height, window_width, data_list, data_dict, functional_annotation_dict, functional_annotation_dict.keys(), explanatory_text, 'browse-functional-annotation')
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

        # set the rows number of "tableswdget"
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

    @staticmethod
    def get_functional_annotation_data(functional_annotation_file):
        '''
        Get functional annotation data.
        '''

        # initialize the functional annotation dictionary
        functional_annotation_dict = {}

        # open the functional annotation file
        if functional_annotation_file.endswith('.gz'):
            try:
                functional_annotation_file_id = gzip.open(functional_annotation_file, mode='rt', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F002', functional_annotation_file)
        else:
            try:
                functional_annotation_file_id = open(functional_annotation_file, mode='r', encoding='iso-8859-1', newline='\n')
            except Exception as e:
                raise genlib.ProgramException(e, 'F001', functional_annotation_file)

        # initialize the annotation counter
        annotation_counter = 0

        # read the first record of the functional annotation file (header)
        (record, key, data_dict) = genlib.read_functional_annotation_record(functional_annotation_file, functional_annotation_file_id, annotation_counter)

        # read the secord record of the functional annotation file (first data record)
        (record, key, data_dict) = genlib.read_functional_annotation_record(functional_annotation_file, functional_annotation_file_id, annotation_counter)
        genlib.Message.print('trace', f'key: {key} - record: {record}')

        # while there are records
        while record != '':

            # add 1 to the annotation counter
            annotation_counter += 1

            # get data
            qseqid = data_dict['qseqid']
            sseqid = data_dict['sseqid']
            pident = data_dict['pident']
            # -- length = data_dict['length']
            # -- mismatch = data_dict['mismatch']
            # -- gapopen = data_dict['gapopen']
            # -- qstart = data_dict['qstart']
            # -- qend = data_dict['qend']
            # -- sstart = data_dict['sstart']
            # -- send = data_dict['send']
            evalue = data_dict['evalue']
            # -- bitscore = data_dict['bitscore']
            algorithm = data_dict['algorithm']
            ncbi_description = data_dict['ncbi_description']
            ncbi_species = data_dict['ncbi_species']
            tair10_ortholog_seq_id = data_dict['tair10_ortholog_seq_id']
            interpro_goterms = data_dict['interpro_goterms']
            panther_goterms = data_dict['panther_goterms']
            metacyc_pathways = data_dict['metacyc_pathways']
            # -- reactome_pathways = data_dict['reactome_pathways']
            eggnog_ortholog_seq_id = data_dict['eggnog_ortholog_seq_id']
            eggnog_ortholog_species = data_dict['eggnog_ortholog_species']
            eggnog_ogs = data_dict['eggnog_ogs']
            cog_category = data_dict['cog_category']
            eggnog_description = data_dict['eggnog_description']
            eggnog_goterms = data_dict['eggnog_goterms']
            ec = data_dict['ec']
            kegg_kos = data_dict['kegg_kos']
            kegg_pathways = data_dict['kegg_pathways']
            kegg_modules = data_dict['kegg_modules']
            kegg_reactions = data_dict['kegg_reactions']
            kegg_rclasses = data_dict['kegg_rclasses']
            brite = data_dict['brite']
            kegg_tc = data_dict['kegg_tc']
            cazy = data_dict['cazy']
            pfams = data_dict['pfams']

            # set the key
            key = f'{qseqid}-{sseqid}'

            # add data to the dictionary
            # -- functional_annotation_dict[key] = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'length': length, 'mismatch': mismatch, 'gapopen': gapopen, 'qstart': qstart, 'qend': qend, 'sstart': sstart, 'send': send, 'evalue': evalue, 'bitscore': bitscore, 'algorithm': algorithm, 'ncbi_description': ncbi_description, 'ncbi_species': ncbi_species, 'tair10_ortholog_seq_id': tair10_ortholog_seq_id, 'interpro_goterms': interpro_goterms, 'panther_goterms': panther_goterms, 'metacyc_pathways': metacyc_pathways, 'reactome_pathways': reactome_pathways, 'eggnog_ortholog_seq_id': eggnog_ortholog_seq_id, 'eggnog_ortholog_species': eggnog_ortholog_species, 'eggnog_ogs': eggnog_ogs, 'cog_category': cog_category, 'eggnog_description': eggnog_description, 'eggnog_goterms': eggnog_goterms, 'ec': ec, 'kegg_kos': kegg_kos, 'kegg_pathways': kegg_pathways, 'kegg_modules': kegg_modules, 'kegg_reactions': kegg_reactions, 'kegg_rclasses': kegg_rclasses, 'brite': brite, 'kegg_tc': kegg_tc, 'cazy': cazy, 'pfams': pfams}
            functional_annotation_dict[key] = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'evalue': evalue, 'algorithm': algorithm, 'ncbi_description': ncbi_description, 'ncbi_species': ncbi_species, 'tair10_ortholog_seq_id': tair10_ortholog_seq_id, 'interpro_goterms': interpro_goterms, 'panther_goterms': panther_goterms, 'metacyc_pathways': metacyc_pathways, 'eggnog_ortholog_seq_id': eggnog_ortholog_seq_id, 'eggnog_ortholog_species': eggnog_ortholog_species, 'eggnog_ogs': eggnog_ogs, 'cog_category': cog_category, 'eggnog_description': eggnog_description, 'eggnog_goterms': eggnog_goterms, 'ec': ec, 'kegg_kos': kegg_kos, 'kegg_pathways': kegg_pathways, 'kegg_modules': kegg_modules, 'kegg_reactions': kegg_reactions, 'kegg_rclasses': kegg_rclasses, 'brite': brite, 'kegg_tc': kegg_tc, 'cazy': cazy, 'pfams': pfams}

            # read the next record
            (record, key, data_dict) = genlib.read_functional_annotation_record(functional_annotation_file, functional_annotation_file_id, annotation_counter)

        # build the data list
        # -- data_list = ['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 'algorithm', 'ncbi_description', 'ncbi_species', 'tair10_ortholog_seq_id', 'interpro_goterms', 'panther_goterms', 'metacyc_pathways', 'reactome_pathways', 'eggnog_ortholog_seq_id', 'eggnog_ortholog_species', 'eggnog_ogs', 'cog_category', 'eggnog_description', 'eggnog_goterms', 'ec', 'kegg_kos', 'kegg_pathways', 'kegg_modules', 'kegg_reactions', 'kegg_rclasses', 'brite', 'kegg_tc', 'cazy', 'pfams']
        data_list = ['qseqid', 'sseqid', 'pident', 'evalue', 'algorithm', 'ncbi_description', 'ncbi_species', 'tair10_ortholog_seq_id', 'interpro_goterms', 'panther_goterms', 'metacyc_pathways', 'eggnog_ortholog_seq_id', 'eggnog_ortholog_species', 'eggnog_ogs', 'cog_category', 'eggnog_description', 'eggnog_goterms', 'ec', 'kegg_kos', 'kegg_pathways', 'kegg_modules', 'kegg_reactions', 'kegg_rclasses', 'brite', 'kegg_tc', 'cazy', 'pfams']

        # build the data dictionary
        data_dict = {}
        data_dict['qseqid'] = {'text': 'Sequence id', 'width': 180, 'alignment': 'left'}
        data_dict['sseqid'] = {'text': 'Cluster id', 'width': 120, 'alignment': 'left'}
        data_dict['pident'] = {'text': 'Ident (%)', 'width': 80, 'alignment': 'right'}
        # -- data_dict['length'] = {'text': 'length', 'width': 80, 'alignment': 'right'}
        # -- data_dict['mismatch'] = {'text': 'mismatch', 'width': 80, 'alignment': 'right'}
        # -- data_dict['gapopen'] = {'text': 'gapopen', 'width': 80, 'alignment': 'right'}
        # -- data_dict['qstart'] = {'text': 'qstart', 'width': 80, 'alignment': 'right'}
        # -- data_dict['qend'] = {'text': 'qend', 'width': 80, 'alignment': 'right'}
        # -- data_dict['sstart'] = {'text': 'sstart', 'width': 80, 'alignment': 'right'}
        # -- data_dict['send'] = {'text': 'send', 'width': 80, 'alignment': 'right'}
        data_dict['evalue'] = {'text': 'evalue', 'width': 80, 'alignment': 'right'}
        # -- data_dict['bitscore'] = {'text': 'bitscore', 'width': 80, 'alignment': 'right'}
        data_dict['algorithm'] = {'text': 'Algorithm', 'width': 80, 'alignment': 'left'}
        data_dict['ncbi_description'] = {'text': 'NCBI description', 'width': 400, 'alignment': 'left'}
        data_dict['ncbi_species'] = {'text': 'NCBI species', 'width': 200, 'alignment': 'left'}
        data_dict['tair10_ortholog_seq_id'] = {'text': 'TAIR10 orth. seq. id', 'width': 180, 'alignment': 'left'}
        data_dict['interpro_goterms'] = {'text': 'Interpro GOterms', 'width': 280, 'alignment': 'left'}
        data_dict['panther_goterms'] = {'text': 'Panther GOterms', 'width': 280, 'alignment': 'left'}
        data_dict['metacyc_pathways'] = {'text': 'Metacyc pathways', 'width': 280, 'alignment': 'left'}
        # -- data_dict['reactome_pathways'] = {'text': 'reactome_pathways', 'width': 280, 'alignment': 'left'}
        data_dict['eggnog_ortholog_seq_id'] = {'text': 'eggNOG orth. seq. id', 'width': 180, 'alignment': 'left'}
        data_dict['eggnog_ortholog_species'] = {'text': 'eggNOG orth. species', 'width': 200, 'alignment': 'left'}
        data_dict['eggnog_ogs'] = {'text': 'eggNOG OGs', 'width': 400, 'alignment': 'left'}
        data_dict['cog_category'] = {'text': 'COG category', 'width': 100, 'alignment': 'left'}
        data_dict['eggnog_description'] = {'text': 'eggNOG description', 'width': 400, 'alignment': 'left'}
        data_dict['eggnog_goterms'] = {'text': 'eggNOG goterms', 'width': 280, 'alignment': 'left'}
        data_dict['ec'] = {'text': 'EC', 'width': 100, 'alignment': 'left'}
        data_dict['kegg_kos'] = {'text': 'KEGG KOs', 'width': 280, 'alignment': 'left'}
        data_dict['kegg_pathways'] = {'text': 'KEGG pathways', 'width': 280, 'alignment': 'left'}
        data_dict['kegg_modules'] = {'text': 'KEGG modules', 'width': 280, 'alignment': 'left'}
        data_dict['kegg_reactions'] = {'text': 'KEGG reactions', 'width': 280, 'alignment': 'left'}
        data_dict['kegg_rclasses'] = {'text': 'KEGG rclasses', 'width': 280, 'alignment': 'left'}
        data_dict['brite'] = {'text': 'BRITE', 'width': 280, 'alignment': 'left'}
        data_dict['kegg_tc'] = {'text': 'KEGG TC', 'width': 280, 'alignment': 'left'}
        data_dict['cazy'] = {'text': 'CAZy', 'width': 100, 'alignment': 'left'}
        data_dict['pfams'] = {'text': 'PFAMs', 'width': 280, 'alignment': 'left'}

        # set the explanatory text
        explanatory_text = 'Double-clicking on a cluster displays the NCBI sequence identifiers clustered in it.'

        # set the window height and width
        window_height = 800
        window_width = 1330

        # return data
        return functional_annotation_dict, data_list, data_dict, window_height, window_width, explanatory_text

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'This file contains the classes related to the functional annotation used in {genlib.get_app_long_name()}')
    sys.exit(0)

#-------------------------------------------------------------------------------
