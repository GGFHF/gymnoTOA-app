#!/bin/bash

#-------------------------------------------------------------------------------

# This script processes a functional annotation using gymnoTOA-app.
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

# Control parameters

if [ "$#" -ne 9 ]; then
    echo '*** ERROR: The following 9 parameters are required:'
    echo
    echo '    gymnotoa_app_dir <- path of the gymnoTOA-app directory.'
    echo '    miniconda3_dir <- path of the gymnoTOA-app Miniconda3 directory (miniconda3_dir value in gymnoTOA-appconfig file).'
    echo '    dbs_dir <- path of the gymnoTOA-app databases directory (database_dir value in gymnoTOA-appconfig file).'
    echo '    annotation_dir <- path of the annotation input directory.'
    echo '    species <- all_species or specific spcecies name.'
    echo '    method <- FDR method: bh (Benjamini-Hochberg) or by (Benjamini-Yekutieli).'
    echo '    msqannot <- minimum sequences number in annotations.'
    echo '    msqspec <- minimum sequences number in species.'
    echo '    enrichment_dir <- path of the enrichment output directory.'
    echo
    echo "Use: ${0##*/} gymnotoa_app_dir miniconda3_dir dbs_dir annotation_dir species method msqannot msqspec enrichment_dir"
    exit 1
fi

GYMNOTOA_APP_DIR=${1}
MINICONDA3_DIR=${2}
DBS_DIR=${3}
ANNOTATION_DIR=${4}
SPECIES=${5}
METHOD=${6}
MSQANNOT=${7}
MSQSPEC=${8}
ENRICHMENT_DIR=${9}

#-------------------------------------------------------------------------------

# set other variables

MINICONDA3_BIN_DIR=$MINICONDA3_DIR/bin
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

function activate_env_base
{
    echo "$SEP"
    echo "Activating environment base ..."
    source $MINICONDA3_BIN_DIR/activate
    RC=$?
    if [ $RC -ne 0 ]; then manage_error conda $RC; fi
    echo "Environment is activated."
}

#-------------------------------------------------------------------------------

function calculate_besthit_enrichment_analysis
{
    echo "$SEP"
    echo "Calculation the enrichment analysis (best hit per sequence) ..."
    cd $ENRICHMENT_DIR
    /usr/bin/time \
        $GYMNOTOA_APP_DIR/calculate-enrichment-analysis.py \
            --db=$DBS_DIR/gymnoTOA-db/gymnoTOA-db.db \
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
    echo "Analysis is calculated."
}

#-------------------------------------------------------------------------------

function calculate_complete_enrichment_analysis
{
    echo "$SEP"
    echo "Calculation the enrichment analysis (all hits per sequence) ..."
    cd $ENRICHMENT_DIR
        /usr/bin/time \
            $GYMNOTOA_APP_DIR/calculate-enrichment-analysis.py \
                --db=$DBS_DIR/gymnoTOA-db/gymnoTOA-db.db \
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
activate_env_base
calculate_besthit_enrichment_analysis
calculate_complete_enrichment_analysis
end
