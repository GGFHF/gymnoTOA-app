#!/bin/bash

#-------------------------------------------------------------------------------

# This script processes a functional annotation using gymnoTOA-app.
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

# Control parameters

PARAM_NUM=8
if [ "$#" -ne "$PARAM_NUM" ]; then
    echo "*** ERROR: The following $PARAM_NUM parameters are required:"
    echo
    echo '    gymnotoa_app_dir <- path of the gymnoTOA-app directory.'
    echo '    gymnotoa_db_dir <- path of the gymnoTOA-db directory.'
    echo '    annotation_dir <- path of the annotation input directory.'
    echo '    species <- "all_species" or specific spcecies name.'
    echo '    method <- FDR method: "bh" (Benjamini-Hochberg) or "by" (Benjamini-Yekutieli).'
    echo '    msqannot <- minimum sequences number in annotations.'
    echo '    msqspec <- minimum sequences number in species.'
    echo '    enrichment_dir <- path of the enrichment output directory.'
    echo
    echo "Use: ${0##*/} gymnotoa_app_dir gymnotoa_db_dir annotation_dir species method msqannot msqspec enrichment_dir"
    exit 1
fi

GYMNOTOA_APP_DIR=${1}
GYMNOTOA_DB_DIR=${2}
ANNOTATION_DIR=${3}
SPECIES=${4}
METHOD=${5}
MSQANNOT=${6}
MSQSPEC=${7}
ENRICHMENT_DIR=${8}

#-------------------------------------------------------------------------------

# set other variables

SEP="#########################################"

#-------------------------------------------------------------------------------

# create directories

if [ -d "$ENRICHMENT_DIR" ]; then rm -rf $ENRICHMENT_DIR; fi; mkdir --parents $ENRICHMENT_DIR 

#-------------------------------------------------------------------------------

function init
{
    INIT_DATETIME=`date +%s`
    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "$SEP"
    echo "Enrichment analysis process started at $FORMATTED_INIT_DATETIME."
}

#-------------------------------------------------------------------------------

function calculate_besthit_enrichment_analysis
{
    echo "$SEP"
    echo "Calculation the enrichment analysis (best hit per sequence) ..."
    cd $ENRICHMENT_DIR
    source activate gymnotoa
    /usr/bin/time \
        $GYMNOTOA_APP_DIR/calculate-enrichment-analysis.py \
            --db=$GYMNOTOA_DB_DIR/gymnoTOA-db.db \
            --annotations=$ANNOTATION_DIR/functional-annotations-besthit.csv \
            --species=$SPECIES \
            --method=$METHOD \
            --msqannot=$MSQANNOT \
            --msqspec=$MSQSPEC \
            --goea=$ENRICHMENT_DIR/besthit-goterm-enrichment-analysis.csv \
            --mpea=$ENRICHMENT_DIR/besthit-metacyc-pathway-enrichment-analysis.csv \
            --koea=$ENRICHMENT_DIR/besthit-kegg-ko-enrichment-analysis.csv \
            --kpea=$ENRICHMENT_DIR/besthit-kegg-pathway-enrichment-analysis.csv \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-blast-data.py $RC; fi
    conda deactivate
    echo "Analysis is calculated."
}

#-------------------------------------------------------------------------------

function calculate_complete_enrichment_analysis
{
    echo "$SEP"
    echo "Calculation the enrichment analysis (all hits per sequence) ..."
    cd $ENRICHMENT_DIR
    source activate gymnotoa
    /usr/bin/time \
        $GYMNOTOA_APP_DIR/calculate-enrichment-analysis.py \
            --db=$GYMNOTOA_DB_DIR/gymnoTOA-db.db \
            --annotations=$ANNOTATION_DIR/functional-annotations-complete.csv \
            --species=$SPECIES \
            --method=$METHOD \
            --msqannot=$MSQANNOT \
            --msqspec=$MSQSPEC \
            --goea=$ENRICHMENT_DIR/complete-goterm-enrichment-analysis.csv \
            --mpea=$ENRICHMENT_DIR/complete-metacyc-pathway-enrichment-analysis.csv \
            --koea=$ENRICHMENT_DIR/complete-kegg-ko-enrichment-analysis.csv \
            --kpea=$ENRICHMENT_DIR/complete-kegg-pathway-enrichment-analysis.csv \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error load-blast-data.py $RC; fi
    conda deactivate
    echo "Analysis is calculated."
}

#-------------------------------------------------------------------------------

function end
{
    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "Enrichment analysis process ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
    echo "$SEP"
    exit 0
}

#-------------------------------------------------------------------------------

function manage_error
{
    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "ERROR: $1 returned error $2"
    echo "Enrichment analysis process ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
    echo "$SEP"
    exit 3
}

#-------------------------------------------------------------------------------

function calculate_duration
{
    DURATION=`expr $END_DATETIME - $INIT_DATETIME`
    HH=`expr $DURATION / 3600`
    MM=`expr $DURATION % 3600 / 60`
    SS=`expr $DURATION % 60`
    FORMATTED_DURATION=`printf "%03d:%02d:%02d\n" $HH $MM $SS`
}

#-------------------------------------------------------------------------------

init
calculate_besthit_enrichment_analysis
calculate_complete_enrichment_analysis
end
