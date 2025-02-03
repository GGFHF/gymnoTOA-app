#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program calculates functional annotation statistics.

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
import sqllib

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

    # connect to the SQLite database
    conn = sqllib.connect_database(args.sqlite_database)

    # calculate functional annotation statistics
    calculate_functional_stats(conn, args.functional_annotation_file, args.output_dir)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates functional annotation statistics.'
    text = f'{genlib.get_app_short_name()} v{genlib.get_app_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--annotations', dest='functional_annotation_file', help='Path of functional annotation file in CSV format (mandatory).')
    parser.add_argument('--outdir', dest='output_dir', help='Path of the directory to save statistics files (mandatory).')
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

    # check "sqlite_database"
    if args.sqlite_database is None:
        genlib.Message.print('error', '*** The SQLite database is not indicated in the input arguments.')
        OK = False

    # check "functional_annotation_file"
    if args.functional_annotation_file is None:
        genlib.Message.print('error', '*** The functional annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.functional_annotation_file):
        genlib.Message.print('error', f'*** The file {args.functional_annotation_file} does not exist.')
        OK = False

    # check "output_dir"
    if args.output_dir is None:
        genlib.Message.print('error', '*** The directory to save statistics files is not indicated in the input arguments.')
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

def calculate_functional_stats(conn, functional_annotation_file, output_dir):
    '''
    Calculate functional annotation statistics.
    '''

    # initialize the statistics dictionaries
    species_stats_dict = {}
    go_stats_dict = {}
    seq_num_per_goterm_id_num_stats_dict = {}

    # open the functional annotation file
    if functional_annotation_file.endswith('.gz'):
        try:
            functional_annotation_file_id = gzip.open(functional_annotation_file, mode='rt', encoding='iso-8859-1')
        except Exception:
            raise genlib.ProgramException('F002', functional_annotation_file) from None
    else:
        try:
            functional_annotation_file_id = open(functional_annotation_file, mode='r', encoding='iso-8859-1')
        except Exception:
            raise genlib.ProgramException('F001', functional_annotation_file) from None

    # initialize the annotation counter
    annotation_counter = 0

    # read the first record of the functional annotation file (header)
    (record, key, data_dict) = genlib.read_functional_annotation_record(functional_annotation_file, functional_annotation_file_id, annotation_counter)

    # read the secord record of the functional annotation file (first data record)
    (record, key, data_dict) = genlib.read_functional_annotation_record(functional_annotation_file, functional_annotation_file_id, annotation_counter)
    genlib.Message.print('trace', f'key: {key} - record: {record}')

    # while there are records
    while record != '':

        # initialize the old sequence identifications
        old_qseqid = data_dict['qseqid']
        old_sseqid = data_dict['sseqid']

        # initialize the best evalue and pident
        best_evalue = 1.
        best_pident = 0.

        # initialize the lists of GO term identifications per sequence
        goterm_ids_per_seq_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_qseqid:

            # if the sequence matched is not a potential lncRNA
            if data_dict['sseqid'] != genlib.get_potential_lncrn():

                # add 1 to the annotation counter
                annotation_counter += 1

                # increase the species counters in the corresponding statistics dictionary
                species_data = species_stats_dict.get(data_dict['ncbi_species'], {'best': 0, 'complete': 0})
                species_data['complete'] = species_data['complete'] + 1
                species_stats_dict[data_dict['ncbi_species']] = species_data

                # extract the GO term identifications and add them into the GO term identifications list.
                # goterms format: "goterm_id1|goterm_id2|...|gotermo_idn"
                if data_dict['interpro_goterms'] != '' and data_dict['interpro_goterms'] != '-':
                    interpro_goterm_id_list = data_dict['interpro_goterms'].split('|')
                else:
                    interpro_goterm_id_list = []
                if data_dict['panther_goterms'] != '' and  data_dict['panther_goterms'] != '-':
                    panther_goterm_id_list = data_dict['panther_goterms'].split('|')
                else:
                    panther_goterm_id_list = []
                if data_dict['eggnog_goterms'] != '' and  data_dict['eggnog_goterms'] != '-':
                    eggnog_goterm_id_list = data_dict['eggnog_goterms'].split('|')
                else:
                    eggnog_goterm_id_list = []
                goterm_id_set = set(interpro_goterm_id_list + panther_goterm_id_list + eggnog_goterm_id_list)
                goterm_id_list = sorted(goterm_id_set)

                # increase the GO term identification counters in the corresponding statistics dictionary
                for goterm_id in goterm_id_list:
                    goterm_data = go_stats_dict.get(goterm_id, {'best': 0, 'complete': 0})
                    goterm_data['complete'] = goterm_data['complete'] + 1
                    go_stats_dict[goterm_id] = goterm_data

                # add GO term identifications to the list of GO term identifications per sequence
                for goterm_id in goterm_id_list:
                    if goterm_id not in goterm_ids_per_seq_list:
                        goterm_ids_per_seq_list.append(goterm_id)

                # save the species with best evalue and pident
                if float(data_dict['evalue']) < best_evalue or float(data_dict['evalue']) == best_evalue and float(data_dict['pident']) > best_pident:
                    best_evalue = float(data_dict['evalue'])
                    best_pident = float(data_dict['pident'])
                    best_species = data_dict['ncbi_species']
                    best_goterm_id_list = goterm_id_list

            genlib.Message.print('verbose', f'\rProcessed functional annotations: {annotation_counter}')

            # read the next record of the functional annotation file
            (record, key, data_dict) = genlib.read_functional_annotation_record(functional_annotation_file, functional_annotation_file_id, annotation_counter)
            genlib.Message.print('trace', f'key: {key} - record: {record}')

        # if the old sequence matched is not a potential lncRNA
        if old_sseqid != genlib.get_potential_lncrn():

            # increase the species counters in the corresponding statistics dictionary (best evalue and pident case)
            species_data = species_stats_dict.get(best_species, {'best': 0, 'complete': 0})
            species_data['best'] = species_data['best'] + 1
            species_stats_dict[best_species] = species_data

            # increase the GO term identification counters in the corresponding statistics dictionary (best evalue and pident case)
            for goterm_id in best_goterm_id_list:
                goterm_data = go_stats_dict.get(goterm_id, {'best': 0, 'complete': 0})
                goterm_data['best'] = goterm_data['best'] + 1
                go_stats_dict[goterm_id] = goterm_data

            # increase the sequence number per Gene Ontology identification number in the corresponding statistics dictionary
            seq_per_go_data = seq_num_per_goterm_id_num_stats_dict.get(len(goterm_ids_per_seq_list), 0)
            seq_num_per_goterm_id_num_stats_dict[len(goterm_ids_per_seq_list)] = seq_per_go_data + 1

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{annotation_counter} records read in functional annotation file.')

    # close functional annotation file
    functional_annotation_file_id.close()

    # build phylogenic statistics files
    build_phylogenic_data_frecuency(species_stats_dict, output_dir, stats_code='species')

    # build ontology statistics files
    build_goterm_data_frecuency(conn, go_stats_dict, output_dir)
    build_x_per_y_stats(seq_num_per_goterm_id_num_stats_dict, output_dir, stats_code='seq-per-goterm')

    # show OK message
    genlib.Message.print('info', f'The statistics files are save in {output_dir}.')

#-------------------------------------------------------------------------------

def build_x_per_y_stats(stats_dict, output_dir, stats_code):
    '''
   Build a data per other data statistics file
    '''

    # get the stats file name
    stats_file = f'{output_dir}/stats-{stats_code}.csv'

    # open the statistics file
    if stats_file.endswith('.gz'):
        try:
            stats_file_id = gzip.open(stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', stats_file) from None
    else:
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', stats_file)

    # write the header
    if stats_code == 'seq-per-goterm':
        stats_file_id.write( '"goterm_num";"seq_num"\n')

    # write data record
    for key in sorted(stats_dict.keys()):
        stats_file_id.write(f'"{key}";"{stats_dict[key]}"\n')

    # close statistics file
    stats_file_id.close()

#-------------------------------------------------------------------------------

def build_phylogenic_data_frecuency(stats_dict, output_dir, stats_code):
    '''
    Build a phylogenic data frecuency file.
    '''

    # get the stats file name
    stats_file = f'{output_dir}/stats-{stats_code}.csv'

    # open the statistics file
    if stats_file.endswith('.gz'):
        try:
            stats_file_id = gzip.open(stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', stats_file) from None
    else:
        try:
            stats_file_id = open(stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', stats_file)

    # write the header
    if stats_code == 'species':
        stats_file_id.write( '"species";"best_hit";"all_hits"\n')

    # write data record
    for key in sorted(stats_dict.keys()):
        if stats_code == 'species':
            if len(key.split()) == 2 and key[0].isalpha() and key[0].isupper() and not key.endswith('sp.') and key.find('AltName') == -1:
                stats_file_id.write(f'''"{key}";{stats_dict[key]['best']};{stats_dict[key]['complete']}\n''')

    # close statistics file
    stats_file_id.close()

#-------------------------------------------------------------------------------

def build_goterm_data_frecuency(conn, goterm_id_stats_dict, output_dir):
    '''
    Build a GO term data frencuency file.
    '''

    # iitialize namespace statistics dictionary
    namespace_stats_dict = {}

    # get the GO ontology dictionary
    go_ontology_dictionary = sqllib.get_go_ontology_dict(conn, goterm_id_list=[])

    # get the stats file names
    goterm_id_stats_file = f'{output_dir}/stats-goterms.csv'
    namespace_stats_file = f'{output_dir}/stats-namespaces.csv'

    # open the file of statistics by GO identifier
    if goterm_id_stats_file.endswith('.gz'):
        try:
            goterm_id_stats_file_id = gzip.open(goterm_id_stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', goterm_id_stats_file) from None
    else:
        try:
            goterm_id_stats_file_id = open(goterm_id_stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', goterm_id_stats_file)

    # write the header in the file of statistics by GO term identifier
    goterm_id_stats_file_id.write( '"goterm_id";"goterm_name";"namespace";"best_hit";"all_hits"\n')

    # write data in the file of statistics by GO identifier and accumulate data in the namespace statistics dictionary
    for key in sorted(goterm_id_stats_dict.keys()):
        try:
            goterm_id_stats_file_id.write(f'''"{key}";"{go_ontology_dictionary[key]['goterm_name']}";"{go_ontology_dictionary[key]['namespace']}";{goterm_id_stats_dict[key]['best']};{goterm_id_stats_dict[key]['complete']}\n''')
            namespace_data = namespace_stats_dict.get(go_ontology_dictionary[key]['namespace'], {'best': 0, 'complete': 0})
            namespace_data['best'] = namespace_data['best'] + goterm_id_stats_dict[key]['best']
            namespace_data['complete'] = namespace_data['complete'] + goterm_id_stats_dict[key]['complete']
            namespace_stats_dict[go_ontology_dictionary[key]['namespace']] = namespace_data
        except Exception:
            goterm_id_stats_file_id.write(f'''"{key}";"N/A";"N/A";{goterm_id_stats_dict[key]['best']};{goterm_id_stats_dict[key]['complete']}\n''')
            namespace_data = namespace_stats_dict.get('N/A', {'best': 0, 'complete': 0})
            namespace_data['best'] = namespace_data['best'] + goterm_id_stats_dict[key]['best']
            namespace_data['complete'] = namespace_data['complete'] + goterm_id_stats_dict[key]['complete']
            namespace_stats_dict['N/A'] = namespace_data

    # close the file of statistics by GO term identifier
    goterm_id_stats_file_id.close()

    # open the file of statistics by namespace
    if namespace_stats_file.endswith('.gz'):
        try:
            namespace_stats_file_id = gzip.open(namespace_stats_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F004', namespace_stats_file)
    else:
        try:
            namespace_stats_file_id = open(namespace_stats_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException('F003', namespace_stats_file)

    # write the header in the file of statistics by namespace
    namespace_stats_file_id.write( '"namespace";"best_hit";"all_hits"\n')

    # write data in the file of statistics by namespace
    for key in sorted(namespace_stats_dict.keys()):

        # write data record
        namespace_stats_file_id.write(f'''"{key}";{namespace_stats_dict[key]['best']};{namespace_stats_dict[key]['complete']}\n''')

    # close the file of statistics by namespace
    namespace_stats_file_id.close()

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
