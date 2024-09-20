#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This source define the main class of gymnoTOA (Gymnosperms Taxonomy-oriented Annotation)
and starts the application.

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
import webbrowser

import genlib

try:
    from PyQt5.QtCore import Qt                  # pylint: disable=no-name-in-module
    from PyQt5.QtGui import QCursor              # pylint: disable=no-name-in-module
    from PyQt5.QtGui import QFont                # pylint: disable=no-name-in-module
    from PyQt5.QtGui import QGuiApplication      # pylint: disable=no-name-in-module
    from PyQt5.QtGui import QIcon                # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QAction          # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QApplication     # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QLabel           # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QMainWindow      # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QMenuBar         # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QMessageBox      # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QVBoxLayout      # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QWidget          # pylint: disable=no-name-in-module
except Exception as e:
    raise genlib.ProgramException('', 'S002', 'PyQt5')

import annotation
import bioinfosw
import configuration
import database
import dialogs
import enrichment
import logs
import stats

#-------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    '''
    the main window class of the application.
    '''

    #---------------

    # set the window dimensions
    WINDOW_HEIGHT = 600
    WINDOW_WIDTH = 910

    #---------------

    def __init__(self):

        # call the init method of the parent class
        super().__init__()

        # initialize the current subwindow
        self.current_subwindow = None

        # build the graphic user interface of the window
        self.build_gui()

        # show the window
        self.show()

    #---------------

    def build_gui(self):
        '''
        Build the graphic user interface of the window.
        '''

        # set the window title and icon
        self.setWindowTitle(genlib.get_app_long_name())
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

        # create and configure "action_exit"
        action_exit = QAction(QIcon('./image-exit.png'),'&Exit', self)
        action_exit.setShortcut('Alt+F4')
        action_exit.setStatusTip(f'Exit {genlib.get_app_long_name()}.')
        action_exit.triggered.connect(self.action_exit_clicked)

        # create and configure "action_recreate_config_file"
        action_recreate_config_file = QAction(f'Recreate {genlib.get_app_short_name()} config file', self)
        action_recreate_config_file.setStatusTip(f'Recreate the {genlib.get_app_short_name()} config file.')
        action_recreate_config_file.triggered.connect(self.action_recreate_config_file_clicked)

        # create and configure "action_browse_config_file"
        action_browse_config_file = QAction(f'Browse {genlib.get_app_short_name()} config file', self)
        action_browse_config_file.setStatusTip(f'Browse the {genlib.get_app_short_name()} config file.')
        action_browse_config_file.triggered.connect(self.action_browse_config_file_clicked)

        # create and configure "action_install_miniconda3"
        action_install_miniconda3 = QAction('Miniconda3 and additional infrastructure software', self)
        action_install_miniconda3.setStatusTip('Install Miniconda3 and additional infrastructure software.')
        action_install_miniconda3.triggered.connect(self.action_install_miniconda3_clicked)

        # create and configure "action_install_blastplus"
        action_install_blastplus = QAction(genlib.get_blastplus_name(), self)
        action_install_blastplus.setStatusTip(f'Install {genlib.get_blastplus_name()} software.')
        action_install_blastplus.triggered.connect(self.action_install_blastplus_clicked)

        # create and configure "action_install_codan"
        action_install_codan = QAction(genlib.get_codan_name(), self)
        action_install_codan.setStatusTip(f'Install {genlib.get_codan_name()} software.')
        action_install_codan.triggered.connect(self.action_install_codan_clicked)

        # create and configure "action_download_gymno_database"
        action_download_gymno_database = QAction(f'Download {genlib.get_app_short_name()} database', self)
        action_download_gymno_database.setStatusTip(f'Download the {genlib.get_app_short_name()} database from the X server.')
        action_download_gymno_database.triggered.connect(self.action_download_gymno_database_clicked)

        # create and configure "action_view_gymno_database_stats"
        action_view_gymno_database_stats = QAction('Statistics', self)
        action_view_gymno_database_stats.setStatusTip('View gymnoTOA database statistics.')
        action_view_gymno_database_stats.triggered.connect(self.action_view_gymno_database_stats_clicked)

        # create and configure "action_run_annotation_pipeline"
        action_run_annotation_pipeline = QAction('Run pipeline', self)
        action_run_annotation_pipeline.setStatusTip('Run an annotation pipeline.')
        action_run_annotation_pipeline.triggered.connect(self.action_run_annotation_pipeline_clicked)

        # create and configure "action_restart_annotation_pipeline"
        action_restart_annotation_pipeline = QAction('Restart pipeline', self)
        action_restart_annotation_pipeline.setStatusTip('Restart an annotation pipeline.')
        action_restart_annotation_pipeline.triggered.connect(self.action_restart_annotation_pipeline_clicked)

        # create and configure "action_browse_goea"
        action_browse_annotation_pipeline = QAction('Browse results', self)
        action_browse_annotation_pipeline.setStatusTip('Browse annotation pipeline results.')
        action_browse_annotation_pipeline.triggered.connect(self.action_browse_annotation_pipeline_clicked)

        # create and configure "action_view_summary_report"
        action_view_summary_report = QAction('Summary report', self)
        action_view_summary_report.setStatusTip('Show the summary report.')
        action_view_summary_report.triggered.connect(self.action_view_summary_report_clicked)

        # create and configure "action_browse_species_frequency"
        action_browse_species_frequency = QAction('Frequency distribution data', self)
        action_browse_species_frequency.setStatusTip('Browse the frequency distribution data.')
        action_browse_species_frequency.triggered.connect(self.action_browse_species_frequency_clicked)

        # create and configure "action_plot_species_frequency"
        action_plot_species_frequency = QAction('Frequency distribution plot', self)
        action_plot_species_frequency.setStatusTip('Show the frequency distribution plot.')
        action_plot_species_frequency.triggered.connect(self.action_plot_species_frequency_clicked)

        # create and configure "action_browse_goterm_frequency"
        action_browse_goterm_frequency = QAction('Frequency distribution per GO term data', self)
        action_browse_goterm_frequency.setStatusTip('Browse the frequency distribution per GO term data.')
        action_browse_goterm_frequency.triggered.connect(self.action_browse_goterm_frequency_clicked)

        # create and configure "action_plot_goterm_frequency"
        action_plot_goterm_frequency = QAction('Frequency distribution per GO term plot', self)
        action_plot_goterm_frequency.setStatusTip('Show the frequency distribution per GO term plot.')
        action_plot_goterm_frequency.triggered.connect(self.action_plot_goterm_frequency_clicked)

        # create and configure "action_browse_namespace_frequency"
        action_browse_namespace_frequency = QAction('Frequency distribution per namespace data', self)
        action_browse_namespace_frequency.setStatusTip('Browse the frequency distribution per namespace data.')
        action_browse_namespace_frequency.triggered.connect(self.action_browse_namespace_frequency_clicked)

        # create and configure "action_plot_namespace_frequency"
        action_plot_namespace_frequency = QAction('Frequency distribution per namespace plot', self)
        action_plot_namespace_frequency.setStatusTip('Show the frequency distribution per namespace plot.')
        action_plot_namespace_frequency.triggered.connect(self.action_plot_namespace_frequency_clicked)

        # create and configure "action_browse_seq_per_goterm"
        action_browse_seq_per_goterm = QAction('Sequences # per GO terms # data', self)
        action_browse_seq_per_goterm.setStatusTip('Browse sequences # per GO terms # data.')
        action_browse_seq_per_goterm.triggered.connect(self.action_browse_seq_per_goterm_clicked)

        # create and configure "action_plot_seq_per_goterm"
        action_plot_seq_per_goterm = QAction('Sequences # per GO terms # plot', self)
        action_plot_seq_per_goterm.setStatusTip('Show sequences # per GO terms # plot.')
        action_plot_seq_per_goterm.triggered.connect(self.action_plot_seq_per_goterm_clicked)

        # create and configure "action_run_enrichment_analysis"
        action_run_enrichment_analysis = QAction('Run analysis', self)
        action_run_enrichment_analysis.setStatusTip('Run an enrichment analysis.')
        action_run_enrichment_analysis.triggered.connect(self.action_run_enrichment_analysis_clicked)

        # create and configure "action_restart_enrichment_analysis"
        action_restart_enrichment_analysis = QAction('Restart analysis', self)
        action_restart_enrichment_analysis.setStatusTip('Restart an enrichment_analysis.')
        action_restart_enrichment_analysis.triggered.connect(self.action_restart_enrichment_analysis_clicked)

        # create and configure "action_browse_goea"
        action_browse_goea = QAction('GO enrichment analysis', self)
        action_browse_goea.setStatusTip('Browse GO enrichment analysis results.')
        action_browse_goea.triggered.connect(self.action_browse_goea_clicked)

        # create and configure "action_browse_mpea"
        action_browse_mpea = QAction('Metacyc pathway enrichment analysis', self)
        action_browse_mpea.setStatusTip('Browse Metacyc pathway enrichment analysis results.')
        action_browse_mpea.triggered.connect(self.action_browse_mpea_clicked)

        # create and configure "action_browse_goea"
        action_browse_koea = QAction('KEGG KO enrichment analysis', self)
        action_browse_koea.setStatusTip('Browse KEGG KO enrichment analysis results.')
        action_browse_koea.triggered.connect(self.action_browse_koea_clicked)

        # create and configure "action_browse_kpea"
        action_browse_kpea = QAction('KEGG pathway enrichment analysis', self)
        action_browse_kpea.setStatusTip('Browse KEGG pathway enrichment analysis results.')
        action_browse_kpea.triggered.connect(self.action_browse_kpea_clicked)

        # create and configure "action_browse_submitting_logs"
        action_browse_submitting_logs = QAction('Submitting logs', self)
        action_browse_submitting_logs.setStatusTip('Browse submitting logs.')
        action_browse_submitting_logs.triggered.connect(self.action_browse_submitting_logs_clicked)

        # create and configure "action_browse_result_logs"
        action_browse_result_logs = QAction('Result logs', self)
        action_browse_result_logs.setStatusTip('Browse result logs.')
        action_browse_result_logs.triggered.connect(self.action_browse_result_logs_clicked)

        # create and configure "action_manual"
        action_manual = QAction('&Manual', self)
        action_manual.setShortcut('F1')
        action_manual.setStatusTip('Open the manual')
        action_manual.triggered.connect(self.accion_manual_clicked)

        # create and configure "action_about"
        action_about = QAction('&About...', self)
        action_about.setStatusTip('Show the application information.')
        action_about.triggered.connect(self.accion_about_clicked)

        # create and configure "menubar"
        menubar = QMenuBar(self)
        menubar.setCursor(QCursor(Qt.PointingHandCursor))

        # create and configure "menu_application"
        menu_application = menubar.addMenu('&Application')
        menu_application.setCursor(QCursor(Qt.PointingHandCursor))
        menu_application.addAction(action_exit)

        # create and configure "menu_configuration" and its submenus
        menu_configuration = menubar.addMenu('&Configuration')
        menu_configuration.setCursor(QCursor(Qt.PointingHandCursor))
        menu_configuration.addAction(action_recreate_config_file)
        menu_configuration.addAction(action_browse_config_file)
        menu_configuration.addSeparator()
        submenu_bioinfo = menu_configuration.addMenu('Bioinfo software installation')
        submenu_bioinfo.addAction(action_install_miniconda3)
        submenu_bioinfo.addSeparator()
        submenu_bioinfo.addAction(action_install_blastplus)
        submenu_bioinfo.addAction(action_install_codan)

        # create and configure "menu_database" and its submenus
        menu_database = menubar.addMenu('&Database')
        menu_database.setCursor(QCursor(Qt.PointingHandCursor))
        menu_database.addAction(action_download_gymno_database)
        menu_database.addSeparator()
        menu_database.addAction(action_view_gymno_database_stats)

        # create and configure "menu_functional_annotation" and its submenus
        menu_functional_annotation = menubar.addMenu('&Functional annotation')
        menu_functional_annotation.setCursor(QCursor(Qt.PointingHandCursor))
        menu_functional_annotation.addAction(action_run_annotation_pipeline)
        menu_functional_annotation.addAction(action_restart_annotation_pipeline)
        menu_functional_annotation.addSeparator()
        menu_functional_annotation.addAction(action_browse_annotation_pipeline)
        menu_functional_annotation.addSeparator()
        submenu_stats = menu_functional_annotation.addMenu('Statistics')
        submenu_stats.setCursor(QCursor(Qt.PointingHandCursor))
        submenu_stats.addAction(action_view_summary_report)
        submenu_stats.addSeparator()
        submenu_species = submenu_stats.addMenu('Species')
        submenu_species.addAction(action_browse_species_frequency)
        submenu_species.addAction(action_plot_species_frequency)
        submenu_stats.addSeparator()
        submenu_go = submenu_stats.addMenu('Gene Ontoloy')
        submenu_go.addAction(action_browse_goterm_frequency)
        submenu_go.addAction(action_plot_goterm_frequency)
        submenu_go.addSeparator()
        submenu_go.addAction(action_browse_namespace_frequency)
        submenu_go.addAction(action_plot_namespace_frequency)
        submenu_go.addSeparator()
        submenu_go.addAction(action_browse_seq_per_goterm)
        submenu_go.addAction(action_plot_seq_per_goterm)
        submenu_stats.addSeparator()

        # create and configure "menu_enrichment_analysis" and its submenus
        menu_enrichment_analysis = menubar.addMenu('&Enrichment analysis')
        menu_enrichment_analysis.setCursor(QCursor(Qt.PointingHandCursor))
        menu_enrichment_analysis.addAction(action_run_enrichment_analysis)
        menu_enrichment_analysis.addAction(action_restart_enrichment_analysis)
        menu_enrichment_analysis.addSeparator()
        submenu_enrichment_analysis_results = menu_enrichment_analysis.addMenu('Browse results')
        submenu_enrichment_analysis_results.addAction(action_browse_goea)
        submenu_enrichment_analysis_results.addSeparator()
        submenu_enrichment_analysis_results.addAction(action_browse_mpea)
        submenu_enrichment_analysis_results.addSeparator()
        submenu_enrichment_analysis_results.addAction(action_browse_koea)
        submenu_enrichment_analysis_results.addAction(action_browse_kpea)

        # create and configure "menu_logs"
        menu_logs = menubar.addMenu('&Logs')
        menu_logs.setCursor(QCursor(Qt.PointingHandCursor))
        menu_logs.addAction(action_browse_submitting_logs)
        menu_logs.addSeparator()
        menu_logs.addAction(action_browse_result_logs)

        # create and configure "menu_help"
        menu_help = menubar.addMenu('&Help')
        menu_help.setCursor(QCursor(Qt.PointingHandCursor))
        menu_help.addAction(action_manual)
        menu_help.addSeparator()
        menu_help.addAction(action_about)

        # set the menu bar in "MainWindow"
        self.setMenuBar(menubar)

        # configure "toolbar" in "MainWindow"
        self.toolbar = self.addToolBar('Salir')
        self.toolbar.setCursor(QCursor(Qt.PointingHandCursor))
        self.toolbar.addAction(action_exit)

        # configure the status bar in "MainWindow"
        self.statusBar().showMessage(f'Welcome to {genlib.get_app_long_name()}.')

        # set the bakcground image in "MainWindow"
        self.set_background_image()

    #---------------

    def closeEvent(self, event):
        '''
        The application is going to be closed.
        '''

        title = f'{genlib.get_app_short_name()} - Exit'
        text = f'Are you sure to exit {genlib.get_app_short_name()}?'
        botton = QMessageBox.question(self, title, text, buttons=QMessageBox.Yes|QMessageBox.No, defaultButton=QMessageBox.No)
        if botton == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    #---------------

    def action_exit_clicked(self):
        '''
        Exit the application.
        '''

        self.close()

    #---------------

    def action_recreate_config_file_clicked(self):
        '''
        Recreate the config file of gymnoTOA.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = configuration.FormRecreateConfigFile(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_config_file_clicked(self):
        '''
        Browse the config file of gtImputation.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = configuration.FormBrowseConfigFile(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_download_gymno_database_clicked(self):
        '''
        Rebuild the database of gymnoTOA from the UPMdrive.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = database.FormDownloadGymnoTOADatabase(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_view_gymno_database_stats_clicked(self):
        '''
        View gymnoTOA database statistics.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = database.FormViewGymnoTOADatabaseStats(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow
    #---------------

    def action_install_miniconda3_clicked(self):
        '''
        Install Miniconda3 software (Conda infrastructure).
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = bioinfosw.FormInstallBioinfoSoftware(self, genlib.get_miniconda3_code(), genlib.get_miniconda3_name())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_install_blastplus_clicked(self):
        '''
        Install BLAST+ software.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = bioinfosw.FormInstallBioinfoSoftware(self, genlib.get_blastplus_code(), genlib.get_blastplus_name())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_install_codan_clicked(self):
        '''
        Install CodAn software.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = bioinfosw.FormInstallBioinfoSoftware(self, genlib.get_codan_code(), genlib.get_codan_name())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_run_annotation_pipeline_clicked(self):
        '''
        Run an annotation pipeline.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = annotation.FormRunAnnotationPipeline(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_restart_annotation_pipeline_clicked(self):
        '''
        Restart an annotation pipeline.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = annotation.FormRestartAnnotationPipeline(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_annotation_pipeline_clicked(self):
        '''
        Browse results of a annotation pipeline.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = annotation.FormBrowseAnnotationResults(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_view_summary_report_clicked(self):
        '''
        Show the summary report.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormViewSummaryReport(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_species_frequency_clicked(self):
        '''
        Browse the frequency distribution data of species.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormBrowseStats(self, stats_code='species')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_plot_species_frequency_clicked(self):
        '''
        Show the frequency distribution plot of species.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormPlotStats(self, stats_code='species')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_goterm_frequency_clicked(self):
        '''
        Browse the frequency distribution data of GO terms.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormBrowseStats(self, stats_code='go')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_plot_goterm_frequency_clicked(self):
        '''
        Show the frequency distribution plot of GO terms.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormPlotStats(self, stats_code='go')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_namespace_frequency_clicked(self):
        '''
        Browse the frequency distribution data of namespaces data.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormBrowseStats(self, stats_code='namespace')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_plot_namespace_frequency_clicked(self):
        '''
        Show the frequency distribution plot of namespaces plot.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormPlotStats(self, stats_code='namespace')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_seq_per_goterm_clicked(self):
        '''
        Browse sequences # per GO terms # data.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormBrowseStats(self, stats_code='seq_per_goterm')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_plot_seq_per_goterm_clicked(self):
        '''
        Show sequences # per GO terms # plot.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = stats.FormPlotStats(self, stats_code='seq_per_goterm')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_run_enrichment_analysis_clicked(self):
        '''
        Run an enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormRunEnrichmentAnalysis(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_restart_enrichment_analysis_clicked(self):
        '''
        Restart an enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormRestartEnrichmentAnalysis(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_goea_clicked(self):
        '''
        Browse results of a GO enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormBrowseEnrichmentAnalysis(self, code=genlib.get_goea_code())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_mpea_clicked(self):
        '''
        Browse results of a Metacyc pathway enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormBrowseEnrichmentAnalysis(self, code=genlib.get_mpea_code())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_koea_clicked(self):
        '''
        Browse results of a KEGG KO enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormBrowseEnrichmentAnalysis(self, code=genlib.get_koea_code())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_kpea_clicked(self):
        '''
        Browse results of a KEGG pathway enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormBrowseEnrichmentAnalysis(self, code=genlib.get_kpea_code())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_metacyc_pathway_enrichment_analysis_clicked(self):
        '''
        Browse a Metacyc pathway enrichment analysis.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = enrichment.FormBrowseEnrichmentAnalysis(self, code=genlib.get_mpea_code())

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_submitting_logs_clicked(self):
        '''
        Browse a submitting logs.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = logs.FormBrowseSubmittingLogs(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def action_browse_result_logs_clicked(self):
        '''
        Browse a result logs.
        '''

        # close the existing subwindow
        if self.current_subwindow is not None:
            self.current_subwindow.close()

        # create a new subwindow to perform the action
        subwindow = logs.FormBrowseResultLogs(self)

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(subwindow, alignment=Qt.AlignCenter)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

        # save the current subwindow
        self.current_subwindow = subwindow

    #---------------

    def accion_manual_clicked(self):
        '''
        Open the help file.
        '''

        # set the path of the manual
        manual = os.path.abspath(genlib.get_app_manual_file())

        # browse the manual
        if os.path.exists(manual):
            webbrowser.open_new(f'file://{manual}')
        else:
            title = f'{genlib.get_app_short_name()} - Help - Manual'
            text = f'The document\n\n{manual}\n\nis not available.'
            QMessageBox.critical(self, title, text, buttons=QMessageBox.Ok)

    #---------------

    def accion_about_clicked(self):
        '''
        Show the application information.
        '''

        # create and execute "dialog_about"
        dialog_about = dialogs.DialogAbout(self)
        dialog_about.exec()

    #---------------

    def set_background_image(self):
        '''
        Set the bakcground image in MainWindow.
        '''

        # create and configure "label_image"
        label_image = QLabel(self)
        label_image.setStyleSheet(f'border-image : url({genlib.get_app_background_image_file()});')

        # create "widget_central"
        widget_central = QWidget(self)

        # create and configure "v_box_layout"
        v_box_layout = QVBoxLayout(widget_central)
        v_box_layout.addWidget(label_image)

        # set the central widget in "MainWindow"
        self.setCentralWidget(widget_central)

    #---------------

    def warn_unavailable_process(self):
        '''
        Show a message warning the process is unavailable.
        '''

        title = f'{genlib.get_app_short_name()} - Warning'
        text = 'This process is been built.\n\nIt is coming soon!'
        QMessageBox.warning(self, title, text, buttons=QMessageBox.Ok)

    #---------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    # check the operating system
    if sys.platform.startswith('win32'):
        command = 'whoami'
        null = open('nul', 'w', encoding='iso-8859-1')
        rc = genlib.run_command(command, null, is_script=False)
        null.close()
        if rc == 0:
            pass
        else:
            print('*** ERROR: The WSL 2 is not installed.')
            sys.exit(1)
    elif not sys.platform.startswith('linux') and not sys.platform.startswith('darwin'):
        print(f'*** ERROR: The {sys.platform} OS is not supported.')
        sys.exit(1)

    # check the Python version
    if sys.version_info[0] == 3 and sys.version_info[1] >= 10:
        pass
    else:
        print('*** ERROR: Python 3.10 or greater is required.')
        sys.exit(1)

    # check if the current directory is gymnoTOA home directory
    current_dir = os.getcwd()
    program_name = os.path.basename(__file__)
    if not os.path.isfile(os.path.join(current_dir, program_name)):
        print(f'*** ERROR: {program_name} has to be run in the {genlib.get_app_short_name()} home directory.')
        sys.exit(1)

    # check if Pandas is installed
    try:
        import pandas
    except Exception as e:
        print('*** ERROR: The library Pandas is not installed.')
        sys.exit(1)

    # check if Matplotlib is installed
    try:
        import matplotlib
    except Exception as e:
        print('*** ERROR: The library Matplotlib is not installed.')
        sys.exit(1)

    # check if Plotnine is installed
    try:
        import plotnine
    except Exception as e:
        print('*** ERROR: The library plotnine is not installed.')
        sys.exit(1)

    # set the font
    (default_font, default_size) = genlib.get_default_font_size()
    font = QFont(default_font, default_size)
    font.setStyleHint(QFont.SansSerif)

    # create and configure "application"
    application = QApplication(sys.argv)
    # -- if sys.platform.startswith('win32'):
    # --     application.setStyle(QStyleFactory.create('Fusion'))
    application.setFont(font)

    # create and execute "mainwindow"
    mainwindow = MainWindow()
    sys.exit(application.exec_())

#-------------------------------------------------------------------------------
