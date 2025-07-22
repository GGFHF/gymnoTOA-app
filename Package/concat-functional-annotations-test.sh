#!/bin/bash

#-------------------------------------------------------------------------------

# This script executes a test of the program concat-annotations.py
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

# Set run environment

APP_DIR=$GYMNOTOA
DATA_DIR=$APP_DIR/data
OUTPUT_DIR=$APP_DIR/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $APP_DIR

#-------------------------------------------------------------------------------

# Run the program concat-functional-annotations.py

/usr/bin/time \
    ./concat-functional-annotations.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --blastp-alignments=$DATA_DIR/blastp-Acrogymnospermae-alignments.csv \
        --blastx-alignments=$DATA_DIR/blastx-Acrogymnospermae-alignments.csv \
        --blastn-alignments=$DATA_DIR/blast-lncRNA-alignments.csv \
        --complete_annotations=$OUTPUT_DIR/complete_functional-annotations.csv \
        --besthit_annotations=$OUTPUT_DIR/besthit_functional-annotations.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
