#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program concats functional annotations corresponding to the BLAST+ alignments using
the database of gymnoTOA (Gymnosperms Taxonomy-oriented Annotation).

This software has been developed by:

    GI en Especies Leñosas (WooSp)
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

    # connect to the gymnoTOA database
    conn = sqllib.connect_database(args.gymnotoa_database)

    # concat functional annotations corresponding to the BLAST+ alignments
    concat_functional_annotations(conn, args.blastp_clade_alignment_file, args.blastx_clade_alignment_file, args.blastn_lncrna_alignment_file, args.complete_functional_annotation_file, args.besthit_functional_annotation_file)

    # close connection to gymnoTOA database
    conn.close()

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program concats functional annotations corresponding to the BLAST+ alignments using\n' \
       f'the {genlib.get_app_short_name()} database.'
    text = f'{genlib.get_app_short_name()} v{genlib.get_app_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='gymnotoa_database', help=f'Path of the {genlib.get_app_short_name} database (mandatory).')
    parser.add_argument('--blastp-alignments', dest='blastp_clade_alignment_file', help='Path of the clade alignment file yielded by blastp (mandatory).')
    parser.add_argument('--blastx-alignments', dest='blastx_clade_alignment_file', help='Path of the clade alignment file yielded by blastp (mandatory).')
    parser.add_argument('--blastn-alignments', dest='blastn_lncrna_alignment_file', help='Path of the lncRNA alignment file yielded by blastn (mandatory).')
    parser.add_argument('--complete_annotations', dest='complete_functional_annotation_file', help='Path of the functional annotation file with all hits per sequence (mandatory).')
    parser.add_argument('--besthit_annotations', dest='besthit_functional_annotation_file', help='Path of the functional annotation file with the best hit per sequence (mandatory).')
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

    # check "gymnotoa_database"
    if args.gymnotoa_database is None:
        genlib.Message.print('error', f'*** The {genlib.get_app_short_name} database is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.gymnotoa_database):
        genlib.Message.print('error', f'*** The file {args.gymnotoa_database} does not exist.')
        OK = False

    # check "blastp_clade_alignment_file"
    if args.blastp_clade_alignment_file is None:
        genlib.Message.print('error', '*** The input blastp alignment file yielded by blastn is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.blastp_clade_alignment_file):
        genlib.Message.print('error', f'*** The file {args.blastp_clade_alignment_file} does not exist.')
        OK = False

    # check "blastx_clade_alignment_file"
    if args.blastx_clade_alignment_file is None:
        genlib.Message.print('error', '*** The input blastx alignment file yielded by blastn is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.blastx_clade_alignment_file):
        genlib.Message.print('error', f'*** The file {args.blastx_clade_alignment_file} does not exist.')
        OK = False
    # check "blastn_lncrna_alignment_file"
    if args.blastn_lncrna_alignment_file is None:
        genlib.Message.print('error', '*** The input lncRNA alignment file yielded by blastn is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.blastn_lncrna_alignment_file):
        genlib.Message.print('error', f'*** The file {args.blastn_lncrna_alignment_file} does not exist.')
        OK = False

    # check "complete_functional_annotation_file"
    if args.complete_functional_annotation_file is None:
        genlib.Message.print('error', '*** The functional annotation file with all hits per sequence is not indicated in the input arguments.')
        OK = False

    # check "besthit_functional_annotation_file"
    if args.besthit_functional_annotation_file is None:
        genlib.Message.print('error', '*** The functional annotation file with  the best hit per sequence is not indicated in the input arguments.')
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

def concat_functional_annotations(conn, blastp_clade_alignment_file, blastx_clade_alignment_file, blastn_lncrna_alignment_file, complete_functional_annotation_file, besthit_functional_annotation_file):
    '''
    Concat functional annotations corresponding to the BLAST+ alignments.
    '''

    # initialize the set of sequence identifications aligned
    qseqid_set = set()

    # open the functional annotation file with all hits per sequence
    if complete_functional_annotation_file.endswith('.gz'):
        try:
            complete_functional_annotation_file_id = gzip.open(complete_functional_annotation_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F004', complete_functional_annotation_file)
    else:
        try:
            complete_functional_annotation_file_id = open(complete_functional_annotation_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', complete_functional_annotation_file)

    # initialize the counter of records written in the functional annotation file with all hits per sequence
    complete_functional_annotation_record_counter = 0

    # open the functional annotation file with the best hit per sequence
    if besthit_functional_annotation_file.endswith('.gz'):
        try:
            besthit_functional_annotation_file_id = gzip.open(besthit_functional_annotation_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F004', besthit_functional_annotation_file)
    else:
        try:
            besthit_functional_annotation_file_id = open(besthit_functional_annotation_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', besthit_functional_annotation_file)

    # initialize the counter of records written in the functional annotation file with the best hit per sequence
    besthit_functional_annotation_record_counter = 0

    # open the clade alignment file yielded by blastp
    if blastp_clade_alignment_file.endswith('.gz'):
        try:
            blastp_clade_alignment_file_id = gzip.open(blastp_clade_alignment_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise genlib.ProgramException(e, 'F002', blastp_clade_alignment_file)
    else:
        try:
            blastp_clade_alignment_file_id = open(blastp_clade_alignment_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise genlib.ProgramException(e, 'F001', blastp_clade_alignment_file)

    # initialize the counter of records corresponding to the clade alignment file yielded by blastp
    blastp_clade_alignment_record_counter = 0

    # read the first record of clade alignment file yielded by blastp
    (blastp_clade_alignment_record, _, blastp_clade_alignment_data_dict) = genlib.read_alignment_record(blastp_clade_alignment_file, blastp_clade_alignment_file_id, blastp_clade_alignment_record_counter)

    # while there are records in the clade alignment file yielded by blastp
    while blastp_clade_alignment_record != '':

        # initialize the old sequence identifications
        old_qseqid = blastp_clade_alignment_data_dict['qseqid']

        # initialize the best evalue and pident
        best_evalue = 1.
        best_pident = 0.

        # while there are records and the same sequence identification
        while blastp_clade_alignment_record != '' and blastp_clade_alignment_data_dict['qseqid'] == old_qseqid:

            # add 1 to record counter
            blastp_clade_alignment_record_counter += 1

            # get alignment data
            qseqid = blastp_clade_alignment_data_dict['qseqid']
            sseqid = blastp_clade_alignment_data_dict['sseqid']
            pident = blastp_clade_alignment_data_dict['pident']
            length = blastp_clade_alignment_data_dict['length']
            mismatch = blastp_clade_alignment_data_dict['mismatch']
            gapopen = blastp_clade_alignment_data_dict['gapopen']
            qstart = blastp_clade_alignment_data_dict['qstart']
            qend = blastp_clade_alignment_data_dict['qend']
            sstart = blastp_clade_alignment_data_dict['sstart']
            send = blastp_clade_alignment_data_dict['send']
            evalue = blastp_clade_alignment_data_dict['evalue']
            bitscore = blastp_clade_alignment_data_dict['bitscore']
            algorithm = 'blastp'

            # get the most frecuent species in sseqid
            (ncbi_description, ncbi_species) = sqllib.get_mmseqs2_seq_mf_data(conn, sseqid)

            # get the TAIR10 ortholog sequence identification
            tair10_ortholog_seq_id = sqllib.get_tair10_ortholog_seq_id(conn, sseqid)

            # get InterproScan functional annotations data
            interproscan_annotation_dict = sqllib.get_interproscan_annotation_dict(conn, sseqid)
            interpro_goterms = interproscan_annotation_dict.get('interpro_goterms', '-')
            panther_goterms = interproscan_annotation_dict.get('panther_goterms', '-')
            metacyc_pathways = interproscan_annotation_dict.get('metacyc_pathways', '-')
            # -- reactome_pathways = annotations_dict.get('reactome_pathways', '-')

            # get eggNOG-mapper functional annotations data
            emapper_annotation_dict = sqllib.get_emapper_annotation_dict(conn, sseqid)
            eggnog_ortholog_seq_id = emapper_annotation_dict.get('ortholog_seq_id', '-')
            eggnog_ortholog_species = emapper_annotation_dict.get('ortholog_species', '-')
            eggnog_ogs = emapper_annotation_dict.get('eggnog_ogs', '-')
            cog_category = emapper_annotation_dict.get('cog_category', '-')
            eggnog_description = emapper_annotation_dict.get('description', '-')
            eggnog_goterms = emapper_annotation_dict.get('goterms', '-')
            ec = emapper_annotation_dict.get('ec', '-')
            kegg_kos = emapper_annotation_dict.get('kegg_kos', '-')
            kegg_pathways = emapper_annotation_dict.get('kegg_pathways', '-')
            kegg_modules = emapper_annotation_dict.get('kegg_modules', '-')
            kegg_reactions = emapper_annotation_dict.get('kegg_reactions', '-')
            kegg_rclasses = emapper_annotation_dict.get('kegg_rclasses', '-')
            brite = emapper_annotation_dict.get('brite', '-')
            kegg_tc = emapper_annotation_dict.get('kegg_tc', '-')
            cazy = emapper_annotation_dict.get('cazy', '-')
            pfams = emapper_annotation_dict.get('pfams', '-')

            # write record of the functional annotation file with all hits per sequence
            # -- functional_annotation_record = f'{qseqid};{sseqid};{pident};{length};{mismatch};{gapopen};{qstart};{qend};{sstart};{send};{evalue};{bitscore};{algorithm};{ncbi_description};{ncbi_species};{tair10_ortholog_seq_id};{interpro_goterms};{panther_goterms};{metacyc_pathways};{reactome_pathways};{eggnog_ortholog_seq_id};{eggnog_ortholog_species};{eggnog_ogs};{cog_category};{eggnog_description};{eggnog_goterms};{ec};{kegg_kos};{kegg_pathways};{kegg_modules};{kegg_reactions};{kegg_rclasses};{brite};{kegg_tc};{cazy};{pfams}'
            functional_annotation_record = f'{qseqid};{sseqid};{pident};{length};{mismatch};{gapopen};{qstart};{qend};{sstart};{send};{evalue};{bitscore};{algorithm};{ncbi_description};{ncbi_species};{tair10_ortholog_seq_id};{interpro_goterms};{panther_goterms};{metacyc_pathways};{eggnog_ortholog_seq_id};{eggnog_ortholog_species};{eggnog_ogs};{cog_category};{eggnog_description};{eggnog_goterms};{ec};{kegg_kos};{kegg_pathways};{kegg_modules};{kegg_reactions};{kegg_rclasses};{brite};{kegg_tc};{cazy};{pfams}'
            complete_functional_annotation_file_id.write(f'{functional_annotation_record}\n')

            # add 1 to the counter of records written in the functional annotation file with all hits per sequence
            complete_functional_annotation_record_counter += 1

            # save the record of the secuence with the best evalue and pident
            if float(evalue) < best_evalue or float(evalue) == best_evalue and float(pident) > best_pident:
                best_functional_annotation_record = functional_annotation_record
                best_evalue = float(evalue)
                best_pident = float(pident)

            # print counters
            genlib.Message.print('verbose', f'\rblastp clade alignment file: {blastp_clade_alignment_record_counter} processed records')

            # read the next record of clade alignment file yielded by blastp
            (blastp_clade_alignment_record, _, blastp_clade_alignment_data_dict) = genlib.read_alignment_record(blastp_clade_alignment_file, blastp_clade_alignment_file_id, blastp_clade_alignment_record_counter)

        # add the sequence identification to the set of sequence identifications aligned
        qseqid_set.add(old_qseqid)

        # write record of the functional annotation file with all hits per sequence
        besthit_functional_annotation_file_id.write(f'{best_functional_annotation_record}\n')

        # add 1 to the counter of records written in the functional annotation file with the best hit per sequence
        besthit_functional_annotation_record_counter += 1

    genlib.Message.print('verbose', '\n')

    # close the clade alignment file yielded by blastp
    blastp_clade_alignment_file_id.close()

    # open the clade alignment file yielded by blastx
    if blastx_clade_alignment_file.endswith('.gz'):
        try:
            blastx_clade_alignment_file_id = gzip.open(blastx_clade_alignment_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise genlib.ProgramException(e, 'F002', blastx_clade_alignment_file)
    else:
        try:
            blastx_clade_alignment_file_id = open(blastx_clade_alignment_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise genlib.ProgramException(e, 'F001', blastx_clade_alignment_file)

    # initialize the counter of records corresponding to the clade alignment file yielded by blastx
    blastx_clade_alignment_record_counter = 0

    # read the first record of clade alignment file yielded by blastx
    (blastx_clade_alignment_record, _, blastx_clade_alignment_data_dict) = genlib.read_alignment_record(blastx_clade_alignment_file, blastx_clade_alignment_file_id, blastx_clade_alignment_record_counter)

    # while there are records in the clade alignment file yielded by blastx
    while blastx_clade_alignment_record != '':

        # initialize the old sequence identifications
        old_qseqid = blastx_clade_alignment_data_dict['qseqid']

        # initialize the best evalue and pident
        best_evalue = 1.
        best_pident = 0.

        # while there are records and the same sequence identification
        while blastx_clade_alignment_record != '' and blastx_clade_alignment_data_dict['qseqid'] == old_qseqid:

            # add 1 to record counter
            blastx_clade_alignment_record_counter += 1

            # get alignment data
            qseqid = blastx_clade_alignment_data_dict['qseqid']
            sseqid = blastx_clade_alignment_data_dict['sseqid']
            pident = blastx_clade_alignment_data_dict['pident']
            length = blastx_clade_alignment_data_dict['length']
            mismatch = blastx_clade_alignment_data_dict['mismatch']
            gapopen = blastx_clade_alignment_data_dict['gapopen']
            qstart = blastx_clade_alignment_data_dict['qstart']
            qend = blastx_clade_alignment_data_dict['qend']
            sstart = blastx_clade_alignment_data_dict['sstart']
            send = blastx_clade_alignment_data_dict['send']
            evalue = blastx_clade_alignment_data_dict['evalue']
            bitscore = blastx_clade_alignment_data_dict['bitscore']
            algorithm = 'blastx'

            # when the "old" sequence identification is not in the sequence identification set
            if old_qseqid not in qseqid_set:

                # get the most frecuent species in sseqid
                (ncbi_description, ncbi_species) = sqllib.get_mmseqs2_seq_mf_data(conn, sseqid)

                # get the TAIR10 ortholog sequence identification
                tair10_ortholog_seq_id = sqllib.get_tair10_ortholog_seq_id(conn, sseqid)

                # get InterproScan functional annotations data
                interproscan_annotation_dict = sqllib.get_interproscan_annotation_dict(conn, sseqid)
                interpro_goterms = interproscan_annotation_dict.get('interpro_goterms', '-')
                panther_goterms = interproscan_annotation_dict.get('panther_goterms', '-')
                metacyc_pathways = interproscan_annotation_dict.get('metacyc_pathways', '-')
                # -- reactome_pathways = annotations_dict.get('reactome_pathways', '-')

                # get eggNOG-mapper functional annotations data
                emapper_annotation_dict = sqllib.get_emapper_annotation_dict(conn, sseqid)
                eggnog_ortholog_seq_id = emapper_annotation_dict.get('ortholog_seq_id', '-')
                eggnog_ortholog_species = emapper_annotation_dict.get('ortholog_species', '-')
                eggnog_ogs = emapper_annotation_dict.get('eggnog_ogs', '-')
                cog_category = emapper_annotation_dict.get('cog_category', '-')
                eggnog_description = emapper_annotation_dict.get('description', '-')
                eggnog_goterms = emapper_annotation_dict.get('goterms', '-')
                ec = emapper_annotation_dict.get('ec', '-')
                kegg_kos = emapper_annotation_dict.get('kegg_kos', '-')
                kegg_pathways = emapper_annotation_dict.get('kegg_pathways', '-')
                kegg_modules = emapper_annotation_dict.get('kegg_modules', '-')
                kegg_reactions = emapper_annotation_dict.get('kegg_reactions', '-')
                kegg_rclasses = emapper_annotation_dict.get('kegg_rclasses', '-')
                brite = emapper_annotation_dict.get('brite', '-')
                kegg_tc = emapper_annotation_dict.get('kegg_tc', '-')
                cazy = emapper_annotation_dict.get('cazy', '-')
                pfams = emapper_annotation_dict.get('pfams', '-')

                # write record of the functional annotation file with all hits per sequence
                # -- functional_annotation_record = f'{qseqid};{sseqid};{pident};{length};{mismatch};{gapopen};{qstart};{qend};{sstart};{send};{evalue};{bitscore};{algorithm};{ncbi_description};{ncbi_species};{tair10_ortholog_seq_id};{interpro_goterms};{panther_goterms};{metacyc_pathways};{reactome_pathways};{eggnog_ortholog_seq_id};{eggnog_ortholog_species};{eggnog_ogs};{cog_category};{eggnog_description};{eggnog_goterms};{ec};{kegg_kos};{kegg_pathways};{kegg_modules};{kegg_reactions};{kegg_rclasses};{brite};{kegg_tc};{cazy};{pfams}'
                functional_annotation_record = f'{qseqid};{sseqid};{pident};{length};{mismatch};{gapopen};{qstart};{qend};{sstart};{send};{evalue};{bitscore};{algorithm};{ncbi_description};{ncbi_species};{tair10_ortholog_seq_id};{interpro_goterms};{panther_goterms};{metacyc_pathways};{eggnog_ortholog_seq_id};{eggnog_ortholog_species};{eggnog_ogs};{cog_category};{eggnog_description};{eggnog_goterms};{ec};{kegg_kos};{kegg_pathways};{kegg_modules};{kegg_reactions};{kegg_rclasses};{brite};{kegg_tc};{cazy};{pfams}'
                complete_functional_annotation_file_id.write(f'{functional_annotation_record}\n')

                # add 1 to the counter of records written in the functional annotation file with all hits per sequence
                complete_functional_annotation_record_counter += 1

                # save the record of the secuence with the best evalue and pident
                if float(evalue) < best_evalue or float(evalue) == best_evalue and float(pident) > best_pident:
                    best_functional_annotation_record = functional_annotation_record
                    best_evalue = float(evalue)
                    best_pident = float(pident)

            # print counters
            genlib.Message.print('verbose', f'\rblastx clade alignment file: {blastx_clade_alignment_record_counter} processed records')

            # read the next record of clade alignment file yielded by blastx
            (blastx_clade_alignment_record, _, blastx_clade_alignment_data_dict) = genlib.read_alignment_record(blastx_clade_alignment_file, blastx_clade_alignment_file_id, blastx_clade_alignment_record_counter)

        # when the "old" sequence identification is not in the sequence identification set
        if old_qseqid not in qseqid_set:

            # add the sequence identification to the set of sequence identifications aligned
            qseqid_set.add(old_qseqid)

            # write record of the functional annotation file with all hits per sequence
            besthit_functional_annotation_file_id.write(f'{best_functional_annotation_record}\n')

            # add 1 to the counter of records written in the functional annotation file with the best hit per sequence
            besthit_functional_annotation_record_counter += 1

    # close the clade alignment file yielded by blastx
    blastx_clade_alignment_file_id.close()

    genlib.Message.print('verbose', '\n')

    # open the lncRNA alignment file yielded by blastn
    if blastn_lncrna_alignment_file.endswith('.gz'):
        try:
            blastn_lncrna_alignment_file_id = gzip.open(blastn_lncrna_alignment_file, mode='rt', encoding='iso-8859-1')
        except Exception as e:
            raise genlib.ProgramException(e, 'F002', blastn_lncrna_alignment_file)
    else:
        try:
            blastn_lncrna_alignment_file_id = open(blastn_lncrna_alignment_file, mode='r', encoding='iso-8859-1')
        except Exception as e:
            raise genlib.ProgramException(e, 'F001', blastn_lncrna_alignment_file)

    # initialize the counter of records of the lncRNA alignment file yielded by blastn
    blastn_lncrna_alignment_record_counter = 0

    # read the first record of lncRNA alignment file yielded by blastn
    (blastn_lncrna_alignment_record, _, blastn_lncrna_alignment_data_dict) = genlib.read_alignment_record(blastn_lncrna_alignment_file, blastn_lncrna_alignment_file_id, blastn_lncrna_alignment_record_counter)

    # while there are records in the lncRNA alignment file yielded by blastn
    while blastn_lncrna_alignment_record != '':

        # add 1 to record counter
        blastn_lncrna_alignment_record_counter += 1

        # get alignment data
        qseqid = blastn_lncrna_alignment_data_dict['qseqid']
        algorithm = 'blastn'

        # when the sequence identification is not in the sequence identification set
        if qseqid not in qseqid_set:

            # add the sequence identification to the set of sequence identifications aligned
            qseqid_set.add(qseqid)

            # write record in the functional annotation files
            # -- functional_annotation_record = f'{qseqid};{genlib.get_potential_lncrn()};-;-;-;-;-;-;-;-;-;-;{algorithm};-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-'
            functional_annotation_record = f'{qseqid};{genlib.get_potential_lncrn()};-;-;-;-;-;-;-;-;-;-;{algorithm};-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-'
            complete_functional_annotation_file_id.write(f'{functional_annotation_record}\n')
            besthit_functional_annotation_file_id.write(f'{functional_annotation_record}\n')

            # add 1 to the counter of records written in the functional annotation file with all hits per sequence
            complete_functional_annotation_record_counter += 1

            # add 1 to the counter of records written in the functional annotation file with the best hit per sequence
            besthit_functional_annotation_record_counter += 1

        # print counters
        genlib.Message.print('verbose', f'\rblastn lncRNA alignment file: {blastn_lncrna_alignment_record_counter} processed records')

        # read the next record of lncRNA alignment file yielded by blastn
        (blastn_lncrna_alignment_record, _, blastn_lncrna_alignment_data_dict) = genlib.read_alignment_record(blastn_lncrna_alignment_file, blastn_lncrna_alignment_file_id, blastn_lncrna_alignment_record_counter)

    # close the lncRNA alignment file yielded by blastn
    blastn_lncrna_alignment_file_id.close()

    # close output files
    complete_functional_annotation_file_id.close()
    besthit_functional_annotation_file_id.close()

    genlib.Message.print('verbose', '\n')
    genlib.Message.print('info', f'The file {complete_functional_annotation_file} is created with {complete_functional_annotation_record_counter} records.')
    genlib.Message.print('info', f'The file {besthit_functional_annotation_file} is created with {besthit_functional_annotation_record_counter} records.')

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
