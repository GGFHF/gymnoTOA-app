#!/bin/bash

#-------------------------------------------------------------------------------

# This example script shows how to run a functional annotation followed by an enrichment
# analysis of annotation results using the scripts run-annotation-pipeline-process.sh
# and run-enrichment-analysis-process.sh.
#
# This software has been developed by:
#
#    GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
#    Dpto. Sistemas y Recursos Naturales
#    ETSI Montes, Forestal y del Medio Natural
#    Universidad Politecnica de Madrid
#    https://github.com/ggfhf/
#
# Licence: GNU General Public Licence Version 3.

#-------------------------------------------------------------------------------

# Infrastructure
# ==============
#
# Before executing this script it is necessary that the software used is installed
# (Miniforge3, CodAn, BLAST+ and DIAMOND) and the gymnoTOA-db is downloaded. Check
# how to perform these actions in the capter "Functional annotation and enrichment
# analysis on Linux servers" of gymnoTOA-app manual.

#-------------------------------------------------------------------------------

# Parameters
# ==========

# This is an example script. Modify the paths of file and directories to assign them
# to PROPER LOCATIONS of the computer where this script will be run.
# The values of the other parameters are assigned according to the experiment.

# commom parameters
GYMNOTOA_APP_DIR=$HOME/Apps/gymnoTOA-app/Package
GYMNOTOA_DB_DIR=$HOME/BioData/gymnoTOA-db
GYMNOTOA_PIPELINES_DIR=$HOME/Apps/gymnoTOA-app/pipelines

# annotation parameters (descriptions in run-annotation-pipeline-process.sh)
FASTA_TYPE=TRANSCRIPTS
FASTA_FILE=$HOME/Apps/gymnoTOA-app/sample-data/PinusCanariensisXilogenesisGESU01.1-1000seqs.fsa
MODEL=PLANTS_full
ALIGNER=BLAST+
EVALUE=1E-6
MAX_TARGET_SEQS=20
MAX_HSPS=999999
QCOV_HSP_PERC=0.0
THREADS=4
ANNOTATION_DIR=$HOME/results/annotation-test

# enrichment parameters (descriptions in run-enrichment-analysis-process.sh)
SPECIES=all_species
METHOD=by
MSQANNOT=5
MSQSPEC=10
ENRICHMENT_DIR=$HOME/results/enrichment-test

#-------------------------------------------------------------------------------

# process the functional annotation

$GYMNOTOA_PIPELINES_DIR/run-annotation-pipeline-process.sh \
    $GYMNOTOA_APP_DIR \
    $GYMNOTOA_DB_DIR \
    $FASTA_TYPE \
    $FASTA_FILE \
    $MODEL \
    $ALIGNER \
    $EVALUE \
    $MAX_TARGET_SEQS \
    $MAX_HSPS \
    $QCOV_HSP_PERC \
    $THREADS \
    $ANNOTATION_DIR
RC=$?
if [ $RC -ne 0 ]; then exit 1; fi

#-------------------------------------------------------------------------------

# process the enrichment analysis

$GYMNOTOA_PIPELINES_DIR/run-enrichment-analysis-process.sh \
    $GYMNOTOA_APP_DIR \
    $GYMNOTOA_DB_DIR \
    $ANNOTATION_DIR \
    $SPECIES \
    $METHOD \
    $MSQANNOT \
    $MSQSPEC \
    $ENRICHMENT_DIR
RC=$?
if [ $RC -ne 0 ]; then exit 1; fi

#-------------------------------------------------------------------------------
