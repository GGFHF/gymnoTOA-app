#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program build-external-inputs.py
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

APP_DIR=$TRABAJO/ProyectosVScode/gymnoTOA
DATA_DIR=$APP_DIR/data
OUTPUT_DIR=$APP_DIR/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $APP_DIR

#-------------------------------------------------------------------------------

# Execute the program build-external-inputs.py

/usr/bin/time \
    ./build-external-inputs.py \
        --annotations=$OUTPUT_DIR/nt-plant-annotation.csv.gz \
        --outdir=$OUTPUT_DIR \
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
