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
This source defines the general functions and classes used in gymnoTOA
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

import collections
import configparser
import datetime
import os
import re
import subprocess
import sys

#-------------------------------------------------------------------------------

def get_app_code():
    '''
    Get the application code.
    '''

    return 'gymnotoa-app'

#-------------------------------------------------------------------------------

def get_app_long_name():
    '''
    Get the application long name.
    '''

    return 'gymnoTOA-app (Gymnosperms Taxonomy-oriented Annotation application)'

#-------------------------------------------------------------------------------

def get_app_short_name():
    '''
    Get the application short name.
    '''

    return 'gymnoTOA-app'

#-------------------------------------------------------------------------------

def get_app_version():
    '''
    Get the application version.
    '''

    return '0.21'

#-------------------------------------------------------------------------------

def get_app_config_dir():
    '''
    Get the application configuration directory.
    '''

    return './config'

#-------------------------------------------------------------------------------

def get_app_config_file():
    '''
    Get the path of the aplication config file.
    '''

    return f'{get_app_config_dir()}/{get_app_code()}-config.txt'

#-------------------------------------------------------------------------------

def get_app_manual_file():
    '''
    Get the file path of application manual.
    '''

    return f'./{get_app_short_name()}-manual.pdf'

#-------------------------------------------------------------------------------

def get_app_image_file():
    '''
    Get the file path of application image.
    '''

    return f'./image-{get_app_short_name()}.png'

#-------------------------------------------------------------------------------

def get_app_background_image_file():
    '''
    Get the file path of the background image.
    '''

    return './image-pinos-perrault.jpg'

#-------------------------------------------------------------------------------

def check_os():
    '''
    Check the operating system.
    '''

    # if the operating system is unsupported, exit with exception
    if not sys.platform.startswith('linux') and not sys.platform.startswith('darwin') and not sys.platform.startswith('win32'):
        raise ProgramException('', 'S001', sys.platform)

#-------------------------------------------------------------------------------

def get_default_font_size():
    '''
    Get the default font depending on the Operating System.
    '''

    # set the default font and its size
    default_font_and_size = 0
    if sys.platform.startswith('linux'):
        default_font_and_size = ('Verdana', 10)
    elif sys.platform.startswith('darwin'):
        default_font_and_size = ('Verdana', 10)
    elif sys.platform.startswith('win32'):
        default_font_and_size = ('DejaVu 10', 10)

    # return the default font
    return default_font_and_size

#-------------------------------------------------------------------------------

def get_db_name():
    '''
    Get the name of the compressed gymnoTOA database.
    '''

    return 'gymnoTOA-db'

#-------------------------------------------------------------------------------

def get_compressed_db_name():
    '''
    Get the name of the compressed gymnoTOA database.
    '''

    return f'{get_db_name()}.zip'

#-------------------------------------------------------------------------------

def get_compressed_db_url():
    '''
    Get the URL where the compressed gymnoTOA database is available to download.
    '''

    return f'https://drive.upm.es/s/LTssGhCHe1Wh9Os/download?path=%%2F&files={get_compressed_db_name()}'

#-------------------------------------------------------------------------------

def get_database_dir():
    '''
    Get the directory where database data are saved.
    '''

    return f'{get_app_short_name()}-databases'

#-------------------------------------------------------------------------------

def get_result_dir():
    '''
    Get the result directory where results datasets are saved.
    '''

    return f'{get_app_short_name()}-results'

#-------------------------------------------------------------------------------

def get_result_database_subdir():
    '''
    Get the result subdirectory where process results related to the genomic database managment are saved.
    '''

    return 'database'

#-------------------------------------------------------------------------------

def get_result_installation_subdir():
    '''
    Get the result subdirectory where installation process results are saved.
    '''

    return 'installation'

#-------------------------------------------------------------------------------

def get_result_run_subdir():
    '''
    Get the result subdirectory where run results are saved.
    '''

    return 'run'

#-------------------------------------------------------------------------------

def get_yml_dir():
    '''
    Get the yml directory where gymnoTOA environment installation is.
    '''

    return 'yml'

#-------------------------------------------------------------------------------

def get_gymnotoa_yml_file():
    '''
    Get the yml file of the gymnoTOA environment installation.
    '''

    return 'gymnotoa.yml'

#-------------------------------------------------------------------------------

def get_log_dir():
    '''
    Get the log file directory.
    '''

    return './logs'

#-------------------------------------------------------------------------------

def get_run_log_file():
    '''
    Get the log file name of a process run.
    '''

    return 'log.txt'

#-------------------------------------------------------------------------------

def get_temp_dir():
    '''
    Get the temporal directory.
    '''

    return './temp'

#-------------------------------------------------------------------------------

def get_fasta_type_proteins():
    '''
    Get the FASTA type for proteins.
    '''

    return 'PROTEINS'

#-------------------------------------------------------------------------------

def get_fasta_type_transcripts():
    '''
    Get the FASTA type for transcripts.
    '''

    return 'TRANSCRIPTS'

#-------------------------------------------------------------------------------

def get_process_download_gymnotoa_db_code():
    '''
    Get the code used to identify processes to download the gymnoTOA database
    from the server X.
    '''

    return f'download-{get_db_name().lower()}'

#-------------------------------------------------------------------------------

def get_process_download_gymnotoa_db_name():
    '''
    Get the name used to title processes to download the gymnoTOA database
    from the server X.
    '''

    return f'Download {get_db_name()}'

#-------------------------------------------------------------------------------

def get_process_run_annotation_pipeline_code():
    '''
    Get the code used to identify processes to run an annotation pipeline.
    '''

    return 'run-annotation-pipeline'

#-------------------------------------------------------------------------------

def get_process_run_annotation_pipeline_name():
    '''
    Get the name used to title processes to run an annotation pipeline.
    '''

    return 'Run annotation pipeline'

#-------------------------------------------------------------------------------

def get_process_restart_annotation_pipeline_code():
    '''
    Get the code used to identify processes to restart an annotation pipeline.
    '''

    return 'restart-annotation-pipeline'

#-------------------------------------------------------------------------------

def get_process_restart_annotation_pipeline_name():
    '''
    Get the name used to title processes to restart an annotation pipeline.
    '''

    return 'Restart annotation pipeline'

#-------------------------------------------------------------------------------

def get_process_run_enrichment_analysis_code():
    '''
    Get the code used to identify processes to run a functional analysis.
    '''

    return 'run-enrichment-analysis'

#-------------------------------------------------------------------------------

def get_process_run_enrichment_analysis_name():
    '''
    Get the name used to title processes to run a functional analysis.
    '''

    return 'Run enrichment analysis'

#-------------------------------------------------------------------------------

def get_process_restart_enrichment_analysis_code():
    '''
    Get the code used to identify processes to restart a functional analysis.
    '''

    return 'restart-enrichment-analysis'

#-------------------------------------------------------------------------------

def get_process_restart_enrichment_analysis_name():
    '''
    Get the name used to title processes to restart a functional analysis.
    '''

    return 'Restart enrichment analysis'

#-------------------------------------------------------------------------------

def get_config_dict(config_file):
    '''
    Get a dictionary with the options retrieved from a configuration file.
    '''

    # initialize the configuration dictionary
    config_dict = {}

    try:

        # create class to parse the configuration files
        config = configparser.ConfigParser()

        # read the configuration file
        config.read(config_file)

        # build the dictionary
        for section in config.sections():
            # get the keys dictionary
            keys_dict = config_dict.get(section, {})
            # for each key in the section
            for key in config[section]:
                # get the value of the key
                value = config.get(section, key, fallback='')
                # add a new enter in the keys dictionary
                keys_dict[key] = get_option_value(value)
            # update the section with its keys dictionary
            config_dict[section] = keys_dict

    except Exception as e:
        raise ProgramException(e, 'F005', config_file) from e

    # return the configuration dictionary
    return config_dict

#-------------------------------------------------------------------------------

def get_option_value(option):
    '''
    Remove comments and spaces from an option retrieve from a configuration file.
    '''

    # remove comments
    position = option.find('#')
    if position == -1:
        value = option
    else:
        value = option[:position]

    # remove spaces
    value = value.strip()

    # return the value
    return value

#-------------------------------------------------------------------------------

def windows_path_2_wsl_path(path):
    '''
    Change a Windows format path to a WSL format path.
    '''

    # change the format path
    new_path = path.replace('\\', '/')
    new_path = f'/mnt/{new_path[0:1].lower()}{new_path[2:]}'

    # return the path
    return new_path

#-------------------------------------------------------------------------------

def wsl_path_2_windows_path(path):
    '''
    Change a WSL format path to a Windows format path.
    '''

    # change the format path
    new_path = f'{path[5:6].upper()}:{path[6:]}'
    new_path = new_path.replace('/', '\\')

    # return the path
    return new_path

#-------------------------------------------------------------------------------

def get_wsl_envvar(envvar):
    '''
    Get the value of a varible environment from WSL.
    '''

    # initialize the environment variable value
    envvar_value = get_na()

    # build the command
    command = f'wsl bash -c "echo ${envvar}"'

    # run the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(process.stdout.readline, b''):
        envvar_value = line.decode('utf-8').replace('\n' ,'')
        break
    process.wait()

    # return the environment variable value
    return envvar_value

#-------------------------------------------------------------------------------

def get_current_run_dir(result_dir, group, process):
    '''
    Get the run directory of a process.
    '''

    # set the run identificacion
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now, '%y%m%d')
    time = datetime.datetime.strftime(now, '%H%M%S')
    run_id = f'{process}-{date}-{time}'

    # set the current run directory
    current_run_dir = f'{result_dir}/{group}/{run_id}'

    # return the run directory
    return current_run_dir

#-------------------------------------------------------------------------------

def get_params_file_name():
    '''
    Get the name of the file to save the parameters.
    '''

    return 'params.txt'

#-------------------------------------------------------------------------------

def get_blastp_clade_alignment_file_name():
    '''
    Get the name of the alignment file yielded by blastp.
    '''

    return 'blastp-clade-alignments.csv'

#-------------------------------------------------------------------------------

def get_blastx_clade_alignment_file_name():
    '''
    Get the name of the alignment file yielded by blastx.
    '''

    return 'blastx-clade-alignments.csv'

#-------------------------------------------------------------------------------

def get_blastn_lncrna_alignment_file_name():
    '''
    Get the name of the alignment file yielded by blastn.
    '''

    return 'blastn-lncrna-alignments.csv'

#-------------------------------------------------------------------------------

def get_complete_functional_annotation_file_name():
    '''
    Get the name of the functional annotation file with all hits per sequence.
    '''

    return 'functional-annotations-complete.csv'

#-------------------------------------------------------------------------------

def get_besthit_functional_annotation_file_name():
    '''
    Get the name of the functional annotation file with the best hit per sequence.
    '''

    return 'functional-annotations-besthit.csv'

#-------------------------------------------------------------------------------

def get_goea_code():
    '''
    Get the code of the GO enrichment analysis.
    '''

    return 'goea'

#-------------------------------------------------------------------------------

def get_goea_name():
    '''
    Get the name of the GO term enrichment analysis.
    '''

    return 'GO term enrichment analysis'

#-------------------------------------------------------------------------------

def get_besthit_goea_file_name():
    '''
    Get the name of the GO term enrichment analysis file (best hit per sequence).
    '''

    return 'besthit-goterm-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_complete_goea_file_name():
    '''
    Get the name of the GO term enrichment analysis file (all hits per sequence).
    '''

    return 'complete-goterm-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_mpea_code():
    '''
    Get the code of the Metacyc pathway enrichment analysis.
    '''

    return 'mpea'

#-------------------------------------------------------------------------------

def get_mpea_name():
    '''
    Get the name of the Metacyc pathway enrichment analysis.
    '''

    return 'Metacyc pathway enrichment analysis'

#-------------------------------------------------------------------------------

def get_besthit_mpea_file_name():
    '''
    Get the name of the Metacyc pathway enrichment analysis file (best hit per sequence).
    '''

    return 'besthit-metacyc-pathway-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_complete_mpea_file_name():
    '''
    Get the name of the Metacyc pathway enrichment analysis file (all hits per sequence).
    '''

    return 'complete-metacyc-pathway-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_koea_code():
    '''
    Get the code of the KEGG KO enrichment analysis.
    '''

    return 'koea'

#-------------------------------------------------------------------------------

def get_koea_name():
    '''
    Get the name of the KEGG KO enrichment analysis.
    '''

    return 'KEGG KO enrichment analysis'

#-------------------------------------------------------------------------------

def get_besthit_koea_file_name():
    '''
    Get the name of the KEGG KO enrichment analysis file (best hit per sequence).
    '''

    return 'besthit-kegg-ko-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_complete_koea_file_name():
    '''
    Get the name of the KEGG KO enrichment analysis file (all hits per sequence).
    '''

    return 'complete-kegg-ko-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_kpea_code():
    '''
    Get the code of the KEGG pathway enrichment analysis.
    '''

    return 'kpea'

#-------------------------------------------------------------------------------

def get_kpea_name():
    '''
    Get the name of the KEGG pathway enrichment analysis.
    '''

    return 'KEGG pathway enrichment analysis'

#-------------------------------------------------------------------------------

def get_besthit_kpea_file_name():
    '''
    Get the name of the KEGG pathway enrichment analysis file (best hit per sequence).
    '''

    return 'besthit-kegg-pathway-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_complete_kpea_file_name():
    '''
    Get the name of the KEGG pathway enrichment analysis file (all hits per sequence).
    '''

    return 'complete-kegg-pathway-enrichment-analysis.csv'

#-------------------------------------------------------------------------------

def get_status_dir(current_run_dir):
    '''
    Get the status directory of a process.
    '''

    return f'{current_run_dir}/status'

#-------------------------------------------------------------------------------

def get_status_ok(current_run_dir):
    '''
    Get the OK status file.
    '''

    return f'{current_run_dir}/status/script.ok'

#-------------------------------------------------------------------------------

def get_status_wrong(current_run_dir):
    '''
    Get the WRONG status file.
    '''

    return f'{current_run_dir}/status/script.wrong'

#-------------------------------------------------------------------------------

def get_submission_log_file(function_name):
    '''
    Get the log file name of a process submission.
    '''

    # set the log file name
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now, '%y%m%d')
    time = datetime.datetime.strftime(now, '%H%M%S')
    log_file_name = f'{get_log_dir()}/{function_name}-{date}-{time}.txt'

    # return the log file name
    return log_file_name

#-------------------------------------------------------------------------------

def get_miniforge3_code():
    '''
    Get the Miniforge3 code used to identify its processes.
    '''

    return 'miniforge3'

#-------------------------------------------------------------------------------

def get_miniforge3_name():
    '''
    Get the Miniforge3 name used to title.
    '''

    return 'Miniforge3'

#-------------------------------------------------------------------------------

def get_miniforge3_url():
    '''
    Get the Minicforge3 URL.
    '''

    # assign the Miniforge3 URL
    miniforge3_url = ''
    if sys.platform.startswith('linux') or sys.platform.startswith('win32'):
        miniforge3_url = 'https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh'
    elif sys.platform.startswith('darwin'):
        miniforge3_url = 'https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh'

    # return the Miniforge3 URL
    return miniforge3_url

#-------------------------------------------------------------------------------

def get_miniforge3_dir():
    '''
    Get the directory where Miniforge3 is installed.
    '''

    return 'Miniforge3'

#-------------------------------------------------------------------------------

def get_miniforge3_dir_in_wsl():
    '''
    Get the directory where Miniforge3 is installed on WSL environment.
    '''

    return '$HOME/Miniforge3'

#-------------------------------------------------------------------------------

def get_miniforge3_current_dir():
    '''
    Get the current directory where Miniforge3 is installed.
    '''

    # get the path of the directory path of the current conda environment
    environment_path = os.getenv('CONDA_PREFIX')
    envs_pos = environment_path.find('/envs')

    # get the miniforge current directory
    miniforge3_current_dir = ''
    if envs_pos == -1:
        miniforge3_current_dir = environment_path
    else:
        miniforge3_current_dir = environment_path[:envs_pos]

    # return the miniforge current directory
    return miniforge3_current_dir

#-------------------------------------------------------------------------------

def get_gymnotoa_env_code():
    '''
    Get the Miniforge3 environment code where the Python packages used by gymnoTOA are
    installed.
    '''

    return 'gymnotoa'

#-------------------------------------------------------------------------------

def get_gymnotoa_env_name():
    '''
    Get the Miniforge3 environment name where the Python packages used by gymnoTOA are
    installed.
    '''

    return 'gymnoTOA environment'

#-------------------------------------------------------------------------------

def get_bioconda_code():
    '''
    Get the Bioconda code used to identify its processes.
    '''

    return 'bioconda'

#-------------------------------------------------------------------------------

def get_bioconda_name():
    '''
    Get the Bioconda name used to title.
    '''

    return 'Bioconda'

#-------------------------------------------------------------------------------

def get_blastplus_code():
    '''
    Get the BLAST+ code used to identify its processes.
    '''

    return 'blast'

#-------------------------------------------------------------------------------

def get_blastplus_name():
    '''
    Get the BLAST+ name used to title.
    '''

    return 'BLAST+'

#-------------------------------------------------------------------------------

def get_blastplus_conda_code():
    '''
    Get the BLAST+ code used to identify the Conda package.
    '''

    return 'blast'

#-------------------------------------------------------------------------------

def get_blastplus_environment():
    '''
    Get the Miniforge3 environment where the BLAST+ software used by gymnoTOA is
    installed.
    '''

    return 'gymnotoa-blast'

#-------------------------------------------------------------------------------

def get_codan_code():
    '''
    Get the CodAn code used to identify its processes.
    '''

    return 'codan'

#-------------------------------------------------------------------------------

def get_codan_name():
    '''
    Get the CodAn name used to title.
    '''

    return 'CodAn'

#-------------------------------------------------------------------------------

def get_codan_conda_code():
    '''
    Get the CodAn code used to identify the Conda package.
    '''

    return 'codan'

#-------------------------------------------------------------------------------

def get_codan_environment():
    '''
    Get the Miniforge3 environment where the CodAn software used by gymnoTOA is
    installed.
    '''

    return 'gymnotoa-codan'

#-------------------------------------------------------------------------------

def get_diamond_code():
    '''
    Get the DIAMOND code used to identify its processes.
    '''

    return 'diamond'

#-------------------------------------------------------------------------------

def get_diamond_name():
    '''
    Get the DIAMOND name used to title.
    '''

    return 'DIAMOND'

#-------------------------------------------------------------------------------

def get_diamond_conda_code():
    '''
    Get the DIAMOND code used to identify the Conda package.
    '''

    return 'diamond'

#-------------------------------------------------------------------------------

def get_diamond_environment():
    '''
    Get the Miniforge3 environment where the DIAMOND software used by gymnoTOA is
    installed.
    '''

    return 'gymnotoa-diamond'

#-------------------------------------------------------------------------------

def check_code(literal, code_list, case_sensitive=False):
    '''
    Check if a text literal is in a code list.
    '''

    # initialize the working list
    w_list = []

    # if the codification is not case sensitive, convert the code and code list to uppercase
    if not case_sensitive:
        try:
            literal = literal.upper()
        except Exception:
            pass
        try:
            w_list = [x.upper() for x in code_list]
        except Exception:
            pass
    else:
        w_list = code_list

    # check if the code is in the code list
    OK = literal in w_list

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def check_int(literal, minimum=(-sys.maxsize - 1), maximum=sys.maxsize):
    '''
    Check if a numeric or text literal is an integer number.
    '''

    # initialize the control variable
    OK = True

    # check the number
    try:
        int(literal)
        int(minimum)
        int(maximum)
    except Exception:
        OK = False
    else:
        if int(literal) < int(minimum) or int(literal) > int(maximum):
            OK = False

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def check_float(literal, minimum=float(-sys.maxsize - 1), maximum=float(sys.maxsize), mne=0.0, mxe=0.0):
    '''
    Check if a numeric or text literal is a float number.
    '''

    # initialize the control variable
    OK = True

    # check the number
    try:
        float(literal)
        float(minimum)
        float(maximum)
        float(mne)
        float(mxe)
    except Exception:
        OK = False
    else:
        if float(literal) < (float(minimum) + float(mne)) or float(literal) > (float(maximum) - float(mxe)):
            OK = False

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def join_text_list_to_literal(text_list):
    '''
    Join a text list in a literal (texts with simple quote and separated by comma).
    '''

    # initialize the literal
    literal = ''

    # concat the items of text list
    for text in text_list:
        literal = f"'{text}'" if literal == '' else f"{literal},'{text}'"

    # return the literal
    return literal

#-------------------------------------------------------------------------------

def check_parameter_list(parameters, key, not_allowed_parameters_list):
    '''
    Check if a string contains a parameter list.
    '''

    # initialize the control variable and error list
    OK = True
    error_list = []

    # get the parameter list
    parameter_list = [x.strip() for x in parameters.split(';')]

    # check the parameter list
    for parameter in parameter_list:
        try:
            if parameter.find('=') > 0:
                pattern = r'^--(.+)=(.+)$'
                mo = re.search(pattern, parameter)
                parameter_name = mo.group(1).strip()
                # -- parameter_value = mo.group(2).strip()
            else:
                pattern = r'^--(.+)$'
                mo = re.search(pattern, parameter)
                parameter_name = mo.group(1).strip()
        except Exception:
            error_list.append(f'*** ERROR: the value of the key "{key}" has to be a valid parameter or NONE.')
            OK = False
            break
        if parameter_name in not_allowed_parameters_list:
            error_list.append(f'*** ERROR: the parameter {parameter_name} is not allowed in "{key}" because it is controled by {get_app_short_name()}.')
            OK = False

    # return the control variable and error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def is_absolute_path(path, operating_system=sys.platform):
    '''
    Check if a path is a absolute path.
    '''

    # initialize control variable
    OK = False

    # check if the path is absolute depending on the operating system
    if operating_system.startswith('linux') or operating_system.startswith('darwin'):
        if path != '':
            # -- OK = is_path_valid(path) and path[0] == '/'
            OK = True
    elif operating_system.startswith('win32'):
        OK = True

    # return control variable
    return OK

#-------------------------------------------------------------------------------

def get_submitting_dict():
    '''
    Get the process submitting dictionary.
    '''

    # build the submitting process dictionary
    submitting_dict = {}
    submitting_dict['download_gymnotoa_db']= {'text': get_process_download_gymnotoa_db_name()}
    submitting_dict['install_miniforge3']= {'text': f'{get_miniforge3_name()} installation'}
    submitting_dict['install_gymnotoa_env']= {'text': f'{get_gymnotoa_env_name()} installation'}
    submitting_dict['install_bioconda_package_list']= {'text': 'Bioconda package list installation'}
    submitting_dict['run_annotation_pipeline']= {'text': get_process_run_annotation_pipeline_name()}
    submitting_dict['restart_annotation_pipeline']= {'text': get_process_restart_annotation_pipeline_name()}
    submitting_dict['run_enrichment_analysis']= {'text': get_process_run_enrichment_analysis_name()}
    submitting_dict['restart_enrichment_analysis']= {'text': get_process_restart_enrichment_analysis_name()}

    # return the submitting process dictionary
    return submitting_dict

#-------------------------------------------------------------------------------

def get_submitting_id(submitting_text):
    '''
    Get the process submitting identification from the submission process text.
    '''

    # initialize the control variable
    submitting_id_found = None

    # get the dictionary of the submitting processes
    submitting_dict = get_submitting_dict()

    # search the submitting process identification
    for key, value in submitting_dict.items():
        if value['text'] == submitting_text:
            submitting_id_found = key
            break

    # return the submitting process identification
    return submitting_id_found

#-------------------------------------------------------------------------------

def get_process_dict():
    '''
    Get the process dictionary.
    '''

    # build the process dictionary
    process_dict = {}
    process_dict[get_process_download_gymnotoa_db_code()]= {'name': get_process_download_gymnotoa_db_name(), 'process_type': get_result_database_subdir()}
    process_dict[get_miniforge3_code()]= {'name': get_miniforge3_name(), 'process_type': get_result_installation_subdir()}
    process_dict[get_gymnotoa_env_code()]= {'name': get_gymnotoa_env_name(), 'process_type': get_result_installation_subdir()}
    process_dict[get_blastplus_code()]= {'name': get_blastplus_name(), 'process_type': get_result_installation_subdir()}
    process_dict[get_codan_code()]= {'name': get_codan_name(), 'process_type': get_result_installation_subdir()}
    process_dict[get_diamond_code()]= {'name': get_diamond_name(), 'process_type': get_result_installation_subdir()}
    process_dict[get_process_run_annotation_pipeline_code()]= {'name': get_process_run_annotation_pipeline_name(), 'process_type': get_result_run_subdir()}
    process_dict[get_process_restart_annotation_pipeline_code()]= {'name': get_process_restart_annotation_pipeline_name(), 'process_type': get_result_run_subdir()}
    process_dict[get_process_run_enrichment_analysis_code()]= {'name': get_process_run_enrichment_analysis_name(), 'process_type': get_result_run_subdir()}
    process_dict[get_process_restart_enrichment_analysis_code()]= {'name': get_process_restart_enrichment_analysis_name(), 'process_type': get_result_run_subdir()}

    # return the process dictionary
    return process_dict

#-------------------------------------------------------------------------------

def get_process_id(process_name):
    '''
    Get the process identification from the process name.
    '''

    # initialize the process identication
    process_id_found = None

    # get the process ddictionary
    process_dict = get_process_dict()

    # search the process identification
    for key, value in process_dict.items():
        if value['name'] == process_name:
            process_id_found = key
            break

    # return the process identication
    return process_id_found

#-------------------------------------------------------------------------------

def get_process_name_list(process_type):
    '''
    Get the list of process name corresponding to a process type.
    '''

    # initialize the process name list
    process_name_list = []

    # get the process ddictionary
    process_dict = get_process_dict()

    # search the process names corresponding to the process type
    for _, value in process_dict.items():
        if value['process_type'] == process_type:
            process_name_list.append(value['name'])

    # return the process name list sorted
    return sorted(process_name_list)

#-------------------------------------------------------------------------------

def get_all_species_code():
    '''
    Get the code used to identify the selection by all species.
    '''

    return 'all_species'

#-------------------------------------------------------------------------------

def get_all_species_name():
    '''
    Get the text used to identify the selection by all species.
    '''

    return 'all species'

#-------------------------------------------------------------------------------

def get_fdr_method_code_list():
    '''
    Get the code list of "fdr_method".
    '''

    return ['bh', 'by']

#-------------------------------------------------------------------------------

def get_fdr_method_code_list_text():
    '''
    Get the code list of "fdr_method" as text.
    '''

    return 'bh (Benjamini-Hochberg) or by (Benjamini-Yekutieli)'

#-------------------------------------------------------------------------------

def get_fdr_method_text_list():
    '''
    Get the list of "fdr_method" as text.
    '''

    return ['Benjamini-Hochberg', 'Benjamini-Yekutieli']

#-------------------------------------------------------------------------------

def get_annotation_result_type_code_list():
    '''
    Get the code list of "fdr_method".
    '''

    return ['complete', 'best']

#-------------------------------------------------------------------------------

def get_annotation_result_type_text_list():
    '''
    Get the list of "fdr_method" as text.
    '''

    return ['all hits per sequence', 'best hit per sequence']

#-------------------------------------------------------------------------------

def get_verbose_code_list():
    '''
    Get the code list of "verbose".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------

def get_verbose_code_list_text():
    '''
    Get the code list of "verbose" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------

def get_trace_code_list():
    '''
    Get the code list of "trace".
    '''

    return ['Y', 'N']

#-------------------------------------------------------------------------------

def get_trace_code_list_text():
    '''
    Get the code list of "trace" as text.
    '''

    return 'Y (yes) or N (no)'

#-------------------------------------------------------------------------------

def get_potential_lncrn():
    '''
    Get the characters to represent potential lncRNA.
    '''

    return 'potential lncRNA'

#-------------------------------------------------------------------------------

def get_na():
    '''
    Get the characters to represent not available.
    '''

    return 'N/A'

#-------------------------------------------------------------------------------

def get_separator():
    '''
    Get the separation line between process steps.
    '''

    return '**************************************************'

#-------------------------------------------------------------------------------

def run_command(command, log, is_script):
    '''
    Run a Bash shell command and redirect stdout and stderr to log.
    '''

    # prepare the command to be execuete on WSL if necessary
    if sys.platform.startswith('win32'):
        if is_script:
            command = command.replace('&', '')
            command = f'wsl bash -c "nohup {command} &>/dev/null"'
        else:
            command = f'wsl bash -c "{command}"'

    # run the command
    current_subprocess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(current_subprocess.stdout.readline, b''):
        line = re.sub(b'[^\x00-\x7F]+', b' ', line) # replace non-ASCII caracters by one blank space
        line = line.decode('iso-8859-1')
        log.write(line)
    rc = current_subprocess.wait()

    # return the return code of the command run
    return rc

#-------------------------------------------------------------------------------

def build_starter(directory, starter_name, script_name, current_run_dir):
    '''
    Build the script to start a process script.
    '''

    # initialize the control variable and the error list
    OK = True
    error_list = []

    # set the starter path
    starter_path = f'{directory}/{starter_name}'

    # write the starter
    try:
        with open(starter_path, mode='w', encoding='iso-8859-1', newline='\n') as file_id:
            file_id.write( '#!/bin/bash\n')
            file_id.write( '#-------------------------------------------------------------------------------\n')
            if sys.platform.startswith('linux') or sys.platform.startswith('win32'):
                file_id.write(f'{current_run_dir}/{script_name} &>>{current_run_dir}/{get_run_log_file()} &\n')
            elif sys.platform.startswith('darwin'):
                file_id.write(f'{current_run_dir}/{script_name} &>{current_run_dir}/{get_run_log_file()} &\n')
    except Exception as e:
        error_list.append(f'*** EXCEPTION: "{e}".')
        error_list.append(f'*** ERROR: The file {starter_path} is not created.')
        OK = False

    # return the control variable and error list
    return (OK, error_list)

#-------------------------------------------------------------------------------

def read_alignment_record(file_name, file_id, record_counter):
    '''
    Read the next record of the alignment file.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # extract data
        # record format: qseqid <field_sep> sseqid <field_sep> pident <field_sep> length <field_sep> mismatch <field_sep> gapopen <field_sep> qstart <field_sep> qend <field_sep> sstart <field_sep> send <field_sep> evalue <field_sep> bitscore <record_sep>
        field_sep = '\t'
        record_sep = '\n'
        data_list = re.split(field_sep, record.replace(record_sep,''))
        try:
            qseqid = data_list[0].strip()
            sseqid = data_list[1].strip()
            pident = data_list[2].strip()
            length = data_list[3].strip()
            mismatch = data_list[4].strip()
            gapopen = data_list[5].strip()
            qstart = data_list[6].strip()
            qend = data_list[7].strip()
            sstart = data_list[8].strip()
            send = data_list[9].strip()
            evalue = data_list[10].strip()
            bitscore = data_list[11].strip()
        except Exception as e:
            raise ProgramException(e, 'F006', os.path.basename(file_name), record_counter) from e

        # set the key
        key = f'{qseqid}-{sseqid}'

        # get the record data dictionary
        data_dict = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'length': length, 'mismatch': mismatch, 'gapopen': gapopen, 'qstart': qstart, 'qend': qend, 'sstart': sstart, 'send': send, 'evalue': evalue, 'bitscore': bitscore}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

def read_functional_annotation_record(file_name, file_id, record_counter):
    '''
    Read the next record of the functional annotation file.
    '''

    # initialize the data dictionary
    data_dict = {}

    # initialize the key
    key = None

    # read next record
    record = file_id.readline()

    # if there is record
    if record != '':

        # extract data
        # record format (old):  qseqid <field_sep> sseqid <field_sep> pident <field_sep> length <field_sep> mismatch <field_sep> gapopen <field_sep> qstart <field_sep> qend <field_sep> sstart <field_sep> send <field_sep> evalue <field_sep> bitscore <field_sep> algorithm <field_sep> ncbi_description <field_sep> ncbi_species <field_sep> tair10_ortholog_seq_id <field_sep> interpro_goterms <field_sep> panther_goterms <field_sep> metacyc_pathways <field_sep> reactome_pathways <field_sep> eggnog_ortholog_seq_id <field_sep> eggnog_ortholog_species <field_sep> eggnog_ogs <field_sep> cog_category <field_sep> eggnog_description <field_sep> eggnog_goterms <field_sep> ec <field_sep> kegg_kos <field_sep> kegg_pathways <field_sep> kegg_modules <field_sep> kegg_reactions <field_sep> kegg_rclasses <field_sep> brite <field_sep> kegg_tc <field_sep> cazy <field_sep> pfams
        # record format: qseqid <field_sep> sseqid <field_sep> pident <field_sep> length <field_sep> mismatch <field_sep> gapopen <field_sep> qstart <field_sep> qend <field_sep> sstart <field_sep> send <field_sep> evalue <field_sep> bitscore <field_sep> algorithm <field_sep> ncbi_description <field_sep> ncbi_species <field_sep> tair10_ortholog_seq_id <field_sep> interpro_goterms <field_sep> panther_goterms <field_sep> metacyc_pathways <field_sep> eggnog_ortholog_seq_id <field_sep> eggnog_ortholog_species <field_sep> eggnog_ogs <field_sep> cog_category <field_sep> eggnog_description <field_sep> eggnog_goterms <field_sep> ec <field_sep> kegg_kos <field_sep> kegg_pathways <field_sep> kegg_modules <field_sep> kegg_reactions <field_sep> kegg_rclasses <field_sep> brite <field_sep> kegg_tc <field_sep> cazy <field_sep> pfams
        field_sep = ';'
        record_sep = '\n'
        data_list = re.split(field_sep, record.replace(record_sep,''))
        try:
            qseqid = data_list[0].strip()
            sseqid = data_list[1].strip()
            pident = data_list[2].strip()
            length = data_list[3].strip()
            mismatch = data_list[4].strip()
            gapopen = data_list[5].strip()
            qstart = data_list[6].strip()
            qend = data_list[7].strip()
            sstart = data_list[8].strip()
            send = data_list[9].strip()
            evalue = data_list[10].strip()
            bitscore = data_list[11].strip()
            algorithm = data_list[12].strip()
            ncbi_description = data_list[13].strip()
            ncbi_species = data_list[14].strip()
            tair10_ortholog_seq_id = data_list[15].strip()
            interpro_goterms = data_list[16].strip()
            panther_goterms = data_list[17].strip()
            metacyc_pathways = data_list[18].strip()
            # -- reactome_pathways = data_list[x].strip()
            eggnog_ortholog_seq_id = data_list[19].strip()
            eggnog_ortholog_species = data_list[20].strip()
            eggnog_ogs = data_list[21].strip()
            cog_category = data_list[22].strip()
            eggnog_description = data_list[23].strip()
            eggnog_goterms = data_list[24].strip()
            ec = data_list[25].strip()
            kegg_kos = data_list[26].strip()
            kegg_pathways = data_list[27].strip()
            kegg_modules = data_list[28].strip()
            kegg_reactions = data_list[29].strip()
            kegg_rclasses = data_list[30].strip()
            brite = data_list[31].strip()
            kegg_tc = data_list[32].strip()
            cazy = data_list[33].strip()
            pfams = data_list[34].strip()
        except Exception as e:
            raise ProgramException(e, 'F006', os.path.basename(file_name), record_counter) from e

        # set the key
        key = f'{qseqid}-{sseqid}'

        # get the record data dictionary
        # -- data_dict = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'length': length, 'mismatch': mismatch, 'gapopen': gapopen, 'qstart': qstart, 'qend': qend, 'sstart': sstart, 'send': send, 'evalue': evalue, 'bitscore': bitscore, 'algorithm': algorithm, 'ncbi_description': ncbi_description, 'ncbi_species': ncbi_species, 'tair10_ortholog_seq_id': tair10_ortholog_seq_id, 'interpro_goterms': interpro_goterms, 'panther_goterms': panther_goterms, 'metacyc_pathways': metacyc_pathways, 'reactome_pathways': reactome_pathways, 'eggnog_ortholog_seq_id': eggnog_ortholog_seq_id, 'eggnog_ortholog_species': eggnog_ortholog_species, 'eggnog_ogs': eggnog_ogs, 'cog_category': cog_category, 'eggnog_description': eggnog_description, 'eggnog_goterms': eggnog_goterms, 'ec': ec, 'kegg_kos': kegg_kos, 'kegg_pathways': kegg_pathways, 'kegg_modules': kegg_modules, 'kegg_reactions': kegg_reactions, 'kegg_rclasses': kegg_rclasses, 'brite': brite, 'kegg_tc': kegg_tc, 'cazy': cazy, 'pfams': pfams}
        data_dict = {'qseqid': qseqid, 'sseqid': sseqid, 'pident': pident, 'length': length, 'mismatch': mismatch, 'gapopen': gapopen, 'qstart': qstart, 'qend': qend, 'sstart': sstart, 'send': send, 'evalue': evalue, 'bitscore': bitscore, 'algorithm': algorithm, 'ncbi_description': ncbi_description, 'ncbi_species': ncbi_species, 'tair10_ortholog_seq_id': tair10_ortholog_seq_id, 'interpro_goterms': interpro_goterms, 'panther_goterms': panther_goterms, 'metacyc_pathways': metacyc_pathways, 'eggnog_ortholog_seq_id': eggnog_ortholog_seq_id, 'eggnog_ortholog_species': eggnog_ortholog_species, 'eggnog_ogs': eggnog_ogs, 'cog_category': cog_category, 'eggnog_description': eggnog_description, 'eggnog_goterms': eggnog_goterms, 'ec': ec, 'kegg_kos': kegg_kos, 'kegg_pathways': kegg_pathways, 'kegg_modules': kegg_modules, 'kegg_reactions': kegg_reactions, 'kegg_rclasses': kegg_rclasses, 'brite': brite, 'kegg_tc': kegg_tc, 'cazy': cazy, 'pfams': pfams}

    # if there is not record
    else:

        # set the key
        key = bytes.fromhex('7E').decode('utf-8')

    # return the record, key and data dictionary
    return record, key, data_dict

#-------------------------------------------------------------------------------

class Const():
    '''
    This class has attributes with values will be used as constants.
    '''

    #---------------

    DEFAULT_FDR_METHOD = 'by'
    DEFAULT_MIN_SEQNUM_ANNOTATIONS = 5
    DEFAULT_MIN_SEQNUM_SPECIES = 10
    DEFAULT_TRACE = 'N'
    DEFAULT_VERBOSE = 'N'

   #---------------

#-------------------------------------------------------------------------------

class Message():
    '''
    This class controls the informative messages printed on the console.
    '''

    #---------------

    verbose_status = False
    trace_status = False

    #---------------

    @staticmethod
    def set_verbose_status(status):
        '''
        Set the verbose status.
        '''

        Message.verbose_status = status

    #---------------

    @staticmethod
    def set_trace_status(status):
        '''
        Set the trace status.
        '''

        Message.trace_status = status

    #---------------

    @staticmethod
    def print(message_type, message_text):
        '''
        Print a message depending to its type.
        '''

        if message_type == 'info':
            print(message_text, file=sys.stdout)
            sys.stdout.flush()
        elif message_type == 'verbose' and Message.verbose_status:
            sys.stdout.write(message_text)
            sys.stdout.flush()
        elif message_type == 'trace' and Message.trace_status:
            print(message_text, file=sys.stdout)
            sys.stdout.flush()
        elif message_type == 'error':
            print(message_text, file=sys.stderr)
            sys.stderr.flush()

    #---------------

#-------------------------------------------------------------------------------

class ProgramException(Exception):
    '''
    This class controls various exceptions that can occur in the execution of the application.
    '''

   #---------------

    def __init__(self, e, code_exception, param1='', param2='', param3=''):
        '''Initialize the object to manage a passed exception.'''

        # call the init method of the parent class
        super().__init__()

        # print the message of the exception
        if e != '':
            Message.print('error', f'*** EXCEPTION: "{e}"')

        # manage the code of exception
        if code_exception == 'B001':
            Message.print('error', f'*** ERROR {code_exception}: The database {param1} can not be connected.')
        elif code_exception == 'B002':
            Message.print('error', f'*** ERROR {code_exception} in sentence:')
            Message.print('error', f'{param1}')
        elif code_exception == 'F001':
            Message.print('error', f'*** ERROR {code_exception}: The file {param1} can not be opened.')
        elif code_exception == 'F002':
            Message.print('error', f'*** ERROR {code_exception}: The GZ compressed file {param1} can not be opened.')
        elif code_exception == 'F003':
            Message.print('error', f'*** ERROR {code_exception}: The file {param1} can not be written.')
        elif code_exception == 'F004':
            Message.print('error', f'*** ERROR {code_exception}: The GZ compressed file {param1} can not be written.')
        elif code_exception == 'F005':
            Message.print('error', f'*** ERROR {code_exception}: The file {param1} has a wrong format.')
        elif code_exception == 'F006':
            Message.print('error', f'*** ERROR {code_exception}: The record # {param2} of file {param1} has a wrong format.')
        elif code_exception == 'P001':
            Message.print('error', f'*** ERROR {code_exception}: The program has parameters with invalid values.')
        elif code_exception == 'L001':
            Message.print('error', f'*** ERROR {code_exception}: There are wrong species identifications.')
        elif code_exception == 'L002':
            Message.print('error', f'*** ERROR {code_exception}: The field {param1} is not found in the variant with identification {param2} and position {param3}.')
        elif code_exception == 'L003':
            Message.print('error', f'*** ERROR {code_exception}: The field {param1} has an invalid value in the variant with identification {param2} and position {param3}.')
        elif code_exception == 'S001':
            Message.print('error', f'*** ERROR {code_exception}: The {param1} OS is not supported.')
        elif code_exception == 'S002':
            Message.print('error', f'*** ERROR {code_exception}: The library {param1} is not installed. Please, review how to install {get_app_short_name()} in the manual.')
        else:
            Message.print('error', f'*** ERROR {code_exception}: The exception is not managed.')

        sys.exit(1)

   #---------------

#-------------------------------------------------------------------------------

class NestedDefaultDict(collections.defaultdict):
    '''
    This class is used to create nested dictionaries.
    '''

    #---------------

    def __init__(self, *args, **kwargs):

        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    #---------------

    def __repr__(self):

        return repr(dict(self))

    #---------------

#-------------------------------------------------------------------------------

class BreakAllLoops(Exception):
    '''
    This class is used to break out of nested loops.
    '''

    pass    #pylint: disable=unnecessary-pass

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'This source contains general functions and classes used in {get_app_long_name()}.')
    sys.exit(0)

#-------------------------------------------------------------------------------
