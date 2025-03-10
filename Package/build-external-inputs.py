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
This program builds files to input in external applications such as agriGO or REVIGO.

This software has been developed by:

    GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
    Dpto. Sistemas y Recursos Naturales
    ETSI Montes, Forestal y del Medio Natural
    Universidad Politecnica de Madrid
    https://github.com/ggfhf/

Licence: GNU General Public Licence Version 3.
'''

#-------------------------------------------------------------------------------

import argparse
import gzip
import os
import sys

import genlib

#-------------------------------------------------------------------------------

def main():
    '''
    Main line of the program.
    '''

    # check the operating system
    genlib.check_os()

    # get and check the arguments
    parser = build_parser()
    args = parser.parse_args()
    check_args(args)

    # calculate functional statistics
    build_external_inputs(args.annotation_file, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program builds files to input in external applications such as agriGO or REVIGO.'
    text = f'{genlib.get_app_short_name()} v{genlib.get_app_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--annotations', dest='annotation_file', help='Path of annotation file in CSV format (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of the directory to save input files to external applications (mandatory).')
    parser.add_argument('--verbose', dest='verbose', help=f'Additional job status info during the run: {genlib.get_verbose_code_list_text()}; default: {genlib.Const.DEFAULT_VERBOSE}.')
    parser.add_argument('--trace', dest='trace', help=f'Additional info useful to the developer team: {genlib.get_trace_code_list_text()}; default: {genlib.Const.DEFAULT_TRACE}.')

    # return the paser
    return parser

#-------------------------------------------------------------------------------

def check_args(args):
    '''
    Check the input arguments.
    '''

    # initialize the control variable
    OK = True

    # check "annotation_file"
    if args.annotation_file is None:
        genlib.Message.print('error', '*** The annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        genlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        genlib.Message.print('error', '*** The directory to save input files to external applications is not indicated in the input arguments.')
        OK = False

    # check "verbose"
    if args.verbose is None:
        args.verbose = genlib.Const.DEFAULT_VERBOSE
    elif not genlib.check_code(args.verbose, genlib.get_verbose_code_list(), case_sensitive=False):
        genlib.Message.print('error', f'*** verbose has to be {genlib.get_verbose_code_list_text()}.')
        OK = False
    if args.verbose.upper() == 'Y':
        genlib.Message.set_verbose_status(True)

    # check "trace"
    if args.trace is None:
        args.trace = genlib.Const.DEFAULT_TRACE
    elif not genlib.check_code(args.trace, genlib.get_trace_code_list(), case_sensitive=False):
        genlib.Message.print('error', f'*** trace has to be {genlib.get_trace_code_list_text()}.')
        OK = False
    if args.trace.upper() == 'Y':
        genlib.Message.set_trace_status(True)

    # if there are errors, exit with exception
    if not OK:
        raise genlib.ProgramException('', 'P001')

#-------------------------------------------------------------------------------

def build_external_inputs(annotation_file, output_dir):
    '''
    Build files to input in external applications such as agriGO or REVIGO.
    '''

    # initialize dictionaries
    agrigo_input_dict = {}
    revigo_input_dict = {}

    # open the annotation file
    if annotation_file.endswith('.gz'):
        try:
            annotation_file_id = gzip.open(annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception:
            raise genlib.ProgramException('F002', annotation_file) from None
    else:
        try:
            annotation_file_id = open(annotation_file, mode='r', encoding='iso-8859-1')
        except Exception:
            raise genlib.ProgramException('F001', annotation_file) from None

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the annotation file (header)
    (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)

    # read the secord record of the annotation file (first data record)
    (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)
    genlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # initialize the old sequence identification
        old_seq_id = data_dict['qseqid']

        # initialize the lists of GO term identifications per sequence
        interpro_goterm_id_list = []
        panther_goterm_id_list = []
        eggnog_goterm_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the GO term identifications and add them into the GO term identifications list.
            # goterms format: "goterm_id1|goterm_id2|...|gotermo_idn"
            if data_dict['interpro_goterms'] != '' and data_dict['interpro_goterms'] != '-':
                interpro_goterm_id_list.extend(data_dict['interpro_goterms'].split('|'))
            if data_dict['panther_goterms'] != '' and  data_dict['panther_goterms'] != '-':
                panther_goterm_id_list.extend(data_dict['panther_goterms'].split('|'))
            if data_dict['eggnog_goterms'] != '' and  data_dict['eggnog_goterms'] != '-':
                eggnog_goterm_id_list.extend(data_dict['eggnog_goterms'].split('|'))

            genlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            genlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list with unique GO term identifications
        goterm_id_set = set(interpro_goterm_id_list + panther_goterm_id_list + eggnog_goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the agriGO input dictionary
        if goterm_id_list != []:
            goterm_id_set = agrigo_input_dict.get(old_seq_id, set())
            goterm_id_set.update(goterm_id_list)
            agrigo_input_dict[old_seq_id] = goterm_id_set

        # increase counters of GO term identifications in the REVIGO input dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = revigo_input_dict.get(goterm_id, 0)
                revigo_input_dict[goterm_id] = counter + 1

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # write input file to agriGO
    write_agrigo_input_file(agrigo_input_dict, output_dir)

    # write input file to REVIGO
    write_revigo_input_file(revigo_input_dict, output_dir)

    # show OK message
    genlib.Message.print('info', f'The input files to external applications are save in {output_dir}.')

#-------------------------------------------------------------------------------

def write_agrigo_input_file(agrigo_input_dict, output_dir):
    '''
    Write the AgriGO input file.
    '''

    # get the Agrigo input file name
    agrigo_input_file = f'{output_dir}/agrigo-input-file.txt'

    # open the Agrigo input file
    if agrigo_input_file.endswith('.gz'):
        try:
            agrigo_input_file_id = gzip.open(agrigo_input_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', agrigo_input_file) from None
    else:
        try:
            agrigo_input_file_id = open(agrigo_input_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', agrigo_input_file)

    # write data record
    for key in sorted(agrigo_input_dict.keys()):
        goterm_id_set = agrigo_input_dict[key]
        for goterm_id in sorted(list(goterm_id_set)):
            agrigo_input_file_id.write(f'{key} {goterm_id}\n')

    # close Agrigo input file
    agrigo_input_file_id.close()

#-------------------------------------------------------------------------------

def write_revigo_input_file(revigo_input_dict, output_dir):
    '''
    Write the REVIGO input file.
    '''

    # get the REVIGO input file name
    revigo_input_file = f'{output_dir}/revigo-input-file.txt'

    # open the REVIGO input file
    if revigo_input_file.endswith('.gz'):
        try:
            revigo_input_file_id = gzip.open(revigo_input_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', revigo_input_file) from None
    else:
        try:
            revigo_input_file_id = open(revigo_input_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', revigo_input_file)

    # write data record
    for key in sorted(revigo_input_dict.keys()):
        revigo_input_file_id.write(f'{key} {revigo_input_dict[key]}\n')

    # close REVIGO input file
    revigo_input_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
