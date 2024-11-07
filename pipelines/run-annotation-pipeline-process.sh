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

if [ "$#" -ne 12 ]; then
    echo '*** ERROR: The following 12 parameters are required:'
    echo
    echo '    gymnotoa_app_dir <- path of the gymnoTOA-app directory.'
    echo '    miniconda3_dir <- path of the gymnoTOA-app Miniconda3 directory (miniconda3_dir value in gymnoTOA-appconfig file).'
    echo '    dbs_dir <- path of the gymnoTOA-app databases directory (database_dir value in gymnoTOA-appconfig file).'
    echo '    transcripts <- transcripts file path.'
    echo '    model <- CodAn model: PLANTS_full or PLANTS_partial.'
    echo '    aligner <- alignment software: BLAST+ or DIAMOND.'
    echo '    ev <- evalue (BLAST+ and DIAMOND parameter).'
    echo '    mts <- max_target_seqs (BLAST+ and DIAMOND parameter).'
    echo '    mh <- max_hsps (BLAST+ and DIAMOND parameter).'
    echo '    qhp <- qcov_hsp_perc (BLAST+ parameter) or 0 (if DIAMOND).'
    echo '    threads <- threads number.'
    echo '    annotation_dir <- path of the annotation output directory.'
    echo
    echo "Use: ${0##*/} gymnotoa_app_dir miniconda3_dir dbs_dir transcripts model aligner ev mts mh qhp threads annotation_dir"
    exit 1
fi

GYMNOTOA_APP_DIR=${1}
MINICONDA3_DIR=${2}
DBS_DIR=${3}
TRANSCRIPTS=${4}
MODEL=${5}
ALIGNER=${6}
EVALUE=${7}
MAX_TARGET_SEQS=${8}
MAX_HSPS=${9}
QCOV_HSP_PERC=${10}
THREADS=${11}
ANNOTATION_DIR=${12}

#-------------------------------------------------------------------------------

# set other variables

MINICONDA3_BIN_DIR=$MINICONDA3_DIR/bin
TEMP=$ANNOTATION_DIR/temp
SEP="#########################################"

#-------------------------------------------------------------------------------

# create directories

if [ -d "$ANNOTATION_DIR" ]; then rm -rf $ANNOTATION_DIR; fi; mkdir --parents $ANNOTATION_DIR 
if [ -d "$TEMP" ]; then rm -rf $TEMP; fi; mkdir --parents $TEMP 

#-------------------------------------------------------------------------------

function init
{
    INIT_DATETIME=`date +%s`
    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "$SEP"
    echo "Functional annotation process started at $FORMATTED_INIT_DATETIME."
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

function predict_orfs
{
    echo "$SEP"
    echo "Predicting ORFs and getting peptide sequences ..."
    cd $ANNOTATION_DIR
    source activate codan
    /usr/bin/time \
        codan.py \
            --cpu=$THREADS \
            --model=$MINICONDA3_DIR/envs/codan/models/$MODEL \
            --transcripts=$TRANSCRIPTS \
            --output=$ANNOTATION_DIR/codan_output
    RC=$?
    if [ $RC -ne 0 ]; then manage_error codan.py $RC; fi
    conda deactivate
    echo "ORFs are predicted and peptide sequences are gotten."
}

#-------------------------------------------------------------------------------

function align_peptides_2_alignment_tool_acrogymnospermae_db
{
    echo "$SEP"
    cd $ANNOTATION_DIR
    if [ "$ALIGNER" = "BLAST+" ]; then
        echo "Aligning peptides to BLAST+ Acrogymnospermae database ..."
        source activate blast
        export BLASTDB=$DBS_DIR/gymnoTOA-db/Acrogymnospermae-consensus-blastplus-db
        /usr/bin/time \
            blastp \
                -num_threads $THREADS \
                -db Acrogymnospermae-consensus-diamond-db \
                -query $ANNOTATION_DIR/codan_output/PEP_sequences.fa \
                -evalue $EVALUE \
                -max_target_seqs $MAX_TARGET_SEQS \
                -max_hsps $MAX_HSPS \
                -qcov_hsp_perc $QCOV_HSP_PERC \
                -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
                -out $TEMP/blastp-clade-alignments.csv
        RC=$?
        if [ $RC -ne 0 ]; then manage_error blastp $RC; fi
        conda deactivate
        echo "Alignment is done."
    elif [ "$ALIGNER" = "DIAMOND" ]; then
        echo "Aligning peptides to DIAMOND Acrogymnospermae database ..."
        source activate diamond
        /usr/bin/time \
            diamond blastp \
                --threads 4 \
                --db $DBS_DIR/gymnoTOA-db/Acrogymnospermae-consensus-diamond-db/Acrogymnospermae-consensus-diamond-db \
                --query $ANNOTATION_DIR/codan_output/PEP_sequences.fa \
                --evalue $EVALUE \
                --max-target-seqs $MAX_TARGET_SEQS \
                --max-hsps $MAX_HSPS \
                --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \
                --out $TEMP/blastp-clade-alignments.csv
        RC=$?
        if [ $RC -ne 0 ]; then manage_error diamond-blastp $RC; fi
        conda deactivate
        echo "Alignment is done."
    else
        manage_error aligner_parameter_wrong 0
    fi
}

#-------------------------------------------------------------------------------
function align_transcriptome_2_alignment_tool_acrogymnospermae_db
{

    echo "$SEP"
    cd $ANNOTATION_DIR
    if [ "$ALIGNER" = "BLAST+" ]; then
        echo "Aligning transcriptome to BLAST+ Acrogymnospermae database ..."
        source activate blast
        export BLASTDB=$DBS_DIR/gymnoTOA-db/Acrogymnospermae-consensus-blastplus-db
        /usr/bin/time \
            blastx \
                -num_threads $THREADS \
                -db Acrogymnospermae-consensus-diamond-db \
                -query $TRANSCRIPTS \
                -evalue $EVALUE \
                -max_target_seqs $MAX_TARGET_SEQS \
                -max_hsps $MAX_HSPS \
                -qcov_hsp_perc $QCOV_HSP_PERC \
                -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
                -out $TEMP/blastx-clade-alignments.csv
        RC=$?
        if [ $RC -ne 0 ]; then manage_error blastx $RC; fi
        conda deactivate
        echo "Alignment is done."
    elif [ "$ALIGNER" = "DIAMOND" ]; then
        echo "Aligning transcriptome to DIAMOND Acrogymnospermae database ..."
        source activate diamond
        /usr/bin/time \
            diamond blastx \
                --threads 4 \
                --db $DBS_DIR/gymnoTOA-db/Acrogymnospermae-consensus-diamond-db/Acrogymnospermae-consensus-diamond-db \
                --query $TRANSCRIPTS \
                --evalue $EVALUE \
                --max-target-seqs $MAX_TARGET_SEQS \
                --max-hsps $MAX_HSPS \
                --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \
                --out $TEMP/blastx-clade-alignments.csv
        RC=$?
        if [ $RC -ne 0 ]; then manage_error diamond-blastx $RC; fi
        conda deactivate
        echo "Alignment is done."
    else
        manage_error aligner_parameter_wrong 0
    fi

}

#-------------------------------------------------------------------------------

function align_trancriptome_2_blastplus_lncrna_db
{
    echo "$SEP"
    echo "Aligning trancriptome to BLAST+ lncRNA database ..."
    cd $ANNOTATION_DIR
    source activate blast
    export BLASTDB=$DBS_DIR/gymnoTOA-db/lncRNA-blastplus-db
    /usr/bin/time \
        blastn \
            -num_threads 4 \
            -db lncRNA-blastplus-db \
            -query $TRANSCRIPTS \
            -evalue 1E-3 \
            -max_target_seqs 1 \
            -max_hsps 1 \
            -qcov_hsp_perc 0.0 \
            -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
            -out $TEMP/blastn-lncrna-alignments.csv
    RC=$?
    if [ $RC -ne 0 ]; then manage_error blastn $RC; fi
    conda deactivate
    echo "Alignment is done."
}

#-------------------------------------------------------------------------------

function concat_functional_annotations
{
    echo "$SEP"
    echo "Concatenating functional annotation to alignment file ..."
    cd $ANNOTATION_DIR
    /usr/bin/time \
        $GYMNOTOA_APP_DIR/concat-functional-annotations.py \
            --db=$DBS_DIR/gymnoTOA-db/gymnoTOA-db.db \
            --blastp-alignments=$TEMP/blastp-clade-alignments.csv \
            --blastx-alignments=$TEMP/blastx-clade-alignments.csv \
            --blastn-alignments=$TEMP/blastn-lncrna-alignments.csv \
            --complete_annotations=$ANNOTATION_DIR/functional-annotations-complete.csv \
            --besthit_annotations=$ANNOTATION_DIR/functional-annotations-besthit.csv \
            --verbose=N \
            --trace=N
        RC=$?
        if [ $RC -ne 0 ]; then manage_error concat-functional-annotations.py $RC; fi
        echo "Data are loaded."
}

#-------------------------------------------------------------------------------

function sort_functional_annotations
{
    echo "$SEP"
    echo "Sorting functional annotations files ..."
    cd $ANNOTATION_DIR
    /usr/bin/time \
        sort \
            --output=$ANNOTATION_DIR/functional-annotations-complete.csv \
            $ANNOTATION_DIR/functional-annotations-complete.csv
    RC=$?
    if [ $RC -ne 0 ]; then manage_error sort $RC; fi
    /usr/bin/time \
        sort \
            --output=$ANNOTATION_DIR/functional-annotations-besthit.csv \
            $ANNOTATION_DIR/functional-annotations-besthit.csv
    RC=$?
    if [ $RC -ne 0 ]; then manage_error sort $RC; fi
    echo "Files are sorted."
}

#-------------------------------------------------------------------------------

function add_heads
{

    echo "$SEP"
    echo "Adding head to annotations files ..."
    cd $ANNOTATION_DIR
    /usr/bin/time \
        sed \
            --in-place \
            "1i qseqid;sseqid;pident;length;mismatch;gapopen;qstart;qend;sstart;send;evalue;bitscore;algorithm;ncbi_description;ncbi_species;tair10_ortholog_seq_id;interpro_goterms;panther_goterms;metacyc_pathways;eggnog_ortholog_seq_id;eggnog_ortholog_species;eggnog_ogs;cog_category;eggnog_description;eggnog_goterms;ec;kegg_kos;kegg_pathways;kegg_modules;kegg_reactions;kegg_rclasses;brite;kegg_tc;cazy;pfams" \
            ./functional-annotations-complete.csv
    RC=$?
    if [ $RC -ne 0 ]; then manage_error sed $RC; fi
    /usr/bin/time \
        sed \
            --in-place \
            "1i qseqid;sseqid;pident;length;mismatch;gapopen;qstart;qend;sstart;send;evalue;bitscore;algorithm;ncbi_description;ncbi_species;tair10_ortholog_seq_id;interpro_goterms;panther_goterms;metacyc_pathways;eggnog_ortholog_seq_id;eggnog_ortholog_species;eggnog_ogs;cog_category;eggnog_description;eggnog_goterms;ec;kegg_kos;kegg_pathways;kegg_modules;kegg_reactions;kegg_rclasses;brite;kegg_tc;cazy;pfams" \
            ./functional-annotations-besthit.csv
    RC=$?
    if [ $RC -ne 0 ]; then manage_error sed $RC; fi
    echo "Heads are added."
}

#-------------------------------------------------------------------------------

function calculate_functional_annotation_stats
{
    echo "$SEP"
    echo "Calculating functional annotation statistics ..."
    cd $ANNOTATION_DIR
    /usr/bin/time \
        $GYMNOTOA_APP_DIR/calculate-functional-annotation-stats.py \
            --db=$DBS_DIR/gymnoTOA-db/gymnoTOA-db.db \
            --annotations=$ANNOTATION_DIR/functional-annotations-complete.csv \
            --outdir=$ANNOTATION_DIR \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-functional-annotation-stats.py $RC; fi
    echo "Statistics are calculated."
}

#-------------------------------------------------------------------------------

function build_external_inputs
{
    echo "$SEP"
    echo "Building inputs to external applications ..."
    cd $ANNOTATION_DIR
    /usr/bin/time \
        $GYMNOTOA_APP_DIR/build-external-inputs.py \
            --annotations=./functional-annotations-complete.csv \
            --outdir=$ANNOTATION_DIR \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error build-external-inputs.py $RC; fi
    echo "Inputs are built."
}

#-------------------------------------------------------------------------------

function end
{
    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "Functional annotation process ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
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
    echo "Functional annotation process ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
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
predict_orfs
align_peptides_2_alignment_tool_acrogymnospermae_db
align_transcriptome_2_alignment_tool_acrogymnospermae_db
align_trancriptome_2_blastplus_lncrna_db
concat_functional_annotations
sort_functional_annotations
add_heads
calculate_functional_annotation_stats
build_external_inputs
end
