#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-except
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=multiple-statements
# pylint: disable=too-many-lines

#-------------------------------------------------------------------------------

'''
This source contains functions for the maintenance of gymnoTOA
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

import sqlite3
import sys

import genlib

#-------------------------------------------------------------------------------

def connect_database(database_path):
    '''
    Connect to the database.
    '''

    # connect to the database
    try:
        conn = sqlite3.connect(database_path)
    except Exception as e:
        raise genlib.ProgramException(e, 'B001', database_path)

    # return connection
    return conn

#-------------------------------------------------------------------------------
# table "interproscan_annotations"
#-------------------------------------------------------------------------------

def get_interproscan_annotation_dict(conn, cluster_id):
    '''
    Get the row data from the table "interproscan_annotations" corresponding to
    a cluster identification.
    '''

    # initialize the dictionary
    annotations_dict = {}

    # select rows from the table "interproscan_annotations"
    sentence = f'''
                SELECT cluster_id, interpro_goterms, panther_goterms, x_goterms, metacyc_pathways, reactome_pathways, x_pathways
                    FROM interproscan_annotations
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        annotations_dict = {'cluster_id': row[0], 'interpro_goterms': row[1], 'panther_goterms': row[2], 'x_goterms': row[3], 'metacyc_pathways': row[4], 'reactome_pathways': row[5], 'x_pathways': row[6]}

    # return the dictionary
    return annotations_dict

#-------------------------------------------------------------------------------

def get_metacyc_pathways_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the MetaCyc pathways of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    pathways_per_cluster_dict = {}

    # select rows from the table "interproscan_annotations"
    if species_name == genlib.get_all_species_code():
        sentence = '''
                   SELECT cluster_id, metacyc_pathways
                       FROM interproscan_annotations
                   '''
    else:
        sentence = f'''
                    SELECT cluster_id, metacyc_pathways
                        FROM interproscan_annotations
                        WHERE cluster_id in (SELECT DISTINCT cluster_id
                                                FROM mmseqs2_relationships
                                                where species like "%{species_name}%");
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        pathways_per_cluster_dict[row[0]] = {'metacyc_pathways': row[1]}

    # return the dictionary
    return pathways_per_cluster_dict

#-------------------------------------------------------------------------------
# table "emapper_annotations"
#-------------------------------------------------------------------------------

def get_emapper_annotation_dict(conn, cluster_id):
    '''
    Get the row data from the table "emapper_annotations" corresponding to
    a cluster identification.
    '''

    # initialize the dictionary
    annotations_dict = {}

    # select rows from the table "emapper_annotations"
    sentence = f'''
                SELECT cluster_id, ortholog_seq_id, ortholog_species, eggnog_ogs, cog_category, description, goterms, ec, kegg_kos, kegg_pathways, kegg_modules, kegg_reactions, kegg_rclasses, brite, kegg_tc, cazy, pfams
                    FROM emapper_annotations
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)


    # add row data to the dictionary
    for row in rows:
        annotations_dict = {'cluster_id': row[0], 'ortholog_seq_id': row[1], 'ortholog_species': row[2], 'eggnog_ogs': row[3], 'cog_category': row[4], 'description': row[5], 'goterms': row[6], 'ec': row[7], 'kegg_kos': row[8], 'kegg_pathways': row[9], 'kegg_modules': row[10], 'kegg_reactions': row[11], 'kegg_rclasses': row[12], 'brite': row[13], 'kegg_tc': row[14], 'cazy': row[15], 'pfams': row[16]}

    # return the dictionary
    return annotations_dict

#-------------------------------------------------------------------------------

def get_kegg_kos_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the KEGG KOs of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    kos_per_cluster_dict = {}

    # select rows from the table "emapper_annotations"
    if species_name == genlib.get_all_species_code():
        sentence = '''
                   SELECT cluster_id, kegg_kos
                       FROM emapper_annotations
                   '''
    else:
        sentence = f'''
                    SELECT cluster_id, kegg_kos
                        FROM emapper_annotations
                        WHERE cluster_id in (SELECT DISTINCT cluster_id
                                                FROM mmseqs2_relationships
                                                where species like "%{species_name}%");
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        kos_per_cluster_dict[row[0]] = {'kegg_kos': row[1]}

    # return the dictionary
    return kos_per_cluster_dict

#-------------------------------------------------------------------------------

def get_kegg_pathways_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the KEGG pathways of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    pathways_per_cluster_dict = {}

    # select rows from the table "emapper_annotations"
    if species_name == genlib.get_all_species_code():
        sentence = '''
                   SELECT cluster_id, kegg_pathways
                       FROM emapper_annotations
                   '''
    else:
        sentence = f'''
                    SELECT cluster_id, kegg_pathways
                        FROM emapper_annotations
                        WHERE cluster_id in (SELECT DISTINCT cluster_id
                                                FROM mmseqs2_relationships
                                                where species like "%{species_name}%");
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        pathways_per_cluster_dict[row[0]] = {'kegg_pathways': row[1]}

    # return the dictionary
    return pathways_per_cluster_dict

#-------------------------------------------------------------------------------
# table "mmseqs2_relationships"
#-------------------------------------------------------------------------------

def get_mmseqs2_relationship_dict(conn, cluster_id):
    '''
    Get rows data from the table "mmseqs2_relationships" corresponding to
    a cluster identification.
    '''

    # initialize the dictionary
    relationships_dict = {}

    # select rows from the table "mmseqs2_relationships"
    sentence = f'''
                SELECT cluster_id, seq_id, description, species
                    FROM mmseqs2_relationships
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        key = f'{row[0]}-{row[1]}'
        relationships_dict[key] = {'cluster_id': row[0], 'seq_id': row[1], 'description': row[2], 'species': row[3]}

    # return the dictionary
    return relationships_dict

#-------------------------------------------------------------------------------

def get_mmseqs2_seq_mf_data(conn, cluster_id):
    '''
    Get the most frequent description and species from the table "mmseqs2_relationships"
    corresponding to a cluster identification.
    '''

    # initialize the description, dictionary
    description_dict = {}

    # initialize the dictionary
    species_dict = {}

    # select rows from the table "mmseqs2_relationships"
    sentence = f'''
                SELECT description, species
                    FROM mmseqs2_relationships
                    WHERE cluster_id = "{cluster_id}";
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # count descriptions and species
    for row in rows:
        # descriptions
        description_counter = description_dict.get(row[0], 0)
        description_dict[row[0]] = description_counter + 1
        # species
        species_counter = species_dict.get(row[1], 0)
        species_dict[row[1]] = species_counter + 1

    # calculate the most frecuent description and species
    higher_counter = -1
    mf_description = ''
    for description, description_counter in description_dict.items():
        if description_counter > higher_counter:
            mf_description = description
            higher_counter = description_counter

    # calculate the most frecuent species
    higher_counter = -1
    mf_species = ''
    for species, species_counter in species_dict.items():
        if species_counter > higher_counter:
            mf_species = species
            higher_counter = species_counter

    # return the most frecuent species
    return mf_description, mf_species

#-------------------------------------------------------------------------------

def get_mmseqs2_species_list(conn):
    '''
    Get the distinct species names in the table "mmseqs2_relationships".
    '''

    # initialize the species names list
    species_names_list = []

    # select rows from the table "mmseqs2_relationships"
    sentence = '''
               SELECT DISTINCT species
                   FROM mmseqs2_relationships
                   ORDER by 1;
               '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)


    # add species name to the species names list
    for row in rows:
        if len(row[0].split()) == 2 and row[0][0].isalpha() and row[0][0].isupper() and not row[0].endswith('sp.') and row[0].find('AltName') == -1:
            species_names_list.append(row[0])

    # return the species names list
    return species_names_list

#-------------------------------------------------------------------------------

def get_goterms_per_cluster_dict(conn, species_name):
    '''
    Get the dictionary of the GO terms of each cluster corresponding to the species.
    '''

    # initialize the dictionary
    goterms_per_cluster_dict = {}

    # select rows from the table "interproscan_annotations"
    if species_name == genlib.get_all_species_code():
        sentence = '''
                   WITH cluster_identifications AS (
                       SELECT DISTINCT cluster_id
                       FROM mmseqs2_relationships
                   )
                   SELECT a.cluster_id, COALESCE(b.interpro_goterms, '-'), COALESCE(b.panther_goterms, '-'), COALESCE(c.goterms, '-')
                   FROM cluster_identifications a
                   LEFT JOIN interproscan_annotations b USING (cluster_id)
                   LEFT JOIN emapper_annotations c USING (cluster_id)
                   WHERE COALESCE(b.interpro_goterms, '-') != '-' OR COALESCE(b.panther_goterms, '-') != '-' OR COALESCE(c.goterms, '-') != '-'; 
                   '''
    else:
        sentence = f'''
                    WITH cluster_identifications AS (
                        SELECT DISTINCT cluster_id
                        FROM mmseqs2_relationships
                        WHERE species LIKE "%{species_name}%"
                    )
                    SELECT a.cluster_id, COALESCE(b.interpro_goterms, '-'), COALESCE(b.panther_goterms, '-'), COALESCE(c.goterms, '-')
                    FROM cluster_identifications a
                    LEFT JOIN interproscan_annotations b USING (cluster_id)
                    LEFT JOIN emapper_annotations c USING (cluster_id)
                    WHERE COALESCE(b.interpro_goterms, '-') != '-' OR COALESCE(b.panther_goterms, '-') != '-' OR COALESCE(c.goterms, '-') != '-';
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # add row data to the dictionary
    for row in rows:
        goterms_per_cluster_dict[row[0]] = {'interpro_goterms': row[1], 'panther_goterms': row[2], 'eggnog_goterms': row[3]}

    # return the dictionary
    return goterms_per_cluster_dict

#-------------------------------------------------------------------------------
# table "tair10_orthologs"
#-------------------------------------------------------------------------------

def get_tair10_ortholog_seq_id(conn, cluster_id):
    '''
    Get the TAIR 10 ortholog sequence identification of a cluster identification.
    '''

    # initialize ortholog sequence identification
    ortholog_seq_id = '-'

    # query
    sentence = f'''
                SELECT ortholog_seq_id
                    FROM tair10_orthologs
                    where cluster_id = '{cluster_id}';
                '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException(e, 'B002', sentence, conn)

    # get the row number
    for row in rows:
        ortholog_seq_id = row[0]
        break

    # return the ortholog sequence identification
    return ortholog_seq_id

#-------------------------------------------------------------------------------
# table "go_ontology"
#-------------------------------------------------------------------------------

def get_go_ontology_dict(conn, goterm_id_list):
    '''
    Get a dictionary of ontology from the table "go_ontology".
    '''

    # initialize the ontology dictionary
    go_onlology_dict = {}

    # select rows from the table "go_ontology"
    if goterm_id_list == []:
        sentence = '''
                   SELECT DISTINCT go_id, go_name, namespace
                       FROM go_ontology;
                   '''
    else:
        sentence = f'''
                    SELECT DISTINCT go_id, go_name, namespace
                        FROM go_ontology
                        WHERE go_id in ({genlib.join_string_list_to_string(goterm_id_list)});
                    '''
    try:
        rows = conn.execute(sentence)
    except Exception as e:
        raise genlib.ProgramException('B002', e, sentence, conn)

    # add ontology data to the dictionary
    for row in rows:
        go_onlology_dict[row[0]] = {'goterm_id':row[0], 'goterm_name':row[1], 'namespace':row[2]}

    # return the ontology dictionary
    return go_onlology_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('This source contains general functions for the maintenance of the TOA SQLite database in both console mode and gui mode.')
    sys.exit(0)

#-------------------------------------------------------------------------------
