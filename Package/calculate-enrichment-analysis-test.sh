#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program calculate-enrichment-analysis.py
# in a Linux environment.
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

# Control parameters

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# Set environment

APP_DIR=$GYMNOTOA
DATA_DIR=$APP_DIR/data
OUTPUT_DIR=$APP_DIR/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $APP_DIR

#-------------------------------------------------------------------------------

# Execute the program calculate-enrichment-analysis.py

/usr/bin/time \
    ./calculate-enrichment-analysis.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --annotations=$OUTPUT_DIR/annotations.csv \
        --species="Pinus taeda" \
        --method=by \
        --msqannot=5 \
        --msqspec=10 \
        --goea=$OUTPUT_DIR/goterm-enrichment-analysis.csv \
        --mpea=$OUTPUT_DIR/metacyc-pathway-enrichment-analysis.csv \
        --koea=$OUTPUT_DIR/kegg-ko-enrichment-analysis.csv \
        --kpea=$OUTPUT_DIR/kegg-pathway-enrichment-analysis.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

echo
echo '**************************************************'
exit 0

#-------------------------------------------------------------------------------
