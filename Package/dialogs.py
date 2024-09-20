#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This source contains the classes related to dialogs of gymnoTOA
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

import os
import sys

from PyQt5.QtCore import Qt                      # pylint: disable=no-name-in-module
from PyQt5.QtGui import QCursor                  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QFont                    # pylint: disable=no-name-in-module
from PyQt5.QtGui import QGuiApplication          # pylint: disable=no-name-in-module
from PyQt5.QtGui import QIcon                    # pylint: disable=no-name-in-module
from PyQt5.QtGui import QPixmap                  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QTextCursor              # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QAbstractItemView    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QDialog              # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGridLayout          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGroupBox            # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QHeaderView          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QLabel               # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QMessageBox          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QPushButton          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidget         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidgetItem     # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTextEdit            # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QVBoxLayout          # pylint: disable=no-name-in-module


import genlib
import sqllib

#-------------------------------------------------------------------------------

class DialogProcess(QDialog):
    '''
    The class of the dialog "DialogProcess".
    '''

    #---------------

    # set the window dimensions
    WINDOW_HEIGHT = 700
    WINDOW_WIDTH = 800

    #---------------

    def __init__(self, parent, head, calling_function, *args):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent
        self.head = head
        self.calling_function = calling_function
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # call the init method of the parent class
        super().__init__()

        # build the graphic user interface of the window
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        self.create_log_file()
        self.calling_function(self, *args)
        self.enable_pushbutton_close()

        # show the window
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the window title and icon
        self.setWindowTitle(f'{genlib.get_app_short_name()} - {self.head}')
        self.setWindowIcon(QIcon(genlib.get_app_image_file()))

        # set the window size
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        # -- self.setMinimumSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        # -- self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # set the window flags
        # -- self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        # -- self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # create and configure "textedit"
        self.textedit = QTextEdit(self)
        self.textedit.setFont(QFont('Consolas', 10))
        self.textedit.setReadOnly(True)

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.addWidget(self.textedit, 0, 0)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_close"
        self.pushbutton_close = QPushButton('Close')
        self.pushbutton_close.setToolTip('Close the window.')
        self.pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 10)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.addWidget(self.pushbutton_close, 0, 1, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 10)
        gridlayout_central.setRowStretch(1, 1)
        gridlayout_central.setColumnStretch(0, 0)
        gridlayout_central.setColumnStretch(1, 1)
        gridlayout_central.setColumnStretch(2, 0)
        gridlayout_central.addWidget(groupbox_data, 0, 1)
        gridlayout_central.addWidget(groupbox_buttons, 1, 1)

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

        # set the cursor "wait"
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        # disable "pushbutton_close"
        self.pushbutton_close.setEnabled(False)

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the log file and window.
        '''

        # close the log file
        self.log_file_path_id.close()

        # close the window
        self.close()

    #---------------

    def enable_pushbutton_close(self):
        '''
        Enable "pushbutton_close".
        '''

        # restore the cursor
        QGuiApplication.restoreOverrideCursor()

        # enable "pushbutton_close"
        self.pushbutton_close.setEnabled(True)

    #---------------

    def create_log_file(self):
        '''
        Create a log file with submission information.
        '''

        # set the log file path
        self.log_file_path = genlib.get_submission_log_file(self.calling_function.__name__)

        # create the log file
        try:
            if not os.path.exists(os.path.dirname(self.log_file_path)):
                os.makedirs(os.path.dirname(self.log_file_path))
            self.log_file_path_id = open(self.log_file_path, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception:
            text = f'*** ERROR: The file {self.log_file_path} can not be created.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)
            self.pushbutton_close_clicked()

    #---------------

    def write(self, text=''):
        '''
        Add a message text in "textedit" and in the log file.
        '''

        # insert text in the current cursor position of "textedit" and process pending events
        self.textedit.insertPlainText(text)
        QApplication.processEvents()

        # write the text in the log file and force the write file to disc
        self.log_file_path_id.write(text)
        self.log_file_path_id.flush()
        os.fsync(self.log_file_path_id.fileno())

#-------------------------------------------------------------------------------

class DialogFileBrowser(QDialog):
    '''
    The class of the dialog "DialogFileBrowser".
    '''

    #---------------

    # set the window dimensions
    WINDOW_HEIGHT = 700
    WINDOW_WIDTH = 800

    #---------------

    def __init__(self, parent, head, file_path):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent
        self.head = head
        self.file_path = file_path
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # call the init method of the parent class
        super().__init__()

        # build the graphic user interface of the window
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # show the window
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        # -- self.showMaximized()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the window title and icon
        self.setWindowTitle(f'{genlib.get_app_short_name()} - {self.head}')
        self.setWindowIcon(QIcon(genlib.get_app_image_file()))

        # set the window size
        # -- self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setMinimumSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # set the window flags
        # -- self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # create and configure "textedit"
        self.textedit = QTextEdit()
        self.textedit.setFont(QFont('Consolas', 10))
        self.textedit.setReadOnly(True)

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.addWidget(self.textedit, 0, 0)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_refresh"
        self.pushbutton_refresh = QPushButton('Refresh')
        self.pushbutton_refresh.setToolTip('Reload the file content.')
        self.pushbutton_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_refresh.clicked.connect(self.pushbutton_refresh_clicked)

        # create and configure "pushbutton_close"
        self.pushbutton_close = QPushButton('Close')
        self.pushbutton_close.setToolTip('Close the window.')
        self.pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 15)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.setColumnStretch(2, 1)
        gridlayout_buttons.addWidget(self.pushbutton_refresh, 0, 1, alignment=Qt.AlignCenter)
        gridlayout_buttons.addWidget(self.pushbutton_close, 0, 2, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 10)
        gridlayout_central.setRowStretch(1, 1)
        gridlayout_central.setColumnStretch(0, 0)
        gridlayout_central.setColumnStretch(1, 1)
        gridlayout_central.setColumnStretch(2, 0)
        gridlayout_central.addWidget(groupbox_data, 0, 1)
        gridlayout_central.addWidget(groupbox_buttons, 1, 1)

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

        # load the file context
        self.load_file_content()

    #---------------

    def pushbutton_refresh_clicked(self):
        '''
        Reload the file content.
        '''

        # load the file context
        self.load_file_content()

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.close()

    #---------------

    def enable_pushbutton_close(self):
        '''
        Enable "pushbutton_close".
        '''

        # restore the cursor
        QGuiApplication.restoreOverrideCursor()

        # enable "pushbutton_close"
        self.pushbutton_close.setEnabled(True)

    #---------------

    def load_file_content(self):
        '''
        Load the file content in the "textedit".
        '''

        # clear the content of "textedit"
        self.textedit.clear()

        # open the file and insert its content in "textedit"
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file_id:
                self.textedit.insertPlainText(file_id.read())
        except Exception:
            title = f'{genlib.get_app_short_name()} - {self.head}'
            text = f'The file\n\n{self.file_path}\n\ncan not be opened.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)

        # move the cursor to start
        # -- text_cursor = QTextCursor(self.textedit.document())
        # -- text_cursor.movePosition(QTextCursor.Start)
        text_cursor = QTextCursor(self.textedit.document().findBlockByLineNumber(0))
        self.textedit.setTextCursor(text_cursor)

        # process pending events
        # -- QApplication.processEvents()

#-------------------------------------------------------------------------------

class DialogDataTable(QDialog):
    '''
    The class of the dialog "DialogDataTable".
    '''

    #---------------

    def __init__(self, parent, head, window_height, window_width, data_list, data_dict, item_dict, key_list, explanatory_text= '', action=None, params=[]):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent
        self.head = head
        self.window_height = window_height
        self.window_width = window_width
        self.data_list = data_list
        self.data_dict = data_dict
        self.item_dict = item_dict
        self.key_list = key_list
        self.explanatory_text = explanatory_text
        self.action = action
        self.params = params
        self.title = f'{genlib.get_app_short_name()} - {self.head}'

        # call the init method of the parent class
        super().__init__()

        # get the dictionary of application configuration
        self.app_config_dict = genlib.get_config_dict(genlib.get_app_config_file())

        # connect to the SQLite database
        app_db_path = self.app_config_dict[f'{genlib.get_app_short_name()} database']['app_db_path']
        if sys.platform.startswith('win32'):
            app_db_path = genlib.wsl_path_2_windows_path(app_db_path)
        self.conn = sqllib.connect_database(app_db_path)

        # build the graphic user interface of the window
        self.build_gui()

        # load initial data in inputs
        self.initialize_inputs()

        # show the window
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        # -- self.showMaximized()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the window title and icon
        self.setWindowTitle(f'{genlib.get_app_short_name()} - {self.head}')
        self.setWindowIcon(QIcon(genlib.get_app_image_file()))

        # set the window size
        # -- self.setFixedSize(self.window_width, self.window_height)
        self.setMinimumSize(self.window_width, self.window_height)
        self.resize(self.window_width, self.window_height)

        # set the window flags
        # -- self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # create and configure "tablewidget"
        self.tablewidget = QTableWidget()
        self.tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.column_name_list = []
        for col in self.data_list:
            self.column_name_list.append(self.data_dict[col]['text'])
        self.tablewidget.setColumnCount(len(self.column_name_list))
        self.tablewidget.setHorizontalHeaderLabels(self.column_name_list)
        for i in range(len(self.data_list)):    # pylint: disable=consider-using-enumerate
            col = self.data_list[i]
            self.tablewidget.setColumnWidth(i, self.data_dict[col]['width'])
        self.tablewidget.verticalHeader().setVisible(True)
        self.tablewidget.currentCellChanged.connect(self.tablewidget_currentCellChanged)
        self.tablewidget.cellClicked.connect(self.tablewidget_cellClicked)
        self.tablewidget.cellDoubleClicked.connect(self.tablewidget_cellDoubleClicked)

        # create and configure "label_transcript_file"
        label_explanatory_text = QLabel()
        label_explanatory_text.setText(self.explanatory_text)

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.addWidget(self.tablewidget, 0, 0)
        gridlayout_data.addWidget(label_explanatory_text, 1, 0)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_close"
        self.pushbutton_close = QPushButton('Close')
        self.pushbutton_close.setToolTip('Close the window.')
        self.pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 15)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.addWidget(self.pushbutton_close, 0, 1, alignment=Qt.AlignCenter)

        # create and configure "groupbox_buttons"
        groupbox_buttons = QGroupBox()
        groupbox_buttons.setObjectName('groupbox_buttons')
        groupbox_buttons.setStyleSheet('QGroupBox#groupbox_buttons {border: 0px;}')
        groupbox_buttons.setLayout(gridlayout_buttons)
        gridlayout_central = QGridLayout()
        gridlayout_central.setRowStretch(0, 10)
        gridlayout_central.setRowStretch(1, 1)
        gridlayout_central.setColumnStretch(0, 0)
        gridlayout_central.setColumnStretch(1, 1)
        gridlayout_central.setColumnStretch(2, 0)
        gridlayout_central.addWidget(groupbox_data, 0, 1)
        gridlayout_central.addWidget(groupbox_buttons, 1, 1)

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

    def tablewidget_cellDoubleClicked(self, row, col):
        '''
        Perform necessary actions after double clicking on "tablewidget" cell.
        '''

        # when the dialog is showing functional annotation data
        if self.action == 'browse-functional-annotation':
            if col == 1:

                # get the cluster identification
                cluster_id = self.tablewidget.item(row, col).text()

                # get MMseqs2 relationships dictionary
                relationships_dict = sqllib.get_mmseqs2_relationship_dict(self.conn, cluster_id)

                # initialize the NCBI sequence dictionary
                ncbi_seq_dict = genlib.NestedDefaultDict()

                # build the NCBI sequence dictionary
                for key, item in relationships_dict.items():
                    ncbi_seq_dict[key] = {'seq_id': item['seq_id'], 'description': item['description'], 'species': item['species']}

                # build the data list
                data_list = ['seq_id', 'description', 'species']

                # build the data dictionary
                data_dict = {}
                data_dict['seq_id'] = {'text': 'NCBI sequence id', 'width': 180, 'alignment': 'left'}
                data_dict['description'] = {'text': 'NCBI description', 'width': 400, 'alignment': 'left'}
                data_dict['species'] = {'text': 'Species', 'width': 200, 'alignment': 'left'}

                # set the explanatory text
                explanatory_text = ''

                # set the window height and width
                window_height = 500
                window_width = 880

                # show functional annotation data
                head = f'NCBI sequences clustering in {cluster_id}'
                data_table = DialogDataTable(self, head, window_height, window_width, data_list, data_dict, ncbi_seq_dict, sorted(ncbi_seq_dict.keys()), explanatory_text, 'browse-cluster')
                data_table.exec()

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.close()

    #---------------

    def enable_pushbutton_close(self):
        '''
        Enable "pushbutton_close".
        '''

        # restore the cursor
        QGuiApplication.restoreOverrideCursor()

        # enable "pushbutton_close"
        self.pushbutton_close.setEnabled(True)

    #---------------

    def load_tablewidget(self):
        '''
        Load data in "tablewidget".
        '''

        # clear the content of "tablewidget"
        self.tablewidget.clearContents()

        # set the rows number of "tablewidget"
        self.tablewidget.setRowCount(len(self.item_dict))

        # check if there are data
        if not self.data_dict:
            text = 'There are no result logs.'
            QMessageBox.critical(self, self.title, text, buttons=QMessageBox.Ok)

        # if there are data
        else:

            # initialize the row counter
            row = 0

            # for each key in the items dictionary
            # -- for key in sorted(self.item_dict.keys()):
            for key in self.item_dict.keys():

                # load data of the key
                for col, data in enumerate(self.data_list):

                    # set the item of the row and column
                    item = QTableWidgetItem(self.item_dict[key][data])
                    if self.data_dict[data]['alignment'] == 'left':
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    elif self.data_dict[data]['alignment'] == 'right':
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    elif self.data_dict[data]['alignment'] == 'center':
                        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    else:
                        item.setTextAlignment(Qt.AlignVCenter)

                    # insert the item in the row and column
                    self.tablewidget.setItem(row, col, item)

                # add 1 to the row counter
                row += 1

#-------------------------------------------------------------------------------

class DialogAbout(QDialog):
    '''
    The class of the dialog "DialogAbout".
    '''

    #---------------

    # set the window dimensions
    WINDOW_HEIGHT = 300
    WINDOW_WIDTH = 750

    #---------------

    def __init__(self, parent):
        '''
        Create a class instance.
        '''

        # save parameters in instance variables
        self.parent = parent

        # call the init method of the parent class
        super().__init__()

        # build the graphic user interface of the window
        self.build_gui()
        self.setWindowModality(Qt.ApplicationModal)

        # show the window
        self.show()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the window title and icon
        self.setWindowTitle(f'{genlib.get_app_short_name()} - About')
        self.setWindowIcon(QIcon(genlib.get_app_image_file()))

        # set the window size
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        # -- self.setMinimumSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        # -- self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # set the window flags
        # -- self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        # -- self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # move the window at center
        rectangle = self.frameGeometry()
        central_point = QGuiApplication.primaryScreen().availableGeometry().center()
        rectangle.moveCenter(central_point)
        self.move(rectangle.topLeft())

        # create and configure "label_image"
        label_image = QLabel()
        label_image.setPixmap(QPixmap(genlib.get_app_image_file()))

        # create and configure "label_project"
        label_project = QLabel()
        label_project.setText(f'{genlib.get_app_long_name()} v{genlib.get_app_version()}')
        label_project.setStyleSheet('font-weight: bold')

        # create and configure "label_research_group"
        label_research_group = QLabel()
        label_research_group.setText('GI en Especies Leñosas (WooSp)')

        # create and configure "label_department"
        label_department = QLabel()
        label_department.setText('Dpto. Sistemas y Recursos Naturales')

        # create and configure "label_college"
        label_college = QLabel()
        label_college.setText('ETSI Montes, Forestal y del Medio Natural')

        # create and configure "label_university"
        label_university = QLabel()
        label_university.setText('Universidad Politécnica de Madrid')

        # create and configure "label_url"
        label_url = QLabel()
        label_url.setText('https://github.com/ggfhf/')

        # create and configure "pushbutton_close"
        pushbutton_close =QPushButton('Close')
        pushbutton_close.setToolTip('Close the window.')
        pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout"
        gridlayout = QGridLayout()
        gridlayout.setRowStretch(0, 2)
        gridlayout.setRowStretch(1, 1)
        gridlayout.setRowStretch(2, 1)
        gridlayout.setRowStretch(3, 1)
        gridlayout.setRowStretch(4, 1)
        gridlayout.setRowStretch(5, 1)
        gridlayout.setRowStretch(6, 1)
        gridlayout.setColumnStretch(0, 1)
        gridlayout.setColumnStretch(1, 1)
        gridlayout.setColumnStretch(2, 1)
        gridlayout.addWidget(label_image, 1, 0, 4, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(label_project, 0, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(label_research_group, 1, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(label_department, 2, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(label_college, 3, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(label_university, 4, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(label_url, 6, 1, alignment=Qt.AlignCenter)
        gridlayout.addWidget(pushbutton_close, 7, 2, alignment=Qt.AlignCenter)

        # create and configure "groupbox"
        groupbox = QGroupBox()
        groupbox.setLayout(gridlayout)

        # create and configure "vboxlayout"
        vboxlayout = QVBoxLayout()
        vboxlayout.addWidget(groupbox)

        # apply the layout "vboxlayout" to the dialog
        self.setLayout(vboxlayout)

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.close()

   #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'This file contains the classes related to dialogs used in {genlib.get_app_long_name()}.')
    sys.exit(1)

#-------------------------------------------------------------------------------
