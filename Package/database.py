#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=unnecessary-pass
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This file contains the classes related to the database of gymnoTOA
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

from PyQt5.QtCore import Qt                # pylint: disable=no-name-in-module
from PyQt5.QtGui import QCursor            # pylint: disable=no-name-in-module
from PyQt5.QtGui import QFontMetrics             # pylint: disable=no-name-in-module
from PyQt5.QtGui import QGuiApplication    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QAbstractItemView    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGridLayout    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QGroupBox      # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QHeaderView          # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QLabel         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QMessageBox    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QPushButton    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidget         # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidgetItem     # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QVBoxLayout    # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QWidget        # pylint: disable=no-name-in-module

import dialogs
import genlib

#-------------------------------------------------------------------------------

class FormDownloadGymnoTOAdb(QWidget):
    '''
    Class used to download gymnoTOA-db.
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
        self.head = f'Download {genlib.get_db_name()}'
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

        # create and configure "pushbutton_execute"
        self.pushbutton_execute = QPushButton('Execute')
        self.pushbutton_execute.setToolTip(f'Download {genlib.get_db_name()}.')
        self.pushbutton_execute.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushbutton_execute.clicked.connect(self.pushbutton_execute_clicked)

        # create and configure "pushbutton_close"
        pushbutton_close = QPushButton('Close')
        pushbutton_close.setToolTip(f'Cancel the {genlib.get_db_name()} and close the window.')
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
        gridlayout_central.addWidget(label_head, 0, 1)
        gridlayout_central.addWidget(QLabel(), 1, 1)
        gridlayout_central.addWidget(groupbox_buttons, 2, 1)

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

        pass

    #---------------

    def check_inputs(self):
        '''
        Check the content of each input and do the actions linked to its value.
        '''

        pass

    #---------------

    def pushbutton_execute_clicked(self):
        '''
        Execute the process.
        '''

        # initialize the control variable
        OK = True

        # confirm the process is executed
        if OK:
            text = f'{genlib.get_db_name()} is going to be download.\n\nAre you sure to continue?'
            botton = QMessageBox.question(self, self.title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
            if botton == QMessageBox.No:
                OK = False

        # execute the process
        if OK:

            # create and execute "DialogProcess"
            process = dialogs.DialogProcess(self, self.head, self.download_gymnotoa_db)
            process.exec()

        # close the windows
        if OK:
            self.pushbutton_close_clicked()

    #---------------

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.parent.current_subwindow = None
        self.close()
        self.parent.set_background_image()

   #---------------

    def download_gymnotoa_db(self, process):
        '''
        Download gymnoTOA-db.
        '''

        # initialize the control variable
        OK = True

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
            current_run_dir = genlib.get_current_run_dir(result_dir, genlib.get_result_database_subdir(), genlib.get_process_download_gymnotoa_db_code())
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
            script_name = f'{genlib.get_process_download_gymnotoa_db_code()}-process.sh'
            process.write(f'Building the process script {script_name} ...\n')
            (OK, _) = self.build_download_gymnotoa_db_script(temp_dir, script_name, current_run_dir)
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
            starter_name = f'{genlib.get_process_download_gymnotoa_db_code()}-process-starter.sh'
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

    def build_download_gymnotoa_db_script(self, directory, script_name, current_run_dir):
        '''
        Build the script to recrate gymnoTOA-db.
        '''

        # initialize the control variable and error list
        OK = True
        error_list = []

        # get items from dictionary of application configuration
        app_dir = self.app_config_dict['Environment parameters']['app_dir']
        miniconda3_bin_dir = self.app_config_dict['Environment parameters']['miniconda3_bin_dir']
        database_dir = self.app_config_dict['Environment parameters']['database_dir']
        compressed_db_url = self.app_config_dict[f'{genlib.get_app_short_name()} database']['compressed_db_url']
        app_db_path = self.app_config_dict[f'{genlib.get_app_short_name()} database']['app_db_path']

        # set the temporal directory
        temp_dir = f'{app_dir}/{os.path.basename(genlib.get_temp_dir())}'

        # set the compressed database path
        compressed_db_path = f'{temp_dir}/{genlib.get_compressed_db_name()}'

        # set the script path
        script_path = f'{directory}/{script_name}'

        # write the script
        try:
            with open(script_path, mode='w', encoding='iso-8859-1', newline='\n') as file_id:
                file_id.write( '#!/bin/bash\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write(f'export PATH={miniconda3_bin_dir}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin\n')
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
                file_id.write( 'function activate_env_base\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Activating environment base ..."\n')
                file_id.write(f'    source {miniconda3_bin_dir}/activate\n')
                file_id.write( '    RC=$?\n')
                file_id.write( '    if [ $RC -ne 0 ]; then manage_error conda $RC; fi\n')
                file_id.write( '    echo "Environment is activated."\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function create_gymnotoa_db_dir\n')
                file_id.write( '{\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write(f'    echo "Creating the {genlib.get_db_name()} directory ..."\n')
                file_id.write( '    /usr/bin/time \\\n')
                file_id.write(f'        rm -rf {os.path.dirname(app_db_path)}\n')
                file_id.write( '    RC=$?\n')
                file_id.write( '    if [ $RC -ne 0 ]; then manage_error rm $RC; fi\n')
                file_id.write( '    /usr/bin/time \\\n')
                file_id.write(f'        mkdir -p {os.path.dirname(app_db_path)}\n')
                file_id.write( '    RC=$?\n')
                file_id.write( '    if [ $RC -ne 0 ]; then manage_error mkdir $RC; fi\n')
                file_id.write( '    echo "Directory is created."\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function download_gymnotoa_db\n')
                file_id.write( '{\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write(f'    echo "Downloading the compressed {genlib.get_db_name()} ..."\n')
                file_id.write( '    /usr/bin/time \\\n')
                file_id.write( '        wget \\\n')
                file_id.write( '            --quiet \\\n')
                file_id.write(f'            --output-document {compressed_db_path} \\\n')
                file_id.write(f'            {compressed_db_url}\n')
                file_id.write( '    wait \n')
                file_id.write( '    # -- RC=$?\n')
                file_id.write( '    # -- if [ $RC -ne 0 ]; then manage_error wget $RC; fi\n')
                file_id.write( '    echo "Database is downloaded."\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function decompress_gymnotoa_db\n')
                file_id.write( '{\n')
                file_id.write(f'    cd {temp_dir}\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write(f'    echo "Decompressing {genlib.get_db_name()} ..."\n')
                file_id.write(f'    cd {temp_dir}\n')
                file_id.write( '    /usr/bin/time \\\n')
                file_id.write( '        unzip \\\n')
                file_id.write( '            -o \\\n')
                file_id.write( '            -j \\\n')
                file_id.write(f'            {genlib.get_compressed_db_name()} \n')
                file_id.write( '    RC=$?\n')
                file_id.write( '    if [ $RC -ne 0 ]; then manage_error unzip $RC; fi\n')
                file_id.write( '    /usr/bin/time \\\n')
                file_id.write( '        unzip \\\n')
                file_id.write(f'            {genlib.get_compressed_db_name()} \\\n')
                file_id.write(f'            -d {database_dir}\n')
                file_id.write( '    RC=$?\n')
                file_id.write( '    if [ $RC -ne 0 ]; then manage_error unzip $RC; fi\n')
                file_id.write( '    echo "Database is decompressed."\n')
                file_id.write( '}\n')
                file_id.write( '#-------------------------------------------------------------------------------\n')
                file_id.write( 'function delete_temp_file\n')
                file_id.write( '{\n')
                file_id.write(f'    cd {current_run_dir}\n')
                file_id.write( '    echo "$SEP"\n')
                file_id.write( '    echo "Deleting the temporal file ..."\n')
                file_id.write( '    /usr/bin/time \\\n')
                file_id.write( '        rm \\\n')
                file_id.write(f'            {compressed_db_path} \n')
                file_id.write( '    RC=$?\n')
                file_id.write( '    if [ $RC -ne 0 ]; then manage_error wget $RC; fi\n')
                file_id.write( '    echo "File is deleted."\n')
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
                file_id.write( 'activate_env_base\n')
                file_id.write( 'create_gymnotoa_db_dir\n')
                file_id.write( 'download_gymnotoa_db\n')
                file_id.write( 'decompress_gymnotoa_db\n')
                file_id.write( 'delete_temp_file\n')
                file_id.write( 'end\n')
        except Exception as e:
            error_list.append(f'*** EXCEPTION: "{e}".')
            error_list.append(f'*** ERROR: The file {script_path} is not created.')
            OK = False

        # return the control variable and error list
        return (OK, error_list)

    #---------------

#-------------------------------------------------------------------------------

class FormViewGymnoTOAdbStats(QWidget):
    '''
    Class used to view the gymnoTOA-db statistics.
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
        self.head = f'View {genlib.get_db_name()} statistics'
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

        # create and configure "label_process_cluster_stats"
        label_cluster_stats = QLabel()
        label_cluster_stats.setText('Cluster statistics')
        label_cluster_stats.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "tablewidget_cluster_stats"
        self.tablewidget_cluster_stats = QTableWidget()
        self.tablewidget_cluster_stats.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidget_cluster_stats.horizontalHeader().setVisible(True)
        self.tablewidget_cluster_stats.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.cluster_stats_column_name_list = ['Data', '#', '%']
        self.tablewidget_cluster_stats.setColumnCount(len(self.cluster_stats_column_name_list))
        self.tablewidget_cluster_stats.setHorizontalHeaderLabels(self.cluster_stats_column_name_list)
        self.tablewidget_cluster_stats.setColumnWidth(0, 250)
        self.tablewidget_cluster_stats.setColumnWidth(1, 55)
        self.tablewidget_cluster_stats.setColumnWidth(2, 50)
        self.tablewidget_cluster_stats.verticalHeader().setVisible(True)

        # create and configure "label_process_busco_stats"
        label_busco_stats = QLabel()
        label_busco_stats.setText('BUSCO statistics')
        label_busco_stats.setFixedWidth(fontmetrics.width('9'*20))

        # create and configure "tablewidget_busco_stats"
        self.tablewidget_busco_stats = QTableWidget()
        self.tablewidget_busco_stats.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidget_busco_stats.horizontalHeader().setVisible(True)
        self.tablewidget_busco_stats.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.busco_stats_column_name_list = ['Data', '#', '%']
        self.tablewidget_busco_stats.setColumnCount(len(self.cluster_stats_column_name_list))
        self.tablewidget_busco_stats.setHorizontalHeaderLabels(self.cluster_stats_column_name_list)
        self.tablewidget_busco_stats.setColumnWidth(0, 250)
        self.tablewidget_busco_stats.setColumnWidth(1, 55)
        self.tablewidget_busco_stats.setColumnWidth(2, 50)
        self.tablewidget_busco_stats.verticalHeader().setVisible(True)

        # create and configure "label_empty"
        label_empty = QLabel()
        label_empty.setFixedWidth(fontmetrics.width('9'*3))

        # create and configure "gridlayout_data"
        gridlayout_data = QGridLayout()
        gridlayout_data.setColumnStretch(0, 15)
        gridlayout_data.setColumnStretch(1, 1)
        gridlayout_data.setColumnStretch(2, 15)
        gridlayout_data.addWidget(label_empty, 0, 0)
        gridlayout_data.addWidget(label_cluster_stats, 1, 0, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(label_busco_stats, 1, 2, alignment=Qt.AlignLeft)
        gridlayout_data.addWidget(self.tablewidget_cluster_stats, 2, 0)
        gridlayout_data.addWidget(self.tablewidget_busco_stats, 2, 2)
        gridlayout_data.addWidget(label_empty, 3, 0)
        gridlayout_data.addWidget(label_empty, 4, 0)

        # create and configure "groupbox_data"
        groupbox_data = QGroupBox()
        groupbox_data.setObjectName('groupbox_data')
        groupbox_data.setStyleSheet('QGroupBox#groupbox_data {border: 0px;}')
        groupbox_data.setLayout(gridlayout_data)

        # create and configure "pushbutton_close"
        pushbutton_close = QPushButton('Close')
        pushbutton_close.setToolTip('Close the window.')
        pushbutton_close.setCursor(QCursor(Qt.PointingHandCursor))
        pushbutton_close.clicked.connect(self.pushbutton_close_clicked)

        # create and configure "gridlayout_buttons"
        gridlayout_buttons = QGridLayout()
        gridlayout_buttons.setColumnStretch(0, 15)
        gridlayout_buttons.setColumnStretch(1, 1)
        gridlayout_buttons.addWidget(pushbutton_close, 0, 1, alignment=Qt.AlignCenter)

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

        # load data in "tablewidget_cluster_stats"
        self.load_tablewidget_cluster_stats()

        # load data in "tablewidget_busco_stats"
        self.load_tablewidget_busco_stats()

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

    def pushbutton_close_clicked(self):
        '''
        Close the window.
        '''

        self.parent.current_subwindow = None
        self.close()
        self.parent.set_background_image()

    #---------------

    def load_tablewidget_cluster_stats(self):
        '''
        Load data in "tablewidget_cluster_stats".
        '''

        # initialize item dictionary
        item_dict = genlib.NestedDefaultDict()

        # get the path of the cluster statistics
        cluster_stats_path = self.app_config_dict[f'{genlib.get_app_short_name()} database']['cluster_stats_path']
        if sys.platform.startswith('win32'):
            cluster_stats_path = genlib.wsl_path_2_windows_path(cluster_stats_path)

        # get the dictionary of statistics
        stats_dict = genlib.get_config_dict(cluster_stats_path)

        # get statistics data
        seqnum_acrogymnospermae = int(stats_dict['statistics']['seqnum_acrogymnospermae'])
        clusternum_total = int(stats_dict['statistics']['clusternum_total'])
        clusternum_interproscan_annotations = int(stats_dict['statistics']['clusternum_interproscan_annotations'])
        clusternum_emapper_annotations = int(stats_dict['statistics']['clusternum_emapper_annotations'])
        clusternum_tair10_ortologs = int(stats_dict['statistics']['clusternum_tair10_ortologs'])
        clusternum_without_annotations =  int(stats_dict['statistics']['clusternum_without_annotations'])

        # calculate percentages
        perc_interproscan_annotations = clusternum_interproscan_annotations / clusternum_total * 100
        perc_emapper_annotations = clusternum_emapper_annotations / clusternum_total * 100
        perc_tair10_ortologs = clusternum_tair10_ortologs / clusternum_total * 100
        perc_without_annotations = clusternum_without_annotations / clusternum_total * 100

        # build statistics dictionary
        item_dict [0] = {'data': 'Acrogymnospermae sequences', 'seqnum': f'{seqnum_acrogymnospermae}', 'perc': ''}
        item_dict [1] = {'data': 'Clusters total', 'seqnum': f'{clusternum_total}', 'perc': ''}
        item_dict [2] = {'data': 'Clusters with InterProScan annotations', 'seqnum': f'{clusternum_interproscan_annotations}', 'perc': f'{perc_interproscan_annotations:5.2f}'}
        item_dict [3] = {'data': 'Clusters with eggNOG-mapper annots', 'seqnum': f'{clusternum_emapper_annotations}', 'perc': f'{perc_emapper_annotations:5.2f}'}
        item_dict [4] = {'data': 'Clusters with TAIR10 orthologs', 'seqnum': f'{clusternum_tair10_ortologs}', 'perc': f'{perc_tair10_ortologs:5.2f}'}
        item_dict [5] = {'data': 'Clusters without annotations', 'seqnum': f'{clusternum_without_annotations}', 'perc': f'{perc_without_annotations:5.2f}'}

        # initialize "tablewidget_cluster_stats"
        self.tablewidget_cluster_stats.clearContents()

        # set the rows number of "tablewidget_cluster_stats"
        self.tablewidget_cluster_stats.setRowCount(len(item_dict))

        # load data in "tablewidget_cluster_stats"
        if item_dict:
            row = 0
            for key in sorted(item_dict.keys()):
                self.tablewidget_cluster_stats.setItem(row, 0, QTableWidgetItem(item_dict[key]['data']))
                item_seqnum= QTableWidgetItem(item_dict[key]['seqnum'])
                item_seqnum.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tablewidget_cluster_stats.setItem(row, 1, item_seqnum)
                item_perc= QTableWidgetItem(item_dict[key]['perc'])
                item_perc.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tablewidget_cluster_stats.setItem(row, 2, item_perc)
                row += 1

    #---------------

    def load_tablewidget_busco_stats(self):
        '''
        Load data in "tablewidget_busco_stats".
        '''

        # initialize item dictionary
        item_dict = genlib.NestedDefaultDict()

        # get the path of the busco statistics
        busco_stats_path = self.app_config_dict[f'{genlib.get_app_short_name()} database']['busco_stats_path']
        if sys.platform.startswith('win32'):
            busco_stats_path = genlib.wsl_path_2_windows_path(busco_stats_path)

        # initialize statistics data
        total_buscos = 0
        num_complete_buscos = 0
        num_complete_single_buscos = 0
        num_complete_duplicate_buscos = 0
        num_fragmented_buscos = 0
        num_mising_buscos = 0

        # get statistics data
        for record in open(busco_stats_path, mode='r', encoding='iso-8859-1', newline='\n'):
            pos = record.find('Total BUSCO groups searched')
            if pos > -1:
                total_buscos = int(record[:pos].strip('\t'))
            else:
                pos = record.find('Complete BUSCOs')
                if pos > -1:
                    num_complete_buscos = int(record[:pos].strip('\t'))
                else:
                    pos = record.find('Complete and single-copy BUSCOs')
                    if pos > -1:
                        num_complete_single_buscos = int(record[:pos].strip('\t'))
                    else:
                        pos = record.find('Complete and duplicated BUSCOs')
                        if pos > -1:
                            num_complete_duplicate_buscos = int(record[:pos].strip('\t'))
                        else:
                            pos = record.find('Fragmented BUSCOs')
                            if pos > -1:
                                num_fragmented_buscos = int(record[:pos].strip('\t'))
                            else:
                                pos = record.find('Missing BUSCOs')
                                if pos > -1:
                                    num_mising_buscos = int(record[:pos].strip('\t'))

        # calculate percentages
        perc_complete_buscos = num_complete_buscos / total_buscos * 100
        perc_complete_single_buscos = num_complete_single_buscos / total_buscos * 100
        perc_complete_duplicate_buscos = num_complete_duplicate_buscos / total_buscos * 100
        perc_fragmented_buscos = num_fragmented_buscos / total_buscos * 100
        perc_mising_buscos = num_mising_buscos / total_buscos * 100

        # build statistics dictionary
        item_dict [0] = {'data': 'Total BUSCO groups searched', 'seqnum': f'{total_buscos}', 'perc': ''}
        item_dict [1] = {'data': 'Complete BUSCOs', 'seqnum': f'{num_complete_buscos}', 'perc': f'{perc_complete_buscos:5.2f}'}
        item_dict [2] = {'data': '    Complete and single-copy BUSCOs', 'seqnum': f'{num_complete_single_buscos}', 'perc': f'{perc_complete_single_buscos:5.2f}'}
        item_dict [3] = {'data': '    Complete and duplicated BUSCOs', 'seqnum': f'{num_complete_duplicate_buscos}', 'perc': f'{perc_complete_duplicate_buscos:5.2f}'}
        item_dict [4] = {'data': 'Fragmented BUSCOs', 'seqnum': f'{num_fragmented_buscos}', 'perc': f'{perc_fragmented_buscos:5.2f}'}
        item_dict [5] = {'data': 'Missing BUSCOs', 'seqnum': f'{num_mising_buscos}', 'perc': f'{perc_mising_buscos:5.2f}'}

        # initialize "tablewidget_busco_stats"
        self.tablewidget_busco_stats.clearContents()

        # set the rows number of "tablewidget_busco_stats"
        self.tablewidget_busco_stats.setRowCount(len(item_dict))

        # load data in "tablewidget_busco_stats"
        if item_dict:
            row = 0
            for key in sorted(item_dict.keys()):
                self.tablewidget_busco_stats.setItem(row, 0, QTableWidgetItem(item_dict[key]['data']))
                item_seqnum= QTableWidgetItem(item_dict[key]['seqnum'])
                item_seqnum.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tablewidget_busco_stats.setItem(row, 1, item_seqnum)
                item_perc= QTableWidgetItem(item_dict[key]['perc'])
                item_perc.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tablewidget_busco_stats.setItem(row, 2, item_perc)
                row += 1

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This file contains the classes related to forms corresponding to menu items in gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
