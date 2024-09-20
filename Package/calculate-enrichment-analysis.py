#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position

#-------------------------------------------------------------------------------

'''
This program calculates the enrichment analysis of GO terms, Metacyc pathways, KEGG KOs and KEGG pathways
from a annotation file and the gymnoTOA database.

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

import numpy as np
import scipy.stats as stats

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

    # calculate the GO term enrichment analysis
    calculate_goterm_enrichment_analysis(conn, args.annotation_file, args.species_name, args.fdr_method, args.min_seqnum_annotations, args.min_seqnum_species, args.goea_file)

    # calculate the Metacyc pathway enrichment analysis
    calculate_metacyc_pathway_enrichment_analysis(conn, args.annotation_file, args.species_name, args.fdr_method, args.min_seqnum_annotations, args.min_seqnum_species, args.mpea_file)

    # calculate the KEGG KO enrichment analysis
    calculate_kegg_ko_enrichment_analysis(conn, args.annotation_file, args.species_name, args.fdr_method, args.min_seqnum_annotations, args.min_seqnum_species, args.koea_file)

    # calculate the KEGG pathway enrichment analysis
    calculate_kegg_pathway_enrichment_analysis(conn, args.annotation_file, args.species_name, args.fdr_method, args.min_seqnum_annotations, args.min_seqnum_species, args.kpea_file)

#-------------------------------------------------------------------------------

def build_parser():
    '''
    Build the parser with the available arguments.
    '''

    # create the parser and add arguments
    description = 'Description: This program calculates the enrichment analysis of GO terms, Metacyc pathways, KEGG KOs\n' \
                  'and KEGG pathways from a annotation file and the gymnoTOA database.'
    text = f'{genlib.get_app_short_name()} v{genlib.get_app_version()} - {os.path.basename(__file__)}\n\n{description}\n'
    usage = f'\r{text.ljust(len("usage:"))}\nUsage: {os.path.basename(__file__)} arguments'
    parser = argparse.ArgumentParser(usage=usage)
    parser._optionals.title = 'Arguments'    #pylint: disable=protected-access
    parser.add_argument('--db', dest='sqlite_database', help='Path of the SQLite database (mandatory).')
    parser.add_argument('--annotations', dest='annotation_file', help='Path of annotation file in CSV format (mandatory).')
    parser.add_argument('--species', dest='species_name', help=f'The species name or "{genlib.get_all_species_code()}" (mandatory).')
    parser.add_argument('--method', dest='fdr_method', help=f'Method used in FDR calcutation: {genlib.get_fdr_method_code_list_text()}; default: {genlib.Const.DEFAULT_FDR_METHOD}.')
    parser.add_argument('--msqannot', dest='min_seqnum_annotations', help=f'Minimum sequence number in annotation; default: {genlib.Const.DEFAULT_MIN_SEQNUM_ANNOTATIONS}.')
    parser.add_argument('--msqspec', dest='min_seqnum_species', help=f'Minimum sequence number in species; default: {genlib.Const.DEFAULT_MIN_SEQNUM_SPECIES}.')
    parser.add_argument('--goea', dest='goea_file', help='Path of the GO term enrichment analysis file (mandatory).')
    parser.add_argument('--mpea', dest='mpea_file', help='Path of the Metacyc pathway enrichment analysis file (mandatory).')
    parser.add_argument('--koea', dest='koea_file', help='Path of the KEGG KO enrichment analysis file (mandatory).')
    parser.add_argument('--kpea', dest='kpea_file', help='Path of the KEGG pathway enrichment analysis file (mandatory).')
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
        OK = False

    # check "annotation_file"
    if args.annotation_file is None:
        genlib.Message.print('error', '*** The annotation file is not indicated in the input arguments.')
        OK = False
    elif not os.path.isfile(args.annotation_file):
        genlib.Message.print('error', f'*** The file {args.annotation_file} does not exist.')
        OK = False

    # check "species"
    if args.species_name is None:
        genlib.Message.print('error', '*** The species is not indicated in the input arguments.')
        OK = False

    # check "fdr_method"
    if args.fdr_method is None:
        args.fdr_method = genlib.Const.DEFAULT_FDR_METHOD
    elif not genlib.check_code(args.fdr_method, genlib.get_fdr_method_code_list(), case_sensitive=False):
        genlib.Message.print('error', f'*** FDR method has to be {genlib.get_fdr_method_code_list_text()}.')
        OK = False
    else:
        args.fdr_method = args.fdr_method.lower()

    # check "min_seqnum_annotations"
    if args.min_seqnum_annotations is None:
        args.min_seqnum_annotations = genlib.Const.DEFAULT_MIN_SEQNUM_ANNOTATIONS
    elif not genlib.check_int(args.min_seqnum_annotations, minimum=1):
        genlib.Message.print('error', 'The minimum sequence number in annotations has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.min_seqnum_annotations = int(args.min_seqnum_annotations)

    # check "min_seqnum_species"
    if args.min_seqnum_species is None:
        args.min_seqnum_species = genlib.Const.DEFAULT_MIN_SEQNUM_SPECIES
    elif not genlib.check_int(args.min_seqnum_species, minimum=1):
        genlib.Message.print('error', 'The minimum sequence number in species has to be an integer number greater than or equal to 1.')
        OK = False
    else:
        args.min_seqnum_species = int(args.min_seqnum_species)

    # check "goea_file"
    if args.goea_file is None:
        genlib.Message.print('error', '*** The GO term enrichment analysis file is not indicated in the input arguments.')
        OK = False

    # check "mpea_file"
    if args.mpea_file is None:
        genlib.Message.print('error', '*** The Metacyc pathway enrichment analysis file is not indicated in the input arguments.')
        OK = False

    # check "koea_file"
    if args.koea_file is None:
        genlib.Message.print('error', '*** The KEGG KO enrichment analysis file is not indicated in the input arguments.')
        OK = False

    # check "kpea_file"
    if args.kpea_file is None:
        genlib.Message.print('error', '*** The KEGG pathway enrichment analysis file is not indicated in the input arguments.')
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

def calculate_goterm_enrichment_analysis(conn, annotation_file, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species, goea_file):
    '''
    calculates the GO term enrichment analysis from a annotation file and the gymnoTOA database.
    '''

    # build the annotation GO term dictionary
    (annotation_goterm_dict, annotation_seqs_wgoterms) = build_annotation_goterm_dict(annotation_file)

    # get the list of GO term identifications involved in the study
    goterm_id_list = sorted(annotation_goterm_dict.keys())

    # build the species GOterm dictionary
    (species_goterm_dict, species_seqs_wgoterms) = build_species_goterm_dict(conn, species_name, goterm_id_list)

    # get the Gene Ontololy dictionary
    gene_ontology_dict = sqllib.get_go_ontology_dict(conn, goterm_id_list)

    # initialize the calculations dictionary
    calcultations_dict = genlib.NestedDefaultDict()

    # perform calulations
    for goterm_id in goterm_id_list:

        # get the annotation data
        annotation_seqs_count = annotation_goterm_dict[goterm_id]
        calcultations_dict[goterm_id]['annotation_seqs_count'] = annotation_seqs_count

        # get the species data
        species_seqs_count =  species_goterm_dict.get(goterm_id, 0)
        calcultations_dict[goterm_id]['species_seqs_count'] = species_seqs_count

        # calculate the enrichment
        try:
            enrichment = (annotation_seqs_count / annotation_seqs_wgoterms) / (species_seqs_count / species_seqs_wgoterms)
        except ZeroDivisionError:
            enrichment = genlib.get_na()
        calcultations_dict[goterm_id]['enrichment'] = enrichment

        # calculate the p-value
        if enrichment != genlib.get_na():
            # -- _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wgoterms], [species_seqs_count, species_seqs_wgoterms]], alternative='two-sided')
            _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wgoterms], [species_seqs_count, species_seqs_wgoterms]], alternative='greater')
            # -- pvalue = stats.hypergeom.sf(annotation_seqs_count, species_seqs_wgoterms, species_seqs_count, annotation_seqs_wgoterms, loc=0)
            if np.isnan(pvalue):
                pvalue = genlib.get_na()
        else:
            pvalue = genlib.get_na()
        calcultations_dict[goterm_id]['pvalue'] = pvalue

        # initilize the FDR data to N/A
        calcultations_dict[goterm_id]['fdr'] = genlib.get_na()

    # get the GO term identification list sorted by the p-value
    temp_goterm_id_list = []    # each item is [GO term, p-value]
    for goterm_id in goterm_id_list:
        pvalue = calcultations_dict[goterm_id]['pvalue']
        if pvalue != genlib.get_na():
            temp_goterm_id_list.append([goterm_id, pvalue])
    pvalue_sorted_goterm_id_list = sorted(temp_goterm_id_list, key=lambda x: float(x[1]), reverse=False)

    # calculate FDR list corresponding to the p-value list
    fdr_list = stats.false_discovery_control(np.array([x[1] for x in pvalue_sorted_goterm_id_list]), axis=0,  method=fdr_method)

    # update FDR data in  the calculations dictionary
    for i, _ in enumerate(pvalue_sorted_goterm_id_list):
        calcultations_dict[pvalue_sorted_goterm_id_list[i][0]]['fdr'] = fdr_list[i]

    # get the GOterm identification list sorted by the FDR
    temp_goterm_id_list_1 = []    # each item is [GOterm, FDR]
    temp_goterm_id_list_2 = []
    for goterm_id in goterm_id_list:
        fdr = calcultations_dict[goterm_id]['fdr']
        if fdr == genlib.get_na():
            temp_goterm_id_list_2.append(goterm_id)
        else:
            temp_goterm_id_list_1.append([goterm_id, fdr])
    fdr_sorted_goterm_id_list_1 = sorted(temp_goterm_id_list_1, key=lambda x: float(x[1]), reverse=False)
    fdr_sorted_goterm_id_list = [x[0] for x in fdr_sorted_goterm_id_list_1] + temp_goterm_id_list_2

    # open the GO term enrichment analysis file
    if goea_file.endswith('.gz'):
        try:
            goea_file_id = gzip.open(goea_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', goea_file) from None
    else:
        try:
            goea_file_id = open(goea_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', goea_file)

    # write the header
    goea_file_id.write( '"GOterm";"Description";"Namespace";"Sequences# with this GOterm in annotations";"Sequences# with GOterms in annotations";"Sequences# with this GOterm in species";"Sequences# with GOtermss in species";"Enrichment";"p-value";"FDR"\n')

    # write data records
    for goterm_id in fdr_sorted_goterm_id_list:

        # get Gene Ontology data
        description = gene_ontology_dict[goterm_id]['goterm_name']
        namespace = gene_ontology_dict[goterm_id]['namespace']

        # get the annotation data
        annotation_seqs_count = calcultations_dict[goterm_id]['annotation_seqs_count']

        # get the species data
        species_seqs_count =  calcultations_dict[goterm_id]['species_seqs_count']

        # get the enrichment
        enrichment = calcultations_dict[goterm_id]['enrichment']

        # get the p-value
        pvalue = calcultations_dict[goterm_id]['pvalue']

        # get the FDR
        fdr = calcultations_dict[goterm_id]['fdr']

        # write record
        if annotation_seqs_count >= min_seqnum_annotations and species_seqs_count >= min_seqnum_species:
            goea_file_id.write(f'"{goterm_id}";"{description}";"{namespace}";{annotation_seqs_count};{annotation_seqs_wgoterms};{species_seqs_count};{species_seqs_wgoterms};{enrichment};{pvalue};{fdr}\n')

    # close the GO term enrichment analysis file
    goea_file_id.close()

    genlib.Message.print('verbose', '\n')
    genlib.Message.print('info', f'The file {goea_file} is created.')

#-------------------------------------------------------------------------------

def build_annotation_goterm_dict(annotation_file):
    '''
    Build the annotation GO term dictionary from the annotations file.
    '''

    # initialize annotation GO term dictionary
    annotation_goterm_dict = {}

    # initialize the counter of annotations sequences with GO terms
    annotation_seqs_wgoterms = 0

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

        # set the old sequence identification
        old_seq_id = data_dict['qseqid']

        # initialize the list of GO term identifications corresponding to the sequence
        goterm_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the GO term identifications and add them into the GO term identification list
            # goterms format: "goterm_id1|goterm_id2|...|gotermo_idn"
            if data_dict['interpro_goterms'] != '' and data_dict['interpro_goterms'] != '-':
                interpro_goterm_id_list = data_dict['interpro_goterms'].split('|')
                goterm_id_list.extend(interpro_goterm_id_list)
            if data_dict['panther_goterms'] != '' and  data_dict['panther_goterms'] != '-':
                panther_goterm_id_list = data_dict['panther_goterms'].split('|')
                goterm_id_list.extend(panther_goterm_id_list)
            if data_dict['eggnog_goterms'] != '' and  data_dict['eggnog_goterms'] != '-':
                eggnog_goterm_id_list = data_dict['eggnog_goterms'].split('|')
                goterm_id_list.extend(eggnog_goterm_id_list)

            genlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            genlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the annotation GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = annotation_goterm_dict.get(goterm_id, 0)
                annotation_goterm_dict[goterm_id] = counter + 1

        # increase the counter of annotations sequences with GO terms
        if goterm_id_list != []:
            annotation_seqs_wgoterms += 1

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation GO term dictionary
    return annotation_goterm_dict, annotation_seqs_wgoterms

#-------------------------------------------------------------------------------

def build_species_goterm_dict(conn, species_name, goterm_id_list):
    '''
    Build the species GO term dictionary from the annotations file.
    '''

    # initialize the species GO term dictionary
    species_goterm_dict = {}

    # initialize the counter of species sequences with GO terms
    species_seqs_wgoterms = 0

    # get the dictionary of the GO terms of each cluster corresponding to the species
    goterms_per_cluster_dict = sqllib.get_goterms_per_cluster_dict(conn, species_name)

    # initialize the species cluster counter
    species_cluster_counter = 0

    for _, data_dict in goterms_per_cluster_dict.items():

        # add 1 to  the species cluster counter
        species_cluster_counter += 1

        # initialize the list of GO term identifications corresponding to the sequence
        goterm_id_list = []

        # extract the GO term identifications and add them into the GO term identification list
        # goterms format: "goterm_id1|goterm_id2|...|gotermo_idn"
        if data_dict['interpro_goterms'] != '' and data_dict['interpro_goterms'] != '-':
            interpro_goterm_id_list = data_dict['interpro_goterms'].split('|')
            goterm_id_list.extend(interpro_goterm_id_list)
        if data_dict['panther_goterms'] != '' and  data_dict['panther_goterms'] != '-':
            panther_goterm_id_list = data_dict['panther_goterms'].split('|')
            goterm_id_list.extend(panther_goterm_id_list)
        if data_dict['eggnog_goterms'] != '' and  data_dict['eggnog_goterms'] != '-':
            eggnog_goterm_id_list = data_dict['eggnog_goterms'].split('|')
            goterm_id_list.extend(eggnog_goterm_id_list)

        # get the list of GO term identifications without duplicates
        goterm_id_set = set(goterm_id_list)
        goterm_id_list = sorted(goterm_id_set)

        # increase the GO term identifications per sequence in the species GOterm dictionary
        if goterm_id_list != []:
            for goterm_id in goterm_id_list:
                counter = species_goterm_dict.get(goterm_id, 0)
                species_goterm_dict[goterm_id] = counter + 1

        # increase the counter of speciess sequences with GO terms
        if goterm_id_list != []:
            species_seqs_wgoterms += 1

        genlib.Message.print('verbose', f'\rProcessed {species_name} clusters: {species_cluster_counter}')

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{species_cluster_counter} clusters read.')

    # return the species GOterm dictionary
    return species_goterm_dict, species_seqs_wgoterms

#-------------------------------------------------------------------------------

def calculate_metacyc_pathway_enrichment_analysis(conn, annotation_file, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species, mpea_file):
    '''
    calculates the Metacyc pathway enrichment analysis from a annotation file and the gymnoTOA database.
    '''

    # build the annotation Metacyc pathway dictionary
    (annotation_metacyc_pathway_dict, annotation_seqs_wmetacycpathways) = build_annotation_metacyc_pathway_dict(annotation_file)

    # get the list of Metacyc pathway identifications involved in the study
    metacyc_pathway_id_list = sorted(annotation_metacyc_pathway_dict.keys())

    # build the species Metacyc pathway dictionary
    (species_metacyc_pathway_dict, species_seqs_wmetacycpathways) = build_species_metacyc_pathway_dict(conn, species_name, metacyc_pathway_id_list)

    # initialize the calculations dictionary
    calcultations_dict = genlib.NestedDefaultDict()

    # perform calulations
    for metacyc_pathway_id in metacyc_pathway_id_list:

        # get the annotation data
        annotation_seqs_count = annotation_metacyc_pathway_dict[metacyc_pathway_id]
        calcultations_dict[metacyc_pathway_id]['annotation_seqs_count'] = annotation_seqs_count

        # get the species data
        species_seqs_count =  species_metacyc_pathway_dict.get(metacyc_pathway_id, 0)
        calcultations_dict[metacyc_pathway_id]['species_seqs_count'] = species_seqs_count

        # calculate the enrichment
        try:
            enrichment = (annotation_seqs_count / annotation_seqs_wmetacycpathways) / (species_seqs_count / species_seqs_wmetacycpathways)
        except ZeroDivisionError:
            enrichment = genlib.get_na()
        calcultations_dict[metacyc_pathway_id]['enrichment'] = enrichment

        # calculate the p-value
        if enrichment != genlib.get_na():
            # -- _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wmetacycpathways], [species_seqs_count, species_seqs_wmetacycpathways]], alternative='two-sided'))
            _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wmetacycpathways], [species_seqs_count, species_seqs_wmetacycpathways]], alternative='greater')
            # -- pvalue = stats.hypergeom.sf(annotation_seqs_count, species_seqs_wmetacycpathways, species_seqs_count, annotation_seqs_wmetacycpathways, loc=0)
            if np.isnan(pvalue):
                pvalue = genlib.get_na()
        else:
            pvalue = genlib.get_na()
        calcultations_dict[metacyc_pathway_id]['pvalue'] = pvalue

        # initilize the FDR data to N/A
        calcultations_dict[metacyc_pathway_id]['fdr'] = genlib.get_na()

    # get the Metacyc pathway identification list sorted by the p-value
    temp_metacyc_pathway_id_list = []    # each item is [Metacyc pathway, p-value]
    for metacyc_pathway_id in metacyc_pathway_id_list:
        pvalue = calcultations_dict[metacyc_pathway_id]['pvalue']
        if pvalue != genlib.get_na():
            temp_metacyc_pathway_id_list.append([metacyc_pathway_id, pvalue])
    pvalue_sorted_metacyc_pathway_id_list = sorted(temp_metacyc_pathway_id_list, key=lambda x: float(x[1]), reverse=False)

    # calculate FDR list corresponding to the p-value list
    fdr_list = stats.false_discovery_control(np.array([x[1] for x in pvalue_sorted_metacyc_pathway_id_list]), axis=0,  method=fdr_method)

    # update FDR data in  the calculations dictionary
    for i, _ in enumerate(pvalue_sorted_metacyc_pathway_id_list):
        calcultations_dict[pvalue_sorted_metacyc_pathway_id_list[i][0]]['fdr'] = fdr_list[i]

    # get the Metacyc pathway identification list sorted by the FDR
    temp_metacyc_pathway_id_list_1 = []    # each item is [Metacyc pathway, FDR]
    temp_metacyc_pathway_id_list_2 = []
    for metacyc_pathway_id in metacyc_pathway_id_list:
        fdr = calcultations_dict[metacyc_pathway_id]['fdr']
        if fdr == genlib.get_na():
            temp_metacyc_pathway_id_list_2.append(metacyc_pathway_id)
        else:
            temp_metacyc_pathway_id_list_1.append([metacyc_pathway_id, fdr])
    fdr_sorted_metacyc_pathway_id_list_1 = sorted(temp_metacyc_pathway_id_list_1, key=lambda x: float(x[1]), reverse=False)
    fdr_sorted_metacyc_pathway_id_list = [x[0] for x in fdr_sorted_metacyc_pathway_id_list_1] + temp_metacyc_pathway_id_list_2

    # open the Metacyc pathway enrichment analysis file
    if mpea_file.endswith('.gz'):
        try:
            mpea_file_id = gzip.open(mpea_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', mpea_file) from None
    else:
        try:
            mpea_file_id = open(mpea_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', mpea_file)

    # write the header
    mpea_file_id.write( '"Metacyc pathway";"Sequences# with this Metacyc pathway in annotations";"Sequences# with Metacyc pathways in annotations";"Sequences# with this Metacyc pathway in species";"Sequences# with Metacyc pathways in species";"Enrichment";"p-value";"FDR"\n')

    # write data records
    for metacyc_pathway_id in fdr_sorted_metacyc_pathway_id_list:

        # get the annotation data
        annotation_seqs_count = calcultations_dict[metacyc_pathway_id]['annotation_seqs_count']

        # get the species data
        species_seqs_count =  calcultations_dict[metacyc_pathway_id]['species_seqs_count']

        # get the enrichment
        enrichment = calcultations_dict[metacyc_pathway_id]['enrichment']

        # get the p-value
        pvalue = calcultations_dict[metacyc_pathway_id]['pvalue']

        # get the FDR
        fdr = calcultations_dict[metacyc_pathway_id]['fdr']

        # write record
        if annotation_seqs_count >= min_seqnum_annotations and species_seqs_count >= min_seqnum_species:
            mpea_file_id.write(f'"{metacyc_pathway_id}";{annotation_seqs_count};{annotation_seqs_wmetacycpathways};{species_seqs_count};{species_seqs_wmetacycpathways};{enrichment};{pvalue};{fdr}\n')

    # close Metacyc pathway enrichment analysis file
    mpea_file_id.close()

    genlib.Message.print('verbose', '\n')
    genlib.Message.print('info', f'The file {mpea_file} is created.')

#-------------------------------------------------------------------------------

def build_annotation_metacyc_pathway_dict(annotation_file):
    '''
    Build the annotation Metacyc pathways dictionary from the annotations file.
    '''

    # initialize annotation Metacyc pathway dictionary
    annotation_metacyc_pathway_dict = {}

    # initialize the counter of annotations sequences with Metacyc pathways
    annotation_seqs_wmetacycpathways = 0

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

        # set the old sequence identification
        old_seq_id = data_dict['qseqid']

        # initialize the list of Metacyc pathway identifications corresponding to the sequence
        metacyc_pathway_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the Metacyc pathway identifications and add them into the Metacyc pathway identification list
            # Metacyc pathway format: "metacyc_pathway_id1|metacyc_pathway_id2|...|metacyc_pathway_idn"
            if data_dict['metacyc_pathways'] != '' and data_dict['metacyc_pathways'] != '-':
                metacyc_pathway_id_list.extend(data_dict['metacyc_pathways'].split('|'))

            genlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            genlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of Metacyc pathway identifications without duplicates
        metacyc_pathway_id_set = set(metacyc_pathway_id_list)
        metacyc_pathway_id_list = sorted(metacyc_pathway_id_set)

        # increase the Metacyc pathway identifications per sequence in the annotation Metacyc pathway dictionary
        if metacyc_pathway_id_list != []:
            for metacyc_pathway_id in metacyc_pathway_id_list:
                counter = annotation_metacyc_pathway_dict.get(metacyc_pathway_id, 0)
                annotation_metacyc_pathway_dict[metacyc_pathway_id] = counter + 1

        # increase the counter of annotations sequences with Metacyc pathways
        if metacyc_pathway_id_list != []:
            annotation_seqs_wmetacycpathways += 1

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation Metacyc pathway dictionary
    return annotation_metacyc_pathway_dict, annotation_seqs_wmetacycpathways

#-------------------------------------------------------------------------------

def build_species_metacyc_pathway_dict(conn, species_name, metacyc_pathway_id_list):
    '''
    Build the species Metacyc pathway dictionary from the annotations file.
    '''

    # initialize the species Metacyc pathway dictionary
    species_metacyc_pathway_dict = {}

    # initialize the counter of species sequences with Metacyc pathways
    species_seqs_wmetacycpataways = 0

    # get the dictionary of the Metacyc pathways of each cluster corresponding to the species
    metacyc_pathways_per_cluster_dict = sqllib.get_metacyc_pathways_per_cluster_dict(conn, species_name)

    # initialize the species cluster counter
    species_cluster_counter = 0

    for _, data_dict in metacyc_pathways_per_cluster_dict.items():

        # add 1 to  the species cluster counter
        species_cluster_counter += 1

        # initialize the list of Metacyc pathway identifications corresponding to the sequence
        metacyc_pathway_id_list = []

        # extract the Metacyc pathway identifications and add them into the Metacy pathway identification list
        # Metacyc pathway format: "metacyc_pathway_id1|metacyc_pathway_id2|...|metacyc_pathway_idn"
        if data_dict['metacyc_pathways'] != '' and data_dict['metacyc_pathways'] != '-':
            metacyc_pathway_id_list.extend(data_dict['metacyc_pathways'].split('|'))

        # get the list of Metacyc pathway identifications without duplicates
        metacyc_pathway_id_set = set(metacyc_pathway_id_list)
        metacyc_pathway_id_list = sorted(metacyc_pathway_id_set)

        # increase the Metacyc pathway identifications per sequence in the species Metacyc pathway dictionary
        if metacyc_pathway_id_list != []:
            for metacyc_pathway_id in metacyc_pathway_id_list:
                counter = species_metacyc_pathway_dict.get(metacyc_pathway_id, 0)
                species_metacyc_pathway_dict[metacyc_pathway_id] = counter + 1

        # increase the counter of speciess sequences with GO terms
        if metacyc_pathway_id_list != []:
            species_seqs_wmetacycpataways += 1

        genlib.Message.print('verbose', f'\rProcessed {species_name} clusters: {species_cluster_counter}')

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{species_cluster_counter} clusters read.')

    # return the species Metacyc pathway dictionary
    return species_metacyc_pathway_dict, species_seqs_wmetacycpataways

#-------------------------------------------------------------------------------

def calculate_kegg_ko_enrichment_analysis(conn, annotation_file, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species, koea_file):
    '''
    calculates the KO enrichment analysis from a annotation file and the gymnoTOA database.
    '''

    # build the annotation KEGG KO dictionary
    (annotation_kegg_ko_dict, annotation_seqs_wkeggkos) = build_annotation_kegg_ko_dict(annotation_file)

    # get the list of KEGG KO identifications involved in the study
    kegg_ko_id_list = sorted(annotation_kegg_ko_dict.keys())

    # build the species KEGG KO dictionary
    (species_kegg_ko_dict, species_seqs_seqs_wkeggkos) = build_species_kegg_ko_dict(conn, species_name, kegg_ko_id_list)

    # initialize the calculations dictionary
    calcultations_dict = genlib.NestedDefaultDict()

    # perform calulations
    for kegg_ko_id in kegg_ko_id_list:

        # get the annotation data
        annotation_seqs_count = annotation_kegg_ko_dict[kegg_ko_id]
        calcultations_dict[kegg_ko_id]['annotation_seqs_count'] = annotation_seqs_count

        # get the species data
        species_seqs_count =  species_kegg_ko_dict.get(kegg_ko_id, 0)
        calcultations_dict[kegg_ko_id]['species_seqs_count'] = species_seqs_count

        # calculate the enrichment
        try:
            enrichment = (annotation_seqs_count / annotation_seqs_wkeggkos) / (species_seqs_count / species_seqs_seqs_wkeggkos)
        except ZeroDivisionError:
            enrichment = genlib.get_na()
        calcultations_dict[kegg_ko_id]['enrichment'] = enrichment

        # calculate the p-value
        if enrichment != genlib.get_na():
            # -- _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wkeggkos], [species_seqs_count, species_seqs_wkeggkos]], alternative='two-sided'))
            _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wkeggkos], [species_seqs_count, species_seqs_seqs_wkeggkos]], alternative='greater')
            # -- pvalue = stats.hypergeom.sf(annotation_seqs_count, species_seqs_wkeggkos, species_seqs_count, annotation_seqs_wkeggkos, loc=0)
            if np.isnan(pvalue):
                pvalue = genlib.get_na()
        else:
            pvalue = genlib.get_na()
        calcultations_dict[kegg_ko_id]['pvalue'] = pvalue

        # initilize the FDR data to N/A
        calcultations_dict[kegg_ko_id]['fdr'] = genlib.get_na()

    # get the KEGG KO identification list sorted by the p-value
    temp_kegg_ko_id_list = []    # each item is [KEGG KO, p-value]
    for kegg_ko_id in kegg_ko_id_list:
        pvalue = calcultations_dict[kegg_ko_id]['pvalue']
        if pvalue != genlib.get_na():
            temp_kegg_ko_id_list.append([kegg_ko_id, pvalue])
    pvalue_sorted_kegg_ko_id_list = sorted(temp_kegg_ko_id_list, key=lambda x: float(x[1]), reverse=False)

    # calculate FDR list corresponding to the p-value list
    fdr_list = stats.false_discovery_control(np.array([x[1] for x in pvalue_sorted_kegg_ko_id_list]), axis=0,  method=fdr_method)

    # update FDR data in  the calculations dictionary
    for i, _ in enumerate(pvalue_sorted_kegg_ko_id_list):
        calcultations_dict[pvalue_sorted_kegg_ko_id_list[i][0]]['fdr'] = fdr_list[i]

    # get the KEGG KO identification list sorted by the FDR
    temp_kegg_ko_id_list_1 = []    # each item is [KEGG KO, FDR]
    temp_kegg_ko_id_list_2 = []
    for kegg_ko_id in kegg_ko_id_list:
        fdr = calcultations_dict[kegg_ko_id]['fdr']
        if fdr == genlib.get_na():
            temp_kegg_ko_id_list_2.append(kegg_ko_id)
        else:
            temp_kegg_ko_id_list_1.append([kegg_ko_id, fdr])
    fdr_sorted_kegg_ko_id_list_1 = sorted(temp_kegg_ko_id_list_1, key=lambda x: float(x[1]), reverse=False)
    fdr_sorted_kegg_ko_id_list = [x[0] for x in fdr_sorted_kegg_ko_id_list_1] + temp_kegg_ko_id_list_2

    # open the KEGG KO enrichment analysis file
    if koea_file.endswith('.gz'):
        try:
            koea_file_id = gzip.open(koea_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', koea_file) from None
    else:
        try:
            koea_file_id = open(koea_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', koea_file)

    # write the header
    koea_file_id.write( '"KEGG KO pathway";"Sequences# with this KEGG KO in annotations";"Sequences# with KEGG KOs in annotations";"Sequences# with this KEGG KO in species";"Sequences# with KEGG KOs in species";"Enrichment";"p-value";"FDR"\n')

    # write data records
    for kegg_ko_id in fdr_sorted_kegg_ko_id_list:

        # get the annotation data
        annotation_seqs_count = calcultations_dict[kegg_ko_id]['annotation_seqs_count']

        # get the species data
        species_seqs_count =  calcultations_dict[kegg_ko_id]['species_seqs_count']

        # get the enrichment
        enrichment = calcultations_dict[kegg_ko_id]['enrichment']

        # get the p-value
        pvalue = calcultations_dict[kegg_ko_id]['pvalue']

        # get the FDR
        fdr = calcultations_dict[kegg_ko_id]['fdr']

        # write record
        if annotation_seqs_count >= min_seqnum_annotations and species_seqs_count >= min_seqnum_species:
            koea_file_id.write(f'"{kegg_ko_id}";{annotation_seqs_count};{annotation_seqs_wkeggkos};{species_seqs_count};{species_seqs_seqs_wkeggkos};{enrichment};{pvalue};{fdr}\n')

    # close KEGG KO enrichment analysis file
    koea_file_id.close()

    genlib.Message.print('verbose', '\n')
    genlib.Message.print('info', f'The file {koea_file} is created.')

#-------------------------------------------------------------------------------

def build_annotation_kegg_ko_dict(annotation_file):
    '''
    Build the annotation KEGG KO dictionary from the annotations file.
    '''

    # initialize annotation KO dictionary
    annotation_kegg_ko_dict = {}

    # initialize the counter of annotations sequences with KEGG KOs
    annotation_seqs_wkeggkos = 0

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

        # set the old sequence identification
        old_seq_id = data_dict['qseqid']

        # initialize the list of KEGG KO identifications corresponding to the sequence
        kegg_ko_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the KEGG KO identifications and add them into the KEGG KO identification list
            # KO format: "kegg_ko_id1|kegg_ko_id2|...|kegg_ko_idn"
            if data_dict['kegg_kos'] != '' and data_dict['kegg_kos'] != '-':
                kegg_ko_id_list.extend(data_dict['kegg_kos'].split('|'))

            genlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            genlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of KEE KO identifications without duplicates
        kegg_ko_id_set = set(kegg_ko_id_list)
        kegg_ko_id_list = sorted(kegg_ko_id_set)

        # increase the KEGG KO identifications per sequence in the annotation KEGG KO dictionary
        if kegg_ko_id_list != []:
            for kegg_ko_id in kegg_ko_id_list:
                counter = annotation_kegg_ko_dict.get(kegg_ko_id, 0)
                annotation_kegg_ko_dict[kegg_ko_id] = counter + 1

        # increase the counter of annotations sequences with KEGG KOs
        if kegg_ko_id_list != []:
            annotation_seqs_wkeggkos += 1

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the KEGG KO dictionary
    return annotation_kegg_ko_dict, annotation_seqs_wkeggkos

#-------------------------------------------------------------------------------

def build_species_kegg_ko_dict(conn, species_name, kegg_ko_id_list):
    '''
    Build the species KEGG KO dictionary from the annotations file.
    '''

    # initialize the species KEGG KO dictionary
    species_kegg_ko_dict = {}

    # initialize the counter of species sequences with KEGG KOs
    species_seqs_wkeggkos = 0

    # get the dictionary of the KEGG KOs of each cluster corresponding to the species
    kegg_kos_per_cluster_dict = sqllib.get_kegg_kos_per_cluster_dict(conn, species_name)

    # initialize the species cluster counter
    species_cluster_counter = 0

    for _, data_dict in kegg_kos_per_cluster_dict.items():

        # add 1 to  the species cluster counter
        species_cluster_counter += 1

        # initialize the list of KEGG KO identifications corresponding to the sequence
        kegg_ko_id_list = []

        # extract the KEGG KO identifications and add them into the KEGG KO identification list
        # KEGG KO format: "kegg_ko_id1|kegg_ko_id2|...|kegg_ko_idn"
        if data_dict['kegg_kos'] != '' and data_dict['kegg_kos'] != '-':
            kegg_ko_id_list.extend(data_dict['kegg_kos'].split('|'))

        # get the list of KEGG KO identifications without duplicates
        kegg_ko_id_set = set(kegg_ko_id_list)
        kegg_ko_id_list = sorted(kegg_ko_id_set)

        # increase the KEGG KO identifications per sequence in the species KEGG KO dictionary
        if kegg_ko_id_list != []:
            for kegg_ko_id in kegg_ko_id_list:
                counter = species_kegg_ko_dict.get(kegg_ko_id, 0)
                species_kegg_ko_dict[kegg_ko_id] = counter + 1

        # increase the counter of speciess sequences with GO terms
        if kegg_ko_id_list != []:
            species_seqs_wkeggkos += 1

        genlib.Message.print('verbose', f'\rProcessed {species_name} clusters: {species_cluster_counter}')

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{species_cluster_counter} clusters read.')

    # return the species KEGG KO pathway dictionary
    return species_kegg_ko_dict, species_seqs_wkeggkos

#-------------------------------------------------------------------------------

def calculate_kegg_pathway_enrichment_analysis(conn, annotation_file, species_name, fdr_method, min_seqnum_annotations, min_seqnum_species, kpea_file):
    '''
    calculates the KEGG pathway enrichment analysis from a annotation file and the gymnoTOA database.
    '''

    # build the annotation KEGG pathway dictionary
    (annotation_kegg_pathway_dict, annotation_seqs_wkeggpathways) = build_annotation_kegg_pathway_dict(annotation_file)

    # get the list of KEGG pathway identifications involved in the study
    kegg_pathway_id_list = sorted(annotation_kegg_pathway_dict.keys())

    # build the species KEGG pathway dictionary
    (species_kegg_pathway_dict, species_seqs_wkeggpathways) = build_species_kegg_pathway_dict(conn, species_name, kegg_pathway_id_list)

    # initialize the calculations dictionary
    calcultations_dict = genlib.NestedDefaultDict()

    # perform calulations
    for kegg_pathway_id in kegg_pathway_id_list:

        # get the annotation data
        annotation_seqs_count = annotation_kegg_pathway_dict[kegg_pathway_id]
        calcultations_dict[kegg_pathway_id]['annotation_seqs_count'] = annotation_seqs_count

        # get the species data
        species_seqs_count =  species_kegg_pathway_dict.get(kegg_pathway_id, 0)
        calcultations_dict[kegg_pathway_id]['species_seqs_count'] = species_seqs_count

        # calculate the enrichment
        try:
            enrichment = (annotation_seqs_count / annotation_seqs_wkeggpathways) / (species_seqs_count / species_seqs_wkeggpathways)
        except ZeroDivisionError:
            enrichment = genlib.get_na()
        calcultations_dict[kegg_pathway_id]['enrichment'] = enrichment

        # calculate the p-value
        if enrichment != genlib.get_na():
            # -- _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wkeggpathways], [species_seqs_count, species_seqs_wkeggpathways]], alternative='two-sided'))
            _, pvalue = stats.fisher_exact([[annotation_seqs_count, annotation_seqs_wkeggpathways], [species_seqs_count, species_seqs_wkeggpathways]], alternative='greater')
            # -- pvalue = stats.hypergeom.sf(annotation_seqs_count, species_seqs_wkeggpathways, species_seqs_count, annotation_seqs_wkeggpathways, loc=0)
            if np.isnan(pvalue):
                pvalue = genlib.get_na()
        else:
            pvalue = genlib.get_na()
        calcultations_dict[kegg_pathway_id]['pvalue'] = pvalue

        # initilize the FDR data to N/A
        calcultations_dict[kegg_pathway_id]['fdr'] = genlib.get_na()

    # get the KEGG pathway identification list sorted by the p-value
    temp_kegg_pathway_id_list = []    # each item is [KEGG pathway, p-value]
    for kegg_pathway_id in kegg_pathway_id_list:
        pvalue = calcultations_dict[kegg_pathway_id]['pvalue']
        if pvalue != genlib.get_na():
            temp_kegg_pathway_id_list.append([kegg_pathway_id, pvalue])
    pvalue_sorted_kegg_pathway_id_list = sorted(temp_kegg_pathway_id_list, key=lambda x: float(x[1]), reverse=False)

    # calculate FDR list corresponding to the p-value list
    fdr_list = stats.false_discovery_control(np.array([x[1] for x in pvalue_sorted_kegg_pathway_id_list]), axis=0,  method=fdr_method)

    # update FDR data in  the calculations dictionary
    for i, _ in enumerate(pvalue_sorted_kegg_pathway_id_list):
        calcultations_dict[pvalue_sorted_kegg_pathway_id_list[i][0]]['fdr'] = fdr_list[i]

    # get the KEGG pathway identification list sorted by the FDR
    temp_kegg_pathway_id_list_1 = []    # each item is [KEGG pathway, FDR]
    temp_kegg_pathway_id_list_2 = []
    for kegg_pathway_id in kegg_pathway_id_list:
        fdr = calcultations_dict[kegg_pathway_id]['fdr']
        if fdr == genlib.get_na():
            temp_kegg_pathway_id_list_2.append(kegg_pathway_id)
        else:
            temp_kegg_pathway_id_list_1.append([kegg_pathway_id, fdr])
    fdr_sorted_kegg_pathway_id_list_1 = sorted(temp_kegg_pathway_id_list_1, key=lambda x: float(x[1]), reverse=False)
    fdr_sorted_kegg_pathway_id_list = [x[0] for x in fdr_sorted_kegg_pathway_id_list_1] + temp_kegg_pathway_id_list_2

    # open the KEGG pathway enrichment analysis file
    if kpea_file.endswith('.gz'):
        try:
            kpea_file_id = gzip.open(kpea_file, mode='wt', encoding='iso-8859-1', newline='\n')
        except Exception:
            raise genlib.ProgramException('F004', kpea_file) from None
    else:
        try:
            kpea_file_id = open(kpea_file, mode='w', encoding='iso-8859-1', newline='\n')
        except Exception as e:
            raise genlib.ProgramException(e, 'F003', kpea_file)

    # write the header
    kpea_file_id.write( '"KEGG pathway";"Sequences# with this KEGG pathway in annotations";"Sequences# with KEGG pathways in annotations";"Sequences# with this KEGG pathway in species";"Sequences# with KEGG pathways in species";"Enrichment";"p-value";"FDR"\n')

    # write data records
    for kegg_pathway_id in fdr_sorted_kegg_pathway_id_list:

        # get the annotation data
        annotation_seqs_count = calcultations_dict[kegg_pathway_id]['annotation_seqs_count']

        # get the species data
        species_seqs_count =  calcultations_dict[kegg_pathway_id]['species_seqs_count']

        # get the enrichment
        enrichment = calcultations_dict[kegg_pathway_id]['enrichment']

        # get the p-value
        pvalue = calcultations_dict[kegg_pathway_id]['pvalue']

        # get the FDR
        fdr = calcultations_dict[kegg_pathway_id]['fdr']

        # write record
        if annotation_seqs_count >= min_seqnum_annotations and species_seqs_count >= min_seqnum_species:
            kpea_file_id.write(f'"{kegg_pathway_id}";{annotation_seqs_count};{annotation_seqs_wkeggpathways};{species_seqs_count};{species_seqs_wkeggpathways};{enrichment};{pvalue};{fdr}\n')

    # close KEGG pathway enrichment analysis file
    kpea_file_id.close()

    genlib.Message.print('verbose', '\n')
    genlib.Message.print('info', f'The file {kpea_file} is created.')

#-------------------------------------------------------------------------------

def build_annotation_kegg_pathway_dict(annotation_file):
    '''
    Build the annotation KEGG pathways dictionary from the annotations file.
    '''

    # initialize annotation KEGG pathway dictionary
    annotation_kegg_pathway_dict = {}

    # initialize the counter of annotations sequences with KEGG pathways
    annotation_seqs_wkeggpathways = 0

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

        # set the old sequence identification
        old_seq_id = data_dict['qseqid']

        # initialize the list of KEGG pathway identifications corresponding to the sequence
        kegg_pathway_id_list = []

        # while there are records and the same sequence identification
        while record != '' and data_dict['qseqid'] == old_seq_id:

            # add 1 to the annotation counter
            annotation_counter += 1

            # extract the KEGG pathway identifications and add them into the KEGG pathway identification list
            # KEGG pathway format: "kegg_pathway_id1|kegg_pathway_id2|...|kegg_pathway_idn"
            if data_dict['kegg_pathways'] != '' and data_dict['kegg_pathways'] != '-':
                kegg_pathway_id_list.extend(data_dict['kegg_pathways'].split('|'))

            genlib.Message.print('verbose', f'\rProcessed annotations: {annotation_counter}')

            # read the next record of the annotation file
            (record, key, data_dict) = genlib.read_functional_annotation_record(annotation_file, annotation_file_id, annotation_counter)
            genlib.Message.print('trace', f'key: {key} - record: {record}')

        # get the list of KEGG pathway identifications without duplicates
        kegg_pathway_id_set = set(kegg_pathway_id_list)
        kegg_pathway_id_list = sorted(kegg_pathway_id_set)

        # increase the KEGG pathway identifications per sequence in the annotation KEGG pathway dictionary
        if kegg_pathway_id_list != []:
            for kegg_pathway_id in kegg_pathway_id_list:
                counter = annotation_kegg_pathway_dict.get(kegg_pathway_id, 0)
                annotation_kegg_pathway_dict[kegg_pathway_id] = counter + 1

        # increase the counter of annotations sequences with KEGG pathways
        if kegg_pathway_id_list != []:
            annotation_seqs_wkeggpathways += 1

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{annotation_counter} records read in annotation file.')

    # close annotation file
    annotation_file_id.close()

    # return the annotation KEGG pathway dictionary
    return annotation_kegg_pathway_dict, annotation_seqs_wkeggpathways

#-------------------------------------------------------------------------------

def build_species_kegg_pathway_dict(conn, species_name, kegg_pathway_id_list):
    '''
    Build the species KEGG pathway dictionary from the annotations file.
    '''

    # initialize the species KEGG pathway dictionary
    species_kegg_pathway_dict = {}

    # initialize the counter of species sequences with KEGG pathways
    species_seqs_wkeggpataways = 0

    # get the dictionary of the KEGG pathways of each cluster corresponding to the species
    kegg_pathways_per_cluster_dict = sqllib.get_kegg_pathways_per_cluster_dict(conn, species_name)

    # initialize the species cluster counter
    species_cluster_counter = 0

    for _, data_dict in kegg_pathways_per_cluster_dict.items():

        # add 1 to  the species cluster counter
        species_cluster_counter += 1

        # initialize the list of KEGG pathway identifications corresponding to the sequence
        kegg_pathway_id_list = []

        # extract the KEGG pathway identifications and add them into the KEGG pathway identification list
        # KEGG pathway format: "kegg_pathway_id1|kegg_pathway_id2|...|kegg_pathway_idn"
        if data_dict['kegg_pathways'] != '' and data_dict['kegg_pathways'] != '-':
            kegg_pathway_id_list.extend(data_dict['kegg_pathways'].split('|'))

        # get the list of KEGG pathway identifications without duplicates
        kegg_pathway_id_set = set(kegg_pathway_id_list)
        kegg_pathway_id_list = sorted(kegg_pathway_id_set)

        # increase the KEGG pathway identifications per sequence in the species KEGG pathway dictionary
        if kegg_pathway_id_list != []:
            for kegg_pathway_id in kegg_pathway_id_list:
                counter = species_kegg_pathway_dict.get(kegg_pathway_id, 0)
                species_kegg_pathway_dict[kegg_pathway_id] = counter + 1

        # increase the counter of speciess sequences with GO terms
        if kegg_pathway_id_list != []:
            species_seqs_wkeggpataways += 1

        genlib.Message.print('verbose', f'\rProcessed {species_name} clusters: {species_cluster_counter}')

    genlib.Message.print('verbose', '\n')

    # print summary
    genlib.Message.print('info', f'{species_cluster_counter} clusters read.')

    # return the species KEGG pathway dictionary
    return species_kegg_pathway_dict, species_seqs_wkeggpataways

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
    sys.exit(0)

#-------------------------------------------------------------------------------
