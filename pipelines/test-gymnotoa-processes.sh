#!/bin/bash

#-------------------------------------------------------------------------------

# This script tests a functional annotation process followed by an enrichment
# analysis of annotation results using the scripts run-annotation-pipeline-process.sh
#  and run-enrichment-analysis-process.sh.
#
# This software has been developed by:
#
#    GI en Especies Leñosas (WooSp)
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
# (Miniconda3, CodAn, BLAST+ and DIAMOND) and the gymnoTOA-db is downloaded. Check
# how to perform these actions in the gymnoTOA-app manual.

#-------------------------------------------------------------------------------

# commom parameters
GYMNOTOA_APP_DIR=$HOME/Apps/gymnoTOA-app-main/Package
MINICONDA3_DIR=$HOME/gymnoTOA-app-Miniconda3
DBS_DIR=$HOME/gymnoTOA-app-databases

# annotation parameters (descriptions in run-annotation-pipeline-process.sh)
TRANSCRIPTS=$HOME/Apps/gymnoTOA/sample-data/PinusCanariensisXilogenesisGESU01.1-1000seqs.fsa
MODEL=PLANTS_full
ALIGNER=DIAMOND
EVALUE=1E-6
MAX_TARGET_SEQS=20
MAX_HSPS=999999
QCOV_HSP_PERC=0.0
THREADS=4
ANNOTATION_DIR=$HOME/Documents/annotation-test

# enrichment parameters (descriptions in run-enrichment-analysis-process.sh)
SPECIES=all_species
METHOD=by
MSQANNOT=5
MSQSPEC=10
ENRICHMENT_DIR=$HOME/Documents/enrichment-test

#-------------------------------------------------------------------------------

# process the funcional annotation

$GYMNOTOA_APP_DIR/pipelines/run-annotation-pipeline-process.sh \
    $GYMNOTOA_APP_DIR \
    $MINICONDA3_DIR \
    $DBS_DIR \
    $TRANSCRIPTS \
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

$GYMNOTOA_APP_DIR/pipelines/run-enrichment-analysis-process.sh \
    $GYMNOTOA_APP_DIR \
    $MINICONDA3_DIR \
    $DBS_DIR \
    $ANNOTATION_DIR \
    $SPECIES \
    $METHOD \
    $MSQANNOT \
    $MSQSPEC \
    $ENRICHMENT_DIR
RC=$?
if [ $RC -ne 0 ]; then exit 1; fi

#-------------------------------------------------------------------------------
